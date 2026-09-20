# TODO

Open work for `kgforais1/pr-agent-kgforais1` (standalone, detached from
`The-PR-Agent/pr-agent` on 2026-09-19). **Open backlog only** — when an item ships,
remove it here and log the outcome in `CHANGELOG.md` (user-facing) and/or
`MAINTENANCE.md` (harness, refactors, process) — archive the ExecPlan under
`docs/plans/completed/` (shipped), `deferred/` (paused), or `superseded/`
(replaced) if one exists). Do not add a Done section to this file.

## Open

### Fork hardening (owner actions, web UI)

- [ ] **Add repo description and topics** (owner account `kgforais1`, repo page →
      About ⚙): description "Detached fork of The-PR-Agent/pr-agent (AI PR review
      agent) with custom changes"; topics `pr-agent`, `code-review`, `llm`.
      Replaces fork-network discoverability lost by detachment.
- Note: ruleset bypass actors intentionally retained (owner decision, 2026-09-19).
  Direct pushes to `main` from a bypass-actor account will bypass the PR requirement
  silently — visible only in push output. Revisit if this ever surprises us.

### Fork cleanup pass

- [ ] **Docs/README audit** — review README and docs/ for upstream-centric claims,
      badges, links, sponsor sections, and "forked from" references; rewrite for a
      standalone repo. (README already has the detached-fork note.)
- [ ] **Packaging/publishing audit** — inventory what assumes upstream's namespaces:
      `publish.yml` (PyPI + 12 Docker targets), `pyproject.toml` package name,
      hardcoded `pragent/pr-agent` Docker Hub refs, and expected secrets
      (`PYPI_API_TOKEN`, `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `RELEASE_TOKEN` —
      check which are even set in this repo). Decide: publish (then rename package +
      images, since `pr-agent`/`pragent` names belong to upstream) or never publish
      (then strip or disable `publish.yml` and document "not published anywhere").
      Owner has never published a package; no commitment made.

### Repo process

- [ ] **Plan/todo lifecycle guidance and repo harness** — codify how work is planned
      and tracked in this repo so every agent session follows it: where durable plans
      live (gitignored `tmp/` plans vanish with local cleanup; decide whether
      substantive plans get promoted into the repo), TODO.md update conventions
      (when items get added and removed on ship), how AGENTS.md should instruct
      agents to check TODO.md at session start, and any supporting scaffolding
      (naming conventions, linting of the tracker, etc.). Aim: no plan or decision
      exists only in chat history.
      **Plan:** [docs/plans/active/plan-lifecycle-harness.md](docs/plans/active/plan-lifecycle-harness.md)

## Scratch notes

Working analysis/plan docs live in the gitignored `tmp/` directory
(`tmp/upstream-pr-prevention-analysis.md`, `tmp/upstream-pr-prevention-plan.md`).
