# Issues

An issue is the spec for its work. Its state shows how far it has been accepted, using
GitHub's own fields:

| State | Meaning | Shown by |
| --- | --- | --- |
| Untriaged | A report or request nobody has judged yet | The `triage` label (issue forms add it) |
| Accepted | Triaged and valid, not scheduled | No `triage` label, no milestone |
| Committed | Planned into a release | A milestone (`vX.Y.Z`) |

A report's existence is not a commitment, and committed work needs verifiable
acceptance criteria. Use no other kinds, issue types, or labels to express state. The
labels themselves are listed in [Repository setup](repository-setup.md).

## Triage

Check for reproduction steps or evidence, search for duplicates
(`gh issue list --search "<terms>" --state all`), and judge whether the request fits the
product's boundaries. Then do one of:

- Ask for the missing information. Leave `triage` on.
- Close it as a duplicate with `gh issue close <n> --duplicate-of <original>`, or as out
  of scope with a comment giving the reason.
- Accept it: remove `triage` (`gh issue edit <n> --remove-label triage`), set exactly
  one change-type label per the `git-branch` skill's label table (`bug`,
  `enhancement`, `documentation`, and the other baseline labels), and set a milestone
  only if the user commits it to a release.

Do not close a valid report just because it is unplanned. Questions about product
boundaries belong to the user. Never create a label outside the baseline; ask instead.

## Write an issue

Use the repository's issue template if one exists, otherwise
`assets/issue-template.md`.

- **Title:** the outcome, such as "Report checksum mismatch in verify command", not the
  activity, such as "Work on verify".
- **Context:** link the brief and the requirement or acceptance criterion this issue
  covers, when a brief exists, or the issue it resolves. Do not paste the brief; a copy
  drifts when the brief changes.
- **Acceptance criteria:** what is observably true when the work is done, including
  important failure behavior.
- **Verification:** how anyone confirms the acceptance criteria. An issue without
  verification cannot be reviewed. Every step must be possible on the branch the work
  lands on: CI that runs only on pull requests to the default branch does not run on a
  stacked layer.
- **Out of scope:** only the exclusions a contributor might otherwise assume.
- **Self-contained:** a reader who sees only the issue understands it. Cite code at a
  commit SHA, never the review, plan, or research file the issue came from, its
  finding IDs (F1, I27, N4), or "the review".
- **Decision needed:** when the work needs a choice from the user, add this section
  with each option, its tradeoff, and your recommendation. When you report back, list
  every open decision by issue number.

Size each issue for one pull request. Split work that needs several independent reviews
into separate issues; dependent layers of one change can stay in one issue and ship as
a stack of pull requests. Record ordering and duplicates as relationships rather than
prose: `--blocked-by` or `--blocking` on `gh issue create`, `--add-blocked-by` or
`--add-blocking` on `gh issue edit`.

Create issues only for work in the current or next release. Do not build speculative
issue trees for distant work; uncommitted ideas belong in the project's Parking Lot, not
in the issue tracker.

When the user has approved a set of issues, create them all in one pass. Do not create
one first and wait for review before the rest, even if an earlier session or a memory
note says otherwise.

### File several issues from a review or plan

1. List what you would file (title, labels, blocked-by) and wait for approval.
2. Before creating anything, have a reviewer that did not draft the bodies check each
   set of acceptance criteria and each Verification against the code. Look especially
   for counted guarantees ("exactly one request"), cache and retry paths, and
   contracts that two issues both define. Fix every valid finding.
3. Create them all in one pass, then search the created bodies for the source file's
   name and finding IDs. Delete the source file once its content is filed.

## Pick up an issue

Read the issue, its comments, and linked context such as the brief. Check that nobody
else holds it: no other assignee and no open pull request
(`gh issue view <n> --json assignees,closedByPullRequestsReferences`). When the user
asks you to take it, assign it (`gh issue edit <n> --add-assignee @me`) and create its
branch, `<type>/issue-<N>-<slug>` as the `git-branch` skill describes.

If the acceptance criteria or verification are missing or ambiguous, fix the issue with
the user before coding rather than guessing. When the work reveals something outside the
issue, open or propose a separate issue instead of growing the pull request.

## Close an issue

A closing keyword in a merged pull request closes the issue (see the pull requests
reference). Close manually only with a reason:
`gh issue close <n> --reason "not planned" --comment "[AgentName] <why>"`. Use
`completed` only when the acceptance criteria were delivered and verified.
