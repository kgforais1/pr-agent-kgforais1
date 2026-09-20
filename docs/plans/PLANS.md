# ExecPlans (this repository)

Source: adapted from the OpenAI Codex cookbook
[Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans)
(archived recipe; pin date 2026-09-20). Do not re-fetch at runtime — this file is the
scaffold for `scripts/new_plan.py`.

## When to write an ExecPlan in this repo

Use an ExecPlan when work spans multiple files, sessions, or PRs, or when a `TODO.md`
item says decide / audit / codify / refactor (multi-file). Exempt one-line typo fixes
and owner web-UI actions marked `<!-- no-plan: owner-web-ui -->`.

Layout: `docs/plans/active/` (in-flight), `completed/` (shipped), `deferred/` (paused),
`superseded/` (replaced). Close with `scripts/archive_plan.py` on the same PR that ends
the work. See `docs/plans/README.md`.

Status line (first 10 lines): `**Status:** active|completed|deferred|superseded`

Required headings for `scripts/check_plans.py` (exact casing): `## Purpose`,
`## Progress`, `## Decision log`, `## Surprises & discoveries`,
`## Outcomes & retrospective`, `## Validation`.

---

# Codex Execution Plans (ExecPlans)

This document describes the requirements for an execution plan ("ExecPlan"), a design
document that a coding agent can follow to deliver a working feature or system change.
Treat the reader as a complete beginner to this repository: they have only the current
working tree and the single ExecPlan file you provide. There is no memory of prior plans
and no external context.

## How to use ExecPlans and PLANS.md

When authoring an executable specification (ExecPlan), follow PLANS.md to the letter. If
it is not in your context, refresh your memory by reading the entire PLANS.md file. Be
thorough in reading (and re-reading) source material to produce an accurate
specification. When creating a spec, start from the skeleton and flesh it out as you do
your research.

When implementing an executable specification (ExecPlan), do not prompt the user for
"next steps"; simply proceed to the next milestone. Keep all sections up to date, add or
split entries in the list at every stopping point to affirmatively state the progress
made and next steps. Resolve ambiguities autonomously, and commit frequently.

When discussing an executable specification (ExecPlan), record decisions in a log in the
spec for posterity; it should be unambiguously clear why any change to the specification
was made. ExecPlans are living documents, and it should always be possible to restart
from only the ExecPlan and no other work.

When researching a design with challenging requirements or significant unknowns, use
milestones to implement proof of concepts that allow validating whether the proposal is
feasible.

## Requirements

NON-NEGOTIABLE REQUIREMENTS:

- Every ExecPlan must be fully self-contained.
- Every ExecPlan is a living document. Contributors must revise it as progress is made.
- Every ExecPlan must enable a complete novice to implement the feature end-to-end.
- Every ExecPlan must produce a demonstrably working behavior, not merely code changes.
- Every ExecPlan must define every term of art in plain language or not use it.

Purpose and intent come first. Begin by explaining why the work matters from a user's
perspective, then guide the reader through the exact steps to achieve that outcome.

## Formatting

When writing an ExecPlan to a Markdown file where the content of the file is only the
single ExecPlan, omit outer triple-backtick fences. Prefer sentences over lists. Checklists
are permitted only in the Progress section, where they are mandatory.

## Living plans and design decisions

- ExecPlans are living documents. Record decisions in the Decision log.
- ExecPlans must contain and maintain Progress, Surprises & discoveries, Decision log,
  and Outcomes & retrospective. These are not optional.
- At completion, write Outcomes & retrospective summarizing what was achieved.

## Skeleton of a Good ExecPlan

    # <Short, action-oriented description>

    **Status:** active
    **TODO:** [link](../../TODO.md#anchor)
    **Created:** YYYY-MM-DD

    This ExecPlan is a living document. Maintain Progress, Surprises & discoveries,
    Decision log, and Outcomes & retrospective as work proceeds. Follow
    docs/plans/PLANS.md.

    ## Purpose

    Explain what someone gains after this change and how they can see it working.

    ## Progress

    - [x] (YYYY-MM-DD) Example completed step.
    - [ ] Example incomplete step.

    ## Surprises & discoveries

    - Observation: …
      Evidence: …

    ## Decision log

    | Date | Decision | Rationale |
    |------|----------|-----------|
    | YYYY-MM-DD | … | … |

    ## Outcomes & retrospective

    Summarize outcomes, gaps, and lessons learned at completion.

    ## Context and Orientation

    Name key files by full path. Define non-obvious terms. Do not refer to prior plans
    that are not checked in.

    ## Plan of Work

    Describe the sequence of edits. Name files and what to change.

    ## Concrete Steps

    Exact commands and working directory. Show short expected transcripts.

    ## Validation

    How to prove success (commands, expected output). Alias of Validation and Acceptance.

    ## Idempotence and Recovery

    Safe retries and rollback.

    ## Artifacts and Notes

    Concise evidence of success.

    ## Interfaces and Dependencies

    Libraries, modules, and signatures that must exist when done.

If you follow the guidance above, a single, stateless agent — or a human novice — can
read the ExecPlan from top to bottom and produce a working, observable result.
