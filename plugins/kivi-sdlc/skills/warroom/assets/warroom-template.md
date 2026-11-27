<!--
The WARROOM SPEC — the anchor for one warroom operation. warroom owns this file
entirely and keeps it current on every wave transition, escalation, answer,
ordering decision, and PR. If context is lost, operation state is rebuilt from here.

Keep entries terse. This is a board, not a transcript; full specs live on the
tickets, plans in their campaigns, and detail in the PRs.
-->

# Warroom — <operation name>

**Opened:** <YYYY-MM-DD>
**Status:** in progress
**Roster size:** <2 or 3> (hard cap 3)
**Done when:** every ticket has an open PR (merging stays with the user)

## Roster

| Ticket | Wave | Status | Areas touched | PR | Worktree (path · branch) | Agent (current phase) |
|--------|------|--------|---------------|-----|--------------------------|-----------------------|
| PROJ-### | recon | queued | — | — | — | — |

- **Wave:** `recon` → `plan` → `work` → `PR`. The fleet clears each wave before any ticket enters the next.
- **Agent:** a fresh agent runs each phase — replace the id on every wave; the worktree path stays.
- **Status:** `queued` · `in progress` · `awaiting you` · `blocked` · `done` · `dropped`

## Cross-ticket relationships

<How the tickets relate, as understood so far. Updated at the ordering checkpoint.>

- **PROJ-123 ↔ PROJ-124** — `independent` | `dependent` | `overlapping` — <reason / shared surface>

## Work order

<Decided at the ordering checkpoint, after the plan wave. Remove the placeholder once set.>

- **Order:** <e.g. `PROJ-123 → PROJ-124 (stacked)`, or `PROJ-123 ∥ PROJ-124 (parallel)`>
- **Reason:** <why this order / what the dependent builds on>
- **Stacking:** <e.g. PROJ-124 branches from PROJ-123's branch; its PR targets that branch and can be retargeted once PROJ-123 merges. Remove if parallel.>

## Escalation queue

<Items warroom judged worth the user's attention, batched by wave. Check off when answered.>

- [ ] **PROJ-###** (`<wave>`) — <the decision or blocker, and what warroom needs back>

## Log

<Append-only record: wave launches and barriers, escalations and answers, the ordering decision, PRs, errors, drops.>

- <YYYY-MM-DD HH:MM> — Opened warroom with roster: <tickets>.
