# kivi-sdlc spec backends

The **spec** is the single source of truth for a piece of work. Every kivi-sdlc skill reads from and writes to it through the generic operations below — none of them hardcode where the spec lives. This file is the one place that knows about storage. Adding a new backend means adding an adapter here; the skills do not change.

## Spec prose and campaigns

A spec has two parts, and the tooling owns only the second:

- **Spec prose** — the ticket description or the spec file. Human-owned. kivi-sdlc reads it and, as a rule, leaves it alone — its own output goes in campaigns. The rare exception is a gap in the prose itself, most often missing or wrong acceptance criteria, which a skill may close through **update-prose**, only with the user's explicit approval of the exact edit. (`/recon` on a freeform task also creates the prose file once, holding the task as given — see Resolving the backend.)
- **Campaigns** — the tooling's output, stored beside the prose, never inside it. One campaign per trip through the pipeline; its content shape, name sequence, and header marker are all defined by the campaign template, `${CLAUDE_PLUGIN_ROOT}/skills/recon/assets/campaign.md`. A second attempt or a bug fix opens the next campaign instead of growing an earlier one.

Only `/recon` starts campaigns. On a spec with none, it opens Campaign Alpha; on a spec that already has campaigns, it asks one question — **continue the latest campaign** (update its Recon) or **open the next one**. It never infers which from state.

The **current campaign** is the latest one. `/plan` and `/work` operate on it; `/respond` operates on the campaign whose PR line matches the PR it was given (falling back to the latest). Earlier campaigns are read only on demand — Summary first, then whatever sections the question needs.

| | Spec prose | Campaign |
|---|---|---|
| `tracker` | ticket description (human-owned) | one comment per campaign |
| `file` | `<dir>/<id>.md` (human-owned) | `<dir>/<id>/<name>.md`, e.g. `docs/specs/PROJ-123/alpha.md` |

## The spec locator

A spec is identified by a **locator** — a single string that both names the spec and tells the adapters apart by its shape:

- **Tracker locator** — a ticket key or tracker URL (e.g. `PROJ-123`, a tracker URL).
- **File locator** — a path to the spec prose file (e.g. `docs/specs/foo.md`, `.claude/kivi-sdlc/scratch/recon-<timestamp>.md`). Its campaigns live in the sibling directory named after it, minus `.md`.

The locator names the spec, not a campaign. It is passed forward through the pipeline: recon resolves it once and prints it in the handoff command (`/plan <locator>`), plan passes it to `/work <locator>`. Downstream skills never re-infer the backend — they detect the adapter from the locator's shape and operate on the current campaign.

## Campaign operations

Every adapter implements the same operations. Campaigns are found by their header marker (`🤖 kivi-sdlc · Campaign <Name>`), never by position.

- **read-prose** — the spec prose, plus (tracker) the ticket's non-campaign comments, which often carry scope and constraints.
- **list-campaigns** — the name, Stage line, PR line, and Summary of every campaign, oldest first. Cheap: enough to pick a campaign without loading the rest.
- **read-campaign** — one campaign in full, by name or `latest`.
- **open-campaign** — create the next campaign: the name after the latest existing one (Alpha when there is none; the sequence is in the campaign template). `/recon` only.
- **update-campaign** — write one named campaign back as a whole unit. Read it first, change only the sections the calling skill owns, then write it back; never touch any other campaign.
- **update-prose** — rare: amend the spec prose to close a gap found in it, most often missing or wrong acceptance criteria. Only with the user's explicit approval of the exact edit, every time; change only what was approved and leave the rest exactly as it was. Never as a side effect of a campaign write.
- **create** — write a new spec's prose, with no campaign. `/carve` creates specs whose prose is a pre-recon **seed** (recon opens Campaign Alpha later). `/recon` creates one only for a freeform task, on the `file` backend, holding the task text (see Resolving the backend). `/recon`, `/plan`, and `/work` never create tracker items.
- **commit** — see each adapter.

Which skill writes what inside a campaign is set by the owning skill; see the campaign template.

## Adapters

### `tracker`

A work item reached through a tracker API, via whatever tracker client is available (a CLI or an MCP); the same shape applies to any tracker.

