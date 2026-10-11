---
name: git-branch
description: Git branch naming guidelines. Use when creating, renaming, or checking out new branches, including branches for stacked pull requests.
allowed-tools: Bash(git branch:*) Bash(git checkout:*) Bash(git switch:*)
---

# Git Branch Naming Guidelines

## Naming Style

Use one convention in every repository, whatever its existing branches look like:

- `<type>/issue-<N>-<slug>` for work on an issue (e.g., `feat/issue-123-add-login-page`)
- `<type>/<slug>` for anything else (e.g., `ci/pin-python-patch`)

`<type>` is the [Conventional Commits](https://www.conventionalcommits.org/) type the
change would carry (`feat:`, `fix:`, `docs:`, …), whether or not the repository's commit
messages use that format, plus two branch-only types, `hotfix/` and `release/`:

- `feat/`: New features (e.g., `feat/issue-123-add-login-page`)
- `fix/`: Bug fixes (e.g., `fix/issue-64-timestamp-fields`)
- `docs/`, `test/`, `refactor/`, `perf/`, `build/`, `ci/`, `chore/`: Changes of that
  type (e.g., `docs/issue-67-readme-concurrency`, `chore/update-dependencies`)
- `hotfix/`: Fixes shipped outside the normal release flow, such as a patch cut from a
  release tag (e.g., `hotfix/security-patch`); ordinary bug fixes use `fix/`
- `release/`: Release preparation, such as a version bump (e.g., `release/v1.2.0`)

`<slug>` is a few lowercase words from the issue title, or from the change's one-line
summary when there is no issue, joined by hyphens.

When a repository's agent instruction files (AGENTS.md, CLAUDE.md) or existing branches
follow another scheme, name new branches with this convention anyway, and point out
the instruction to the user so it can be updated. Do not rename existing branches.

## Additional Rules

- Dots allowed only for version numbers in `release/` branches
- Do NOT use `git -C <path>` when the current directory is already the repository root
