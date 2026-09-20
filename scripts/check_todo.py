#!/usr/bin/env python3
"""
Validate TODO.md structure and plan cross-links.

Inputs: repository root TODO.md and docs/plans/active/*.md
Outputs: ERROR lines on stdout; exit 0 if clean, 1 if violations.
Requirements: Python 3.12+ stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Allow `python3 scripts/check_todo.py` from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_lib import (  # noqa: E402
    ACTIVE_DIR,
    PLAN_TRIGGER_WORDS,
    REPO_ROOT,
    TODO_PATH,
    error,
    iter_plan_files,
    load_exempt_slugs,
    parse_todo_items,
)

ANCHOR_TARGETS = {
    "repo-process": "### Repo process",
}


def github_slug(heading: str) -> str:
    text = heading.lstrip("#").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def check_todo(*, strict_anchors: bool) -> list[str]:
    errors: list[str] = []
    if not TODO_PATH.is_file():
        return [error("todo", TODO_PATH, 1, "TODO.md missing")]

    text = TODO_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    if re.search(r"^##\s+Done\b", text, re.MULTILINE):
        for i, line in enumerate(lines, 1):
            if re.match(r"^##\s+Done\b", line):
                errors.append(error("todo", TODO_PATH, i, "Done section not allowed (open backlog only)"))
                break

    for i, line in enumerate(lines, 1):
        if line.startswith("- [x]"):
            errors.append(error("todo", TODO_PATH, i, "checked items not allowed; remove on ship"))

    # Scratch notes must not contain checkboxes
    scratch_start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Scratch notes\b", line):
            scratch_start = i
            break
    if scratch_start is not None:
        for j in range(scratch_start + 1, len(lines)):
            if lines[j].startswith("## "):
                break
            if lines[j].startswith("- [ ") or lines[j].startswith("- [x]"):
                errors.append(
                    error("todo", TODO_PATH, j + 1, "Scratch notes must not contain checklist items")
                )

    items = parse_todo_items(text)
    exempt_slugs = load_exempt_slugs()
    linked_slugs: set[str] = set()

    for item in items:
        if item.first_line.startswith("- [x]"):
            continue
        for slug in item.plan_slugs:
            linked_slugs.add(slug)
            plan_path = ACTIVE_DIR / f"{slug}.md"
            if not plan_path.is_file():
                errors.append(
                    error(
                        "todo",
                        TODO_PATH,
                        item.start_line,
                        f"plan link target missing: docs/plans/active/{slug}.md",
                    )
                )

        lowered = item.text.lower()
        needs_plan = any(word in lowered for word in PLAN_TRIGGER_WORDS)
        if needs_plan and not item.plan_slugs:
            if item.no_plan_reason or any(
                s in item.text for s in exempt_slugs
            ):
                pass
            else:
                # Also allow exempt file match on bold slug-ish title
                bold = re.search(r"\*\*([^*]+)\*\*", item.first_line)
                title = bold.group(1).lower() if bold else ""
                slug_guess = re.sub(r"[^a-z0-9]+", "-", title).strip("-")
                if slug_guess in exempt_slugs:
                    pass
                else:
                    errors.append(
                        error(
                            "todo",
                            TODO_PATH,
                            item.start_line,
                            "item triggers plan requirement (decide/audit/codify/refactor) "
                            "but has no Plan link; add link or <!-- no-plan: … -->",
                        )
                    )

    for plan in iter_plan_files(ACTIVE_DIR):
        slug = plan.stem
        if slug not in linked_slugs:
            errors.append(
                error(
                    "todo",
                    plan,
                    1,
                    f"active plan not linked from TODO.md (expected docs/plans/active/{slug}.md)",
                )
            )

    if strict_anchors:
        heading_slugs = {
            github_slug(m.group(2)): (i + 1, m.group(0))
            for i, line in enumerate(lines)
            if (m := re.match(r"^(#{2,3})\s+(.+?)\s*$", line))
        }
        for anchor, expected_heading in ANCHOR_TARGETS.items():
            if anchor not in heading_slugs:
                errors.append(
                    error(
                        "todo",
                        TODO_PATH,
                        1,
                        f"missing heading for anchor #{anchor} (expected {expected_heading!r})",
                    )
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict-anchors",
        action="store_true",
        help="Require known TODO.md section anchors (e.g. #repo-process)",
    )
    args = parser.parse_args(argv)
    # Always run from repo root semantics
    _ = REPO_ROOT
    errors = check_todo(strict_anchors=args.strict_anchors)
    for err in errors:
        print(err)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
