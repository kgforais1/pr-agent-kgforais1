"""Unit tests for scripts/check_todo.py (stdlib harness)."""

from __future__ import annotations


def test_rejects_done_section(tmp_path, monkeypatch, load_harness_script, patch_todo_module):
    mod = load_harness_script("check_todo")
    patch_todo_module(
        mod,
        monkeypatch,
        tmp_path,
        "# TODO\n\n## Open\n\n- [ ] **x**\n\n## Done\n\n- [x] old\n",
    )
    errors = mod.check_todo(strict_anchors=False)
    assert any("Done section" in e for e in errors)


def test_requires_plan_for_audit_verb(tmp_path, monkeypatch, load_harness_script, patch_todo_module):
    mod = load_harness_script("check_todo")
    patch_todo_module(
        mod,
        monkeypatch,
        tmp_path,
        "# TODO\n\n## Open\n\n- [ ] **Docs audit** — audit the README\n",
    )
    errors = mod.check_todo(strict_anchors=False)
    assert any("plan requirement" in e for e in errors)


def test_rejects_uppercase_checked(tmp_path, monkeypatch, load_harness_script, patch_todo_module):
    mod = load_harness_script("check_todo")
    patch_todo_module(
        mod,
        monkeypatch,
        tmp_path,
        "# TODO\n\n## Open\n\n- [X] **done-looking**\n",
    )
    errors = mod.check_todo(strict_anchors=False)
    assert any("checked items not allowed" in e for e in errors)


def test_trigger_word_uses_boundaries(tmp_path, monkeypatch, load_harness_script, patch_todo_module):
    mod = load_harness_script("check_todo")
    # "indecisive" must NOT trigger; "audit" as whole word must
    patch_todo_module(
        mod,
        monkeypatch,
        tmp_path,
        "# TODO\n\n## Open\n\n- [ ] **Indecisive copy** — wording only\n",
    )
    assert mod.check_todo(strict_anchors=False) == []


def test_exempt_no_plan_marker(tmp_path, monkeypatch, load_harness_script, patch_todo_module):
    mod = load_harness_script("check_todo")
    patch_todo_module(
        mod,
        monkeypatch,
        tmp_path,
        "# TODO\n\n## Open\n\n"
        "- [ ] **Docs audit** <!-- no-plan: pending-execplan --> — audit the README\n",
    )
    errors = mod.check_todo(strict_anchors=False)
    assert errors == []
