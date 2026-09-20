# Plans

Durable execution plans for substantial repo work. Ephemeral scratch notes stay in
gitignored `tmp/`; anything that must survive agent sessions, PR handoffs, or local
cleanup is promoted here.

## Layout

| Path | Purpose |
|------|---------|
| `docs/plans/active/` | In-flight ExecPlans linked from `TODO.md` |
| `docs/plans/completed/` | Archived plans (moved here when work ships) |
| `docs/plans/PLANS.md` | ExecPlan template and authoring rules (added by implementation PR) |

## Lifecycle (target state)

See [active/plan-lifecycle-harness.md](active/plan-lifecycle-harness.md) for the
full design. Summary:

1. **Open** — `TODO.md` lists only unfinished work; each item may link to an ExecPlan
   under `active/`.
2. **Implement** — The implementing PR updates the plan (progress, decisions) and
   adds a `CHANGELOG.md` and/or `MAINTENANCE.md` entry on the **same PR** that ships
   the work (user-facing vs under-the-hood).
3. **Close** — On merge: move plan to `completed/`, **remove** the TODO item (no Done
   section), log in the appropriate file(s). Completed history is not kept in `TODO.md`.
