#!/usr/bin/env python3
"""
Archive an active ExecPlan: move to completed/deferred/superseded, remove TODO block,
rewrite links, append log bullet(s).

Requirements: Python 3.12+ stdlib only. Prefer running from repo root.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_lib import (  # noqa: E402
    ACTIVE_DIR,
    ARCHIVE_DIRS,
    REPO_ROOT,
    TODO_PATH,
    is_checkbox_item,
    parse_todo_items,
    plan_path,
    validate_slug,
    write_text_under,
)

CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
MAINTENANCE_PATH = REPO_ROOT / "MAINTENANCE.md"
NONE_YET_RE = re.compile(r"^- \(none yet\b", re.IGNORECASE)


def _run_git_mv(src: Path, dest: Path, *, dry_run: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise SystemExit(
            f"ERROR: archive — refusing to overwrite existing {dest.relative_to(REPO_ROOT)}"
        )
    if dry_run:
        print(f"DRY-RUN: git mv {src.relative_to(REPO_ROOT)} -> {dest.relative_to(REPO_ROOT)}")
        return
    try:
        subprocess.run(
            ["git", "mv", str(src), str(dest)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        if dest.exists():
            raise SystemExit(
                f"ERROR: archive — git mv failed and destination already exists: "
                f"{dest.relative_to(REPO_ROOT)}"
            ) from None
        shutil.move(str(src), str(dest))


def _set_status_and_outcomes(text: str, dest: str, message: str | None) -> str:
    text2, n = re.subn(
        r"(\*\*Status:\*\*\s*)(active|completed|deferred|superseded)\b",
        rf"\1{dest}",
        text,
        count=1,
    )
    if n == 0:
        lines = text2.splitlines()
        insert_at = 1 if lines else 0
        lines.insert(insert_at, f"**Status:** {dest}")
        text2 = "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    if message:
        outcomes = message.strip()
        if len(outcomes) < 100:
            outcomes = outcomes + " " + (
                "This archive closes the plan on the same PR as the implementing work, "
                "per repo harness same-PR close rules."
            )
        pattern = r"(## Outcomes & retrospective\n)(.*?)(\n## |\Z)"

        def _sub(m: re.Match[str]) -> str:
            return f"{m.group(1)}\n{outcomes}\n{m.group(3)}"

        text2, count = re.subn(pattern, _sub, text2, count=1, flags=re.DOTALL)
        if count == 0:
            text2 = text2.rstrip() + f"\n\n## Outcomes & retrospective\n\n{outcomes}\n"
    return text2


def _find_todo_item_for_slug(slug: str):
    text = TODO_PATH.read_text(encoding="utf-8")
    for item in parse_todo_items(text):
        if slug in item.plan_slugs or f"active/{slug}.md" in item.text:
            return item
        bold = re.search(r"\*\*([^*]+)\*\*", item.first_line)
        if bold and re.sub(r"[^a-z0-9]+", "-", bold.group(1).lower()).strip("-") == slug:
            return item
    return None


def _remove_todo_block(slug: str, *, dry_run: bool) -> bool:
    text = TODO_PATH.read_text(encoding="utf-8")
    items = parse_todo_items(text)
    plain = text.splitlines()
    target = None
    for item in items:
        if slug in item.plan_slugs or f"active/{slug}.md" in item.text:
            target = item
            break
        bold = re.search(r"\*\*([^*]+)\*\*", item.first_line)
        if bold and re.sub(r"[^a-z0-9]+", "-", bold.group(1).lower()).strip("-") == slug:
            target = item
            break
    if target is None:
        return False

    start = target.start_line - 1
    end = start + 1
    while end < len(plain):
        if is_checkbox_item(plain[end]):
            break
        if re.match(r"^## ", plain[end]):
            break
        if re.match(r"^### ", plain[end]):
            break
        end += 1

    new_plain = plain[:start] + plain[end:]
    new_text = "\n".join(new_plain) + ("\n" if text.endswith("\n") else "")
    if dry_run:
        print(f"DRY-RUN: remove TODO.md lines {start + 1}-{end}")
        return True
    # TODO_PATH is a fixed repo-root constant (not CLI-derived).
    TODO_PATH.write_text(new_text, encoding="utf-8")
    return True


def _rewrite_links(slug: str, dest: str, *, dry_run: bool) -> None:
    old = f"docs/plans/active/{slug}.md"
    new = f"docs/plans/{dest}/{slug}.md"
    replacements = (
        (old, new),
        (f"docs/plans/active/{slug}", f"docs/plans/{dest}/{slug}"),
        (f"../active/{slug}.md", f"../{dest}/{slug}.md"),
        (f"](active/{slug}.md)", f"]({dest}/{slug}.md)"),
        (f"(active/{slug}.md)", f"({dest}/{slug}.md)"),
    )
    roots = [
        REPO_ROOT / "docs",
        REPO_ROOT / "README.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".github" / "workflows",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            if root.name == "workflows":
                files.extend(root.glob("*.yml"))
                files.extend(root.glob("*.yaml"))
            else:
                files.extend(root.rglob("*.md"))

    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if f"active/{slug}" not in text:
            continue
        updated = text
        for old_s, new_s in replacements:
            updated = updated.replace(old_s, new_s)
        if updated == text:
            continue
        if dry_run:
            print(f"DRY-RUN: rewrite links in {path.relative_to(REPO_ROOT)}")
        else:
            path.write_text(updated, encoding="utf-8")


def _log_path_for_kind(kind: str) -> Path:
    """Resolve log path from a closed set of kinds (never from a free-form path)."""
    if kind == "user":
        return CHANGELOG_PATH
    if kind == "maintenance":
        return MAINTENANCE_PATH
    raise SystemExit(f"unknown log kind: {kind}")


def _append_log(kind: str, bullet: str, *, dry_run: bool) -> None:
    """Append under ## [Unreleased] / ### Added for a whitelist log kind."""
    path = _log_path_for_kind(kind)
    if not path.is_file():
        raise SystemExit(f"log file missing: {path}")
    text = path.read_text(encoding="utf-8")
    marker = "## [Unreleased]"
    if marker not in text:
        raise SystemExit(f"{path.name} missing {marker} section")
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    inserted = False
    while i < len(lines):
        out.append(lines[i])
        if not inserted and lines[i].strip() == marker:
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                out.append(lines[j])
                j += 1
            if j < len(lines) and lines[j].strip() == "### Added":
                out.append(lines[j])
                j += 1
                # Drop recognized empty-state placeholders before first real bullet.
                while j < len(lines) and NONE_YET_RE.match(lines[j].strip()):
                    j += 1
                out.append(f"- {bullet}")
                i = j - 1
                inserted = True
            else:
                out.append("")
                out.append("### Added")
                out.append(f"- {bullet}")
                inserted = True
        i += 1
    if not inserted:
        raise SystemExit(f"failed to insert into {path.name}")
    new_text = "\n".join(out) + ("\n" if text.endswith("\n") else "")
    if dry_run:
        print(f"DRY-RUN: append to {path.name}: - {bullet}")
        return
    path.write_text(new_text, encoding="utf-8")


