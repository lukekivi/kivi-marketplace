# kivi-sdlc

Personal SDLC workflow for Claude Code, run like a field operation: recon the task, plan it, work it to a PR, respond to review. Spec-driven: when a task has a ticket, **the ticket is the source of truth**. The skills read it and record their work in campaigns beside it, leaving what you wrote alone unless you approve an edit.

## The spec

Every task has a **spec** in two parts: the **prose** (the ticket description or spec file; it's yours, and the tooling edits it only to close a gap, with your approval of the exact edit) and **campaigns** (the tooling's output, stored beside the prose). A campaign is one full trip through the pipeline (recon → plan → work → respond). Its anatomy, naming, and header marker are defined once, in [`campaign.md`](skills/recon/assets/campaign.md).

Where the spec lives is pluggable; see [`spec-backends.md`](spec-backends.md). Two adapters today:

- **tracker** — a work item reached by API. Prose is the description; each campaign is one comment.
- **file** — a markdown file at a path, with campaigns in a sibling directory: `docs/specs/PROJ-123.md` plus `docs/specs/PROJ-123/alpha.md`. This covers both checked-in specs and throwaway ones (`.claude/kivi-sdlc/scratch/`).

`/recon` infers the backend (and asks when it can't), opens or continues a campaign, then passes the locator forward so `/plan` and `/work` operate on the same spec's current campaign.

## Skills

| Skill | What it does |
|---|---|
| `/recon` | Entry point for a single-PR task. Reads the ticket and its comments, does light reconnaissance, scores readiness, opens a campaign, and hands off to `/plan`. Tells you to split work that's too big for one PR. |
| `/uav` | Read-only investigator that chases one historical question through git history, PRs, and tickets, then returns a digest. Dispatched by the other skills, or run standalone. |
| `/plan` | Makes the design decisions (architecture, module placement, contracts) and writes the plan into the current campaign, or a local plan file when there's no spec. |
| `/work` | Implements the plan, validates with subagent review, commits, and leaves Work notes on the campaign. |
| `/respond` | Triages review threads on an open PR, makes the fixes in the repo's review-fix commit style, and drafts replies that post only on your say-so. |
| `/carve` | Splits an epic into independently shippable pieces, each a pre-recon seed in a tracker or file backend, plus a roadmap tying them together. |
| `/warroom` | Drives 2–3 tickets through the pipeline in waves, one background agent per ticket, escalating only what needs you. Hard-capped at 3; never merges. |

Each skill's own doc carries the full workflow and rules.

## Typical flow

For an epic too big for one PR, start with `/carve "<epic>"` (or `/carve PROJ-123`) to carve it into pieces, each a generic ticket/spec in a tracker or file backend. Then run the flow below on each piece, or hand 2–3 ready pieces to `/warroom PROJ-123 PROJ-124` to drive them to PR in waves while you stay the one decision point.

1. `/recon PROJ-123` (or `/recon "<task description>"`) — review the readiness score; when prompted, choose to investigate deeper (dispatches UAVs), proceed, or supply the context yourself. recon opens Campaign Alpha beside the spec (a ticket comment, or a file next to the spec file, depending on the backend).
2. `/clear`, then `/plan PROJ-123` — writes the Plan into the current campaign (or a local plan file when there's no spec).
3. `/clear`, then `/work PROJ-123` — implements, reviews, commits, marks the campaign's Stage complete, and writes its PR line and Work notes.
4. When review lands, `/respond <PR#>` — fixes what's right, drafts replies, and posts them if you say to.
5. For a bug fix or a second attempt, `/recon PROJ-123` again and choose to open the next campaign (Bravo); it re-derives acceptance criteria for the new PR, reading Alpha as context.
