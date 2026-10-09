# Pull requests

A pull request delivers one issue and carries the evidence that it works. Reviewers
should be able to judge it from the PR, its issue, and the linked brief alone.

## Scope

Deliver one issue per pull request by default. Split dependent concerns into stacked
pull requests (the `git-commit` skill). Put an unrelated fix found along the way on its
own branch and pull request, opening an issue for it when it is committed work.

## Before opening

- Run the issue's verification and the repository's QA checks. Note each command or
  scenario and its result.
- Compare the diff with the issue's outcome, its out-of-scope list, and the brief's
  exclusions. Remove anything that does not belong.

## Open

Push and open the pull request only when the user asks. Use the repository's template
(`.github/pull_request_template.md`) if one exists, otherwise
`assets/pull-request-template.md`. Write the body to a file and pass it with
`--body-file`.

- Open it as a draft (`gh pr create --draft`) while work or verification is incomplete,
  or when early feedback is wanted. Mark it ready with `gh pr ready <n>`.
- Title it with the outcome, following the repository's title conventions.
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
Use the repository's merge method, such as `gh pr merge <n> --rebase`, or
`gh stack merge` for a stack. Delete the branch if the repository does. Never use
`--admin` to bypass branch protection.

After the merge, confirm that the linked issues closed. If the merge closed the last
open sub-issue of a slice, the next step is the slice review, not closing the parent.
