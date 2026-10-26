---
name: git-commit
description: Git commit guidelines, including which branch a commit goes on, the first commit, and GitHub stacked pull requests. Use before every git commit, including a bare "commit" or "commit and push" request, and when amending, squashing, rewording, staging files, writing commit messages, or splitting dependent changes into stacked branches and pull requests.
allowed-tools: Bash(git add:*) Bash(git branch:*) Bash(git commit:*) Bash(git diff:*) Bash(git fetch:*) Bash(git log:*) Bash(git merge:*) Bash(git rebase:*) Bash(git show:*) Bash(git status:*) Bash(gh extension list:*) Bash(gh stack add:*) Bash(gh stack bottom:*) Bash(gh stack checkout:*) Bash(gh stack down:*) Bash(gh stack init:*) Bash(gh stack rebase:*) Bash(gh stack top:*) Bash(gh stack up:*) Bash(gh stack view:*)
---

# Git Commit Guidelines

## Where to Commit

Never commit on the repository's default branch. Before the first commit of a change,
run `git branch --show-current`. If it prints the default branch, create a branch named
as the `git-branch` skill describes and commit there.

Two exceptions:

- **The first commit of a repository** (see First Commit) goes straight onto the default
  branch.
- **Straight-to-main repositories:** when the repository's agent instruction files
  (AGENTS.md, CLAUDE.md) allow or require committing straight to the default branch,
  commit there, with no branches or pull requests. Once the user has approved a change
  and it is finished and checked, commit it (signed) without asking. Push only when the
  user asks, and close issues with `Closes #N` in the commit message.

## Message Style

With squash merges, only the pull request title reaches the default branch, as one
commit. Write it in Conventional Commits without a scope: `<type>: <description>`, or
`<type>!: <description>` for a breaking change (the `github-workflow` skill, if
installed, has the details). Commits on the branch are free-form but clear: say what
changed and why in a short subject.

