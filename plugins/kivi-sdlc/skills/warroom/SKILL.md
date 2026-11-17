---
name: warroom
description: Oversee 2–3 tickets through the kivi-sdlc pipeline (recon → uav → plan → work) to open PRs. Moves the fleet in waves — all tickets recon, then all plan, then all work — with a fresh background agent per ticket per phase, each ticket in its own worktree. Between the plan and work waves it decides work ordering, stacking a dependent ticket on the one it builds from. Acts as the judgment layer, advancing routine work itself and escalating conservatively. Tracks everything in a persistent warroom spec. Use when you want a couple of related tickets driven to PR at once without babysitting each. Not for a single ticket, and hard-capped at 3. Never writes code; it commands the agents that do.
argument-hint: "[2-3 ticket keys (e.g. PROJ-123 PROJ-124) and/or a carve roadmap path]"
disable-model-invocation: true
---

## What warroom is

warroom is the command center. You hand it **2–3 tickets**; it drives them through the kivi-sdlc pipeline — `/recon → /uav → /plan → /work` — to open PRs. Each ticket lives in its own **worktree**, and each phase of it is run by a **fresh background agent** — the spec on disk is the handoff between phases, never an agent's memory.

The fleet moves in **waves**: every ticket completes `recon` before any starts `plan`, and every ticket completes `plan` before any starts `work`. Between the plan and work waves sits the **ordering checkpoint** — with every plan in hand, warroom decides whether the work can run in parallel or must be **stacked** (a dependent ticket branching off the one it builds from).

warroom never implements. It dispatches, triages, orders, and tracks. It is the **judgment layer**: ticket-agents report to it, and it decides — conservatively — what is worth your attention. The lasting artifact is the **warroom spec**: a persistent board (the anchor) that survives context compaction and lets warroom resume where it left off.

## Hard rules (apply throughout)

- **warroom commands; it never implements.** No production code, no spec writes, no plans. The ticket-agents run the pipeline; warroom orchestrates them. Its only writes are to the **warroom spec**.
- **Roster is 2–3 tickets. This is a hard cap.** One ticket → warroom is the wrong tool; send the user to the direct pipeline and stop. More than three → stop and make them trim. The cap protects both your context and the user's attention.
- **Keep warroom's own context lean.** warroom holds oversight for every ticket across three waves, so it is the context bottleneck — the subagents are not (each gets fresh context in its own worktree). Ticket-agents return **concise reports**, never full plans, file dumps, or diffs. Details live in the spec, the ticket, and the PR; read them only when a decision actually requires it.
- **warroom is the judgment layer; escalate conservatively.** Ticket-agents **cannot reach the user** — warroom is the one channel. Review each report and apply a **high bar**: bring the user only a genuine product/scope decision, an ambiguity you can't safely resolve, conflicting signals, or a blocker. Routine advancement you approve yourself. **Batch** escalations — a wave produces one consolidated prompt, not a message per ticket. If a consequential call is genuinely unclear, surface it rather than guess.
- **One isolated worktree per ticket.** Spawn every ticket-agent with `isolation: worktree` so parallel runs never clobber each other's working tree or branch. (This prevents *concurrent-edit* collisions. It does **not** prevent merge conflicts between two PRs touching the same lines — those are the user's to reconcile.)
- **Fresh agent per phase — never resume one into the next phase.** The pipeline tells a human to `/clear` between recon, plan, and work; warroom honors that by spawning a **new** agent for every phase of every ticket, not `SendMessage`-ing the previous one. The spec block in the ticket's worktree carries everything forward. `SendMessage` to an agent is only for a correction or a spec-write approval **within the phase it is currently running** (e.g. "amend this into your commit"). Never forward a "next: `/clear` then …" line as a resume.
- **The worktree outlives the agents.** Recon creates each ticket's worktree (`isolation: worktree`); record its **path** and branch in the roster from the completion notification. Later-phase agents are spawned **without** `isolation` and briefed to work **only** inside that recorded path — a fresh `isolation: worktree` would start from the default branch and lose the uncommitted spec block. If a ticket's worktree was auto-cleaned (recon left no changes), spawn the next phase with `isolation: worktree` and record the new path.
- **Waves, not races.** Never advance a ticket into the next phase until every ticket has cleared the current one. A wave is a barrier *and* a thinking checkpoint.
- **The warroom spec is the anchor — keep it current.** Update it on every wave transition, escalation, answer, ordering decision, and PR. If you lose context, rebuild state from it.
- **Let the pipeline run; don't gate its routine steps.** A commit and opening the PR are expected pipeline actions — they happen without pinging the user. The firm human gate is **merging**; everything else is warroom's conservative judgment.
- **Spec-backend writes need warroom's approval.** Ticket-agents write the managed `🤖 kivi-sdlc spec` block to whichever backend holds it — tracker, checked-in file, or scratch (see `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`). For a **shared backend** (a tracker field or a checked-in file), before **any** write the agent ends its turn with a `SPEC WRITE REQUEST`: `{ locator, backend, change summary, touches anything outside the 🤖 kivi-sdlc spec block? }`, and waits. warroom reviews it and replies with `SendMessage` — approve, or correct — and the agent then writes and re-reads to verify. A write request is not a phase report and does not clear the wave barrier. Approve routine managed-block writes yourself; bring the user any write that would touch human-authored prose, another field, status, or comments.
- **Done = PR opened.** warroom drives each ticket to an open PR and stands down. **Merging is always yours** — warroom never merges.

