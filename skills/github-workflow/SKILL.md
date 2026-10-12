---
name: github-workflow
description: Track work in GitHub issues and deliver it through pull requests and reviews. Load it before changing code for a GitHub issue, however the user names it ("#24", "issue 24", "let's work on issue 24", or an issue URL), and before any push, pull request, or merge, including "merge PR 116" or "merge PRs 140-143". Also use it to create, triage, or close issues, including filing issues from a review or plan file; to group tasks under a parent issue; to review a pull request against its issue; to respond to review findings; or to configure a review bot. Not for checking the findings of a review file when nothing will be filed or committed.
allowed-tools: Bash(gh issue list:*) Bash(gh issue view:*) Bash(gh pr checks:*) Bash(gh pr diff:*) Bash(gh pr list:*) Bash(gh pr view:*) Bash(gh repo view:*)
---

# GitHub Workflow

Issues state what to do and how to verify it. Pull requests deliver it. Reviews check
that the delivery matches the issue. Each piece links to its source instead of copying
it, so one edit never leaves a stale duplicate behind.

`Issue → Branch → Pull request → Reviews → Merge → Issue closed`

## Orient

Read agent instruction files (AGENTS.md, CLAUDE.md) and the repository's existing GitHub
conventions before acting: templates under `.github/`, labels, issue types, Projects in
use, and the allowed merge method. Mirror them; the templates and rules in this skill
are fallbacks. Branch names are the exception: `<type>/issue-<N>-<slug>` for an issue,
`<type>/<slug>` otherwise (the `git-branch` skill), in every repository.

When the project plans work with Slice Briefs (the `product-development-system` skill),
that skill decides whether work deserves an issue and owns the slice review. This skill
covers the mechanics.

Load only the reference the task needs. Paths are relative to this skill directory.

| Current task | Read |
| --- | --- |
| Create, triage, structure, pick up, or close an issue | [Issues](references/issues.md) |
| Open, describe, update, or merge a pull request | [Pull requests](references/pull-requests.md) |
| Review a pull request, respond to findings, or configure a review bot | [Review](references/review.md) |

## Shared rules

- **Visible actions need authorization.** Creating or editing issues, pushing, opening
  pull requests, posting comments or reviews, and merging are seen by others. Do them
  when the user asks or has already authorized them, without adding routine
  confirmation. Reading is always fine.
- **Scratch files are not deliverables.** Review, plan, and research files the user
  asked for (REVIEW.md, PLAN*.md, IMPROVEMENTS.md, exported research), often kept in a
  scratch directory the agent instruction files name, stay uncommitted unless the user
  asks to commit them. Nothing posted on GitHub refers to them: they are deleted once
  their content is filed.
- **Link, don't copy.** Issues link the committed brief they come from, never a scratch
  file. Pull requests link their issues. Restate only what a reader needs to act. When
  `gh` can record a link as an issue relationship (parent, blocked by, blocking,
  duplicate of), set the relationship instead of writing the link in the body, where it
  would go stale.
- **Report real evidence.** Claim a verification step only after running it. Mark
  anything unverified as such; never tick a checkbox without evidence.
- **Prefix agent comments.** Start agent-authored comments, replies, and review bodies
  with `[AgentName]`, using the configured name or the agent's actual identity, such as
  `[Claude]` or `[Codex]`. Issue and pull request bodies are artifacts and take no
  prefix.
- **Defer to the Git skills.** Follow the `git-branch` and `git-commit` skills, if
  installed, for branch names, commits, stacked pull requests, and force pushes.

Use the GitHub CLI (`gh`). If it is unavailable or the repository is not on GitHub,
prepare the exact titles, bodies, and comments with their intended destination, and say
that nothing was posted.

End with what changed on GitHub (with links), what awaits the user, such as a review or
merge decision, and the next useful step.