Commits that land as-is, such as those in straight-to-main repositories, follow the
repository's style. Run `git log --oneline -20` (or
`git log -20 --format=%B` when you need bodies) and mirror the prevailing subject
format, casing, tense, prefixes, scopes, and body usage. If the history is too short to
show a style, use [Conventional Commits](https://www.conventionalcommits.org/). The
first commit has its own message (see First Commit).

## Split Check

Before committing, review all staged and unstaged changes to decide how to divide them
into branches and pull requests. Changes belong in separate branches when they are
different kinds of change (e.g., a feature and a bug fix), affect unrelated areas, or
serve distinct purposes. Commits within a branch need no such split: only the pull
request title reaches the default branch.

If the user has not explicitly asked to split, suggest doing so and list the proposed
branches. Proceed with a single branch only if all changes are logically cohesive. In a
straight-to-main repository, apply the check to commits instead, since each commit lands
as-is.

Also check for changes made outside the current session (e.g., editor saves, other
tools). If they are relevant to the commit, offer to include them. If they are
unrelated, silently ignore them unless the user asks to include them.

cSpell words added outside the session (typically by the user, in `cspell.json`,
`.cspell.json`, `.vscode/settings.json`, or a custom dictionary file) are an exception:
include them, without asking, in the commit that introduces the text using them. When
changes are split, put each word in the change it relates to.

## Staging

Stage files by explicit path (`git add <path>…`), and commit only what you staged. Never
use `git commit -a`, `git commit -am`, `git add -A` or `git add .`: other sessions or
the user may have uncommitted edits in the same checkout. To change another repository,
work in its own worktree, never in its main checkout.

## First Commit

The first commit of a repository (no commits yet, so `git log` reports none) is the
exception to "never commit on the default branch":

- It goes straight onto the default branch (`main`), with no split check.
- It uses this exact message, overriding the message style rules above:

  ```text
  That's one small step for mankind, one giant leap for a man
  ```

- It may contain a generated project skeleton, minimal README content, and the
  Manifesto. It contains no real work: start that on a branch.

Follow these rules unless the user instructs otherwise.

## Pushed Commits

Never rewrite pushed commits. Fix review findings with new commits on top. Do not force
push. To check whether a commit has been pushed, run
`git branch -r --contains <commit>`; empty output means it is unpushed.

Amending unpushed commits is allowed, but never required. Use `git commit --amend` for
the last commit, or `git commit --fixup=<commit>` followed by
`git rebase --autosquash <commit>~1` for an older one.

Why squash merges: they are the only GitHub merge method that keeps the default branch
linear with every commit signed and verified; the full rationale is in
`github-workflow/references/repository-setup.md`, if the `github-workflow` skill is
installed. The only force push the workflow allows is the rejected-layer procedure of
the `parallel-issues` skill (if installed), and only with the user's approval.

## Stacked Pull Requests

Use
[GitHub stacked pull requests](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs)
when the work spans several dependent concerns that each deserve their own review, such
as a schema change, then the API using it, then the UI. Each concern gets its own
branch, and each branch builds on the one below it. A single cohesive change needs one
branch, not a stack. Independent changes go on separate branches off the default branch.

Stacks follow dependencies. The `parallel-issues` skill, if installed, also stacks
issues that edit the same files, and owns that exception.

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

When splitting changes during the split check, list the proposed branches by layer with
their changes. Order the layers so code sits in the same branch as its dependencies or
above them.

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

Name each branch following the `git-branch` skill: `<type>/issue-<N>-<slug>` for an
issue, `<type>/<slug>` otherwise, and its Stacked Layers section when one issue spans
several layers.

### Updating Layers

Never cherry-pick between branches.

**Update pushed layers by merging.** A merge rewrites nothing that is pushed, and the
squash drops the merge commits. Sign each merge commit (`git merge -S`).

- **Fix a lower layer:** check out its branch (`gh stack checkout <branch>`), commit the
  fix on top, then check out each layer above it in order and `git merge -S` the branch
  just below it.
- **Catch up with the trunk:** `git fetch origin <trunk>`, merge `origin/<trunk>` into
  the bottom branch, then each layer into the next one up.
- **Conflicts:** resolve them, stage with `git add`, and run `git commit -S` to finish
  the merge, or `git merge --abort` to undo it. `git show --remerge-diff <merge>` shows
  how a merge commit resolved its conflicts, for a review of the resolutions alone.
- Push each updated branch normally, bottom first.

**Unpushed layers may be rebased.** Never rebase a pushed layer, or any layer with a
pushed layer above it: replaying the layers above would need a force push.

- **Fix a lower layer:** check out its branch with `gh stack down` or
  `gh stack checkout <branch>`, fold the change into the right commit with
  `git commit --fixup=<commit>` and `git rebase --autosquash`, then run
  `gh stack rebase --upstack` to replay the layers above.
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

### Pushing and Merging

Push, open pull requests, or merge only when the user asks. The `github-workflow`
skill's pull requests reference, if installed, owns how stacks are pushed, opened and
merged. Without it: open a stack with `gh stack submit --auto` from the top branch, and
merge squash-only, with `gh stack merge --yes --squash` and no number for a whole stack.

## Identity and Pushing

A throwaway test repository sets its identity per command:
`git -c user.name=<name> -c user.email=<email> …`, or
`env GIT_AUTHOR_NAME=<name> GIT_AUTHOR_EMAIL=<email> … git …`. Never `export` it in a
persistent shell: the exported identity leaks into later real commits.

Before pushing, check the author and committer of the commits being pushed:
`git log --format='%h %an <%ae> / %cn <%ce>' <upstream>..`.

## Additional Guidelines

- Always sign commits with `git commit -S`
- Do NOT add `Co-authored-by` or any other attribution for AI agents: agents are tools,
  and the user signs off on every commit. Commits by external tools such as Dependabot
  keep their own identity
- Do NOT use `git -C <path>` when the current directory is already the repository root
