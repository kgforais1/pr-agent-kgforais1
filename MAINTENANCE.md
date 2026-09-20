# Maintenance log

Harness, CI, refactors, and repo process — not user-facing product changes.
User-facing history: [CHANGELOG.md](CHANGELOG.md).

## [Unreleased]

### Added

- Repo harness Phase A: `docs/plans/` lifecycle (`active`/`completed`/`deferred`/`superseded`),
  `docs/process/` conventions, dual `CHANGELOG.md` + `MAINTENANCE.md` logging, open-only
  `TODO.md`, stdlib scripts (`check_todo`/`check_plans`/`archive_plan`/`new_plan`),
  `.github/workflows/repo-harness.yml`, pre-commit harness hooks, and git-native
  `.githooks/commit-msg` soft hint (plan `plan-lifecycle-harness`; PR #9, 2026-09-20).
- SonarCloud hardening for PR #9: slug path validation (`validate_slug`/`plan_path`),
  heading regex without super-linear backtracking, harness CI without `uv` (pinned
  pytest only; avoids GH-Actions S8541/S8544), shared harness fixtures in
  `tests/unittest/conftest.py` to cut duplication below the new-code density gate.
