---
name: git-commit
description: Git commit guidelines, including GitHub stacked pull requests. Use when creating, amending, squashing, or rewording git commits, staging files, writing commit messages, or splitting dependent changes into stacked branches and pull requests.
allowed-tools: Bash(git add:*) Bash(git branch:*) Bash(git commit:*) Bash(git diff:*) Bash(git log:*) Bash(git rebase:*) Bash(git status:*) Bash(gh extension list:*) Bash(gh stack add:*) Bash(gh stack bottom:*) Bash(gh stack checkout:*) Bash(gh stack down:*) Bash(gh stack init:*) Bash(gh stack rebase:*) Bash(gh stack top:*) Bash(gh stack up:*) Bash(gh stack view:*)
---

# Git Commit Guidelines

## Message Style

Match the repository's existing style. Run `git log --oneline -20` (or
`git log -20 --format=%B` when you need bodies) and mirror the prevailing subject
format, casing, tense, prefixes, scopes, and body usage.

If the history is too short to show a style, use
[Conventional Commits](https://www.conventionalcommits.org/).

## Pre-Commit Review

Before committing, review all staged and unstaged changes to determine if they should be
split into multiple commits. Changes belong in separate commits when they are different
kinds of change (e.g., a feature and a bug fix), affect unrelated areas, or serve
distinct purposes.

If the user has not explicitly asked to split, suggest doing so and list the proposed
commits. Proceed with a single commit only if all changes are logically cohesive.

Also check for changes made outside the current session (e.g., editor saves, other
tools). If they are relevant to the commit, offer to include them. If they are
unrelated, silently ignore them unless the user asks to include them.

cSpell words added outside the session (typically by the user, in `cspell.json`,
`.cspell.json`, `.vscode/settings.json`, or a custom dictionary file) are an exception:
include them, without asking, in the commit that introduces the text using them. When
commits are split, put each word in the commit it relates to.

## First Commit

Unless the user instructs otherwise, the first commit of a repository (no commits yet,
so `git log` reports none) must use this exact message, overriding the message style
rules above:

```text
That's one small step for mankind, one giant leap for a man
```

## Clean History

The user typically rebase-merges pull requests, so every commit lands on the main branch
as-is. Keep the commit history clean at all times: each commit should be a complete,
logical change with no "fix typo" or "address review" follow-ups.

When changes correct or complete a previous commit (e.g., a quick fix or forgotten
file), fold them into that commit instead of creating a new one:

- **Not pushed:** amend it without asking. Use `git commit --amend` for the last commit,
  or `git commit --fixup=<commit>` followed by `git rebase --autosquash <commit>~1` for
  an older one.
- **Pushed:** rewriting it requires a force push. Ask the user whether to amend and
  force push, or create a new commit.

To check whether a commit has been pushed, run `git branch -r --contains <commit>`.
Empty output means it is unpushed.

## Stacked Pull Requests

Use
[GitHub stacked pull requests](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs)
when the work spans several dependent concerns that each deserve their own review, such
as a schema change, then the API using it, then the UI. Each concern gets its own
branch, and each branch builds on the one below it. A single cohesive change needs one
branch, not a stack. Independent changes go on separate branches off the trunk.

### Availability

Stacks are available when the repository is hosted on GitHub and the `gh stack`
extension is installed. Check with `gh extension list` and look for `github/gh-stack`.
Do NOT run a `gh stack` command to find out: recent GitHub CLI versions install the
extension silently when `gh stack` is invoked.

- **`gh` is missing or the repository is not on GitHub:** skip stacks and use plain git
  branches.
- **Extension missing:** ask the user whether to install it with
  `gh extension install github/gh-stack`. If they decline, use plain git branches and do
  not ask again in this session.
- **A `gh stack` command exits with code 9:** stacked pull requests are not enabled for
  the repository. Tell the user and fall back to plain git branches.

### Building a Stack

When splitting changes during the pre-commit review, group the proposed commits by layer
and list the proposed branches with their commits. Order the layers so code sits in the
same branch as its dependencies or above them.

1. Only after `gh extension list` shows `github/gh-stack`, run `gh stack view --short`.
   Exit code 0 means the current branch already belongs to a stack; exit code 2 means it
   does not.
2. To start a stack, run `gh stack init <branch>` from the trunk to create and check out
   the bottom branch. When the current branch already holds the first concern, run
   `gh stack init <current-branch>` to adopt it. Pass `--base <trunk>` when the trunk is
   not the repository's default branch.
3. Commit the layer's changes with `git commit -S`.
4. For the next layer, run `gh stack add <branch>` from the top branch, then commit. Do
   NOT use `gh stack add -m`: it can commit on the current branch instead of the new
   one, and it does not sign the commit.

Name each branch following the `git-branch` skill if installed; otherwise mirror the
repository's existing branch names (`git branch -a`).

### Rebase Only

Use rebase for every cross-branch operation. Never merge one branch into another or
cherry-pick between branches.

- **Fix a lower layer:** check out its branch with `gh stack down` or
  `gh stack checkout <branch>`, fold the change into the right commit as described in
  Clean History, then run `gh stack rebase --upstack` to replay the layers above.
- **Catch up with the trunk:** run `gh stack rebase`.
- **Move commits between layers or reorder them:** from the top branch, run
  `git rebase -i --update-refs <trunk>` so every branch moves with its commits. Supply
  the todo list through `GIT_SEQUENCE_EDITOR` (e.g., write the edited todo to a file and
  run `GIT_SEQUENCE_EDITOR='cp <todo-file>' git rebase -i --update-refs <trunk>`), since
  an agent cannot drive an interactive editor. Keep each
  `update-ref refs/heads/<branch>` line after the last commit of its layer. Do NOT use
  `gh stack modify`: it needs an interactive terminal and folds branches by
  cherry-picking.
- **Conflicts:** resolve them and stage with `git add`. During `gh stack rebase`, run
  `gh stack rebase --continue`, or `gh stack rebase --abort` to restore every branch.
  During a plain `git rebase`, run `git rebase --continue` or `git rebase --abort`, then
  `gh stack rebase --upstack` if a lower layer changed.

Rewriting a pushed layer, including the layers above it that a cascading rebase replays,
follows the pushed-commit rule in Clean History: ask before force pushing.

### Pushing and Merging

Push, open pull requests, or merge only when the user asks.

- **Open pull requests:** run `gh stack submit --auto`. It pushes every branch, opens
  one pull request per branch, and links them into a stack. Without `--auto`, it opens
  an editor that needs an interactive terminal. New pull requests are drafts unless you
  pass `--open`.
- **Push after rewriting layers:** run `gh stack push`, which uses `--force-with-lease`.
- **Merge:** run `gh stack merge --rebase <pr-number>` to merge every pull request up to
  and including that one.

## Additional Guidelines

- Always sign commits with `git commit -S`
- Do NOT include AI co-authoring information
- Do NOT use `git -C <path>` when the current directory is already the repository root
