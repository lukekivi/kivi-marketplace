---
name: plan
description: Brainstorm a feature or change with the user, do the real codebase read to understand how it fits, then produce a clear, implementable spec for /work — centered on the high-level coding decisions (architecture, module placement, approach, contracts) rather than an exhaustive step-by-step checklist. Works from a spec locator — a ticket key or a spec file (checked-in or scratch) — reading the spec prose and its current campaign's Recon and writing the plan into that campaign; or from a freeform task. With no spec, creates `.claude/kivi-sdlc/plans/YYYY-MM-DD-NNN-slug.md`.
argument-hint: "[spec locator (ticket key or spec file), or a feature idea]"
---

## Hard rules (apply throughout every phase)

- **Settle the plan's scope before handoff.** Ask and resolve every open question the plan raises — approach, module placement, contracts — so `/work` inherits decisions, not questions.

## Workflow

### Phase 0 — Detect mode

1. Check if `$ARGUMENTS` is a **spec locator** — a tracker key/URL (`PROJ-###`, a tracker URL) or a path to a spec file with campaigns beside it (the recon spec, checked-in or in `.claude/kivi-sdlc/scratch/`).
   - If yes, enter **spec mode**: through the matching adapter in `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`, read the spec prose and the **current campaign's Recon** — nothing else by default. Recon has already framed the work there — the task, its acceptance criteria, and what reconnaissance learned. That is your starting point: build on it rather than redoing it. Earlier campaigns are on demand: list them and read a Summary first when a question needs one. Record the locator as the output target and pass it forward. Continue in normal mode.
   - If the locator's spec has **no campaign yet**, this is not spec mode — only `/recon` opens campaigns. Treat the prose as the freeform task and write a normal-mode plan file; tell the user that running `/recon <locator>` first would put the plan on the spec.
   - If `$ARGUMENTS` is any other existing file path, read the file's contents and treat them as the freeform task description. Continue in normal mode.
   - Otherwise, proceed in normal mode treating `$ARGUMENTS` as the freeform task description.

### Phase 1 — Understand

2. Read `<feature_description> $ARGUMENTS </feature_description>`; if it is empty, ask what they want to plan and stop.
3. Decide whether brainstorming is needed.
   - If the request already has concrete scope, clear acceptance criteria, and constrained behavior, skip to Phase 2.
   - If the idea is fuzzy, broad, or has multiple possible interpretations, or if the user requests it, brainstorm first.
4. Brainstorm through collaborative dialogue.
   - Reframe the problem as a "How might we..." question.
   - Start with "why" questions and go a few levels deep. The stated request is often a proxy for the real problem.
   - Ask one question at a time using `AskUserQuestion`.
   - Move from broad to narrow: purpose and users first, then constraints, edge cases, dependencies, and success criteria.
   - Prefer multiple choice when natural options exist — it's faster for the user and forces you to think about realistic possibilities.
   - Keep a running list of assumptions and validate them explicitly.
   - Ask about success criteria: how will the user know this worked?
   - Treat constraints as creative inputs; they often determine which approaches are actually viable.
   - Continue until the idea is clear or the user says "proceed."

### Phase 2 — Explore the repo

5. Do the real codebase read — recon kept its reconnaissance light, so this is where the codebase is understood in depth. Explore to understand how the feature fits.
   - Find similar features, adjacent code, and prior attempts at the same problem.
   - Understand the existing architecture. Map the layers, modules, and boundaries the change will touch.
6. Evaluate the change through PHAME lenses.
   - **Hierarchy** — Does the change respect the existing layer structure? Do dependencies flow in the right direction?
   - **Abstraction** — Is the feature at the right level of abstraction? Does it mix high-level orchestration with low-level detail?
   - **Modularization** — Where does this responsibility belong? Would adding it to an existing module create a God module or violate single-purpose? Would a new module be a nano-module?
   - **Encapsulation** — Does the change respect existing boundaries? Would it require exposing internals that should stay private?
   - If the cleanest solution requires refactoring existing code, say so. The architecture is a living thing. New features should not be bolted on — they should be integrated thoughtfully. It is better to refactor first and then add the feature cleanly than to wedge it in and create structural debt.
7. Decide whether more research is needed and announce the decision.
   - **Skip research:** strong local patterns already exist, the repo documents its conventions, and the user has clear intent.
   - **Research when uncertain:** unfamiliar territory, no codebase examples, new technology or library, ambiguous behavior.
