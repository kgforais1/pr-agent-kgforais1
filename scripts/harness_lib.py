#!/usr/bin/env python3
"""Shared helpers for repo-harness scripts (stdlib only)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TODO_PATH = REPO_ROOT / "TODO.md"
PLANS_ROOT = REPO_ROOT / "docs" / "plans"
ACTIVE_DIR = PLANS_ROOT / "active"
COMPLETED_DIR = PLANS_ROOT / "completed"
DEFERRED_DIR = PLANS_ROOT / "deferred"
SUPERSEDED_DIR = PLANS_ROOT / "superseded"
ARCHIVE_DIRS = {
    "completed": COMPLETED_DIR,
    "deferred": DEFERRED_DIR,
    "superseded": SUPERSEDED_DIR,
}
EXEMPT_FILE = REPO_ROOT / "docs" / "process" / "todo-exempt.txt"

STATUS_RE = re.compile(r"\*\*Status:\*\*\s*(active|completed|deferred|superseded)\b")
PLAN_LINK_RE = re.compile(
    r"docs/plans/active/([a-z0-9][a-z0-9-]*)\.md"
)
NO_PLAN_RE = re.compile(r"<!--\s*no-plan:\s*([a-z0-9-]+)\s*-->")
CHECKED_RE = re.compile(r"^- \[[xX]\]")
UNCHECKED_RE = re.compile(r"^- \[ \]")
CHECKBOX_START_RE = re.compile(r"^- \[[ xX]\]")
HEADING_RE = re.compile(r"^(#{2,3})\s+(\S.*)$")
REQUIRED_PLAN_HEADINGS = (
    "## Purpose",
    "## Progress",
    "## Decision log",
    "## Surprises & discoveries",
    "## Outcomes & retrospective",
    "## Validation",
)
PLAN_TRIGGER_WORDS = ("decide", "audit", "codify", "refactor")
PLAN_TRIGGER_RE = re.compile(
    r"\b(" + "|".join(PLAN_TRIGGER_WORDS) + r")\b",
    re.IGNORECASE,
)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def validate_slug(slug: str) -> str:
    """Reject empty, traversal, or non-kebab slugs (Sonar S2083 / path safety)."""
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(
            f"invalid slug {slug!r}: must match ^[a-z0-9][a-z0-9-]*$"
        )
    return slug


def plan_path(directory: Path, slug: str) -> Path:
    """Return directory/slug.md resolved and guaranteed under directory."""
    validate_slug(slug)
    base = directory.resolve()
    path = (base / f"{slug}.md").resolve()
    if path != base / path.name or path.parent != base:
        raise ValueError(f"plan path escapes directory: {path}")
    return path


_SAFE_PLAN_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.md$")


def write_text_under(directory: Path, filename: str, content: str) -> Path:
    """Write content to directory/filename after rejecting path traversal.

    ``filename`` must be a bare ``slug.md`` (no separators). Used so filesystem
    writes do not take a caller-supplied Path (Sonar pythonsecurity:S2083/S8707).
    """
    if not _SAFE_PLAN_NAME_RE.fullmatch(filename):
        raise ValueError(f"invalid plan filename {filename!r}")
    if "/" in filename or "\\" in filename or ".." in filename:
        raise ValueError(f"path traversal rejected in filename {filename!r}")
    base = directory.resolve()
    path = (base / filename).resolve()
    if path.parent != base:
        raise ValueError(f"plan path escapes directory: {path}")
    path.write_text(content, encoding="utf-8")
    return path

def is_checked_item(line: str) -> bool:
    return bool(CHECKED_RE.match(line))


def is_unchecked_item(line: str) -> bool:
    return bool(UNCHECKED_RE.match(line))


def is_checkbox_item(line: str) -> bool:
    return bool(CHECKBOX_START_RE.match(line))


def needs_plan_link(text: str) -> bool:
    return bool(PLAN_TRIGGER_RE.search(text))


def error(check: str, path: Path | str, line: int, reason: str) -> str:
    if isinstance(path, str):
        rel = path
    else:
        try:
            rel = path.relative_to(REPO_ROOT)
        except ValueError:
            rel = path
    return f"ERROR: {check} — {rel}:{line} {reason}"


@dataclass
class TodoItem:
    start_line: int  # 1-based
    end_line: int  # exclusive, 1-based end = last line + 1 conceptually via slice
    lines: list[str]
    text: str
    first_line: str

    @property
    def no_plan_reason(self) -> str | None:
        m = NO_PLAN_RE.search(self.first_line)
        return m.group(1) if m else None

    @property
    def plan_slugs(self) -> list[str]:
        return PLAN_LINK_RE.findall(self.text)


def load_exempt_slugs() -> set[str]:
    if not EXEMPT_FILE.is_file():
        return set()
    slugs: set[str] = set()
    for raw in EXEMPT_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        slugs.add(line)
    return slugs


def parse_todo_items(text: str) -> list[TodoItem]:
    lines = text.splitlines()
    items: list[TodoItem] = []
    i = 0
    while i < len(lines):
        if is_checkbox_item(lines[i]):
            start = i
            i += 1
            while i < len(lines):
                line = lines[i]
                if is_checkbox_item(line):
                    break
                if HEADING_RE.match(line) and line.startswith("##"):
                    break
                i += 1
            block = lines[start:i]
            items.append(
                TodoItem(
                    start_line=start + 1,
                    end_line=i + 1,
                    lines=block,
                    text="\n".join(block),
                    first_line=block[0],
                )
            )
            continue
        i += 1
    return items


def iter_plan_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.md") if p.name != ".gitkeep")


def read_status(path: Path) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines()[:10]
    for line in lines:
        m = STATUS_RE.search(line)
        if m:
            return m.group(1)
    return None


def section_body(text: str, heading: str) -> str:
    """Return body text under a ## heading until the next ##."""
    lines = text.splitlines()
    capturing = False
    body: list[str] = []
    for line in lines:
        if line.strip() == heading:
            capturing = True
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            body.append(line)
    return "\n".join(body).strip()