## Workflow

### Phase 0 — Muster the roster

1. Resolve `$ARGUMENTS` into the ticket roster:
   - **Ticket keys** (`PROJ-###`, space/comma-separated) → each is a ticket in the roster.
   - **A carve roadmap path** (`.claude/kivi-sdlc/carves/*/roadmap.md`) → read it; its pieces are the roster, and **inherit their dependencies/ordering**.
   - A mix of the two is fine.
2. **Validate the roster size before anything else:**
   - **0** → ask which tickets to run, and stop.
   - **1** → **cut out.** warroom's value is overseeing a fleet; for one ticket it is pure overhead and you lose the richer interactivity of driving it yourself. Tell the user to run `/recon <ticket>` → `/plan` → `/work` directly, and stop.
   - **More than 3** → **stop.** The cap is three. Say why (warroom's own context, and your attention as the single decision point), and ask them to pick three — or to run separate warrooms, one after another.
   - **2–3** → proceed.
3. Read each ticket **including its comments** (through the available tracker client). Note anything hinting at a cross-ticket relationship or shared surface area.
4. **Size the tickets.** Judge each one's weight from the ticket plus a light look at the areas it touches. Each should be plausibly **one PR**. If a ticket is really an epic, say so and recommend `/carve`-ing it first or running it on its own — an oversized ticket is what actually blows warroom's context, not the count. Raise any sizing concern with the user now, before deploying.

### Phase 1 — Open the warroom (write the anchor)

5. Create the warroom home: `.claude/kivi-sdlc/warrooms/YYYY-MM-DD-slug/` (today's date; slug is a 3–5 word kebab summary). Write `warroom.md` from `${CLAUDE_SKILL_DIR}/assets/warroom-template.md`.
6. Populate the roster table (one row per ticket, wave `recon`, status `queued`), any cross-ticket relationships already known (from a carve roadmap or the tickets themselves), an empty escalation queue, and an opening log entry.

### Phase 2 — Brief the campaign

7. Present the plan to the user with `AskUserQuestion` — the roster, the wave structure, any known relationships, and any sizing concerns from step 4. Adjust until it's right. This is the one upfront confirmation; after this, warroom runs the fleet and comes back only when it conservatively judges that something needs the user.

### Phase 3 — Wave 1: recon

8. Spawn one **background agent per ticket** with the **Agent tool** (`general-purpose`, `isolation: worktree`). Launch them **all in a single message** so they run in parallel. Each brief is self-contained and states:
   - **Role**: you carry ONE ticket through ONE pipeline phase, then stop and report. You are commanded by warroom and **cannot reach the user** — never call `AskUserQuestion`; surface everything to warroom instead.
   - **Ticket + phase**: the ticket key/locator, and that this wave is `/recon`. Follow the kivi-sdlc workflow for it (recon dispatches its own `/uav` investigators as needed — expected, not something to ask about).
   - **Run the phase, then stop and report; don't guess.** Run it to its natural end — including recon's spec-block write to the ticket — then **STOP** and return a concise `WARROOM REPORT`: `{ ticket, phase, outcome, locator, worktree path, readiness, open questions[], blockers, areas touched[] }`. Stop early only for a genuine question/decision needing a human, or a blocker. Never advance into the next phase on your own.
   - **Spec writes**: before any write to a shared spec backend, end your turn with a `SPEC WRITE REQUEST` (shape in the hard rules) and wait for warroom's `SendMessage`. Write only what was approved, then re-read to verify.
   - **Be terse.** Summaries only — no full specs, file dumps, or diffs. warroom is context-constrained; detail belongs in the spec/ticket.
   - **Worktree**: you have your own worktree; work only there.
9. Record each agent's id in its roster row; set status `in progress`. When each completes, record its **worktree path** and branch in the roster — every later phase runs there.
10. **Hold the barrier.** Wait for every ticket's report before advancing anything. As each lands, update the spec (status, readiness, areas touched, anything noteworthy).
11. **Triage the wave.** Once all reports are in, decide — conservatively — what needs the user, and bring the whole wave's escalations in **one** consolidated `AskUserQuestion`. Apply answers; if a ticket is unsalvageable, drop it from the roster and note why.

### Phase 4 — Wave 2: plan

12. Spawn a **fresh** agent per ticket to run `/plan` (Agent tool, `general-purpose`, background, **no `isolation`**), all in the same message. Do **not** resume the recon agents. Each brief is self-contained — the new agent knows nothing:
    - the same **Role**, **report**, **spec writes**, and **be terse** rules as step 8;
    - **Worktree**: the ticket's recorded absolute path. First action: `cd` there and confirm `git rev-parse --show-toplevel` matches; every command and file path stays inside it. Never touch the main checkout or a sibling's worktree;
    - **Input**: the uncommitted spec block from the prior phase, at its locator in that worktree — read it, don't rely on the brief to restate it;
    - **Decisions**: the user's answers and warroom's own calls from the recon wave. The agent records them in the spec's Clarifications so the next fresh agent inherits them from disk.

    Record the new agent id in the roster. warroom holds the cross-ticket picture itself — pass a sibling's context down to an agent **only when it actually bears on that ticket** (a dependency, or an overlap warroom has already spotted), never as a blanket briefing.
13. **Hold the barrier** again — every ticket plans before any works. Update the spec as reports land; each report should name the **areas/files the plan will touch**.
14. **Triage the wave** as in step 11: one consolidated escalation prompt.

### Phase 5 — Ordering checkpoint

This is the moment warroom finally knows what each ticket really involves. Decide how the work wave runs **before** launching it.

15. Compare the plans across tickets and classify the relationships:
    - **Independent** — neither builds on the other. Work runs in parallel, each branching from the default branch.
    - **Dependent** — one ticket builds on another's code (B needs A's foundation). Work runs **in sequence**, and B is **stacked**: B's worktree branches from **A's branch**, not the default branch, so B is genuinely built on A.
    - **Overlapping** — no dependency, but the plans touch the same files. Not a reason to stack on its own: note it in the spec, mention it at the ordering escalation, and run them in parallel. Any merge reconciliation is the user's to do. Stack these only if the user asks.
16. Record the resulting **work order / chain** in the warroom spec (e.g. `PROJ-123 → PROJ-124 (stacked)`), with the reason.
17. **Escalate the ordering to the user.** This is a genuine decision, not routine — present the proposed order and stacking with `AskUserQuestion` and adjust to their preference.

### Phase 6 — Wave 3: work

18. Run the work wave per the agreed order:
    - Every ticket gets a **fresh** `/work` agent, spawned exactly as in step 12 (no `isolation`, briefed with the recorded worktree path, the plan wave's decisions, and repo conventions for branching, commits, and PRs). Never resume a plan agent.
    - **Work notes are mandatory.** The brief orders: commit → open the PR → then `/work`'s spec write (Stage flip + collapsed **Work notes**, PR link included) through a `SPEC WRITE REQUEST`. They are the only memory a later `/respond` agent gets — reject a write request whose notes are thin (no decisions, deviations, or soft spots) and send it back.
    - **Parallel tickets**: spawn their work agents together in one message.
    - **Stacked chain**: run it in sequence. Spawn A's; when A's work is complete and its **PR is open**, spawn B's with the instruction to branch from **A's branch** and open its PR **against A's branch** (a stacked PR, retargetable to the default branch once A merges). Repeat down the chain.
19. Each agent runs `/work` to its natural end — implementation, review, commits, PR — then reports `{ ticket, phase, outcome, pr, work notes written, follow-ups[], blockers }`.
20. **Hold the barrier** until every ticket has an open PR. Update the spec as each lands. Triage and escalate conservatively, batched.
21. **Handle trouble.** If an agent errors, stalls, or returns something incoherent, surface it with the options you see (retry the phase with a fresh agent in the same worktree, intervene manually, drop the ticket). Never silently retry an irreversible step. If a stacked ticket's blocker fails, hold the dependent and tell the user.

### Phase 7 — Stand down

22. Set the spec status to `stood down` and give a final muster: each ticket, its PR link (noting any stacking), and any follow-ups the agents surfaced.
23. Leave merging to the user — in a stacked chain, say which PR merges first. Never merge, and never write implementation code.