8. Dispatch UAV investigators when the uncertainty is *historical* — or whenever the user tells you to investigate deeper.
   - Reach for this when a current behavior, constraint, or prior decision is unclear and the answer lives in git history, a past PR, or a ticket and its comments rather than in the code in front of you.
   - One goal per UAV. For each concern write a brief: **Goal** (one line — the question this UAV answers), **Seeds** (the deterministic Phase 2 anchors: paths, commit hashes, ticket keys, PR numbers), **Suggestions** (soft hints on where to look, optional).
   - Launch each UAV with the **Agent tool** (`general-purpose` subagent). The prompt must be self-contained and mirror the `uav` skill: state the read-only UAV role, the goal, the seeds, the surfaces available (git history; PRs via commit hash → `gh`; tickets + comments via the available tracker client (a CLI or an MCP); traverse commit → PR → ticket freely), and the expected `UAV DIGEST` output shape. **Launch all UAVs of a wave in a single message so they run in parallel.**
   - Fold each returned digest into your understanding and note anything that shifts scope or approach. UAVs are read-only — if one reports a mutation, treat it as a bug and discard its result.

### Phase 3 — Recommend

Do not recommend on a weak foundation — keep exploring (Phase 2) or dispatch UAVs (step 8) until the codebase is understood well enough to commit to an approach.

9. Explore and narrow the solution space.
   - Diverge before converging. Generate a few plausible approaches without judgment first — draw from repo patterns, analogous domains, inversion of the obvious solution, and the simplest thing that could work.
   - Stress-test the strongest options: "Imagine this failed in six months. What went wrong?"
   - Present the 2-3 strongest approaches with: brief description, pros, cons, failure modes, and when it's best suited.
   - Lead with your recommendation and why. Prefer simpler approaches (YAGNI). Highlight any refactoring the recommended approach requires and why it's worthwhile.
   - Ask the user which approach they prefer using `AskUserQuestion`. Refine until aligned.

### Phase 4 — Write the plan

10. Determine the output destination:
   - **Spec mode**: the plan lives in the current campaign. Write its **Plan** section via the adapter's **update-campaign** from `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`, flip its Stage to `recon ✓ · plan ✓ · work`, and refresh its Summary if the plan changes the picture. Never touch the campaign's Recon or any other campaign. Leave the spec prose alone except through an approved **update-prose**. On a tracker, confirm before writing. A long plan may live inline in the campaign or in a local plan file linked from it — keep the campaign readable.
   - **Normal mode** (no spec): generate `.claude/kivi-sdlc/plans/YYYY-MM-DD-NNN-slug.md` where `YYYY-MM-DD` is today's date, `NNN` is the next available zero-padded sequence for that date, and the slug is a short kebab-case summary (3-5 words). Create the `.claude/kivi-sdlc/plans/` directory if it does not exist.
11. Write the plan from `${CLAUDE_SKILL_DIR}/assets/plan-template.md`.
    - Treat the template as a scaffold. Keep only the sections that apply, and add sections when the work needs more structure.
    - Make the high-level coding decisions crisply — architecture, module placement, the chosen approach, and the contracts/interfaces between the pieces. These are the heart of the spec.
    - The task list should be executable but not exhaustively micro-stepped: capture the key implementation steps and decisions, and leave fine-grained sequencing to `/work`. A reader should be able to execute from it without re-deriving the design.
    - If refactoring is part of the plan, list refactoring tasks before feature tasks. Explain what each refactor achieves structurally.
    - Include validation steps: what tests to write, what commands to run, what to verify manually.
    - Resolve every open question with the user before handoff, so the finished plan carries none (see Hard rules). As each is answered, fold the decision into the relevant plan sections (goal, implementation tasks, structural considerations, etc.) and delete the question — a plan should read as a coherent document, not a Q&A transcript.
    - `Related code` must be concrete: repo-relative paths plus one-line reasons each file matters. Vague references like "the auth module" are not useful.
12. After writing, print where the plan landed (plan path or ticket key) and stop.
13. Strongly suggest that the user run `/clear` before starting `/work`. Planning conversations consume significant context — starting `/work` in a fresh session preserves context for the actual implementation. Name the exact next command, passing the locator forward: `/work <locator>` in spec mode, otherwise `/work <plan path>`.
14. Never code here.
