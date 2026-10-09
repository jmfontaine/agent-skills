---
name: github-workflow
description: Track work in GitHub issues and deliver it through pull requests and reviews. Use when creating, triaging, picking up, or closing an issue; grouping a slice's tasks under a parent issue; opening, describing, updating, or merging a pull request; reviewing a pull request against its issue and acceptance criteria; responding to review findings; or configuring an AI review bot. Use it even for short requests such as "work on #17", "open a PR", or "review PR 42".
allowed-tools: Bash(gh issue list:*) Bash(gh issue view:*) Bash(gh pr checks:*) Bash(gh pr diff:*) Bash(gh pr list:*) Bash(gh pr view:*)
---

# GitHub Workflow

Issues state what to do and how to verify it. Pull requests deliver it. Reviews check
that the delivery matches the issue. Each piece links to its source instead of copying
it, so one edit never leaves a stale duplicate behind.

`Issue → Branch → Pull request → Reviews → Merge → Issue closed`

## Orient

Read agent instruction files (AGENTS.md, CLAUDE.md) and the repository's existing GitHub
conventions before acting: templates under `.github/`, labels, issue types, Projects in
use, branch names, and the allowed merge method. Mirror them; the templates and rules in
this skill are fallbacks.

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
- **Link, don't copy.** Issues link the brief or report they come from. Pull requests
  link their issues. Restate only what a reader needs to act.
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
