<!--
This is a PRE-RECON SEED — the body a piece of work starts life with, ready to be
picked up by `/recon`. It becomes the piece's spec prose, which stays
human-owned; recon opens Campaign Alpha BESIDE it (a ticket comment, or
`<piece>/alpha.md` next to this file).

Carve fills this in at the PRODUCT level — what the piece delivers and why, its
scope and boundaries. It must NOT contain a campaign, a Stage line, or acceptance
criteria — those belong to recon's campaign — and it is not a design: how to
build it is `/plan`'s job. Code pointers are orientation, not prescriptions.

The frontmatter below is optional and file-backend only. In the tracker backend the
seed is the ticket description (no frontmatter); the epic link and roadmap carry the
same linkage.
-->
---
carve: ../roadmap.md
piece: NN
---

# <Piece Title>

## Goal

<One or two sentences: what this piece delivers and why it stands as its own unit of work.>

## Scope

**In:** <What this piece includes.>
**Out:** <What is deferred to another piece or left out of the epic entirely.>

## Dependencies

- **Requires:** <Pieces/locators that must land before this one can start, or "none">
- **Enables:** <Pieces this one unblocks, or "none">

<!-- When a Requires dependency is a hard block, link it at the backend level too: a tracker "is blocked by" link between tickets, or the blocking piece's locator above. -->

## Affected areas

<The product surfaces and high-level areas this piece touches — screens, flows, modules, layers — enough to orient recon. Not a design or a file-by-file plan; how to build it is `/plan`'s job. Name a specific technical approach only when it's obvious or genuinely necessary to scope the piece, and even then as a suggestion, not a directive.>

## Reference material

### Code
- `path/to/file` — why it's relevant to this piece (a pointer for recon/plan, not a prescription of what to change)

### In-progress work
- <Branch / stash / draft PR and what it contains. Remove if none.>

## Notes

<Constraints, risks, decisions, or context from the carve dialogue that recon should know.>
