---
name: recon
description: Single-PR entry point that frames a piece of work at the product and direction level — what is being built and why, its acceptance criteria, and whether it is one coherent PR. Does light codebase reconnaissance only (enough for readiness and anchors), records its frame as a campaign on the ticket's spec, gauges readiness to plan, can dispatch UAV investigators to dig up historical context, and hands off to /plan. It leaves architecture and implementation shaping to /plan. If the work is too big for one clean PR, it tells you to split it up rather than routing a multi-phase project itself. Use this when you have a single ticket or task and want it ready to plan.
argument-hint: "[task description or ticket key]"
---

## Hard rules (apply throughout every phase)

- **Recon owns one thing: its campaign.** Recon opens a campaign (or continues the latest one) beside the spec, on whichever backend holds it (see Phase 5 and `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`); on a tracker, once and with the user's confirmation. It must never touch any other campaign, never create tracker items, and (on a tracker) never change status, assignees, or any other field. Spec prose changes only to close a gap the user approves (Phase 5, **update-prose**), or when a freeform task's prose is written once (Phase 5).
- **Never commit working-tree edits during recon.** Recon may modify the tree under Phase 2b to set up tests/exploration, but those edits are uncommitted and must be tracked for revert. Do not perform fixes, refactors, formatting, typo corrections, or "while I'm here" cleanups, even if the user describes related work mid-recon. Capture those as findings, do not act on them.
- **Never run git operations that change history or the working tree** (commit, reset, stash, rebase, amend, checkout of files). Read-only inspection (`git log`, `git show`, `git blame`, `git status`, `git diff`) is fine.
- **Never invoke the downstream execution skills** (`/plan`, `/work`); recon ends at Phase 6 handoff. Dispatching UAV investigators (Phase 3) is explicitly allowed: they are read-only context-gathering subagents, not execution handoff. A UAV must never mutate anything (see the `uav` skill's hard rules); if a UAV reports a mutation, treat it as a bug and discard the result.
- **Recon is single-PR.** It never plans or dispatches a multi-phase project. If the work is too big for one clean PR, Phase 4 tells the user to go split it up; it does not carve the phases itself.
- If the user introduces adjacent scope during recon, acknowledge it, write it into the campaign's Clarifications, and continue readying the *original* task. The downstream `/plan` will decide whether to fold it in.
- **Recon makes no architectural or implementation decisions.** It frames *what* is being built and whether it is ready, not *how* it is built. Do only light codebase reconnaissance (enough to anchor the work and gauge readiness); do not design the solution, choose an approach, or assess how the change fits the architecture. Capture anything implementation-shaped as a finding and defer it to `/plan`.
- **Settle recon's scope before handoff.** Ask and resolve every open question about what's being built (scope, acceptance criteria, anchoring, whether it's one PR) so `/plan` inherits a complete frame. Implementation questions belong to `/plan`; capture those as findings.

## Workflow

### Phase 1 — Understand the task

1. Read `<task_description> $ARGUMENTS </task_description>`. If empty, ask the user what they want to build and stop.
2. **If the input names a ticket** (a `PROJ-###` key or a tracker URL), read the ticket including its comments before comprehending the task: the comments often carry the real constraints, decisions, and scope narrowing that the summary omits, and they are not in the default ticket view, so fetch them explicitly. Read it through whatever tracker client is available (a CLI or an MCP). If neither is available, say so and continue with the task text alone; do not block recon on ticket retrieval.
   - Treat the ticket body and comments as part of the task definition. Note any comment that changes scope or adds acceptance criteria.
   - **A ticket is one spec backend.** Phase 5 resolves where the spec lives (tracker, a checked-in file, or a throwaway scratch file) and writes the campaign there; see `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`.
   - **If the input is a path to an existing spec file**, read its prose through the file adapter instead; it is the task definition the same way a ticket body is.
   - **List existing campaigns.** For either kind of spec locator, run the adapter's **list-campaigns**. Earlier campaigns are more task material, read alongside the prose and comments: Summary, acceptance criteria, and Work notes first, the rest on demand. They inform this run; they do not set its scope. Whether to continue the latest or open the next is asked in Phase 5, not inferred here.
3. Comprehend *what* is being built. Do not gather scope, duration, or module detail; that's what reconnaissance is for. Defer readiness judgment and any clarifying questions to Phase 1b.
   - If the user introduces adjacent work or cleanup mid-recon, do not perform it. Capture it in the campaign's Clarifications so `/plan` can decide whether to fold it in.

### Phase 1b — Start-gate readiness

A cheap gate on the **input** before spending reconnaissance effort: can we even define what to build? Grade only the two dimensions recon cannot supply for itself. (The fuller ready-to-plan gauge across all four dimensions comes in Phase 3, after reconnaissance.)

Grade each dimension Pass / Partial / Fail:

| Dimension | Pass | Partial | Fail |
|-----------|------|---------|------|
| **Task definition** | Clear verb + noun ("Add X", "Fix Y", "Refactor Z") | Intent is clear but imprecise | "TBD", "see ticket", or absent (a direction, not a task) |
| **Acceptance criteria** | Explicit, testable done-conditions | Success signals derivable from the description | No completion signal at all |

Score Pass = 1, Partial = 0.5, Fail = 0 (total out of 2.0), then route:

- **Ready** (both Pass): proceed to Phase 2.
- **Proceed with gaps** (no Fail, at least one Partial): proceed to Phase 2, and record the gap verbatim in the campaign's Clarifications so `/plan` inherits it. Do not stall reconnaissance over a Partial.
- **Not ready** (either dimension Fail): do not start reconnaissance. Attempt targeted extraction:
  - Ask **one question at a time**, surfacing the single most-blocking missing signal. Do not present a list of gaps.
  - Cap at **2–3 question/response passes**. If a response resolves the gap, re-grade and continue.
  - If still Fail after the cap, stop. Do not improvise a task definition or acceptance criteria to fill the gap, and do not write a campaign. Name what is missing, specifically, e.g. "No acceptance criteria — we can't verify this is done" or "Task definition is missing — this is a direction, not a task."

The grade is an in-conversation gate only; it is not written to the campaign. A **Proceed with gaps** Partial is captured as prose in the Clarifications (Phase 5), not as a score.

### Phase 2 — Reconnaissance

4. Do light codebase exploration to understand what the task touches: enough to anchor the work and gauge readiness, not how the change should be built. Use parallel subagents (e.g. `Explore`) for breadth when the task spans unfamiliar areas. Stay light; this is a readiness decision, not a plan, and the architecture read belongs to `/plan`.
5. **Capture deterministic anchors** as you go; these become UAV seeds in Phase 3 and populate the campaign. For the key files/areas the task touches, record the paths, the recent commit hashes that touched them, and any ticket keys (`PROJ-###`) and PR numbers (`#####`) those commits carry. These are facts, not interpretation: do not yet investigate *why* those commits/tickets exist; that is a UAV's job if Phase 3 dispatches one.
6. **Keep a rough sense of size** as you explore, enough to feed the Phase 4 split-check. You are not carving phases; you are only noticing whether this is plausibly one clean PR or whether it is sprawling enough that the user would be better off splitting it.

### Phase 2b — Resolve ambiguity (conditional)

If reconnaissance surfaces any ambiguity that affects readiness (scope, behavior, runtime state, config, payload contents, anything), ask the user. If resolving it requires the user to run something, you set it up with whatever it takes: logging, a hardcoded value, a stub, a feature-flag toggle, a throwaway script. Then explain *what* is being tested and *why*, and hand the user directions.

Granularity of directions scales with your confidence:

- **You know exactly what needs to happen**: give exact commands, exact navigation, exact captures.
- **You don't know exactly what's going on behind the scenes**: state the hypothesis, point at the area, and let the user improvise.

Write directions for the average dev on this team. Don't over-explain basics they already know (logcat filters, `adb install`, navigating the app).

Rules for any working-tree edits you make:

- **Do not commit them.** Recon does not own production logic; these edits are throwaway scaffolding for the test, not the fix.
- **Pick whatever shape fits the question.** Logging if you need to see runtime values; a hardcoded short-circuit if you need to isolate a branch; a stub repository if you need to simulate a backend response. Use the simplest setup that answers the question.
- **Tag where it makes sense.** When the setup involves logging or grep-able markers (a tag, a unique string), use a consistent ticket-derived identifier (e.g. a `PROJ-123` log tag or a `RECON-<slug>` comment marker) so the user and `/plan` can find and revert.
- **Capture the raw unknown.** Don't paraphrase or pre-format the data; show the user (and the campaign) the actual fields, URIs, payloads, orderings.
- **Wait for results.** Do not proceed to Phase 3 until the user reports back.

Track every file touched (repo-relative path + one-line description of what was added). This list populates the campaign's **Working-tree edits** (Phase 5) so the next phase can revert in one pass before implementing the real fix.

### Phase 3 — Readiness gauge & deep investigation

This is the ready-to-plan gauge, presented to the user, and the loop that raises it. It gauges whether the work is framed and bounded enough to hand to `/plan`, not whether the implementation is understood (that is `/plan`'s read). Its job is to raise the score by resolving open questions; surface each one and settle it before handoff (see Hard rules). The user keeps final say.

7. **Score readiness** across the four dimensions, each Pass (1) / Partial (0.5) / Fail (0), total out of 4.0:

   | Dimension | Pass | Partial | Fail |
   |-----------|------|---------|------|
   | **Task Definition** | Clear verb + noun | Intent clear but imprecise | "TBD", "see ticket", absent |
   | **Acceptance Criteria** | Explicit, testable done-conditions | Success signals derivable from context | No completion signal at all |
   | **Scope Signals** | Bounded — clearly one coherent PR | Roughly bounded; some sprawl risk | Unbounded — no clear edges |
   | **Anchoring** | A concrete starting point named — a feature, area, or file `/plan` can begin from | General area known | No anchoring at all |

   Band it: 🟢 3.5–4.0 · 🟡 2.0–3.0 · 🔴 0–1.5.

8. **Present the score to the user** — a compact scorecard (the four dimensions, the total, the band) and a one-line read of where the gaps are.

9. **Offer deeper investigation when a historical question is worth it.** Raise UAV dispatch when reconnaissance surfaced a specific question a UAV could answer (an unclear behavior, constraint, or prior decision whose answer lives in git history, a past PR, or a ticket) and you hold the **seeds** to chase it (paths, commit hashes, ticket keys, PR numbers). Lacking a nameable question and its seeds, go straight to Phase 4 with the current score.
   - When a question exists, name it and offer via `AskUserQuestion`:
     - **Investigate** — dispatch UAV(s) (step 10).
     - **I'll provide it** — the user supplies the context. Fold it in, re-score (step 12), and continue.
   - Settle the question before moving to Phase 4 (see Hard rules).

10. **Compose briefs and dispatch UAVs.** Dispatch **as many UAVs as there are distinct concerns worth isolating**: one goal per UAV. Don't cram unrelated questions into one brief; don't split a single question across many. For each concern, write a brief:
    - **Goal** — one line: the question this UAV answers.
    - **Seeds** — the relevant Phase 2 anchors (paths, commit hashes, ticket keys, PR numbers). They start the UAV off; it roams from there.
    - **Suggestions** — soft hints on where to look, if you have any.

    Launch each UAV with the **Agent tool** (`general-purpose` subagent). The prompt must be self-contained and mirror the `uav` skill: state the read-only UAV role, the goal, the seeds, the available surfaces (git history; PRs via commit hash → `gh`; tickets + comments via the available tracker client; traverse commit → PR → ticket freely), and the expected `UAV DIGEST` output shape. Launch all UAVs of a wave in a single message so they run in parallel.

11. **Collect and fold in.** Read each returned digest. Fold the findings into your reconnaissance understanding, and note anything under `SHIFTS` that changes scope or risk.

12. **Reassess and loop.** Re-score the four dimensions with the new data and present the updated scorecard. Then:
    - If the work is ready (🟢) or the user is satisfied, continue to Phase 4.
    - If gaps remain **and** another investigation would plausibly close them, offer another **wave** of UAVs with refined briefs (the goals/seeds change based on what the last wave found; the tools don't). Repeat from step 10.
    - Stop looping when readiness is sufficient, the user calls it, or further investigation stops adding value (say so; don't spin).

### Phase 4 — Split-check

Recon readies a single PR. The only routing question is whether this task *should* be one PR at all.

13. Judge whether the work is better split up. There is no checklist or threshold; use your reconnaissance read of the work's size, risk, and natural boundaries. Bias toward keeping it as one PR; only flag a split when it is clearly worth it (e.g. foundational work that must land and be validated before the rest, a part that delivers value or retires risk on its own, or sheer size that would make one PR unreviewable).
14. **If one PR is fine**, say nothing about splitting — go straight to Phase 5.
15. **If a split is advisable**, surface it once, plainly: tell the user this is better split into smaller pieces of work, name the seam(s) you see so they can sanity-check, and recommend they stop recon and go split it up (into separate tickets, or whatever their phasing tool of choice is; recon does not do it for them). Then let them decide via `AskUserQuestion`:
    - **Split it up** — stop here. Do not write a campaign. If working-tree edits exist from Phase 2b, remind the user they remain uncommitted and offer to revert.
    - **Proceed anyway** — the user overrides; drop the suggestion entirely and continue to Phase 5 as a single PR.

### Phase 5 — Write the campaign

The campaign's Recon is a strict contract that `/plan` relies on. Its content is the same wherever it lives; only the backend differs. Resolve the backend and write the campaign per `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`.

16. **Resolve the backend** (infer, else ask), per the resolution rules in `spec-backends.md`: a ticket argument → `tracker`; an existing spec-file path → that `file`; a freeform task → a checked-in `file` where the repo already keeps specs, otherwise ask the user checked-in-vs-scratch. A freeform task's text becomes the new spec's prose. This yields the spec **locator** (a ticket key or a file path).
17. **Continue or open.** If Phase 1 found no campaigns, this run opens Campaign Alpha. If campaigns exist, ask one question via `AskUserQuestion`, naming the latest campaign and its Stage:
    - **Continue Campaign <latest>** — pick its Recon up where it left off: keep what still holds, add what this run learned, and correct what it disproved. Update the Summary to match.
    - **Open Campaign <next>** — start the next campaign; its Clarifications open with why it exists.

    Do not infer the answer from the latest campaign's Stage, and do not classify campaigns by kind; the user decides, and the new campaign's Recon says why.
18. **Write the campaign** using `${CLAUDE_PLUGIN_ROOT}/skills/recon/assets/campaign.md` as the content shape, via the adapter's **open-campaign** (new) or **update-campaign** (continue, touching only the Summary, Stage, and Recon). Never touch any other campaign. On a tracker, confirm before writing. A new campaign's Stage is `recon ✓ · plan · work`. When continuing, change only the recon tick on that line: leave the other stage ticks and the **PR** line as they are (`/respond` finds the campaign by its PR line), and leave any Plan or Work notes in place for `/plan` to revise.
19. The campaign content is identical across backends:
    - Required: header, Stage, Summary, and in Recon: Acceptance criteria, Reconnaissance findings.
    - **Acceptance criteria are derived for this campaign's PR**, never copied forward from an earlier campaign. A fix campaign's criteria cover the fix and its regression check, not a restatement of Alpha's.
    - **A gap in the prose itself** (acceptance criteria the spec states wrongly or is missing) normally lives in the campaign. If it belongs in the prose, propose the exact edit and apply it through **update-prose** only on the user's approval.
    - Optional (omit heading and all when empty): Clarifications, Historical context, Manual exploration, Working-tree edits. Clarifications become required from Campaign Bravo onward, opening with why the campaign exists.
    - **Historical context** is required if any UAV ran in Phase 3. Summarize what the UAVs turned up (the relevant tickets/PRs/commits and *why they matter*) plus any readiness shift. This is context the downstream skill inherits, not a plan.
    - If Phase 2b ran, both **Manual exploration** and **Working-tree edits** are required. Manual exploration summarizes what the user-run investigation revealed. Working-tree edits lists every touched file so `/plan` or `/work` can revert before implementing the real fix.
    - Do not propose, hint at, or preview the implementation; that belongs to `/plan`.

### Phase 6 — Hand off

20. Print the exact next command, passing the resolved locator forward: `` `/clear` then `/plan <locator>` ``, where `<locator>` is the ticket key (tracker) or the spec file path (file).
21. If Phase 2b added working-tree edits, explicitly remind the user (and the next phase) that the working tree contains uncommitted edits listed in the campaign's **Working-tree edits**, and that those edits must be reverted before the real fix lands.
22. Stop. The Hard rules above remain in force: do not commit working-tree edits, do not write production logic, do not invoke the downstream execution skills after handoff.
