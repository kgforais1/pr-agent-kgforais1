# ExecPlan: Plan / TODO lifecycle and repo harness

**Status:** active
**TODO:** [Plan/todo lifecycle guidance and repo harness](../../TODO.md#repo-process)
**Owner:** repo maintainers + agents
**Created:** 2026-09-20

## Purpose

Codify how work is planned, tracked, and closed in `kgforais1/pr-agent-kgforais1` so
no plan or decision exists only in chat history. Agents should be able to onboard from
the repository alone, following patterns inspired by
[OpenAI harness engineering](https://openai.com/index/harness-engineering/) and
[ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans).

This plan designs the harness; a follow-up implementation PR delivers the scaffolding.

## Problem

| Gap | Impact |
|-----|--------|
| Scratch plans in gitignored `tmp/` vanish on cleanup | Lost decisions, repeated discovery |
| `TODO.md` has no link or close protocol | Agents skip or duplicate tracker updates |
| `AGENTS.md` is comprehensive but not a map | Context bloat; no pointer to process docs |
| Upstream `CHANGELOG.md` frozen at 2023 | No fork changelog for user-visible or maintenance work |
| No mechanical checks on docs/TODO cross-links | Drift between tracker, plans, and reality |

## Goals

1. **Durable plans** — Substantive work has a checked-in ExecPlan before or during the
   implementing PR.
2. **Single PR close** — Archive plan, update TODO, and log maintenance/semver on the
   **same PR** that ships the work (not a follow-up).
3. **Agent map** — Short additions to `AGENTS.md` point to `TODO.md`, plan dirs, and
   process docs; details live under `docs/`.
4. **Mechanical enforcement** — Scripts + pre-commit/CI catch broken links, stale
   active plans, and TODO items without plans when required.
5. **Semver alignment** — User-visible changes go in `CHANGELOG.md`; under-the-hood work
   (harness, CI, refactors, process) goes in `MAINTENANCE.md`. Both use Keep a Changelog
   style; `pyproject.toml` version bumps align with `CHANGELOG.md` releases.

## Non-goals (this initiative)

- Rewriting all of `AGENTS.md` into a 100-line map (incremental trim + pointers only).
- Changing upstream release automation (`publish.yml`) beyond documenting fork policy.
- Mandating ExecPlans for one-line typo fixes.

## Design

### 1. Knowledge layout (harness map)

Keep `AGENTS.md` as the entry point; add a **Repository process** section (~15 lines)
linking to:

```
docs/
├── plans/
│   ├── README.md           # index + lifecycle summary
│   ├── PLANS.md            # ExecPlan template & authoring rules
│   ├── active/             # in-flight ExecPlans
│   └── completed/          # archived ExecPlans
├── process/
│   ├── todo-conventions.md # when to add/remove open TODO items
│   ├── semver.md           # fork versioning vs upstream tags
│   └── agent-session.md    # session-start checklist for agents
CHANGELOG.md                # user-facing fork changes (semver releases)
MAINTENANCE.md              # harness, CI, refactors, process (under the hood)
TODO.md                     # open work only (no completed history)
```

`tmp/` remains for ephemeral analysis only. Promotion rule: if the outcome affects
future agents or maintainers, move content into `docs/` or an ExecPlan before the PR
merges.

### 2. ExecPlan standard (`docs/plans/PLANS.md`)

**Adopt the canonical Codex `PLANS.md` skeleton verbatim** (self-containment, envelope
rules, Context & Orientation, Plan of Work, Concrete Steps with expected transcripts,
Validation & Acceptance, Idempotence & Recovery, Interfaces & Dependencies, Artifacts &
Notes), plus the four living sections: Progress, Decision log, Surprises & discoveries,
Outcomes & retrospective.

Prepend a ≤20-line fork preamble: **When to write an ExecPlan in this repo** — use when
work spans multiple files/sessions/PRs, or the TODO says decide/audit/codify; exempt
one-line typo fixes.

Add to `AGENTS.md` (pointer only):

> When writing complex features or significant refactors, use an ExecPlan (as described
> in `docs/plans/PLANS.md`) from design to implementation.

Status line convention (all plans): `**Status:** active|completed` on line 3 (not YAML
front-matter) so `check_plans.py` can lint mechanically.

### 3. TODO.md conventions

**Open backlog only.** `TODO.md` lists work not yet shipped. It does not track
completed items — no `## Done` section. History lives in `CHANGELOG.md` and/or
`MAINTENANCE.md` (what shipped), `docs/plans/completed/` (how it was planned), and
`git log`.

Slug grammar: `kebab-case` (e.g. `plan-lifecycle-harness`). Pin exact formats in
`docs/process/todo-conventions.md`.

| Action | Rule |
|--------|------|
| **Add** | Item under `## Open` → `### <category>` with stable `**slug**`; link ExecPlan if non-trivial |
| **Start** | Create `docs/plans/active/<slug>.md`; add `**Plan:** […](docs/plans/active/<slug>.md)` |
| **Ship** | **Delete** the open bullet from `TODO.md` on the implementing PR (same PR as archive + log) |
| **History** | Log in `CHANGELOG.md` and/or `MAINTENANCE.md` (PR #, date); fill plan `Outcomes & retrospective` |

**Which log?** Use the table in §5. Mixed PRs may touch both. At least one log entry is
required when closing a TODO item (unless the change is docs-only with zero repo impact).

`scripts/check_todo.py` enforces: all items use `- [ ]` (unchecked only); every non-exempt
`active/*.md` is back-linked from `TODO.md`; plan links resolve; items containing
codify/audit/decide require a plan link. Reject any `## Done` section or `- [x]` items.

Section anchors: keep `### Repo process` under `## Open`; validate `#repo-process`
with `check_todo.py --strict-anchors`.

### 4. Close-on-same-PR workflow (owner preference)

When implementation PR merges (all in one PR; use `scripts/archive_plan.py`):

1. `git mv docs/plans/active/<slug>.md` → `docs/plans/completed/<slug>.md`
2. Set `**Status:** completed`; fill **Outcomes & retrospective** (≥2 sentences)
3. **Remove** the open TODO bullet (do not add a Done entry — `TODO.md` is open-only)
4. Rewrite any in-repo links from `active/<slug>` → `completed/<slug>` (atomic with move)
5. Add entry to `CHANGELOG.md` and/or `MAINTENANCE.md` under `[Unreleased]` with PR #
   and date (see §5 — user-facing vs under-the-hood)
6. If `CHANGELOG.md` has release-worthy user-facing changes (post packaging audit):
   bump `pyproject.toml` version and cut a `## [X.Y.Z]` section

**Enforcement:** soft hint at commit time (`.githooks/commit-msg`, exit 0); hard gate in
CI (`repo-harness.yml` on the PR). Never defer steps 1–5 to a follow-up PR.

**Escape hatch:** only when a reviewer requests a split PR; the remainder keeps the
plan in `active/` with a Progress entry naming the follow-up PR/issue. No silent deferrals.

**Rollback:** if a branch is abandoned after archive, `git mv` back to `active/` and
revert TODO/MAINTENANCE edits on that branch.

### 5. Changelog, maintenance log, and semver

Two logs, one version line. Both use [Keep a Changelog](https://keepachangelog.com/)
sections (`Added`, `Changed`, `Fixed`, `Removed`, `Security`) under `[Unreleased]`.

| Artifact | Audience | Examples |
|----------|----------|----------|
| `CHANGELOG.md` | Users, operators, downstream consumers | New `/review` behavior, config key changes, bug fixes in tools, breaking API changes |
| `MAINTENANCE.md` | Maintainers, agents, CI | Harness scaffolding, refactors, CI workflows, `AGENTS.md`/plan lifecycle, dependency-only bumps with no user impact |
| `pyproject.toml` `version` | Package releases | Bumps when cutting a `CHANGELOG.md` release (gated on packaging audit) |
| Git tags / Releases | Optional fork policy | Document in `docs/process/semver.md` |

`CHANGELOG.md` structure after the existing upstream archive (pre-fork history stays
untouched above a `---` divider):

```markdown
---

## Fork changelog

Fork-specific changes from 2026-09-19 (detachment). Under-the-hood work:
[MAINTENANCE.md](MAINTENANCE.md).

## [Unreleased]

### Added
- …

## [0.45.1] — 2026-09-20

### Fixed
- …
```

`MAINTENANCE.md` (new file):

```markdown
# Maintenance log

Harness, CI, refactors, and repo process — not user-facing product changes.
User-facing history: [CHANGELOG.md](CHANGELOG.md).

## [Unreleased]

### Added
- Repo harness scaffolding (plan lifecycle, check scripts, CI) (PR #N)
```

**Routing rule (same PR):**

| Change type | Log |
|-------------|-----|
| User-visible feature, fix, or breaking change | `CHANGELOG.md` |
| Refactor, harness, CI, agent docs, internal tooling | `MAINTENANCE.md` |
| Both (e.g. feature + harness to ship it) | Both |

`scripts/archive_plan.py --kind user|maintenance|both` selects target log(s); default
`maintenance` for plan/harness work.

**Interim policy (until packaging audit closes):** accumulate under `[Unreleased]` in
both files; do not bump `pyproject.toml` until publish-vs-strip is decided. Harness-only
shipments may log only `MAINTENANCE.md`.

Semver rules for `CHANGELOG.md` releases (once packaging policy is set):

- **MAJOR** — breaking config/API for fork consumers
- **MINOR** — new user-facing features or capabilities
- **PATCH** — user-visible bug fixes, non-breaking behavior tweaks

`MAINTENANCE.md` is not required to bump package version; batch maintenance entries and
cut a release when `CHANGELOG.md` warrants it.

### 6. Agent session checklist (`docs/process/agent-session.md`)

At session start, agents should:

1. Read `TODO.md` open items
2. Check `docs/plans/active/` for linked ExecPlan
3. Read `AGENTS.md` safety rules (upstream PR ban, no direct push to `main`)
4. For implementation: confirm branch, run `uv sync`, note relevant CI workflows

At session end (if work shipped or plan advanced):

1. Update ExecPlan progress/decisions
2. Ensure TODO link still valid
3. Do not leave decisions only in chat

### 7. Mechanical enforcement (proposed)

| Check | Where | What |
|-------|-------|------|
| TODO + plan links | `scripts/check_todo.py` + unit tests | Structure, anchors, bidirectional plan↔TODO links |
| Plan lifecycle | `scripts/check_plans.py` + unit tests | No `**Status:** active` in `completed/`; required headings; Outcomes non-empty when completed |
| Markdown links | Phase B: `scripts/check_links.py` (stdlib) | `TODO.md` → plan paths exist; prefer no lychee dep in Phase A |
| AGENTS.md size | Phase B CI warning | Flag if > 200 lines without process pointers near top |

Run via `uv run --frozen python scripts/…` in CI; `PYTHONPATH=.` only if imports need it.
Bootstrap: first implementing PR may use a one-time allowlist until `completed/` exists.

### 8. Hooks and CI integration

**Git hooks (`.githooks/`):**

- Existing `pre-push` blocks direct `main` pushes (unchanged)
- New `.githooks/commit-msg` (soft warn, **exit 0**): if commit touches
  `docs/plans/active/` and `TODO.md` is not in the same commit, or no log file
  (`CHANGELOG.md` / `MAINTENANCE.md`) is touched, print a hint about same-PR close.
  Not a `pre-commit` framework hook.

**CI (`.github/workflows/repo-harness.yml`):**

```yaml
# Trigger: pull_request, paths filter TODO.md, docs/plans/**, CHANGELOG.md, MAINTENANCE.md, scripts/**
# Jobs: uv sync --frozen → check_todo.py → check_plans.py
# Fail PR if any check fails (hard gate for same-PR close invariants)
```

Add harness scripts to `.pre-commit-config.yaml` local hooks only if each runs <2s;
otherwise rely on `repo-harness.yml` (avoid duplicating full checkout in two workflows).

**Doc-gardening (Phase B):** `.github/workflows/doc-gardening.yml`, monthly cron,
detection-only issue listing `active/*.md` older than 60 days with no linked open TODO
(mirrors `upstream-pr-leak-check` philosophy).

### 9. Scripts (proposed)

| Script | Contract |
|--------|----------|
| `scripts/check_todo.py` | Exit 1 on violation; `--strict-anchors` validates `#repo-process` etc. |
| `scripts/check_plans.py` | Match `**Status:** active|completed`; exact required heading strings |
| `scripts/archive_plan.py` | `--slug S --pr N [--kind user\|maintenance\|both]`: `git mv`, flip status, remove TODO line, insert log bullet(s); `--dry-run` prints diff |
| `scripts/new_plan.py` | `--slug S`: scaffold from `docs/plans/PLANS.md` into `active/` |

Unit tests: `tests/unittest/test_check_todo.py`, `test_check_plans.py` with fixtures.

### 10. AGENTS.md changes (minimal)

Insert **Repository process** after Dos/Don'ts (~15 lines, links only):

- `TODO.md` — open work (read at session start)
- `docs/plans/README.md` + `docs/plans/PLANS.md` — ExecPlan lifecycle
- `docs/process/agent-session.md` — session checklist
- `CHANGELOG.md` — user-facing changes; `MAINTENANCE.md` — harness/refactors/process
- Rules: substantive plans in repo not `tmp/`; on ship remove TODO item, archive plan, log appropriate file(s) on same PR

`AGENTS.md` is already ~122 lines; pointer section goes near top to reduce context noise.
Full prose trim deferred to Phase B (tracked TODO, not optional).

### 11. MkDocs integration

`docs/plans/` and `docs/process/` sit outside `docs/docs/` (MkDocs content root).
Phase A must decide explicitly (one line in `semver.md` or plan PR):

- **Exclude** from site (agent/maintainer docs only; document in `docs/plans/README.md`), or
- **Include** via `docs/mkdocs.yml` nav entries

Default recommendation: exclude from public MkDocs nav; link from `AGENTS.md` only.

### 12. Agent coordination (multi-agent work)

For delegated reviewer/implementer agents (Paseo, Cursor subagents):

- One worktree or branch per agent task; no concurrent edits to same plan file
- Reviewer agents read-only on `active/` plans; edits go to implementing PR author
- Exit criteria: harness CI green + reviewer sign-off recorded in plan Decision log
- Parallel agents: disjoint file ownership or sequential handoff via plan Progress section

## Implementation phases

### Phase A — Docs skeleton (implementing PR for this TODO)

- [ ] Add `docs/plans/PLANS.md` template
- [ ] Add `docs/process/todo-conventions.md`, `agent-session.md`, `semver.md`
- [ ] Add `MAINTENANCE.md` with initial `[Unreleased]` section
- [ ] Add fork `## [Unreleased]` section to `CHANGELOG.md` (keep upstream archive above divider)
- [ ] Add **Repository process** section to `AGENTS.md`
- [ ] Implement `scripts/check_todo.py`, `check_plans.py`, `new_plan.py`, `archive_plan.py`
- [ ] Add CI workflow `repo-harness.yml`
- [ ] Add pre-commit hooks for harness scripts (if fast enough)
- [ ] Archive this plan to `completed/`, remove TODO item, log in `MAINTENANCE.md` on same PR

### Phase B — Hardening (follow-up)

- [ ] `scripts/check_links.py` or lychee in CI
- [ ] `doc-gardening.yml` (60-day stale active plans, issue-only)
- [ ] Trim `AGENTS.md` redundant prose into `docs/process/`
- [ ] `docs/plans/tech-debt-tracker.md` for fork-specific debt
- [ ] `AGENTS.md` size warning in CI (>200 lines)
- [ ] Full semver policy after packaging audit

## Progress

- [x] Draft ExecPlan (this document)
- [x] Review by StepFun 3.7 Flash free (`kilo/stepfun/step-3.7-flash:free`)
- [x] Review by Muse Spark 1.3 contributor (`opencode/opencode-go/muse-spark-1.3-contributor`)
- [x] Incorporate reviewer feedback into this plan (2026-09-20)
- [ ] Owner review and Phase A PR

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-20 | Plans live under `docs/plans/{active,completed}/` | Matches harness-engineering layout; visible in docs site |
| 2026-09-20 | Dual logs: `CHANGELOG.md` (user-facing) + `MAINTENANCE.md` (under the hood) | Owner preference; semver tracks product, maintenance tracks harness |
| 2026-09-20 | Close plan+TODO+log on same PR | Owner workflow; reduces orphan cleanup PRs |
| 2026-09-20 | ExecPlan required for TODO items that say codify/audit/decide | Aligns tracker with durable artifacts |
| 2026-09-20 | Adopt canonical PLANS.md verbatim + fork preamble | Reviewers: thin plans are not executable specs |
| 2026-09-20 | TODO open-only; no Done section | Owner preference; history in CHANGELOG/MAINTENANCE + completed plans + git |
| 2026-09-20 | `archive_plan.py` edits files, not print-only | Same-PR close must be mechanical |
| 2026-09-20 | Defer `pyproject.toml` bump until packaging audit | Avoid meaningless version publishes |
| 2026-09-20 | `commit-msg` hook soft; CI hard gate | Stacked commits stay usable |
| 2026-09-20 | Exclude `docs/plans/` from MkDocs nav by default | Agent docs, not user-facing site |
| 2026-09-20 | Remove `## Done` from `TODO.md`; reject `- [x]` in linter | Owner: TODO is open backlog only |

## Surprises & discoveries

- Both external reviewers endorsed same-PR close with CI hard gate + soft commit hint.
- Muse flagged bootstrap paradox (checks must pass on the PR that creates them).
- StepFun recommended `docs/plans/tech-debt-tracker.md` (OpenAI harness pattern).

## Outcomes & retrospective

_(fill when archived to `completed/`)_

## Validation

When Phase A ships:

```bash
PYTHONPATH=. uv run python scripts/check_todo.py
PYTHONPATH=. uv run python scripts/check_plans.py
uv run pre-commit run --files TODO.md docs/plans/ AGENTS.md CHANGELOG.md MAINTENANCE.md
```

CI `repo-harness.yml` must pass on the implementing PR.

## External review summary (2026-09-20)

| Reviewer | Verdict |
|----------|---------|
| Muse Spark 1.3 contributor | ~80% shippable; needs spec precision (headings, script contracts, semver ordering) |
| StepFun 3.7 Flash free | Structurally sound; fix incomplete §2, define MAINTENANCE format, pin CI path |

Consensus must-haves for Phase A: canonical `PLANS.md`, `check_*` scripts + tests,
`repo-harness.yml`, `MAINTENANCE.md` bootstrap, open-only TODO (remove on ship),
`commit-msg` soft hint, `archive_plan.py` that edits (not prints).

## References

- [Harness engineering (OpenAI, Feb 2026)](https://openai.com/index/harness-engineering/)
- [Codex ExecPlans cookbook](https://developers.openai.com/cookbook/articles/codex_exec_plans)
- [AGENTS.md best practices](https://developers.openai.com/codex/guides/agents-md)
- Repo: `TODO.md`, `AGENTS.md`, `.githooks/`, `.pre-commit-config.yaml`
