---
name: work
description: "Execute a repo plan end to end: implement, validate with parallel subagent review, and commit at the end."
argument-hint: "[ticket key, .claude/kivi-sdlc/plans/... plan, or .claude/kivi-sdlc/todo/... file path]"
---

## Workflow

### Pre-flight

1. Check that the git repo is clean.
   - Run `git status`. If there are staged changes, unstaged changes, or untracked files, stop and report them to the user.
   - Offer to commit the changes, add them to `.gitignore`, or stash them — whatever makes sense for what you see.
   - Do not proceed until the repo is clean or the user explicitly says to continue with dirty state.
2. If this work will produce committable code/repo changes, assert an appropriate working branch.
   - Run `git branch --show-current`. You need a correctly named branch before committing if you are on the default branch, or on a branch whose name does not reflect this work.
   - Choose a name that follows the repo's existing branch-naming convention — inferred from recent branch names or repo documentation — and describes the work at hand. Confirm it with the user.

### Orientation

3. Resolve `<input_document> $ARGUMENTS </input_document>`.
   - If it is a **spec locator** — a tracker key/URL, or a path to a file carrying a `🤖 kivi-sdlc spec` block — read the spec through the matching adapter in `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`. The block's **Plan** section is your work doc; the surrounding sections are the context recon and plan left behind.
   - Otherwise it is a plain file path. Prefer `.claude/kivi-sdlc/plans/` for implementation plans and `.claude/kivi-sdlc/todo/` for tracked follow-up work.
4. Read the work doc completely.
5. If anything is unclear or ambiguous after reading the plan, references, and related code, ask the user now.
   - Better to ask once before starting than to build the wrong thing. Get user approval to proceed.
   - If the ambiguity is *historical* — why the code is the way it is, what a past decision assumed — you can dispatch a UAV investigator to ascertain it instead of (or before) asking. See **Investigating deeper (UAV)** below.
   - Skip this step if the plan is clear and the path forward is obvious.
6. Verify the repo setup and baseline quality commands before major edits — run this in a subagent.
   - Launch a subagent (model: "haiku") that confirms dependencies are installed, then runs tests, lint, formatter, and type checks.
   - The subagent should return a concise summary: what passed, what failed, and any broken baseline issues.
   - If the baseline is already broken, tell the user before proceeding.
7. Create a Todo list from the plan's implementation tasks.
   - Include testing tasks alongside implementation tasks.
   - Keep tasks specific and completable — each one should map to a checkable plan item.

### Execution

8. Execute the plan task by task — **code first, fix tests after**.
    - Read the related code and nearby patterns before implementing each task.
    - Implement in repo style. Match naming conventions, error handling patterns, and file organization.
    - Comment the code well. Comments should explain the architecture and the "why", not merely describe what the code does.
    - Write or update tests for each piece of new functionality, but don't stop to chase test failures mid-implementation. The goal is to get all the code written for a chunk first, then circle back to make the tests green.
    - Update Todo state and mark the matching plan checkbox complete (`[ ]` → `[x]`).
    - Keep the implementation aligned with the plan unless the user explicitly redirects or the plan is clearly wrong.
    - **After all code for a chunk is written**, run the relevant checks and fix any test failures or lint issues before moving to validation.
    - _Exception for longer, phased plans:_ If the plan has multiple phases that build on each other and the complexity is high enough that deferred test failures would be hard to diagnose, you may test as you go — but state why in your Todo list or message to the user before doing so. The default is still code-first.
9. If you find yourself spinning your wheels or faced with an unexpected obstacle, stop and ask the user for guidance.
    - If the obstacle is a gap in historical context — a behavior or constraint you can't explain from the code — consider dispatching a UAV (see **Investigating deeper (UAV)**) before escalating.

Repeat steps 8–9 until the plan is complete.

If you start to run out of context, stop and offer to run `/handoff` so we can finish the work in a follow-up session without losing anything important.

### Validate

After all plan work is complete, validate the full body of work with subagent review.

