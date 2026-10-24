---
name: github-workflow
description: Track work in GitHub issues and deliver it through pull requests and reviews. Load it before changing code for a GitHub issue, however the user names it ("#24", "issue 24", "let's work on issue 24", or an issue URL), before any push, pull request, or merge, including "merge PR 116" or "merge PRs 140-143", and when the user reports a merge, such as "I merged PR 4". Also use it to create, triage, or close issues, including filing issues from a review or plan file; to review a pull request against its issue; to respond to review findings; to configure a review bot; or to set up or check a repository's settings, labels, and templates. Not for checking the findings of a review file when nothing will be filed or committed.
allowed-tools: Bash(gh issue list:*) Bash(gh issue view:*) Bash(gh label list:*) Bash(gh pr checks:*) Bash(gh pr diff:*) Bash(gh pr list:*) Bash(gh pr view:*) Bash(gh repo view:*)
---

# GitHub Workflow

Issues state what to do and how to verify it. Pull requests deliver it. Reviews check
that the delivery matches the issue. Each piece links to its source instead of copying
it, so one edit never leaves a stale duplicate behind.

`Issue → Branch → Pull request → Agent review → Maintainer review → Merge → Cleanup`

## Orient

Read agent instruction files (AGENTS.md, CLAUDE.md) and the repository's existing GitHub
conventions before acting: templates under `.github/`, labels, milestones, and the
allowed merge method. Compare them with
[Repository setup](references/repository-setup.md): every repository uses the same
configuration, and a difference without a reason recorded under "Deviations from the
shared workflow" in AGENTS.md is drift to report, not to mirror. Branch names follow the
`git-branch` skill in every repository: `<type>/issue-<N>-<slug>` for an issue,
`<type>/<slug>` otherwise.

When agent instruction files allow or require committing straight to the default branch,
there are no branches, pull requests, or reviews. Commit on the default branch, push
only when the user asks, and close issues with `Closes #N` in the commit message.
Commits there land as they are, so write them in the repository's commit message style.
The issues reference still applies.

When agent instruction files say the repository's GitHub settings are managed as code,
change settings, labels, and templates there through a pull request, never with
`gh api` or the web UI.

When the project plans with the `product-development-system` skill, if installed, that
skill decides what goes into a milestone and runs the release review once a milestone's
issues are closed. This skill covers the mechanics. Without it, a milestone is a plain
GitHub milestone named for a release.

Load only the reference the task needs. Paths are relative to this skill directory.

| Current task | Read |
| --- | --- |
| Create, triage, structure, pick up, or close an issue | [Issues](references/issues.md) |
| Open, describe, update, or merge a pull request | [Pull requests](references/pull-requests.md) |
| Review a pull request, respond to findings, or configure a review bot | [Review](references/review.md) |
| Set up or check a repository's settings, labels, and templates | [Repository setup](references/repository-setup.md) |

## Shared rules

- **Visible actions need authorization.** Creating or editing issues, pushing, opening
  pull requests, posting comments or reviews, and merging are seen by others. Do them
  when the user asks or has already authorized them, without adding routine
  confirmation. Reading is always fine. A request covers every step that completes it:
  asking to open a pull request covers its agent review, the fixes for its findings,
  and posting the review; asking to merge, or saying a merge happened, covers the
  cleanup. Clearing a blocker, such as a ruleset change, is not a request to merge.
- **Scratch files are not deliverables.** Working material for a task in progress
  (reviews, plans, research exports, draft bodies, handoff notes, task data) belongs in
  the scratch directory the agent instruction files name, else an ignored `.scratch/`
  at the repository root. Never commit it unless the user asks. Nothing posted on
  GitHub refers to it. Delete it once its content is filed or the task is done.
- **Link, don't copy.** Issues link the brief they come from when one exists, never a
  scratch file. Pull requests link their issues. Restate only what a reader needs to
  act. When `gh` can record a link as an issue relationship (blocked by, blocking,
  duplicate of), set the relationship instead of writing the link in the body, where it
  would go stale.
- **Report real evidence.** Claim a verification step only after running it. Mark
  anything unverified as such; never tick a checkbox without evidence.
- **Prefix agent comments.** Start agent-authored comments, replies, and review bodies
  with `[AgentName]`, using the configured name or the agent's actual identity, such as
  `[Claude]` or `[Codex]`. An agent review and its inline comments add the role, such
  as `[Claude reviewer]`, so the review stands apart from the author's replies even
  when both run on the same model. Issue and pull request bodies are artifacts and
  take no prefix.
- **Defer to the Git skills.** Follow the `git-branch` and `git-commit` skills, if
  installed, for branch names, commits, and stacked pull requests. Without them, sign
  every commit and never rewrite pushed commits.

Use the GitHub CLI (`gh`). If it is unavailable or the repository is not on GitHub,
prepare the exact titles, bodies, and comments with their intended destination, and say
that nothing was posted.

End with what changed on GitHub (with links), what awaits the user, such as a review or
merge decision, and the next useful step.