def _refresh_pr_pending_for_slug(text: str, slug: str, pr: int) -> str:
    """Replace 'PR pending' only on lines that mention this slug."""
    if pr <= 0 or "PR pending" not in text:
        return text
    out: list[str] = []
    for line in text.splitlines():
        if "PR pending" in line and (f"`{slug}`" in line or f"/{slug}" in line or slug in line):
            out.append(line.replace("PR pending", f"PR #{pr}"))
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _ensure_log_bullet(slug: str, pr: int, kind: str, message: str | None, *, dry_run: bool) -> None:
    """Append or refresh the Unreleased log bullet for this slug (idempotent)."""
    today = dt.date.today().isoformat()
    pr_label = "PR pending" if pr <= 0 else f"PR #{pr}"
    if message:
        bullet = f"{message.rstrip('.')} ({pr_label}, {today})"
    else:
        bullet = f"Archived plan `{slug}` → `docs/plans/` ({pr_label}, {today})"

    kinds: list[str] = []
    if kind in ("maintenance", "both"):
        kinds.append("maintenance")
    if kind in ("user", "both"):
        kinds.append("user")

    for log_kind in kinds:
        path = _log_path_for_kind(log_kind)
        text = path.read_text(encoding="utf-8")
        mentions = f"`{slug}`" in text or f"/{slug}" in text
        if message and message[:48] in text:
            mentions = True
        if mentions:
            updated = _refresh_pr_pending_for_slug(text, slug, pr)
            if updated != text:
                if dry_run:
                    print(f"DRY-RUN: refresh PR # for {slug!r} in {path.name}")
                else:
                    path.write_text(updated, encoding="utf-8")
            elif dry_run:
                print(f"DRY-RUN: log already mentions {slug!r} in {path.name}")
            continue
        _append_log(log_kind, bullet, dry_run=dry_run)


