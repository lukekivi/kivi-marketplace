---
name: respond
description: "Address code review on an open PR: read the spec and its Work notes as the handoff from /work, triage every unresolved review thread (fix, push back, or ask), make the fixes in the repo's review-fix commit style, re-validate, push, and draft a reply per thread — posting them only when the user says to. Use when review comments land on a PR built by /work or /warroom."
argument-hint: "[PR number or URL, optionally a spec locator and --post (e.g. 3466 PROJ-123 --post)]"
---

## What respond is

The review-time counterpart to `/work`. The agent that implemented the PR is gone; the spec's **Work notes** (written by `/work`) are its handoff — decisions, deviations, soft spots. respond starts from those plus the PR itself, the way a compacted `/work` session would.

respond **drafts** a reply per thread and posts them only when the user says to — `--post` in the arguments, or after reading the drafts. Resolving threads also needs the user's say-so.

## Workflow

### Pre-flight

1. Resolve `$ARGUMENTS`: the PR (number or URL) and, if given, the spec locator. With no locator, find it from the PR — a ticket key in the branch name, title, or commit subjects — and read it through the adapter in `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`. No spec at all is fine; say so and continue on the PR alone.
2. Check out the PR's head branch and confirm the tree is clean and in sync with the remote (`git status`, `git fetch`, compare to `origin/<branch>`).
3. Make sure the PR's base is sensible; report it if it isn't.

### Gather

4. Read the spec — especially **Plan** and **Work notes**.
5. Fetch every **unresolved** review thread, plus top-level review bodies and PR conversation comments addressed to the change. Skip resolved threads and automated bot noise unless it flags a real failure.
6. Read the PR diff and the code around each thread.

### Infer the review-fix commit style

7. **Match how this repo lands review fixes.** Some repos fold each fix into the commit it belongs to and force-push; others add new commits on top. The wrong one clutters history or rewrites commits reviewers already read. Work it out from the repo: its contributing docs and PR template first (an explicit rule wins), then how recently merged PRs handled review. If it's still unclear, ask. State the style and your evidence in the report.

### Triage

8. Classify each thread:
   - **fix** — the reviewer is right, or it's a cheap improvement within the PR's scope.
   - **push back** — the current code is right; cite the Work notes, plan, or code that justifies it. Disagreement is fine when warranted — don't fix just to placate.
   - **ask** — needs a product/scope call or the reviewer's intent is unclear.
   - **defer** — valid but out of scope; propose a follow-up.
9. Present the triage to the user (one line per thread, with the planned action) and get approval before changing code.

### Fix

10. Make the approved fixes in repo style, as `/work` would. Run the relevant tests, lint, and checks the repo defines; fix failures.
11. Commit per the inferred style (step 7) and the repo's commit-message rules. Push.
12. **Stacked PRs**: if another open PR is built on this branch, it now needs a rebase onto the new head. Don't do it here; report which PR and why.

### Hand back

13. **Draft replies** — one per thread, keyed by the thread URL. Short and direct: what changed (with the commit, if useful) or why not. No sycophancy.
14. **Post** — only if the user said to (`--post`, or after reading the drafts): post each reply in its thread. Resolve a thread only if the user asks.
15. If the work came from a spec, append a **Review round** to its Work notes via the adapter, from `${CLAUDE_SKILL_DIR}/assets/review-round.md`.
16. Report: inferred commit style + evidence, threads addressed, commits pushed, checks run, the reply drafts and which were posted, anything left for the user (asks, rebases owed, follow-ups).

## Principles

- **The Work notes are the memory** — start from them; don't re-derive decisions the implementer already made and wrote down.
- **Repo conventions over habit** — commit style is inferred, never assumed.
- **The user owns the conversation with reviewers** — replies post only on their say-so.
- **Push back when right** — a review comment is input, not an order.
