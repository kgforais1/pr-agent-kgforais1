# Fork semver and logging

## Dual logs

| File | Audience | Examples |
|------|----------|----------|
| `CHANGELOG.md` | Users / operators | Tool behavior, config keys, bug fixes, breaking API |
| `MAINTENANCE.md` | Maintainers / agents | Harness, CI, refactors, `AGENTS.md`, process docs |

Both use [Keep a Changelog](https://keepachangelog.com/) sections under `## [Unreleased]`.

## Package version

`pyproject.toml` `version` bumps when cutting a user-facing `CHANGELOG.md` release.

**Interim (until packaging/publishing audit closes):** accumulate under `[Unreleased]` in
both logs; do **not** bump `pyproject.toml` or cut Git tags for harness-only work.
`release-drafter.yml` / `publish.yml` still reflect upstream packaging assumptions —
do not treat their drafts as fork release policy until that audit decides
publish-and-rename vs never-publish.

## Semver (once packaging policy is set)

- **MAJOR** — breaking config/API for fork consumers
- **MINOR** — new user-facing features
- **PATCH** — user-visible bug fixes

`MAINTENANCE.md` entries alone do not require a version bump.

## MkDocs

`docs/plans/` and `docs/process/` are **excluded** from the public MkDocs nav
(`docs/mkdocs.yml`). They are agent/maintainer docs linked from `AGENTS.md`.