def archive(
    slug: str,
    pr: int,
    dest: str,
    kind: str,
    message: str | None,
    *,
    dry_run: bool,
    require_todo: bool = True,
) -> int:
    try:
        slug = validate_slug(slug)
    except ValueError as exc:
        raise SystemExit(f"ERROR: archive — {exc}") from exc

    src = plan_path(ACTIVE_DIR, slug)
    dest_dir = ARCHIVE_DIRS[dest]
    dest_path = plan_path(dest_dir, slug)
    already = dest_path.is_file() and not src.is_file()

    if src.is_file() and dest_path.is_file():
        raise SystemExit(
            f"ERROR: archive — both active and {dest}/ copies exist for {slug!r}; "
            "resolve manually before re-running"
        )

    # Preflight: validate TODO before any filesystem mutation.
    if not already and require_todo and _find_todo_item_for_slug(slug) is None:
        raise SystemExit(
            f"ERROR: archive — TODO.md:1 no open bullet found for slug {slug!r}; "
            "same-PR close requires removing the TODO item (checked before archive)"
        )

    if already:
        print(f"already archived: {dest_path.relative_to(REPO_ROOT)} — converging TODO/log")
    elif not src.is_file():
        raise SystemExit(f"active plan not found: {src.relative_to(REPO_ROOT)}")
    else:
        text = src.read_text(encoding="utf-8")
        updated = _set_status_and_outcomes(text, dest, message)
        content = updated if updated.endswith("\n") else updated + "\n"
        if not dry_run:
            # Write via whitelist directory + validated slug basename (Sonar S2083/S8707).
            write_text_under(ACTIVE_DIR, f"{slug}.md", content)
        else:
            print(f"DRY-RUN: would set status={dest} and outcomes on {slug}")
        _run_git_mv(src, dest_path, dry_run=dry_run)

    removed = _remove_todo_block(slug, dry_run=dry_run)
    if not removed and require_todo and not already:
        raise SystemExit(
            f"ERROR: archive — TODO.md:1 no open bullet found for slug {slug!r}; "
            "same-PR close requires removing the TODO item"
        )
    if not removed and already:
        print(f"TODO.md already has no open bullet for {slug!r}")

    if not already:
        _rewrite_links(slug, dest, dry_run=dry_run)

    _ensure_log_bullet(slug, pr, kind, message, dry_run=dry_run)
    print(f"archived {slug} -> docs/plans/{dest}/{slug}.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument(
        "--dest",
        choices=sorted(ARCHIVE_DIRS),
        default="completed",
    )
    parser.add_argument(
        "--kind",
        choices=("user", "maintenance", "both"),
        default="maintenance",
    )
    parser.add_argument("--message", default=None, help="Outcomes text / log bullet stem")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return archive(
        args.slug,
        args.pr,
        args.dest,
        args.kind,
        args.message,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
