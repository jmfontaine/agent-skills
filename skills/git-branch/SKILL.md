---
name: git-branch
description: Git branch naming guidelines. Use when creating, renaming, or checking out new branches, including branches for stacked pull requests.
allowed-tools: Bash(git branch:*) Bash(git checkout:*) Bash(git switch:*)
---

# Git Branch Naming Guidelines

## Naming Style

Match the repository's existing branch names. Run `git branch -a` and mirror the
prevailing prefixes, separators, casing, and ticket formats.

If the repository has no branches besides the default branch, use
[Conventional Branch](https://conventionalbranch.org/) with one of these prefixes:

- `feat/`: New features (e.g., `feat/add-login-page`)
- `fix/`: Bug fixes (e.g., `fix/header-bug`)
- `hotfix/`: Urgent fixes (e.g., `hotfix/security-patch`)
- `release/`: Release preparation (e.g., `release/v1.2.0`)
- `chore/`: Non-code tasks (e.g., `chore/update-dependencies`)

## Additional Rules

- Include ticket numbers when applicable (e.g., `feat/issue-123-new-login`)
- Dots allowed only for version numbers in `release/` branches
- Do NOT use `git -C <path>` when the current directory is already the repository root
