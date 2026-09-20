"""Unit tests for scripts/check_todo.py (stdlib harness)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "check_todo.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_todo", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_rejects_done_section(tmp_path, monkeypatch):
    mod = _load()
    todo = tmp_path / "TODO.md"
    todo.write_text("# TODO\n\n## Open\n\n- [ ] **x**\n\n## Done\n\n- [x] old\n", encoding="utf-8")
    monkeypatch.setattr(mod, "TODO_PATH", todo)
    monkeypatch.setattr(mod, "ACTIVE_DIR", tmp_path / "active")
    (tmp_path / "active").mkdir()
    errors = mod.check_todo(strict_anchors=False)
    assert any("Done section" in e for e in errors)


def test_requires_plan_for_audit_verb(tmp_path, monkeypatch):
    mod = _load()
    todo = tmp_path / "TODO.md"
    todo.write_text(
        "# TODO\n\n## Open\n\n- [ ] **Docs audit** — audit the README\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "TODO_PATH", todo)
    monkeypatch.setattr(mod, "ACTIVE_DIR", tmp_path / "active")
    (tmp_path / "active").mkdir()
    errors = mod.check_todo(strict_anchors=False)
    assert any("plan requirement" in e for e in errors)


def test_rejects_uppercase_checked(tmp_path, monkeypatch):
    mod = _load()
    todo = tmp_path / "TODO.md"
    todo.write_text("# TODO\n\n## Open\n\n- [X] **done-looking**\n", encoding="utf-8")
    monkeypatch.setattr(mod, "TODO_PATH", todo)
    monkeypatch.setattr(mod, "ACTIVE_DIR", tmp_path / "active")
    (tmp_path / "active").mkdir()
    errors = mod.check_todo(strict_anchors=False)
    assert any("checked items not allowed" in e for e in errors)


def test_trigger_word_uses_boundaries(tmp_path, monkeypatch):
    mod = _load()
    todo = tmp_path / "TODO.md"
    # "indecisive" must NOT trigger; "audit" as whole word must
    todo.write_text(
        "# TODO\n\n## Open\n\n- [ ] **Indecisive copy** — wording only\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "TODO_PATH", todo)
    monkeypatch.setattr(mod, "ACTIVE_DIR", tmp_path / "active")
    (tmp_path / "active").mkdir()
    assert mod.check_todo(strict_anchors=False) == []


def test_exempt_no_plan_marker(tmp_path, monkeypatch):
    mod = _load()
    todo = tmp_path / "TODO.md"
    todo.write_text(
        "# TODO\n\n## Open\n\n"
        "- [ ] **Docs audit** <!-- no-plan: pending-execplan --> — audit the README\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "TODO_PATH", todo)
    monkeypatch.setattr(mod, "ACTIVE_DIR", tmp_path / "active")
    (tmp_path / "active").mkdir()
    errors = mod.check_todo(strict_anchors=False)
    assert errors == []
