# TODO

Tracked work for the `kgforais1/pr-agent-kgforais1` repo (standalone, detached from
`The-PR-Agent/pr-agent` on 2026-09-19). Update this file as items complete.

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
      (when items get added, moved to Done, pruned), how AGENTS.md should instruct
      agents to check TODO.md at session start, and any supporting scaffolding
      (naming conventions, linting of the tracker, etc.). Aim: no plan or decision
      exists only in chat history.

### Security

- [ ] **Dependabot findings** — 1 critical, 1 high, 1 moderate on the default branch
      (see Security tab). Triage and fix or dismiss-with-reason.

## Done (2026-09-19)

- [x] PR #1 merged — `.githooks/` (pre-push blocks direct pushes to `main`;
      pre-commit shim bridging to the pre-commit framework) + AGENTS.md safety rules.
- [x] Detached from fork network (UI, owner action) — PRs to upstream **from this
      repository** are now impossible server-side, accidental and deliberate alike.
      (This does not stop a brand-new fork of upstream being created under this
      account; see the leak-check item below.)
- [x] `.gitignore` — scratch dirs (`tmp/`, `temp/`), secrets patterns, tool caches.
- [x] `AGENTS.md` — upstream-PR prohibition, base-verification rule, no-bypass rule,
      no-direct-push rule with release-workflow exemption.
- [x] `.github/workflows/upstream-sync-check.yml` — daily 08:00 UTC, maintains a
      single rolling `upstream-sync` tracking issue for new upstream commits.
- [x] `.github/workflows/upstream-pr-leak-check.yml` — weekly **detection-only**
      check for rogue PRs opened against upstream from this account (covers the
      new-fork residual risk; it cannot prevent them).
- [x] CodeQL dual-setup conflict resolved by disabling GitHub's default setup
      (kept the richer in-repo workflow).
- [x] `gh repo set-default kgforais1/pr-agent-kgforais1` in the primary clone.

## Scratch notes

Working analysis/plan docs live in the gitignored `tmp/` directory
(`tmp/upstream-pr-prevention-analysis.md`, `tmp/upstream-pr-prevention-plan.md`).