10. Run the full suite.
    - Run tests, lint, formatter, and type checks as applicable.
    - Use the commands the repo documents, not ad hoc substitutes.
    - Fix any failures before proceeding.
11. Launch two review subagents **in parallel** using the Agent tool.
    - Both subagents must use `model: "sonnet"` for speed and cost efficiency.
    - Each Agent invocation starts with fresh context — include all necessary details in the prompt.
    - Build each subagent prompt by reading the corresponding template, then filling in the specifics of the full plan.
    - **Completeness review** — Read `${CLAUDE_SKILL_DIR}/assets/completeness-review-prompt.md` for the prompt framework. Fill in the plan path, all tasks completed, and the list of all changed files. The subagent reads the plan and all changed files, then evaluates whether the work is genuinely complete with no omissions, hacks, disabled warnings, or workarounds. The subagent should assume that the code builds and the tests pass and should not verify this itself.
    - **Test quality review** — Read `${CLAUDE_SKILL_DIR}/assets/test-quality-review-prompt.md` for the prompt framework. Fill in the plan path, all tasks completed, the test files, and the implementation files. The subagent reads the implementation and tests, then evaluates whether the tests verify real behavior, cover edge cases, and would actually catch bugs.
12. Act on review findings.
    - If either reviewer reports issues worth fixing: fix them, then re-run the relevant quality checks.
    - If both reviewers pass, proceed to handoff.

### Commit & Handoff

13. Commit all work using the 7 rules of great commit messages AND WITH NO CLAUDE CODE ATTRIBUTION.
    - Split the work into commits per the repo's commit-structuring convention — distinct changes get distinct commits.
    - Do not commit if tests are failing or work is incomplete.
14. If the work came from a spec, update its `🤖 kivi-sdlc spec` block via the adapter from `${CLAUDE_PLUGIN_ROOT}/spec-backends.md`, never touching any human-authored prose above the block — in one write:
    - flip the Stage line to `recon ✓ · plan ✓ · work ✓`;
    - write the collapsed **Work notes** (shape in `${CLAUDE_PLUGIN_ROOT}/skills/recon/assets/spec-block.md`). This is **required** — it is the handoff a later `/respond` agent starts from when review comes in, in place of your memory. Write what the diff won't say: decisions, deviations, soft spots. Add the PR link once one exists.

    A checked-in spec file's edit rides along in the working tree — do not give it a dedicated commit. With no spec (a plan/todo file), append the Work notes to that file instead.
15. Report what shipped, quality-check results, commit summary, branch name, and any follow-up work.

## Investigating deeper (UAV)

Dispatch UAV investigators whenever a *historical* question is blocking progress — why the code behaves as it does, what a prior decision assumed, whether an approach was already tried — or whenever the user tells you to investigate deeper. Don't reach for a UAV to answer questions the current code and plan already settle; it ascertains history, not implementation.

- One goal per UAV. For each concern write a brief: **Goal** (one line — the question this UAV answers), **Seeds** (deterministic anchors: paths, commit hashes, ticket keys, PR numbers), **Suggestions** (soft hints on where to look, optional).
- Launch each UAV with the **Agent tool** (`general-purpose` subagent). The prompt must be self-contained and mirror the `uav` skill: state the read-only UAV role, the goal, the seeds, the surfaces available (git history; PRs via commit hash → `gh`; tickets + comments via the available tracker client (a CLI or an MCP); traverse commit → PR → ticket freely), and the expected `UAV DIGEST` output shape. **Launch all UAVs of a wave in a single message so they run in parallel.**
- Fold each returned digest into your understanding before continuing. UAVs are read-only — if one reports a mutation, treat it as a bug and discard its result.

## Principles

- **Start clean** — verify the repo state before touching anything.
- **The plan is your guide** — follow its references, don't reinvent.
- **Code first, then fix tests** — get the implementation down, then make it green. Except in complex phased work where early feedback is worth the interruption.
- **Commit after review** — split validated work into distinct commits per the repo's commit-structuring convention.
- **Validate at the end** — subagent review catches what you miss across the full body of work.
- **Ship complete features** — don't leave things 80% done.
