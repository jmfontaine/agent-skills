# Pull requests

A pull request delivers one issue and carries the evidence that it works. Reviewers
should be able to judge it from the PR, its issue, and the linked brief alone.

## Scope

Deliver one issue per pull request by default. Split dependent concerns into stacked
pull requests (the `git-commit` skill). Put an unrelated fix found along the way on its
own branch and pull request, opening an issue for it when it is committed work.

## Before opening

- Before each commit, have a reviewer that did not write the change, such as a fresh
  subagent, check the uncommitted diff against the issue's outcome and verification,
  and for defects. Fix valid findings and review again until none is blocking. Note
  any rejected finding for the Scope notes.
- Run the issue's verification and the repository's QA checks. Note each command or
  scenario and its result.
- Compare the diff with the issue's outcome, its out-of-scope list, and the brief's
  exclusions. Remove anything that does not belong.

## Open

Push and open the pull request only when the user asks. Launching an unattended run,
such as with the `parallel-issues` skill, is that request for the runs it starts. Use
the repository's template
(`.github/pull_request_template.md`) if one exists, otherwise
`assets/pull-request-template.md`. Write the body to a file and pass it with
`--body-file`.

- Open it as a draft (`gh pr create --draft`) while work or verification is incomplete,
  or when early feedback is wanted. Mark it ready with `gh pr ready <n>`.
- Title it with the outcome, following the repository's title conventions. When the
  repository squash-merges, the title becomes the commit subject on the default branch:
  write it in the repository's commit message style, such as Conventional Commits.
- Link each issue the PR completes with a closing keyword on its own line:
  `Closes #42`. Use `Refs #42` for partial work, such as a lower layer of a stack.
  Closing keywords take effect only when the PR merges into the default branch.
- Under Verification, list what you ran and the result, then anything unverified and
  why.
- Under Scope notes, list deviations from the issue, follow-up issues created, and
  changes to canonical artifacts.

Once the pull request is open, tell the user it is ready for a spec check from a fresh
agent session (see the review reference).

## Changes to the brief or other canonical artifacts

Implementation sometimes shows that a Slice Brief, Technical Foundation, or Decision
Record is wrong or incomplete. Keep those changes reviewable on their own:

- **Clarification without a scope change**, such as recording a decision made during
  implementation: a separate commit in the same pull request, such as
  `docs(slices): record checksum algorithm choice`.
- **Change to scope, acceptance criteria, or appetite:** a product decision. Stop and
  present the tradeoff to the user first; until they decide, keep the implementation
  within the current brief. Once they agree, put the artifact change in its own pull
  request stacked below the implementation (`gh stack`, per the `git-commit` skill), so
  it can be accepted or rejected alone and merges first. Without stack support, open it
  from the trunk and rebase the implementation onto it after it merges.

## Update after review

Treat each finding as a claim to check, not an order. Fix valid findings by folding the
change into the commit it corrects, as the `git-commit` skill describes, including
asking before force pushing. Reply to each addressed thread with what changed, or why
the finding does not apply, prefixed with `[AgentName]`. Leave resolving a thread to
whoever opened it unless the user says otherwise.

After pushing fixes, request a re-review only where the reviewer expects it, such as
`@codex review` or `@claude review` for a bot running in manual mode.

## Merge

Merge only when the user asks. Before merging, confirm that checks pass
(`gh pr checks <n>`), blocking findings are resolved, and the user has reviewed the PR.
Use the repository's merge method and delete the branch if the repository does. Never
use `--admin` to bypass branch protection. Find the allowed methods with
`gh repo view --json squashMergeAllowed,rebaseMergeAllowed,mergeCommitAllowed`.

### Squash merge

GitHub creates the squash commit and signs it with its own key, and the branch does not
need to contain the base first. A ruleset that requires signed commits still checks
every commit on the pull request branch, so each one must be signed and verified: an
unsigned commit blocks the merge until it is rebased, signed, and force pushed.

`gh pr view <n> --json mergeStateStatus` tells whether a branch needs updating first:
`DIRTY` is a conflict, and `BEHIND` matters only when a ruleset requires up-to-date
branches. Update by merging, never by rebasing, so nothing pushed is rewritten and no
force push is needed; the squash drops the merge commits.

- **Single pull request:** `gh pr merge <n> --squash`. When it is only `BEHIND`, run
  `gh pr update-branch <n>` first: GitHub adds a merge commit it signs. On a conflict,
  merge the base into the branch locally as the `git-commit` skill describes (Updating
  Layers), signed with your key, push, and wait for the checks.
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

### Fast-forward merge

GitHub's **Rebase and merge** rewrites the commits on its servers and cannot sign them,
so a ruleset that requires signed commits rejects it. When the repository requires
signed commits and does not allow squash merges, merge with a local fast-forward,
which lands the pull request's own signed commits unchanged:

1. Run `git fetch origin` and check that the branch contains the base:
   `git merge-base --is-ancestor origin/<base> origin/<branch>`. If it does not,
   rebase the branch onto `origin/<base>`, which signs the rewritten commits with your
   key, force push it with `--force-with-lease` (a request to merge this pull request
   authorizes it; see the `git-commit` skill), and wait for the checks.
2. Push the branch's head to the base: `git push origin origin/<branch>:<base>`.
   GitHub marks the pull request merged once its head is on the base branch.
3. Delete the merged remote branch (`git push origin --delete <branch>`) if the
   repository deletes merged branches and GitHub has not already.

Fast-forward a stack one layer at a time, bottom first. Pushing the top branch would
merge every layer at once, but only the bottom pull request closes its issues: GitHub
reads closing keywords only from pull requests that target the default branch, and a
higher layer targets the branch below it. After each layer merges, GitHub re-targets
the next one to the base without re-reading its body, so save the body again unchanged
(`gh pr view <n> --json body --jq .body > <file>`, then
`gh pr edit <n> --body-file <file>`), confirm that
`gh pr view <n> --json closingIssuesReferences` lists its issues, and merge it.

### Several at once

When the user asks to merge several pull requests or stacks (a list, a range, or "the
ready ones"), merge them in one pass without asking about each one. When several are
ready, suggest this; never require it.

1. Skip any pull request with failing checks or an unresolved blocking finding, and
   report it.
2. Merge one stack or pull request at a time. Rebase only when the merge method or a
   conflict requires it, and only the one about to merge: every merge moves the base
   again, so rebasing the others would be repeated.
3. Stop only for a conflict whose resolution changes behavior, or for a failing check.
   Resolve import-only and formatting conflicts yourself.

After the merge, confirm that the linked issues closed. If the merge closed the last
open sub-issue of a slice, the next step is the slice review, not closing the parent.
