---
name: carve
description: Divide an epic into a set of ready-to-recon pieces. Runs a meta-planning dialogue to understand the full scope, proposes how to carve the epic into independently shippable units, resolves a spec backend (tracker or file) the way recon does, and creates one generic ticket/spec per piece — each a pre-recon seed carrying its goal, scope, dependencies, and rough areas — plus a roadmap tying them together. Each piece then enters the pipeline on its own via `/recon <locator>`. Use this when a feature or epic is too large for a single PR and you want it split into discrete, pipeline-ready work items. Carve sits upstream of recon; it never writes campaigns (recon opens Campaign Alpha on each piece) and never writes implementation code.
argument-hint: "[epic to divide — a description, an epic ticket key, or a file]"
disable-model-invocation: true
---

## What carve produces

Carve's output is a set of **pieces**, each a **generic ticket/spec** in a resolved backend (a tracker ticket or a spec file — see `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`), plus a **roadmap** tying them together. Each piece is a **pre-recon seed**: the body a work item starts life with — goal, scope, dependencies, rough areas — ready to be picked up by `/recon`. Carve is **upstream** of recon: a piece re-enters the pipeline at `/recon <locator>`, then `/plan`, then `/work`.

## Hard rules (apply throughout every phase)

- **Carve divides; it never implements.** No production code, no refactors, no drive-by edits. It does not flesh out plans — that is `/plan`.
- **Carve stays at the product level.** It names *what* each piece delivers and *why*, plus its scope, boundaries, and sequencing — not *how* to build it. Carve may surface a technical constraint or suggest an approach, but only when it's obvious or truly necessary to size or sequence a piece, and always as a suggestion, not a directive. Real design and implementation decisions belong to `/plan`.
- **Carve writes pre-recon seeds, not campaigns.** Each piece carries only its *body* (the spec prose a ticket/spec starts with): goal, scope, dependencies, rough areas. Carve must **never** write a campaign, a **Stage** line, or acceptance criteria — recon opens Campaign Alpha *beside* the seed. Leave acceptance criteria to recon.
- **Carve may create tracker items** (unlike recon). Creating one ticket per piece is its whole job in the tracker backend. On a tracker, **confirm before creating** anything, and never touch the epic's own prose.
- **Read-only git; never commit a piece or roadmap on its own.** File-backed pieces are left in the working tree (scratch files under `.claude/` are untracked; checked-in pieces ride along with later work's commits). Do not create a dedicated commit for carve output. No history-changing git operations.
- **One backend for the whole epic.** Resolve the backend once (Phase 5) and create every piece in it.

## Workflow

### Phase 1 — Understand the epic

1. Resolve `$ARGUMENTS` and take in whatever context it makes available — all of it is the epic description. Where it already carries analysis of the work (findings, constraints, seams, history), build on it rather than redoing it.
   - If the input names an **epic ticket** (a `PROJ-###` key or a tracker URL), read the ticket **including its comments** — scope, constraints, and child-work expectations tend to hide in the comments. Read it through whatever tracker client is available (a CLI or an MCP). If neither is available, say so and continue with the task text alone.
   - If it's an existing file path, read its contents.
   - Otherwise, read `<epic_description> $ARGUMENTS </epic_description>` directly.
   - If empty, ask what they want to build and stop.
2. Decide whether brainstorming is needed. If the scope is already clear and the carve is obvious, skip to Phase 2.
3. Brainstorm through collaborative dialogue — one question at a time using `AskUserQuestion`. Focus on what matters for carving the epic:
   - **Goal**: What does "fully shipped" look like? What's the user or business outcome?
   - **Value**: Which parts deliver value independently, before the whole epic is done?
   - **Risk**: Which parts are technically uncertain or high-risk and should be isolated and proved out first?
   - **Constraints**: External dependencies, other teams, migrations, deadlines — anything that constrains ordering?
   - **PR norms**: Does the team have strong opinions on PR size or review scope?
   - Move from broad to narrow. Stop when you have enough to move on.

### Phase 2 — Orient

4. Ask the user if they already have a rough breakdown in mind using `AskUserQuestion`.
   - If yes: collect their pieces (all at once, or one at a time if they prefer). Record them as the working breakdown, then proceed to Phase 3 with a **validation** lens.
   - If no: proceed to Phase 3 with a **generative** lens.

### Phase 3 — Explore the repo

5. Explore the codebase. The goal depends on what Orient found:
   - **Validating user pieces**: look for evidence their boundaries hold at the code level. Hidden dependencies between pieces? Is any piece much larger or smaller than expected? Does the ordering make sense given how the code is structured? Is there a more natural way to divide things the user may not have considered?
   - **Generating pieces**: look for natural seams where the work splits cleanly. Find the layers, modules, and boundaries the epic touches. Identify what exists vs. what must be built. Note anything foundational that must come first.
   - Use parallel subagents (e.g. `Explore`) for breadth when the epic spans unfamiliar areas. Stay light — you are finding seams at the product/architecture level, not designing or planning any single piece.
6. In both cases, evaluate through a sequencing lens:
   - What work unblocks other work? (foundational first)
   - What work can merge safely even if the epic is incomplete? (feature flags, internal-only changes, pure additions)
   - What work carries the most external risk or unknowns? (consider isolating early so failures are cheap)

### Phase 4 — Propose the pieces

7. Present the carve — derived from repo exploration or built from the user's input. For each piece, define:
   - **Goal**: One sentence — what this piece delivers.
   - **Independently shippable**: Can it merge without breaking anything even if the next piece isn't done?
   - **Dependencies**: Which pieces must land before this one (and which it unblocks)?
   - **Rough scope**: the product surfaces and high-level areas it touches — enough to size and sequence it; the design belongs to `/plan`.
8. Ask the user to review and refine using `AskUserQuestion`. Adjust until the carve feels right.
   - Common adjustments: split a piece that's too large, merge two that are too small, reorder based on dependencies or team preferences.

### Phase 5 — Resolve the backend

Resolve **one** backend for the whole epic, the way recon resolves a spec backend (see `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`). Infer first; ask only when inference fails. Unlike recon, carve **may create tracker items**, so the tracker backend is available even for a freeform epic.

9. Infer:
   - **Epic is a tracker ticket/URL** → `tracker`. Create each piece as a tracker item linked to the epic (a child, or a relates-to link if the tracker lacks a parent/child relation).
   - **Epic came from a recon scratch file, another file path, or freeform** → ask the user (one `AskUserQuestion`): create the pieces as **tracker tickets**, or as **files**? If files, follow recon's file rules — a checked-in specs home if the repo keeps specs checked in, otherwise scratch under `.claude/`.
10. The result is, per piece, a **locator** to hand forward: a ticket key (tracker) or a file path (file).

### Phase 6 — Create the pieces and roadmap

11. Decide the carve home for the roadmap (and file-backed pieces): `.claude/kivi-sdlc/carves/YYYY-MM-DD-slug/` where `YYYY-MM-DD` is today's date and slug is a 3-5 word kebab-case summary of the epic. Create the directory (and a `pieces/` subdirectory for the file backend).
12. Create each piece from `${CLAUDE_SKILL_DIR}/assets/piece-seed-template.md` — the **seed body only**, no campaign:
    - **File backend**: write the seed to `pieces/NN-slug.md` (zero-padded, e.g. `pieces/01-auth-foundation.md`). Markdown throughout. The optional frontmatter may point back to `roadmap.md`. The piece's locator is this file path.
    - **Tracker backend**: **confirm, then create** a ticket — title = piece title, description = the seed body rendered in whatever format the field requires — linked to the epic. The piece's locator is the new ticket key. The seed lives in the ticket description; no local piece file is written.
    - Fill in: goal, scope (in/out), dependencies (requires/enables), the affected areas (product surfaces / high-level areas, for orientation only), reference material (any code pointers surfaced in Phase 3 that recon/plan may find useful — not a prescription of what to change; plus in-progress branches/stashes/draft PRs that apply), and notes from the dialogue. **Do not** write acceptance criteria, a design, or a campaign — recon and plan add those.
13. Record dependencies **both** at the roadmap level and, for hard blocks, at the backend level:
    - The roadmap always carries the ordered piece table plus a dependencies/ordering section.
    - When a piece is **truly blocked** by another, link them explicitly: on a tracker, create an "is blocked by" issue link between the created tickets; in the file backend, record the blocking piece's locator under that piece's **Requires**.
14. Write `roadmap.md` from `${CLAUDE_SKILL_DIR}/assets/roadmap-template.md`:
    - Include the epic overview, the ordered piece table (all statuses `seed`, the Locator column holding each piece's ticket key or file path), the dependencies/ordering section, and any cross-cutting constraints or open questions from the dialogue.

### Phase 7 — Hand off

15. Print the roadmap path and each piece's locator.
16. Tell the user each piece is ready to recon: run `` `/recon <locator>` `` per piece (then `/plan <locator>`, then `/work <locator>`). Suggest `/clear` between sessions — each piece is its own pipeline run.
17. Never write implementation code here.
