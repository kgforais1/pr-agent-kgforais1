import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def isolate_run_details():
    """Start each test from a clean run-details ContextVar and restore it.

    The collector lives in a module-level ContextVar, so a test that leaves
    details behind would otherwise be visible to whichever test runs next.
    """
    from pr_agent.algo import run_details

    token = run_details._run_details.set(None)
    yield
    run_details._run_details.reset(token)


@pytest.fixture
def load_harness_script():
    """Return a loader for scripts/<name>.py via importlib."""

    def _load(name: str):
        path = REPO / "scripts" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod

    return _load


@pytest.fixture
def patch_todo_module():
    """Return a helper that points check_todo at a temp TODO.md + active/."""

    def _patch(mod: Any, monkeypatch: Any, tmp_path: Path, todo_text: str) -> Path:
        todo = tmp_path / "TODO.md"
        todo.write_text(todo_text, encoding="utf-8")
        active = tmp_path / "active"
        active.mkdir(exist_ok=True)
        monkeypatch.setattr(mod, "TODO_PATH", todo)
        monkeypatch.setattr(mod, "ACTIVE_DIR", active)
        return todo

    return _patch


@pytest.fixture
def patch_plans_module():
    """Return a helper that wires check_plans dirs and status maps."""

    def _patch(mod: Any, monkeypatch: Any, tmp_path: Path) -> dict[str, Path]:
        dirs = {
            "active": tmp_path / "active",
            "completed": tmp_path / "completed",
            "deferred": tmp_path / "deferred",
            "superseded": tmp_path / "superseded",
        }
        for d in dirs.values():
            d.mkdir()
        monkeypatch.setattr(mod, "ACTIVE_DIR", dirs["active"])
        monkeypatch.setattr(mod, "COMPLETED_DIR", dirs["completed"])
        monkeypatch.setattr(mod, "DEFERRED_DIR", dirs["deferred"])
        monkeypatch.setattr(mod, "SUPERSEDED_DIR", dirs["superseded"])
        monkeypatch.setattr(
            mod,
            "FOLDER_STATUS",
            {
                dirs["active"]: "active",
                dirs["completed"]: "completed",
                dirs["deferred"]: "deferred",
                dirs["superseded"]: "superseded",
            },
        )
        monkeypatch.setattr(
            mod,
            "ARCHIVE_DIRS",
            {
                "completed": dirs["completed"],
                "deferred": dirs["deferred"],
                "superseded": dirs["superseded"],
            },
        )
        return dirs

    return _patch
