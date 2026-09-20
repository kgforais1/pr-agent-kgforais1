# Agent session checklist

## Session start

1. Read `TODO.md` open items.
2. Check `docs/plans/active/` for a linked ExecPlan.
3. Read `AGENTS.md` safety rules (upstream PR ban, no direct push to `main`).
4. For implementation: confirm branch (not `main`), run `uv sync`, note relevant CI
   (`repo-harness`, `pre-commit`, `build-and-test`).

## During work

- Keep ExecPlan Progress / Decision log updated.
- Substantive plans live under `docs/plans/`, not only gitignored `tmp/`.
- Do not leave decisions only in chat history.

## Session end (if work shipped or plan closed)

1. Run `scripts/archive_plan.py` (or `--dry-run` first) so TODO remove + plan archive +
   log entry happen together.
2. Ensure `python3 scripts/check_todo.py` and `python3 scripts/check_plans.py` pass.
3. Prefer one PR that closes the TODO item, archives the plan, and updates
   `CHANGELOG.md` / `MAINTENANCE.md`.

## Logs

| File | Audience |
|------|----------|
| `CHANGELOG.md` | User-facing product changes |
| `MAINTENANCE.md` | Harness, CI, refactors, process |
