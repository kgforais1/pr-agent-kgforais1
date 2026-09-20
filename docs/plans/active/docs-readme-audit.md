# Docs and README standalone audit

**Status:** active
**TODO:** [Docs/README audit](../../../TODO.md#fork-cleanup-pass)
**Created:** 2026-09-20

This ExecPlan is a living document. Maintain Progress, Surprises & discoveries,
Decision log, and Outcomes & retrospective as work proceeds. Follow
`docs/plans/PLANS.md`.

## Purpose

Make `README.md` and `docs/` describe `kgforais1/pr-agent-kgforais1` as a standalone
detached fork: drop or rewrite upstream-centric claims, badges, sponsor copy, and
"forked from" language so a newcomer can install and operate this repo without
thinking they are on The-PR-Agent/pr-agent or Qodo's product.

Out of scope unless it is a docs-only mention: `publish.yml` / PyPI / Docker Hub
namespace decisions (that is the separate packaging audit).

## Progress

- [x] Draft context and plan of work
- [x] Implement
- [ ] Validate
- [ ] Archive on same PR (`scripts/archive_plan.py`)

Research: `tmp/docs-readme-audit-research.md` (gitignored). Strategy: Option 2
(fork-first landing, upstream as lineage). Locked decisions below; Composer
implements on `docs/readme-audit`.

## Surprises & discoveries

- Naive bulk-replace of every `github.com/the-pr-agent/pr-agent` URL would
  404 demo PRs and upstream issue numbers that do not exist on this fork.
  Source/clone/blob links go to the fork; historical demos stay upstream and
  are labeled.
- `docs-ci.yaml` still runs `mkdocs gh-deploy` and `docs/docs/CNAME` was
  `docs.pr-agent.ai`. CNAME deleted in this rewrite so a fork Pages deploy would not mis-claim upstream's domain.
- Implementation used a Python bulk script for blob/tree/clone URL rewrites under `docs/docs/`; demo PR and upstream issue links were left in place and labeled where visible.
- Parent review (2026-09-20): Composer omitted `.github/ISSUE_TEMPLATE/config.yml` (upstream Discussions). Also tightened “our” Docker/Action wording, CLI/`pip` upstream-PyPI caveats, `/help_docs` issue label, MOSAICO “ships in every release” claim, and the MkDocs tagging-bot link (relative `../../README.md` is outside `docs_dir`).

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-20 | Created plan `docs-readme-audit` | Scaffolded via `scripts/new_plan.py` |
| 2026-09-20 | Keep public name **PR-Agent**; identify repo as `kgforais1/pr-agent-kgforais1` | No rename without an explicit owner naming decision |
| 2026-09-20 | Remove Qodo/Codium promo, sponsors, “Big News”, Naor/foundation, GTM | Fork-first; one lineage subsection only |
| 2026-09-20 | Docs stay in-repo; no invented Pages URL; delete `docs/docs/CNAME` | No fork domain yet; do not publish as `docs.pr-agent.ai` |
| 2026-09-20 | Keep Docker/`uses:` examples with an upstream-artifact caveat | Packaging audit is a separate TODO; examples stay technically accurate |
| 2026-09-20 | SECURITY keeps one-sentence “not Qodo commercial”; reports go to this fork | Legal separation without routing readers to Qodo or upstream advisories |
| 2026-09-20 | Demo PRs stay as labeled upstream examples | Those PRs/comments live only on The-PR-Agent/pr-agent |
| 2026-09-20 | `RELEASE_NOTES.md` stays; add archival header only | Historical upstream notes; not onboarding |
| 2026-09-20 | Update `pyproject.toml` `[project.urls]` to this fork | Identity metadata (Homepage/Docs/Repo/Issues); leave package name and authors for the packaging audit |

## Outcomes & retrospective

_(fill when archived)_

## Context and Orientation

Name key files by full path. Define non-obvious terms.

## Plan of Work

Describe the sequence of edits.

## Concrete Steps

Exact commands and working directory.

## Validation

Commands and expected output that prove success.

## Idempotence and Recovery

Safe retries and rollback.

## Artifacts and Notes

_(optional)_

## Interfaces and Dependencies

_(optional)_
