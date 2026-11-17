# kivi-sdlc

Personal SDLC workflow for Claude Code. Spec-driven: when a task has a ticket, **the ticket is the source of truth** — recon fleshes it out and the downstream skills read and update it in place.

## The spec

Every task is readied into a **spec** — a managed block (below your own prose, anchored by a `🤖 kivi-sdlc spec` heading, owned entirely by the tooling) carrying the same content wherever it lives, plus a lightweight `recon · plan · work` **Stage** line so you can see how far a task has gotten.

Where the spec lives is pluggable — see [`spec-backends.md`](spec-backends.md). Two adapters today:

- **tracker** — a work item reached by API. The block lives in the description.
- **file** — a markdown file at a path. This covers both **checked-in** specs (a committed path like `docs/specs/PROJ-123.md`) and **throwaway** ones (`.claude/kivi-sdlc/scratch/`).

`/recon` infers the backend (and asks when it can't), then passes the locator forward so `/plan` and `/work` operate on the same spec.

## Skills

- **`/recon`** — single-PR entry point. Takes a task description or ticket key, reads the ticket and its comments, does focused codebase reconnaissance, presents a readiness score, and can dispatch `/uav` investigators to ascertain historical context. Writes the spec (ticket block, or fallback file) and hands off to `/plan`. If the work is too big for one clean PR, it tells you to go split it up — it does not plan a multi-phase project itself.
- **`/uav`** — Unmanned Ascertainment Vehicle. An autonomous, read-only investigator dispatched by `/recon`, `/plan`, or `/work` (or run standalone) toward a single goal. Given deterministic seeds (paths, commit hashes, ticket keys, PR numbers), it investigates git history, related PRs, and related tickets and their comments — traversing commit → PR → ticket freely — and returns a scoped digest. Changes nothing.
- **`/plan`** — produces a concrete implementation plan. Accepts a ticket key (reads the ticket's spec block, writes the plan back onto it), a freeform task, or a recon fallback spec file. Can dispatch `/uav` investigators when a historical question surfaces.
- **`/work`** — executes a plan end-to-end with subagent review and a commit at the end. Accepts a ticket key (reads the plan from the ticket's spec block) or a plan/todo file path. Flips the Stage line and writes the collapsed **Work notes** when done. Can dispatch `/uav` investigators when a historical question blocks progress.
- **`/respond`** — addresses code review on an open PR. Starts from the spec's collapsed **Work notes** (the handoff `/work` leaves behind), triages each unresolved thread (fix / push back / ask / defer), makes fixes in the review-fix commit style it **infers from the repo** (docs first, then merged-PR history), re-validates, and **drafts** a reply per thread — posting them only when you say to (`--post`, or after reading the drafts). Appends a review round to the Work notes.
- **`/carve`** — divides an **epic** into a set of ready-to-recon pieces. Runs a meta-planning dialogue, proposes how to carve the epic into independently shippable units, resolves a spec backend (tracker or file) the way recon does, and creates one generic ticket/spec per piece — each a **pre-recon seed** carrying its goal, scope, dependencies, and rough areas — plus a roadmap tying them together. Each piece then enters the pipeline on its own via `/recon <locator>`. Carve stays at the **product level** — what each piece delivers and why, not how to build it (that's `/plan`). It sits **upstream** of recon, does not write the managed spec block (recon owns that), and never writes code. Invoked directly when you already know a feature is too big for one PR (recon never routes here — but when recon tells you to split, this is the tool).
- **`/warroom`** — the command center that oversees **2–3 tickets** through the pipeline (`recon → uav → plan → work`) to open PRs. One background agent per ticket, each in its own worktree, moving in **waves**: all tickets recon, then all plan, then all work. Between the plan and work waves it runs an **ordering checkpoint** — with every plan in hand it decides whether work runs in parallel or **stacked** (a dependent ticket branching off the one it builds from, so they're genuinely built on each other). Acts as the **judgment layer**, advancing routine work itself and escalating **conservatively** — only decisions that genuinely need a human, batched per wave. Tracks everything in a persistent **warroom spec**. Accepts ticket keys and/or a `/carve` roadmap. Hard-capped at 3 and not for a single ticket (run the pipeline directly instead). Never writes code — it commands the agents that do; merging stays with you.

## Typical flow

For an epic too big for one PR, start with `/carve "<epic>"` (or `/carve PROJ-123`) to carve it into pieces — each a generic ticket/spec in a tracker or file backend. Then run the flow below on each piece — or hand 2–3 ready pieces to `/warroom PROJ-123 PROJ-124` to drive them to PR in waves while you stay the one decision point.

1. `/recon PROJ-123` (or `/recon "<task description>"`) — review the readiness score; when prompted, choose to investigate deeper (dispatches UAVs), proceed, or supply the context yourself. recon writes the spec onto the ticket.
2. `/clear`, then `/plan PROJ-123` — fleshes the plan onto the ticket's spec block (or writes a local plan file when there's no ticket).
3. `/clear`, then `/work PROJ-123` — implements, reviews, commits, marks the Stage complete, and writes the Work notes.
4. When review lands, `/respond <PR#>` — fixes what's right, drafts replies, and posts them if you say to.
