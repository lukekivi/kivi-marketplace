# kivi-sdlc spec backends

The **spec** is the single source of truth for a piece of work. Every kivi-sdlc skill reads from and writes to it through the generic operations below — none of them hardcode where the spec lives. This file is the one place that knows about storage. Adding a new backend means adding an adapter here; the skills do not change.

## The spec is backend-agnostic content

Whatever the backend, the spec carries the same content, defined by `${CLAUDE_PLUGIN_ROOT}/skills/recon/assets/spec-block.md`: a **Stage** line plus Acceptance criteria, Reconnaissance findings, optional Clarifications / Historical context / Manual exploration / Working-tree edits, a **Plan** section, and a collapsed **Work notes** section. The user's own prose is never part of the managed content — the tooling owns only the block anchored by the `🤖 kivi-sdlc spec` heading, and never edits anything above it.

## The spec locator

A spec is identified by a **locator** — a single string that both names the spec and tells the adapters apart by its shape:

- **Tracker locator** — a ticket key or tracker URL (e.g. `PROJ-123`, a tracker URL).
- **File locator** — a path to a markdown file (e.g. `docs/specs/foo.md`, `.claude/kivi-sdlc/scratch/recon-<timestamp>.md`).

The locator is **passed forward** through the pipeline: recon resolves it once and prints it in the handoff command (`/plan <locator>`), plan passes it to `/work <locator>`. Downstream skills never re-infer the backend — they detect the adapter from the locator's shape and operate.

## Adapters

### `tracker`

A work item reached through a tracker API, via whatever tracker client is available (a CLI or an MCP); the same shape applies to any tracker.

- **read** — fetch the item's description/body in the field's **native** format (e.g. ADF for Jira) when the client supports it, including the `🤖 kivi-sdlc spec` block and the user's comments. Verify the response actually came back in that format — clients can silently ignore a format parameter. Settle what the client supports by checking a response, never by assumption, in either direction.
- **write-block / update-stage / write-plan / write-work-notes** — edit the description in that same native format: replace the existing `🤖 kivi-sdlc spec` block (found by its heading) or append a fresh one below the existing body, change only the block's nodes (or the Work notes node), leave every other node identical, and write back in that format. Never touch the user's prose above the block.
- **No native read** — if the client can only read the field in a lossy format (e.g. Markdown for a rich-text field), any write round-trips the user's prose through it, and formatting outside the block may change (panels, mentions, tables, colors, expand nodes, media, bold/code boundaries). Never rewrite the field that way silently: before the first write, say so, name that risk and the alternatives — the user pastes the block in manually, or a client that supports the native format is used — and write only on explicit approval.
- **Work notes** render as the tracker's native collapsible titled "Work notes" at the end of the block, so they sit collapsed. Replace that one node on rewrite; append inside it for a new review round.
- **create** — used by `/carve` only: create a new work item (title + body) and link it to its epic, confirming before writing. The body is a pre-recon **seed** — prose with no `🤖 kivi-sdlc spec` block (recon appends the block later). `/recon`, `/plan`, and `/work` never create items.
- **commit** — none. Tracker writes are remote; nothing is committed.

### `file`

A markdown file at a path. This single adapter covers both **checked-in** specs (a committed path like `docs/specs/PROJ-123.md`) and **throwaway** specs (`.claude/kivi-sdlc/scratch/recon-<timestamp>.md`). The only difference is the path and whether git tracks it — the operations are identical.

- **read** — read the file, including the `🤖 kivi-sdlc spec` block.
- **write-block / update-stage / write-plan / write-work-notes** — edit the file in place, replacing the existing block (found by its heading) or appending one below any human-authored prose at the top. Markdown throughout; Work notes go in a `<details><summary>Work notes</summary>` element.
- **create** — used by `/carve` only: write a new file whose contents are a pre-recon **seed** — prose with no `🤖 kivi-sdlc spec` block (recon appends the block later). `/recon`, `/plan`, and `/work` never create spec files.
- **commit** — **never commit the spec on its own.** Checked-in spec edits are left in the working tree to ride along with the work's own commits. Do not create a dedicated spec commit, and do not force spec changes into a commit the user did not intend.

## Resolving the backend (spec-creating skills only)

Only the skills that **create** specs infer a backend: `/recon` (one spec per run) and `/carve` (one piece per phase when it carves an epic). Downstream skills (`/plan`, `/work`, `/respond`) never infer — they are handed a locator and detect `tracker` vs `file` from its shape. Infer first; ask only when inference fails.

`/recon` resolves a backend as follows:

1. **Argument is a tracker locator** (`PROJ-###` / tracker URL) → `tracker`.
2. **Argument is a path to an existing spec file** → `file` at that path.
3. **No locator — a freeform task.** Decide where a file-backed spec should live:
   - Look for an existing checked-in specs home: a `specs/` or `docs/specs/` directory, or committed `*.md` files that already carry a `🤖 kivi-sdlc spec` block. If one is found, write the new spec there (checked-in), naming it by ID when one exists, otherwise a short kebab-slug.
   - If nothing in the repo indicates where checked-in specs go, **ask the user directly** (one question): checked-in at a suggested path, or throwaway in `.claude/kivi-sdlc/scratch/`. Honor their choice; default the scratch file to `recon-<timestamp>.md`.

`/carve` resolves one backend for the whole epic and may create tracker items (unlike recon): an epic that is itself a tracker ticket → `tracker` (create one linked item per piece); a freeform or file-based epic → it asks the user tracker-vs-file. See the carve skill for the full rules.

## Identity / naming

- Tracker specs are named by the tracker (`PROJ-123`).
- File specs use the ID when one exists (`PROJ-123.md`), otherwise a timestamp slug for scratch (`recon-<timestamp>.md`) or a short kebab-slug for a checked-in spec with no ID.
