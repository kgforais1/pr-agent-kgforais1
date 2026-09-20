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
- SonarCloud / CodeRabbit hardening for PR #9: slug path validation, heading regex,
  wheel-only pytest in harness CI, archive preflight (TODO + logs + outcomes /
  replacement), slug-tagged log bullets, resolved Markdown replacement links,
  allowlisted `no-plan` reasons, and `../../../TODO.md` links from plan trees.
