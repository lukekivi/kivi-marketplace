# kivi-sdlc campaign

A **campaign** is one full trip through the pipeline — recon → plan → work → respond — and where the kivi-sdlc skills write their output onto a spec. It is the one content shape for **every** backend (see `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`): a tracker comment, a checked-in file, or a throwaway scratch file all carry this same unit. It is stored **beside** the spec prose, never inside it; the prose stays human-owned (the rare approved edit to it is **update-prose** in `spec-backends.md`).

Each campaign is self-contained. A second attempt, a bug fix, or follow-on work opens the next campaign instead of growing an earlier one, so an agent loads only the campaign it is working on and reads earlier ones on demand (Summary first).

## Names

Campaigns are named from the NATO alphabet, in order: Alpha, Bravo, Charlie, Delta, Echo, Foxtrot, Golf, Hotel, India, Juliett, Kilo, Lima, Mike, November, Oscar, Papa, Quebec, Romeo, Sierra, Tango, Uniform, Victor, Whiskey, X-ray, Yankee, Zulu. The next campaign takes the name after the latest existing one.

After Zulu, the sequence extends by appending: Zulu Alpha, Zulu Bravo, … Zulu Zulu, then Zulu Zulu Alpha, and so on. The rule: if the latest name ends in Zulu, append Alpha; otherwise advance its last word. Every name sorts alphabetically in sequence order, so a file backend needs no numeric prefix — compare names, not file names (on disk, `zulu-alpha.md` lists before `zulu.md`).

## Header and marker

Every campaign opens with the heading `🤖 kivi-sdlc · Campaign <Name>`. That heading is the marker: skills find campaigns by it — among a ticket's comments, or at the top of a campaign file — never by position or by any other text.

## Ownership

| Part | Written by |
|---|---|
| Header, Recon | `/recon` (opens the campaign, or updates its Recon when continuing it) |
| Plan | `/plan` |
| Work notes, PR line | `/work`; `/respond` appends review rounds inside Work notes |
| Stage | each skill ticks its own stage |
| Summary | `/recon` writes it; `/plan` and `/work` rewrite it when the picture changes (after `/work`, it says what shipped) |

## Rendering

The shape below is the canonical content, not a literal byte format. Render it in whatever the backend needs: Markdown with `<details><summary>…</summary>` elements for a file; the tracker's rich format and its native expand/collapse for a ticket comment. Recon, Plan, and Work notes always sit **collapsed** so the header, Stage, and Summary are all a reader sees at first.

---

## 🤖 kivi-sdlc · Campaign Alpha

**Stage:** recon ✓ · plan · work · **PR:** <link — omit until a PR exists>

<!-- ticked as the pipeline advances: `recon ✓ · plan ✓ · work ▸` etc. Agnostic to any tracker's own workflow — it tracks kivi-sdlc stages only. -->

**Summary:** <One or two lines: what this campaign sets out to do — and, once `/work` runs, what shipped. Enough for an agent to decide whether to open the rest.>

<details><summary>Recon</summary>

**Acceptance criteria**

<Derived for this campaign's PR. Never copied forward from an earlier campaign: a fix campaign's criteria cover the fix and its regression check, not a restatement of Alpha's.>

- <explicit, testable done-condition>

**Reconnaissance findings**

- `path/to/file` — why it matters for this task

**Clarifications**

<Prose. On Alpha, only present if clarification was gathered — omit heading and body when empty. From Bravo onward, required, and it opens with why this campaign exists: which campaign it follows and what that one left.>

**Historical context**

<Only present if a UAV ran. Relevant tickets/PRs/commits, each with a one-line reason it matters, plus any readiness shift. Omit when no UAV ran.>

- `PROJ-123` — decision/constraint learned, and where it shows up

**Manual exploration**

<Only present if recon Phase 2b ran. What the user-run investigation revealed — relevant log lines, payloads, observed behavior verbatim; root cause or remaining unknowns. Omit when Phase 2b did not run.>

**Working-tree edits**

<Only present if recon Phase 2b added edits. Every file touched, one-line description. These are uncommitted scaffolding the next phase must revert before implementing the real fix. Omit when none exist.>

- `path/to/file` — what was added

</details>

<details><summary>Plan</summary>

<Filled in by `/plan`: the implementation plan (inline or a link). Omit the section until planning runs.>

</details>

<details><summary>Work notes</summary>

<Written by `/work` when it finishes; `/respond` appends a dated round per review it addresses. Omit until `/work` runs. This is the durable handoff a later agent (e.g. `/respond`) starts from instead of the implementing agent's memory, so write what the diff alone won't tell it.>

- **Shipped**: branch, PR, commits (one line each)
- **Decisions**: calls made while coding that the plan didn't settle, with the why
- **Deviations from plan**: what changed and why
- **Validation**: what ran and passed
- **Soft spots**: what a reviewer is likely to poke at — risky edges, deliberate trade-offs, things left as-is on purpose
- **Follow-ups**: out-of-scope work surfaced

</details>
