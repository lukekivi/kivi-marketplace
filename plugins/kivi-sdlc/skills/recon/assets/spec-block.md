# kivi-sdlc spec block

This is the managed spec block the kivi-sdlc skills maintain. It is the one content shape for **every** backend (see `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`) — a tracker description, a checked-in file, or a throwaway scratch file all carry this same block. It is anchored by its heading — the `🤖 kivi-sdlc spec` line — which is how a skill finds an existing block to update instead of appending a duplicate.

The block is owned entirely by the tooling and is appended **below** any human-authored prose (a ticket body, a spec file's intro); that prose is never touched. The shape below is the canonical content, not a literal byte format: render it in whatever the backend needs — Markdown for a file, or whatever rich format a tracker field needs.

---

## 🤖 kivi-sdlc spec

**Stage:** recon ✓ · plan · work

<!-- ticked as the pipeline advances: `recon ✓ · plan ✓ · work ▸` etc. Agnostic to any tracker's own workflow — it tracks kivi-sdlc stages only. -->

**Acceptance criteria**

- <explicit, testable done-condition>

**Reconnaissance findings**

- `path/to/file` — why it matters for this task

**Clarifications**

<Only present if clarification was gathered. Prose. Omit heading and body when empty.>

**Historical context**

<Only present if a UAV ran. Relevant tickets/PRs/commits, each with a one-line reason it matters, plus any readiness shift. Omit when no UAV ran.>

- `PROJ-123` — decision/constraint learned, and where it shows up

**Manual exploration**

<Only present if recon Phase 2b ran. What the user-run investigation revealed — relevant log lines, payloads, observed behavior verbatim; root cause or remaining unknowns. Omit when Phase 2b did not run.>

**Working-tree edits**

<Only present if recon Phase 2b added edits. Every file touched, one-line description. These are uncommitted scaffolding the next phase must revert before implementing the real fix. Omit when none exist.>

- `path/to/file` — what was added

**Plan**

<Filled in by `/plan`: the implementation plan (inline or a link). Empty until planning runs.>

**Work notes** _(collapsible)_

<Written by `/work` when it finishes; `/respond` appends a dated round per review it addresses. Rendered **collapsed** — the tracker’s native collapsible if it has one, or `<details><summary>Work notes</summary>` in Markdown. Omit until `/work` runs. This is the durable handoff a later agent (e.g. `/respond`) starts from instead of the implementing agent's memory, so write what the diff alone won't tell it.>

- **Shipped**: branch, PR, commits (one line each)
- **Decisions**: calls made while coding that the plan didn't settle, with the why
- **Deviations from plan**: what changed and why
- **Validation**: what ran and passed
- **Soft spots**: what a reviewer is likely to poke at — risky edges, deliberate trade-offs, things left as-is on purpose
- **Follow-ups**: out-of-scope work surfaced
