#!/usr/bin/env python3
"""
Validate ExecPlan lifecycle invariants under docs/plans/.

Inputs: docs/plans/{active,completed,deferred,superseded}/*.md
Outputs: ERROR lines on stdout; exit 0 if clean, 1 if violations.
Requirements: Python 3.12+ stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_lib import (  # noqa: E402
    ACTIVE_DIR,
    ARCHIVE_DIRS,
    COMPLETED_DIR,
    DEFERRED_DIR,
    PLANS_ROOT,
    REQUIRED_PLAN_HEADINGS,
    SUPERSEDED_DIR,
    error,
    iter_plan_files,
    read_status,
    section_body,
)

FOLDER_STATUS = {
    ACTIVE_DIR: "active",
    COMPLETED_DIR: "completed",
    DEFERRED_DIR: "deferred",
    SUPERSEDED_DIR: "superseded",
}

MIN_OUTCOMES_CHARS = 100


def check_plans(*, allow_empty_archives: bool) -> list[str]:
    errors: list[str] = []

    for directory, expected_status in FOLDER_STATUS.items():
        if not directory.is_dir():
            if directory is ACTIVE_DIR:
                errors.append(error("plans", directory, 1, "active/ directory missing"))
            elif not allow_empty_archives:
                # Missing archive dirs are OK if allow_empty; create advice for Phase A
                pass
            continue

        plans = iter_plan_files(directory)
        if not plans and directory is not ACTIVE_DIR and not allow_empty_archives:
            # Empty archive dirs with .gitkeep only are fine
            pass

        for path in plans:
            text = path.read_text(encoding="utf-8")
            status = read_status(path)
            if status is None:
                errors.append(
                    error("plans", path, 1, "missing **Status:** in first 10 lines")
                )
            elif status != expected_status:
                errors.append(
                    error(
                        "plans",
                        path,
                        1,
                        f"status {status!r} does not match folder {expected_status!r}",
                    )
                )

            for heading in REQUIRED_PLAN_HEADINGS:
                if heading not in text:
                    errors.append(
                        error("plans", path, 1, f"missing required heading {heading!r}")
                    )

            if expected_status != "active":
                outcomes = section_body(text, "## Outcomes & retrospective")
                if len(outcomes) < MIN_OUTCOMES_CHARS:
                    errors.append(
                        error(
                            "plans",
                            path,
                            1,
                            f"Outcomes & retrospective must be ≥{MIN_OUTCOMES_CHARS} chars "
                            f"when archived (got {len(outcomes)})",
                        )
                    )

            if expected_status == "superseded":
                if "docs/plans/" not in outcomes and "replacement" not in outcomes.lower():
                    # Prefer an explicit link to another plan
                    if not re.search(r"docs/plans/(active|completed|deferred|superseded)/", text):
                        errors.append(
                            error(
                                "plans",
                                path,
                                1,
                                "superseded plan must link a replacement under docs/plans/",
                            )
                        )

    # Ensure archive directories exist (create guidance) when not allowing empty bootstrap
    if not allow_empty_archives:
        for name, directory in ARCHIVE_DIRS.items():
            if not directory.is_dir():
                errors.append(
                    error("plans", PLANS_ROOT / name, 1, f"{name}/ directory missing")
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-empty-archives",
        action="store_true",
        help="Do not require archive directories to exist (birth PR bootstrap)",
    )
    args = parser.parse_args(argv)
    errors = check_plans(allow_empty_archives=args.allow_empty_archives)
    for err in errors:
        print(err)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
