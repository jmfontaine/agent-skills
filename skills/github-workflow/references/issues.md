# Issues

An issue is either intake or committed work. Keep the distinction visible: a report's
existence is not a commitment, and committed work needs a verifiable outcome.

| Kind | Purpose | Created by |
| --- | --- | --- |
| Intake | A bug report or request awaiting triage | Users, or anyone relaying them |
| Task | Actionable committed work with an outcome and verification | A deliberate planning decision |
| Slice | Parent of the active slice's tasks, when the project plans in slices | A deliberate planning decision |

Express the kind with the repository's existing issue types or labels (`--type`,
`--label`). Do not invent a new taxonomy.

## Triage intake

Check for reproduction steps or evidence, search for duplicates
(`gh issue list --search "<terms>" --state all`), and judge whether the request fits the
product's boundaries. Then do one of:

- Ask for the missing information.
- Close it as a duplicate or out of scope, linking the reason.
- Keep it as accepted intake, unscheduled.
- Turn it into a task, linking the active slice when one applies.

Do not close a valid report just because it is unplanned. Questions about product
boundaries belong to the user.

## Write a task issue

Use the repository's issue template if one exists, otherwise
`assets/issue-template.md`.

- **Title:** the outcome, such as "Report checksum mismatch in verify command", not the
  activity, such as "Work on verify".
- **Context:** link the Slice Brief and the requirement or acceptance criterion this
  issue covers, or the intake issue it resolves. Do not paste the brief; a copy drifts
  when the brief changes.
- **Outcome:** what is true when the work is done.
- **Verification:** how anyone confirms the outcome, including important failure
  behavior. An issue without verification cannot be reviewed.
- **Out of scope:** only the exclusions a contributor might otherwise assume.

Size each task for one pull request. Split work that needs several independent reviews
into separate issues; dependent layers of one change can stay in one issue and ship as
stacked pull requests. Record ordering with `--blocked-by` rather than prose.

Create issues only for committed work in the active or near-term plan. Do not build
speculative issue trees for distant work.

## Group a slice under a parent issue

When the project plans in slices, create one parent issue for the active slice once its
brief is canonical in Git. The parent holds pointers only:

```markdown
Brief: https://github.com/<owner>/<repo>/blob/main/docs/slices/archive-integrity.md
Milestone: Users can verify archived sources
Appetite: 2 weeks
```

Scope, requirements, and acceptance criteria stay in the brief. Add the parent to the
project's GitHub Project (`--project <title>`, which needs the `project` token scope:
`gh auth refresh -s project`) so it represents the slice on the board.

Attach each task as a sub-issue, at creation with `gh issue create --parent <slice>` or
afterwards with `gh issue edit <slice> --add-sub-issue <task>,<task>`. GitHub then shows
the slice's progress on the parent.

Closed sub-issues do not make the slice done. Close the parent only after the slice
review, posted as a comment on it. At review, every open sub-issue needs an explicit
decision: finish it in this slice, move it to later work (`--remove-parent`), or close
it as not planned with a reason.

## Pick up an issue

Read the issue, its comments, its parent, and linked context such as the brief. Check
that nobody else holds it: no other assignee and no open pull request
(`gh issue view <n> --json assignees,closedByPullRequestsReferences`). When the user
asks you to take it, assign it (`gh issue edit <n> --add-assignee @me`) and create a
branch that includes the issue number.

If the outcome or verification is missing or ambiguous, fix the issue with the user
before coding rather than guessing. When the work reveals something outside the issue,
open or propose a separate issue instead of growing the pull request.

## Close an issue

A closing keyword in a merged pull request closes the issue (see the pull requests
reference). Close manually only with a reason:
`gh issue close <n> --reason "not planned" --comment "[AgentName] <why>"`. Use
`completed` only when the outcome was delivered and verified.
