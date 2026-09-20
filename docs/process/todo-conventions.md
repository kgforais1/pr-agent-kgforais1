# TODO.md conventions

`TODO.md` is an **open backlog only**. It does not track completed work.

## Structure

```markdown
# TODO
…
## Open
### <category>
- [ ] **slug title** — description
      **Plan:** [docs/plans/active/<slug>.md](…)   # when required

## Scratch notes
Prose only — no checkboxes.
```

- Checklist items must use `- [ ]` (unchecked). `- [x]` and a `## Done` section are
  rejected by `scripts/check_todo.py`.
- Slugs are `kebab-case` (e.g. `plan-lifecycle-harness`), usually the bold lead phrase
  of the bullet.
- Multi-line bullets continue until the next `- [ ]`, `###`, or `##`.

## When to add a plan link

Required when the item text contains `decide`, `audit`, `codify`, or `refactor`
(multi-file intent), or the work spans multiple sessions/PRs:

```markdown
**Plan:** [docs/plans/active/<slug>.md](docs/plans/active/<slug>.md)
```

## Exempt from plan link

On the first line of the bullet, or listed in `docs/process/todo-exempt.txt`:

| Marker | Use |
|--------|-----|
| `<!-- no-plan: owner-web-ui -->` | Owner-only GitHub UI actions (no repo file changes) |
| `<!-- no-plan: pending-execplan -->` | Open item that will get an ExecPlan soon; temporary |
| `<!-- no-plan: typo -->` | One-line typo / copy fix |

## On ship / defer / supersede

1. Remove the open TODO block (do not move to Done).
2. Archive the ExecPlan with `scripts/archive_plan.py --dest completed|deferred|superseded`.
3. Log in `CHANGELOG.md` and/or `MAINTENANCE.md` on the **same PR**.

History lives in those logs, `docs/plans/{completed,deferred,superseded}/`, and `git log`.
