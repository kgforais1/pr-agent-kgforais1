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


def test_requires_exact_headings(tmp_path, monkeypatch, load_harness_script, patch_plans_module):
    mod = load_harness_script("check_plans")
    dirs = patch_plans_module(mod, monkeypatch, tmp_path)
    bad = MINIMAL.format(status="active", outcomes="x").replace("## Purpose", "## Purposeful")
    (dirs["active"] / "bad-heading.md").write_text(bad, encoding="utf-8")
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("## Purpose" in e for e in errors)


def test_superseded_requires_replacement_link(
    tmp_path, monkeypatch, load_harness_script, patch_plans_module
):
    mod = load_harness_script("check_plans")
    dirs = patch_plans_module(mod, monkeypatch, tmp_path)
    outcomes = (
        "There is no replacement for this work, but we still archived it with enough "
        "retrospective text to satisfy the minimum outcomes length requirement."
    )
    (dirs["superseded"] / "old.md").write_text(
        MINIMAL.format(status="superseded", outcomes=outcomes),
        encoding="utf-8",
    )
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("replacement" in e for e in errors)


def test_superseded_accepts_relative_replacement_link(
    tmp_path, monkeypatch, load_harness_script, patch_plans_module
):
    mod = load_harness_script("check_plans")
    dirs = patch_plans_module(mod, monkeypatch, tmp_path)
    (dirs["active"] / "successor.md").write_text(
        MINIMAL.format(status="active", outcomes="x"),
        encoding="utf-8",
    )
    outcomes = (
        "Superseded by the successor plan after enough retrospective detail. "
        "See [successor](../active/successor.md) for the continuing workstream."
    )
    (dirs["superseded"] / "old.md").write_text(
        MINIMAL.format(status="superseded", outcomes=outcomes),
        encoding="utf-8",
    )
    import harness_lib as hl

    monkeypatch.setattr(hl, "PLANS_ROOT", tmp_path)
    errors = mod.check_plans(allow_empty_archives=True)
    assert not any("replacement" in e for e in errors)


def test_superseded_rejects_broken_docs_plans_link(
    tmp_path, monkeypatch, load_harness_script, patch_plans_module
):
    mod = load_harness_script("check_plans")
    dirs = patch_plans_module(mod, monkeypatch, tmp_path)
    outcomes = (
        "Claimed successor is missing on disk, with enough retrospective text here. "
        "See [missing](docs/plans/active/does-not-exist.md) which should fail validation."
    )
    (dirs["superseded"] / "old.md").write_text(
        MINIMAL.format(status="superseded", outcomes=outcomes),
        encoding="utf-8",
    )
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("replacement" in e for e in errors)


def test_superseded_rejects_image_posing_as_replacement(
    tmp_path, monkeypatch, load_harness_script, patch_plans_module
):
    mod = load_harness_script("check_plans")
    dirs = patch_plans_module(mod, monkeypatch, tmp_path)
    (dirs["active"] / "successor.md").write_text(
        MINIMAL.format(status="active", outcomes="x"),
        encoding="utf-8",
    )
    outcomes = (
        "Only an image points at the successor, which must not count as a link. "
        "![successor](../active/successor.md) should fail the replacement check."
    )
    (dirs["superseded"] / "old.md").write_text(
        MINIMAL.format(status="superseded", outcomes=outcomes),
        encoding="utf-8",
    )
    import harness_lib as hl

    monkeypatch.setattr(hl, "PLANS_ROOT", tmp_path)
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("replacement" in e for e in errors)