- **read-prose** — fetch the item's description and its comments, skipping campaign comments.
- **list-campaigns / read-campaign** — fetch the comments and keep those whose body opens with the campaign header; order by creation time.
- **open-campaign** — add one new comment holding the campaign. Render it in whatever format the tracker needs (some need a rich-text format, not Markdown); the collapsed sections use the tracker's native expand/collapse.
- **Lossless reads** — clients can silently ignore a format parameter (e.g. return Markdown when asked for ADF). Whenever a write depends on a lossless read, check that the response actually came back in the requested format. Settle what a client supports by checking a response, never by assumption, in either direction.
- **update-campaign** — edit that comment. Tracker comment edits replace the whole body, so fetch it first in a lossless format (e.g. HTML rather than Markdown, which can drop expands and other rich nodes) and write the full body back. If the client can't read it losslessly, rebuild the full body in the tracker's format from the campaign template, re-rendering the collapsed sections as native expands, rather than writing the lossy read back as-is.
- **update-prose** — edit the description. Like a comment edit, it replaces the whole field: fetch it in a lossless format, change only the approved part, leave everything else identical, and write the full field back in that same format. If the client can't read the field losslessly, say so and hand the user the edit to paste instead — never round-trip the prose through a lossy format, even with approval.
- **Size** — trackers cap comment length (e.g. 32,767 characters). A campaign fits in practice; no special handling. If a write is ever rejected for size, report it and let the user trim by hand.
- Never edit other comments, status, assignees, or any other field, nor the description outside **update-prose**.
- **commit** — none. Tracker writes are remote; nothing is committed.

### `file`

A markdown file at a path. This single adapter covers both **checked-in** specs (a committed path like `docs/specs/PROJ-123.md`) and **throwaway** specs (`.claude/kivi-sdlc/scratch/recon-<timestamp>.md`). The only difference is the path and whether git tracks it — the operations are identical.

- **read-prose** — read `<dir>/<id>.md`.
- **list-campaigns / read-campaign** — read the campaign files in `<dir>/<id>/`. Campaign names sort alphabetically in sequence order, so ordering the files by name (without `.md`) is campaign order; no numeric prefix.
- **open-campaign** — write `<dir>/<id>/<name>.md` (lowercase name, e.g. `alpha.md`, `x-ray.md`), creating the directory if needed. Markdown throughout; collapsed sections are `<details><summary>…</summary>` elements.
- **update-campaign** — rewrite that one file.
- **update-prose** — edit `<dir>/<id>.md` in place, changing only the approved lines.
- **commit** — **never commit spec or campaign files on their own.** Checked-in edits are left in the working tree to ride along with the work's own commits. Do not create a dedicated spec commit, and do not force spec changes into a commit the user did not intend.

## Resolving the backend (spec-creating skills only)

Only the skills that create specs infer a backend: `/recon` (one spec per run) and `/carve` (one piece per phase when it carves an epic). Downstream skills (`/plan`, `/work`, `/respond`) never infer — they are handed a locator and detect `tracker` vs `file` from its shape. Infer first; ask only when inference fails.

`/recon` resolves a backend as follows:

1. **Argument is a tracker locator** (`PROJ-###` / tracker URL) → `tracker`.
2. **Argument is a path to an existing spec file** → `file` at that path.
3. **No locator — a freeform task.** Decide where a file-backed spec should live, then write the task text, as given, as the spec prose — human-owned from then on, like any other prose:
   - Look for an existing checked-in specs home: a `specs/` or `docs/specs/` directory, or committed spec files with campaign directories beside them. If one is found, write the new spec there (checked-in), naming it by ID when one exists, otherwise a short kebab-slug.
   - If nothing in the repo indicates where checked-in specs go, ask the user directly (one question): checked-in at a suggested path, or throwaway in `.claude/kivi-sdlc/scratch/`. Honor their choice; default the scratch file to `recon-<timestamp>.md`.

`/carve` resolves one backend for the whole epic and may create tracker items (unlike recon): an epic that is itself a tracker ticket → `tracker` (create one linked item per piece); a freeform or file-based epic → it asks the user tracker-vs-file. See the carve skill for the full rules.

## Identity / naming

- Tracker specs are named by the tracker (`PROJ-123`).
- File specs use the ID when one exists (`PROJ-123.md`), otherwise a timestamp slug for scratch (`recon-<timestamp>.md`) or a short kebab-slug for a checked-in spec with no ID.
- Campaigns are named from the NATO alphabet in order (see the campaign template); on a file spec, the file name is the lowercase name with words joined by hyphens (`alpha.md`, `zulu-alpha.md`).
