"""Unit tests for scripts/check_plans.py (stdlib harness)."""

from __future__ import annotations

MINIMAL = """# Test plan

**Status:** {status}

## Purpose

Purpose text.

## Progress

- [ ] step

## Surprises & discoveries

None.

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-20 | x | y |

## Outcomes & retrospective

{outcomes}

## Validation

Run tests.
"""


def test_status_must_match_folder(tmp_path, monkeypatch, load_harness_script, patch_plans_module):
    mod = load_harness_script("check_plans")
    dirs = patch_plans_module(mod, monkeypatch, tmp_path)
    (dirs["completed"] / "bad.md").write_text(
        MINIMAL.format(status="active", outcomes="x" * 120),
        encoding="utf-8",
    )
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("does not match folder" in e for e in errors)


def test_outcomes_min_length_for_completed(
    tmp_path, monkeypatch, load_harness_script, patch_plans_module
):
    mod = load_harness_script("check_plans")
    dirs = patch_plans_module(mod, monkeypatch, tmp_path)
    (dirs["completed"] / "short.md").write_text(
        MINIMAL.format(status="completed", outcomes="too short"),
        encoding="utf-8",
    )
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("Outcomes & retrospective" in e for e in errors)
