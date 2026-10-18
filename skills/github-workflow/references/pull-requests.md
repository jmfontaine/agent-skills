# Pull requests

A pull request delivers one issue and carries the evidence that it works. Reviewers
should be able to judge it from the PR, its issue, and the linked brief (when one
exists) alone.

## Scope

Deliver one issue per pull request. Split dependent concerns into stacked pull requests
(the `git-commit` skill, if installed). Put an unrelated fix found along the way on its
own branch and pull request, opening an issue for it when it is committed work.

## Before opening

- Run the issue's verification and the repository's QA checks. Note each command or
  scenario and its result.
- Compare the diff with the issue's acceptance criteria and out-of-scope list, and with
  the brief's exclusions when a brief exists. Remove anything that does not belong.

Interactive work has no per-commit reviewer. The agent review happens once the pull
request is open (see the review reference).

## Open

Push and open the pull request only when the user asks. Launching an unattended run,
such as with the `parallel-issues` skill, is that request for the runs it starts. Use
the repository's template (`.github/pull_request_template.md`) if one exists, otherwise
`assets/pull-request-template.md`. Write the body to a file and pass it with
`--body-file`.

- Open it as a draft (`gh pr create --draft`) while work or verification is incomplete,
  or when early feedback is wanted. Mark it ready with `gh pr ready <n>`.
- **Title:** only the title survives a squash merge, so write it as the commit on the
  default branch: Conventional Commits without a scope, `<type>: <description>`, or
  `<type>!: <description>` for a breaking change. The type is what the change actually
  is; the `git-branch` skill's label table maps the issue's change-type label to a
  type, and the title wins when they disagree. Follow another title convention only
  when AGENTS.md records it as a deviation.
- Link each issue the PR completes with a closing keyword on its own line:
  `Closes #42`. Use `Refs #42` for partial work, such as a lower layer of a stack.
  Closing keywords take effect only when the PR merges into the default branch.
- Under Verification, list what you ran and the result, then anything unverified and
  why.
- Under Scope notes, list deviations from the issue, follow-up issues created, and
  changes to canonical artifacts.

Once the pull request is open, tell the user it is ready for an agent review from a
fresh session (see the review reference).

## Changes to the brief or other canonical artifacts

Implementation sometimes shows that a brief, an ADR, the Manifesto, or the Architecture
section of AGENTS.md is wrong or incomplete. Keep those changes reviewable:

- **Clarification without a scope change**, such as recording a decision made during
  implementation: include it in the same pull request and list it under Scope notes.
- **Change to scope, acceptance criteria, or appetite:** a product decision. Stop and
  present the tradeoff to the user first; until they decide, keep the implementation
  within the current brief. Once they agree, put the artifact change in its own pull
  request and merge it first, so it can be accepted or rejected alone. Then bring the
  implementation pull request up to date by merging the default branch into it.

## Update after review

Treat each finding as a claim to check, not an order. Fix valid findings with new
commits on top of the branch. Never rewrite pushed commits, which means no force
pushes. Reply to each addressed thread with what changed, or why the finding does not
apply, prefixed with `[AgentName]`. Leave resolving a thread to whoever opened it unless
the user says otherwise.

After pushing fixes, request a re-review only where the reviewer expects it, such as
`@codex review` or `@claude review` for a bot running in manual mode.

## Merge

Merge only when the user asks. Squash merge is the only merge method (the rationale is
in [Repository setup](repository-setup.md)). Find out whether the repository allows it:
`gh repo view --json squashMergeAllowed`. If it does not, stop and ask the user.

Before merging, confirm that checks pass (`gh pr checks <n>`), blocking findings are
resolved, and the user has reviewed the PR. Never use `--admin` to bypass branch
protection or a ruleset.

GitHub creates the squash commit and signs it with its own key, and the branch does not
need to contain the base first. A ruleset that requires signed commits still checks
every commit on the pull request branch, so each one must be signed and verified.

`gh pr view <n> --json mergeStateStatus` tells whether a branch needs updating first:
`DIRTY` is a conflict, and `BEHIND` matters only when a ruleset requires up-to-date
branches. `UNKNOWN` means GitHub is still computing it, as it does for a few seconds
after the base branch moves: query again until it changes, and never merge on it.
Update by merging the base into the branch, never by rebasing, so nothing pushed is
rewritten and no force push is needed; the squash drops the merge commits.

An external pull request with unsigned commits is blocked by the signed-commit ruleset.
Ask the maintainer to merge it; never bypass the ruleset.

- **Single pull request:** `gh pr merge <n> --squash`. When it is only `BEHIND`, run
  `gh pr update-branch <n>` first: GitHub adds a merge commit it signs. On a conflict,
  merge the base into the branch locally, signed, push, and wait for the checks.
- **Stack:** from a worktree that has the stack checked out, run
  `gh stack merge --yes --squash` with no number. It merges every pull request of the
  stack in one all-or-nothing operation, one squashed commit each, through GitHub's
  asynchronous merge API. Do not pass a pull request number with `--yes`:
  `gh stack merge` reads a bare number as a stack number first, so it can merge a
  different stack without asking. To merge only the lower part of a stack, use its
  interactive picker or ask the user. After a partial merge, GitHub re-targets the
  lowest unmerged layer at the base and rebases the layers above it. Do not use
  `gh pr merge` on a stacked pull request. `gh pr update-branch` refuses a stacked pull
  request (HTTP 403), so update a stack that is behind or conflicts locally: merge the
  base into the bottom branch, then each layer into the next one up.

### Several at once

When the user asks to merge several pull requests or stacks (a list, a range, or "the
ready ones"), merge them in one pass without asking about each one. When several are
ready, suggest this; never require it.

1. Skip any pull request with failing checks or an unresolved blocking finding, and
   report it.
2. Merge one stack or pull request at a time. Update only the one about to merge: every
   merge moves the base again, so updating the others would be repeated.
3. Stop only for a conflict whose resolution changes behavior, or for a failing check.
   Resolve import-only and formatting conflicts yourself.

After the merge, confirm that the linked issues closed. When a milestone's issues are
all closed, the next step is the release review (the `product-development-system` skill,
if installed).
