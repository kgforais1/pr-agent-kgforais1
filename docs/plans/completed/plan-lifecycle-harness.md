# ExecPlan: Plan / TODO lifecycle and repo harness

**Status:** completed
**TODO:** [Plan/todo lifecycle guidance and repo harness](../../TODO.md#repo-process)
**Owner:** repo maintainers + agents
**Created:** 2026-09-20

## Purpose

Codify how work is planned, tracked, and closed in `kgforais1/pr-agent-kgforais1` so
no plan or decision exists only in chat history. Agents should be able to onboard from
the repository alone, following patterns inspired by
[OpenAI harness engineering](https://openai.com/index/harness-engineering/) and
[ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans).

This is a **design ExecPlan** — it specifies policy and file layout. The Phase A
implementation PR adds the executable spec (Concrete Steps, expected transcripts, per-file
edits) in its own Progress section and dogfoods `archive_plan.py --kind maintenance`.

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
│   ├── completed/          # shipped (archived on implementing PR)
│   ├── deferred/           # paused — may resume later
│   └── superseded/         # replaced by another plan — do not resurrect
├── process/
│   ├── todo-conventions.md # when to add/remove open TODO items
│   ├── semver.md           # fork versioning vs upstream tags
│   └── agent-session.md    # session-start checklist for agents
CHANGELOG.md                # user-facing fork changes (semver releases)
MAINTENANCE.md              # harness, CI, refactors, process (under the hood)
TODO.md                     # open work only (no completed history)
```

| Destination | When | Status line | Resume? |
|-------------|------|-------------|---------|
| `completed/` | Work shipped | `**Status:** completed` | No |
| `deferred/` | Paused (blocked, owner hold, waiting on audit, etc.) | `**Status:** deferred` | Yes — move back to `active/` + re-add TODO |
| `superseded/` | Replaced by a new plan/approach | `**Status:** superseded` | No — link replacement in Outcomes |

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

Status line convention: `**Status:** active|completed|deferred|superseded`
(conventionally line 3; linter matches first `**Status:**` in the first 10 lines, not
YAML front-matter).

Required plan headings (exact casing for `check_plans.py`): `## Purpose`, `## Progress`,
`## Decision log`, `## Surprises & discoveries`, `## Outcomes & retrospective`,
`## Validation`.

Pin canonical skeleton in `docs/plans/PLANS.md` at implementation time (verbatim from
[Codex cookbook](https://developers.openai.com/cookbook/articles/codex_exec_plans), SHA
noted in file header) — do not rely on live external fetch in `new_plan.py`.

### 3. TODO.md conventions

**Open backlog only.** `TODO.md` lists work not yet shipped. It does not track
completed items — no `## Done` section. History lives in `CHANGELOG.md` and/or
`MAINTENANCE.md` (what shipped or why deferred/superseded), archived plans under
`docs/plans/{completed,deferred,superseded}/`, and `git log`.

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

`scripts/check_todo.py` enforces: all checklist items use `- [ ]` (unchecked only);
every non-exempt `active/*.md` is back-linked from `TODO.md`; plan links resolve.
Reject any `## Done` section or `- [x]` items. Allow `## Scratch notes` (prose only, no
checkboxes).

**Plan link required** when a TODO item contains `decide`, `audit`, `codify`, or
`refactor` (multi-file), or spans multiple sessions/PRs.

**Exempt from plan link** (pin in `docs/process/todo-conventions.md`):

- Owner web-UI actions (no repo changes): suffix `<!-- no-plan: owner-web-ui -->` on the
  bullet's first line, or match slug in `docs/process/todo-exempt.txt`
- One-line typo fixes (§Non-goals)

Violations print `ERROR: <check> — <file>:<line> <reason>` and exit 1.

Section anchors: keep `### Repo process` under `## Open`; validate `#repo-process`
with `check_todo.py --strict-anchors`.

### 4. Close-on-same-PR workflow (owner preference)

Close an active plan on the **same PR** that ends the work (ship, pause, or replace).
Use `scripts/archive_plan.py --dest completed|deferred|superseded` (default: `completed`):

1. `git mv docs/plans/active/<slug>.md` → `docs/plans/<dest>/<slug>.md`
2. Set `**Status:**` to match dest; fill **Outcomes & retrospective** (≥2 sentences).
   For `deferred/`: state why paused and what unblocks resume. For `superseded/`: link
   the replacement plan (required).
3. **Remove** the open TODO block (multi-line bullets: parse from `- [ ]` until next
   `- [ ]`, `###`, or `##`; match by `**slug**` or `active/<slug>.md` link)
4. Rewrite links from `active/<slug>` → `<dest>/<slug>` in Markdown under `docs/`,
   `README.md`, `AGENTS.md`, and `#` comments in `.github/workflows/*.yml` (code
   docstrings deferred to Phase B). Use `rg -l 'active/<slug>'` then replace.
5. Add entry to `CHANGELOG.md` and/or `MAINTENANCE.md` under `[Unreleased]` with PR #
   and date (see §5). Deferred/superseded usually log `MAINTENANCE.md` only.
6. If dest is `completed/` and `CHANGELOG.md` has release-worthy user-facing changes
   (post packaging audit): bump `pyproject.toml` version and cut a `## [X.Y.Z]` section

**Enforcement:** soft hint at commit time (`.githooks/commit-msg`, exit 0); hard gate in
CI (`repo-harness.yml` on the PR). Never defer steps 1–5 to a follow-up PR.

**Escape hatch:** only when a reviewer requests a split PR; the remainder keeps the
plan in `active/` with a Progress entry naming the follow-up PR/issue. No silent
`deferred/` moves without Outcomes + MAINTENANCE entry.

**Resume from deferred:** `git mv` back to `active/`, set `**Status:** active`, re-add
TODO item with plan link, log resume in `MAINTENANCE.md` on the same PR.

**Rollback:** if a branch is abandoned after archive, `git mv` back to `active/` and
revert TODO/log edits on that branch. Concurrent PRs closing different TODO items may
conflict on `TODO.md` — rebase before merge.

`archive_plan.py` is the single source of truth for steps 1–5; idempotent re-run on an
already-archived slug exits 0 (no-op).

### 5. Changelog, maintenance log, and semver

Two logs, one version line. Both use [Keep a Changelog](https://keepachangelog.com/)
sections (`Added`, `Changed`, `Fixed`, `Removed`, `Security`) under `[Unreleased]`.

| Artifact | Audience | Examples |
|----------|----------|----------|
| `CHANGELOG.md` | Users, operators, downstream consumers | New `/review` behavior, config key changes, bug fixes in tools, breaking API changes |
| `MAINTENANCE.md` | Maintainers, agents, CI | Harness scaffolding, refactors, CI workflows, `AGENTS.md`/plan lifecycle, dependency-only bumps with no user impact |
| `pyproject.toml` `version` | Package releases | Bumps when cutting a `CHANGELOG.md` release (gated on packaging audit) |
| Git tags / Releases | Optional fork policy | Document in `docs/process/semver.md` |

Replace the upstream "no longer updated per release" header (lines 1–9) with a fork
notice pointing to `MAINTENANCE.md` for harness work; keep the 2023 Archive section
above the new divider. Document fork tag policy (`release-drafter.yml` /
`publish.yml` interaction) in `docs/process/semver.md` — interim: no tags until
packaging audit.

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
| Harness/CI/docs-only, no TODO close | `MAINTENANCE.md` only |
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
| Plan lifecycle | `scripts/check_plans.py` + unit tests | Status matches folder (`active`/`completed`/`deferred`/`superseded`); no `**Status:** active` outside `active/`; required headings; Outcomes non-empty (≥100 chars) in non-active folders; `superseded/` must link a replacement plan |
| Markdown links | Phase B: `scripts/check_links.py` (stdlib) | `TODO.md` → plan paths exist; prefer no lychee dep in Phase A |
| AGENTS.md size | Phase B CI warning | Flag if > 200 lines without process pointers near top |

Scripts are stdlib-only (no `pr_agent/` imports) so CI and pre-commit can use `python3
scripts/…` directly. CI: `uv sync --frozen` then `python3 scripts/…` + pytest in
`repo-harness.yml`. Pre-commit local hooks: `python3` only if each check runs <2s.

Bootstrap: `check_plans.py --allow-empty-archives` for the birth PR that creates
`completed/`, `deferred/`, `superseded/`; one-time allowlist until `PLANS.md` /
`MAINTENANCE.md` exist.

### 8. Hooks and CI integration

**Git hooks (`.githooks/`):**

- Existing `pre-push` blocks direct `main` pushes (unchanged)
- New git-native `.githooks/commit-msg` (filename `commit-msg`, `chmod +x`; **not** a
  `.pre-commit-config.yaml` entry): soft warn, **exit 0** always. If commit touches
  `docs/plans/active/` without `TODO.md` in the same commit, hint to run
  `scripts/archive_plan.py --dry-run`. One-line note in `AGENTS.md` hooks setup if needed.

**CI (`.github/workflows/repo-harness.yml`):**

```yaml
# on: pull_request — NO paths filter (cheap scripts; must catch missing-plan violations)
# Python version: match build-and-test.yml
# Jobs: uv sync --frozen → python3 scripts/check_todo.py [--strict-anchors]
#       → python3 scripts/check_plans.py → pytest test_check_*.py -q
# Fail PR on any non-zero exit
```

Do not duplicate full checkout in two workflows; harness checks live here, not in a
second copy of `pre-commit.yml`.

**Doc-gardening (Phase B):** `.github/workflows/doc-gardening.yml`, monthly cron,
detection-only issue listing `active/*.md` whose git birth date (`git log --diff-filter=A
--format=%ci`) is >60 days ago with no open-TODO backlink (mirrors
`upstream-pr-leak-check.yml`).

### 9. Scripts (proposed)

| Script | Contract |
|--------|----------|
| `scripts/check_todo.py` | Multi-line bullet parsing; `--strict-anchors`; exempt grammar; `ERROR: …` format |
| `scripts/check_plans.py` | Status in first 10 lines matches folder; pinned heading list; non-active Outcomes ≥100 chars; `superseded/` requires replacement link; `--allow-empty-archives` |
| `scripts/archive_plan.py` | `--slug S --pr N --dest completed\|deferred\|superseded [--kind user\|maintenance\|both] [--dry-run] [--message]`: block-delete TODO, `git mv` to dest, link rewrite (§4 scope), log bullets with `(PR #N)`; idempotent |
| `scripts/new_plan.py` | `--slug S`: scaffold from pinned `docs/plans/PLANS.md` into `active/` |

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
- [ ] Archive via `archive_plan.py --dest completed --kind maintenance`; remove TODO item; log `MAINTENANCE.md`

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
- [x] Incorporate v1 reviewer feedback (2026-09-20)
- [x] Re-review by StepFun + Muse; incorporate re-review feedback (2026-09-20)
- [x] Phase A implementation shipped (this archive)

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-20 | Plans live under `docs/plans/{active,completed,deferred,superseded}/` | Matches harness layout; keep `active/` clean; deferred may resume, superseded must not |
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
| 2026-09-20 | `repo-harness.yml` runs on all PRs (no paths filter) | Paths filter hollows out plan-link enforcement |
| 2026-09-20 | Allow `## Scratch notes`; exempt grammar for owner-web-ui items | Matches real `TODO.md` shape |
| 2026-09-20 | Harness scripts stdlib-only, `python3` in CI/pre-commit | `uv run` cold-start exceeds 2s hook budget |
| 2026-09-20 | Add `deferred/` and `superseded/` archive folders | Owner: pause vs replace are distinct from ship; resume only from deferred |

## Surprises & discoveries

- Both external reviewers endorsed same-PR close with CI hard gate + soft commit hint.
- Muse flagged bootstrap paradox (checks must pass on the PR that creates them).
- StepFun recommended `docs/plans/tech-debt-tracker.md` (OpenAI harness pattern).
- Re-review consensus (~85% shippable): no structural rework; pin mechanical contracts.

## Outcomes & retrospective

Phase A shipped on this branch: durable plans under docs/plans/{active,completed,deferred,superseded},
process docs, dual CHANGELOG/MAINTENANCE logs, open-only TODO.md, stdlib harness scripts with unit
tests, repo-harness.yml CI on all PRs, and a soft commit-msg hook. The design ExecPlan was archived
via archive_plan.py on the same change set (dogfooding same-PR close).

## Validation

When Phase A ships:

```bash
PYTHONPATH=. uv run python scripts/check_todo.py
PYTHONPATH=. uv run python scripts/check_plans.py
uv run pre-commit run --files TODO.md docs/plans/ AGENTS.md CHANGELOG.md MAINTENANCE.md
```

CI `repo-harness.yml` must pass on the implementing PR.

## External review summary

| Round | Reviewer | Verdict |
|-------|----------|---------|
| v1 | Muse Spark 1.3 contributor | ~80% shippable; spec precision needed |
| v1 | StepFun 3.7 Flash free | Structurally sound; pin CI + MAINTENANCE format |
| v2 | StepFun 3.7 Flash free | Dual-log + open-only TODO endorsed; pin skeleton + block-delete |
| v2 | Muse Spark 1.3 contributor | ~85% shippable; 6 mechanical pins before Phase A |

Phase A blocking pins (from v2): `archive_plan.py` block-delete semantics, exempt
grammar, unconditional `repo-harness.yml`, CHANGELOG header + fork tag policy,
`## Scratch notes` + heading casing, ship `PLANS.md` + process docs + tests.

## References

- [Harness engineering (OpenAI, Feb 2026)](https://openai.com/index/harness-engineering/)
- [Codex ExecPlans cookbook](https://developers.openai.com/cookbook/articles/codex_exec_plans)
- [AGENTS.md best practices](https://developers.openai.com/codex/guides/agents-md)
- Repo: `TODO.md`, `AGENTS.md`, `.githooks/`, `.pre-commit-config.yaml`
