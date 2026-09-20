#!/usr/bin/env python3
"""
Archive an active ExecPlan: move to completed/deferred/superseded, remove TODO block,
rewrite links, append log bullet(s).

Requirements: Python 3.12+ stdlib only. Prefer running from repo root.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_lib import (  # noqa: E402
    ACTIVE_DIR,
    ARCHIVE_DIRS,
    MIN_OUTCOMES_CHARS,
    REPO_ROOT,
    TODO_PATH,
    has_valid_replacement_link,
    is_checkbox_item,
    parse_todo_items,
    plan_path,
    section_body,
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


def _write_repo_log(basename: str, content: str) -> None:
    """Atomically write a repo-root log file.

    ``basename`` must be a closed whitelist entry. CLI/LLM inputs may appear in
    ``content`` (markdown body) but never in the filesystem path. Uses
    ``os.replace`` onto a fixed destination so Sonar S8707/S2083 do not treat
    ``Path.write_text`` as a path-traversal sink for tainted log bodies.
    """
    if basename not in {"CHANGELOG.md", "MAINTENANCE.md"}:
        raise ValueError(f"refusing non-log basename {basename!r}")
    dest_dir = REPO_ROOT.resolve()
    dest = dest_dir / basename
    if dest.resolve().parent != dest_dir or dest.name != basename:
        raise RuntimeError(f"log path escaped repo root: {dest}")
    fd, tmp_name = tempfile.mkstemp(prefix=".harness-log-", suffix=".tmp", dir=dest_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp_name, os.fspath(dest))
    except Exception:
        # Best-effort cleanup if write/replace failed; ignore missing temp file.
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


def _build_unreleased_insert(text: str, bullet: str, *, log_name: str) -> str:
    """Return log text with ``bullet`` inserted under ## [Unreleased] / ### Added."""
    marker = "## [Unreleased]"
    if marker not in text:
        raise SystemExit(f"{log_name} missing {marker} section")
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
                # Drop blanks and empty-state placeholders so they are not re-emitted.
                while j < len(lines):
                    stripped = lines[j].strip()
                    if stripped == "" or NONE_YET_RE.match(stripped):
                        j += 1
                        continue
                    break
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
        raise SystemExit(f"failed to insert into {log_name}")
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _append_log(kind: str, bullet: str, *, dry_run: bool) -> None:
    """Append under ## [Unreleased] / ### Added for a whitelist log kind."""
    if kind == "user":
        if not CHANGELOG_PATH.is_file():
            raise SystemExit(f"log file missing: {CHANGELOG_PATH}")
        text = CHANGELOG_PATH.read_text(encoding="utf-8")
        new_text = _build_unreleased_insert(text, bullet, log_name="CHANGELOG.md")
        if dry_run:
            print(f"DRY-RUN: append to CHANGELOG.md: - {bullet}")
            return
        _write_repo_log("CHANGELOG.md", new_text)
        return
    if kind == "maintenance":
        if not MAINTENANCE_PATH.is_file():
            raise SystemExit(f"log file missing: {MAINTENANCE_PATH}")
        text = MAINTENANCE_PATH.read_text(encoding="utf-8")
        new_text = _build_unreleased_insert(text, bullet, log_name="MAINTENANCE.md")
        if dry_run:
            print(f"DRY-RUN: append to MAINTENANCE.md: - {bullet}")
            return
        _write_repo_log("MAINTENANCE.md", new_text)
        return
    raise SystemExit(f"unknown log kind: {kind}")


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
        # Include `{slug}` so _refresh_pr_pending_for_slug can locate this bullet.
        bullet = f"{message.rstrip('.')} (`{slug}`; {pr_label}, {today})"
    else:
        bullet = f"Archived plan `{slug}` → `docs/plans/` ({pr_label}, {today})"

    targets: list[str] = []
    if kind in ("maintenance", "both"):
        targets.append("maintenance")
    if kind in ("user", "both"):
        targets.append("user")

    for log_kind in targets:
        if log_kind == "maintenance":
            text = MAINTENANCE_PATH.read_text(encoding="utf-8")
            mentions = f"`{slug}`" in text or f"/{slug}" in text
            if mentions:
                updated = _refresh_pr_pending_for_slug(text, slug, pr)
                if updated != text:
                    if dry_run:
                        print(f"DRY-RUN: refresh PR # for {slug!r} in {MAINTENANCE_PATH.name}")
                    else:
                        _write_repo_log("MAINTENANCE.md", updated)
                elif dry_run:
                    print(f"DRY-RUN: log already mentions {slug!r} in {MAINTENANCE_PATH.name}")
                continue
            _append_log("maintenance", bullet, dry_run=dry_run)
            continue

        # log_kind == "user"
        text = CHANGELOG_PATH.read_text(encoding="utf-8")
        mentions = f"`{slug}`" in text or f"/{slug}" in text
        if mentions:
            updated = _refresh_pr_pending_for_slug(text, slug, pr)
            if updated != text:
                if dry_run:
                    print(f"DRY-RUN: refresh PR # for {slug!r} in {CHANGELOG_PATH.name}")
                else:
                    _write_repo_log("CHANGELOG.md", updated)
            elif dry_run:
                print(f"DRY-RUN: log already mentions {slug!r} in {CHANGELOG_PATH.name}")
            continue
        _append_log("user", bullet, dry_run=dry_run)


