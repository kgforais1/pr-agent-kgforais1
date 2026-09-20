"""Unit tests for scripts/check_plans.py (stdlib harness)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "check_plans.py"

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


def _load():
    spec = importlib.util.spec_from_file_location("check_plans", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_status_must_match_folder(tmp_path, monkeypatch):
    mod = _load()
    active = tmp_path / "active"
    completed = tmp_path / "completed"
    deferred = tmp_path / "deferred"
    superseded = tmp_path / "superseded"
    for d in (active, completed, deferred, superseded):
        d.mkdir()
    (completed / "bad.md").write_text(
        MINIMAL.format(status="active", outcomes="x" * 120),
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ACTIVE_DIR", active)
    monkeypatch.setattr(mod, "COMPLETED_DIR", completed)
    monkeypatch.setattr(mod, "DEFERRED_DIR", deferred)
    monkeypatch.setattr(mod, "SUPERSEDED_DIR", superseded)
    monkeypatch.setattr(
        mod,
        "FOLDER_STATUS",
        {
            active: "active",
            completed: "completed",
            deferred: "deferred",
            superseded: "superseded",
        },
    )
    monkeypatch.setattr(
        mod,
        "ARCHIVE_DIRS",
        {"completed": completed, "deferred": deferred, "superseded": superseded},
    )
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("does not match folder" in e for e in errors)


def test_outcomes_min_length_for_completed(tmp_path, monkeypatch):
    mod = _load()
    active = tmp_path / "active"
    completed = tmp_path / "completed"
    deferred = tmp_path / "deferred"
    superseded = tmp_path / "superseded"
    for d in (active, completed, deferred, superseded):
        d.mkdir()
    (completed / "short.md").write_text(
        MINIMAL.format(status="completed", outcomes="too short"),
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ACTIVE_DIR", active)
    monkeypatch.setattr(mod, "COMPLETED_DIR", completed)
    monkeypatch.setattr(mod, "DEFERRED_DIR", deferred)
    monkeypatch.setattr(mod, "SUPERSEDED_DIR", superseded)
    monkeypatch.setattr(
        mod,
        "FOLDER_STATUS",
        {
            active: "active",
            completed: "completed",
            deferred: "deferred",
            superseded: "superseded",
        },
    )
    monkeypatch.setattr(
        mod,
        "ARCHIVE_DIRS",
        {"completed": completed, "deferred": deferred, "superseded": superseded},
    )
    errors = mod.check_plans(allow_empty_archives=True)
    assert any("Outcomes & retrospective" in e for e in errors)
