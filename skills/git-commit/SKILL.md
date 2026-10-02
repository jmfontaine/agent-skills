---
name: git-commit
description: Git commit guidelines. Use when creating, amending, squashing, or rewording git commits, staging files, or writing commit messages.
allowed-tools: Bash(git add:*) Bash(git branch:*) Bash(git commit:*) Bash(git diff:*) Bash(git log:*) Bash(git rebase:*) Bash(git status:*)
---

# Git Commit Guidelines

## Message Style

Match the repository's existing style. Run `git log --oneline -20` (or `git log -20 --format=%B` when you need bodies) and mirror the prevailing subject format, casing, tense, prefixes, scopes, and body usage.

If the history is too short to show a style, use [Conventional Commits](https://www.conventionalcommits.org/).

## Pre-Commit Review

Before committing, review all staged and unstaged changes to determine if they should be split into multiple commits. Changes belong in separate commits when they are different kinds of change (e.g., a feature and a bug fix), affect unrelated areas, or serve distinct purposes.

If the user has not explicitly asked to split, suggest doing so and list the proposed commits. Proceed with a single commit only if all changes are logically cohesive.

Also check for changes made outside the current session (e.g., editor saves, other tools). If they are relevant to the commit, offer to include them. If they are unrelated, silently ignore them unless the user asks to include them.

cSpell words added outside the session (typically by the user, in `cspell.json`, `.cspell.json`, `.vscode/settings.json`, or a custom dictionary file) are an exception: include them, without asking, in the commit that introduces the text using them. When commits are split, put each word in the commit it relates to.

## First Commit

Unless the user instructs otherwise, the first commit of a repository (no commits yet, so `git log` reports none) must use this exact message, overriding the message style rules above:

```text
That's one small step for mankind, one giant leap for a man
```

## Clean History

The user typically rebase-merges pull requests, so every commit lands on the main branch as-is. Keep the commit history clean at all times: each commit should be a complete, logical change with no "fix typo" or "address review" follow-ups.

When changes correct or complete a previous commit (e.g., a quick fix or forgotten file), fold them into that commit instead of creating a new one:

- **Not pushed:** amend it without asking. Use `git commit --amend` for the last commit, or `git commit --fixup=<commit>` followed by `git rebase --autosquash <commit>~1` for an older one.
- **Pushed:** rewriting it requires a force push. Ask the user whether to amend and force push, or create a new commit.

To check whether a commit has been pushed, run `git branch -r --contains <commit>`. Empty output means it is unpushed.

## Additional Guidelines

- Always sign commits with `git commit -S`
- Do NOT include AI co-authoring information
- Do NOT use `git -C <path>` when the current directory is already the repository root
