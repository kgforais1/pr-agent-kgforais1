#!/usr/bin/env python3
"""
Scaffold a new ExecPlan under docs/plans/active/ from docs/plans/PLANS.md.

Requirements: Python 3.12+ stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_lib import ACTIVE_DIR, PLANS_ROOT, REPO_ROOT  # noqa: E402

TEMPLATE = """# {title}

**Status:** active
**TODO:** [link from TODO.md](../../TODO.md)
**Created:** {today}

This ExecPlan is a living document. Maintain Progress, Surprises & discoveries,
Decision log, and Outcomes & retrospective as work proceeds. Follow
`docs/plans/PLANS.md`.

## Purpose

Describe what someone gains after this change and how they can see it working.

## Progress

- [ ] Draft context and plan of work
- [ ] Implement
- [ ] Validate
- [ ] Archive on same PR (`scripts/archive_plan.py`)

## Surprises & discoveries

_(none yet)_

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| {today} | Created plan `{slug}` | Scaffolded via `scripts/new_plan.py` |

## Outcomes & retrospective

_(fill when archived)_

## Context and Orientation

Name key files by full path. Define non-obvious terms.

## Plan of Work

Describe the sequence of edits.

## Concrete Steps

Exact commands and working directory.

## Validation

Commands and expected output that prove success.

## Idempotence and Recovery

Safe retries and rollback.

## Artifacts and Notes

_(optional)_

## Interfaces and Dependencies

_(optional)_
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, help="kebab-case plan filename stem")
    parser.add_argument("--title", default=None, help="Plan H1 title (default: slug to title)")
    args = parser.parse_args(argv)

    slug = args.slug.strip()
    if not slug or "/" in slug or " " in slug:
        raise SystemExit("slug must be kebab-case without spaces or slashes")

    plans_md = PLANS_ROOT / "PLANS.md"
    if not plans_md.is_file():
        raise SystemExit(f"missing template rules file: {plans_md.relative_to(REPO_ROOT)}")

    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    dest = ACTIVE_DIR / f"{slug}.md"
    if dest.exists():
        raise SystemExit(f"already exists: {dest.relative_to(REPO_ROOT)}")

    title = args.title or slug.replace("-", " ").title()
    today = dt.date.today().isoformat()
    dest.write_text(TEMPLATE.format(title=title, slug=slug, today=today), encoding="utf-8")
    print(f"created {dest.relative_to(REPO_ROOT)}")
    print("Remember to link it from TODO.md and keep PLANS.md conventions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