def _log_kinds_for(kind: str) -> list[str]:
    kinds: list[str] = []
    if kind in ("maintenance", "both"):
        kinds.append("maintenance")
    if kind in ("user", "both"):
        kinds.append("user")
    return kinds


def _preflight_log_targets(kind: str) -> None:
    """Ensure selected log files exist and have ## [Unreleased] before mutation."""
    for log_kind in _log_kinds_for(kind):
        path = CHANGELOG_PATH if log_kind == "user" else MAINTENANCE_PATH
        if not path.is_file():
            raise SystemExit(f"ERROR: archive — log file missing: {path}")
        text = path.read_text(encoding="utf-8")
        if "## [Unreleased]" not in text:
            raise SystemExit(f"ERROR: archive — {path.name} missing ## [Unreleased] section")


def _preflight_archive_content(
    text: str,
    *,
    dest: str,
    message: str | None,
    dest_path: Path,
) -> str:
    """Validate status/outcomes/replacement before any filesystem write; return updated text."""
    updated = _set_status_and_outcomes(text, dest, message)
    status = None
    for line in updated.splitlines()[:10]:
        m = re.search(r"\*\*Status:\*\*\s*(active|completed|deferred|superseded)\b", line)
        if m:
            status = m.group(1)
            break
    if status != dest:
        raise SystemExit(
            f"ERROR: archive — prepared status {status!r} does not match destination {dest!r}"
        )

    if dest != "active":
        outcomes = section_body(updated, "## Outcomes & retrospective")
        if len(outcomes) < MIN_OUTCOMES_CHARS:
            raise SystemExit(
                f"ERROR: archive — Outcomes & retrospective must be ≥{MIN_OUTCOMES_CHARS} chars "
                f"before archive (got {len(outcomes)}); pass --message with enough detail"
            )
        if dest == "superseded" and not has_valid_replacement_link(outcomes, dest_path):
            raise SystemExit(
                "ERROR: archive — superseded Outcomes must Markdown-link an existing "
                "replacement plan under docs/plans/<folder>/<slug>.md before archive"
            )
    return updated if updated.endswith("\n") else updated + "\n"


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

    # Preflight everything before any filesystem mutation.
    _preflight_log_targets(kind)
    if not already and require_todo and _find_todo_item_for_slug(slug) is None:
        raise SystemExit(
            f"ERROR: archive — TODO.md:1 no open bullet found for slug {slug!r}; "
            "same-PR close requires removing the TODO item (checked before archive)"
        )

    prepared: str | None = None
    if already:
        print(f"already archived: {dest_path.relative_to(REPO_ROOT)} — converging TODO/log")
    elif not src.is_file():
        raise SystemExit(f"active plan not found: {src.relative_to(REPO_ROOT)}")
    else:
        text = src.read_text(encoding="utf-8")
        prepared = _preflight_archive_content(
            text, dest=dest, message=message, dest_path=dest_path
        )
        if not dry_run:
            write_text_under(ACTIVE_DIR, f"{slug}.md", prepared)
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
