---
name: parallel-issues
description: Work several GitHub issues in parallel with unattended coding agents, one Herdr workspace and git worktree per group of issues, each group delivered as a stack of signed, reviewed pull requests. Use when the user wants to fix a batch, list, or milestone of issues at once, run agents overnight or while away, fan issues out to parallel agents, or check on, review, merge, or clean up such a run. Use it even for short requests such as "work on #12, #13 and #14 in parallel" or "launch the milestone before I go to bed".
compatibility: Requires Herdr (run from a Herdr pane), gh with the github/gh-stack extension, the 1Password CLI (op), git with SSH commit signing, and Python 3.10+. Agents start as omp by default.
---

# Parallel Issues

Plan a batch of GitHub issues with the user, then launch one coding agent per group of
issues that touch the same code. Each agent works unattended in its own worktree and
delivers its group as a stack of pull requests, one per issue, each signed, checked,
and reviewed before it is committed. The user reviews and merges the pull requests when
they are back.

The launcher is `scripts/parallel_issues.py` (path relative to this skill directory).
Run it from the repository's main checkout. The agents follow `assets/prompt.md`, the
`github-workflow` and `git-commit` skills, and the repository's agent instruction files
(AGENTS.md, CLAUDE.md). Keep repository-specific rules, such as tests that must not
run concurrently, in those instruction files rather than in the prompt.

## Before the first run

Check each item and fix what is missing with the user; the launcher refuses to start
otherwise.

- This session runs in a Herdr pane (`HERDR_ENV=1`). For agent status to be accurate,
  Herdr's integration for the agent must be installed (`herdr integration status`).
- `gh extension list` shows `github/gh-stack`.
- Agents sign every commit with their own key, never the user's:
  - `git config commit.gpgsign` is `true` in the repository.
  - `git config agent.signingKey` holds a 1Password reference to the agent's SSH
    private key, such as `op://Private/Agent signing/private key`. It can differ per
    directory tree through `includeIf`.
  - The agent's public key is in `gpg.ssh.allowedSignersFile` for the repository's
    `user.email`, and is added to the user's GitHub account as a **Signing** key.
  - The user is present at launch: reading the key asks 1Password once.
- The default branch should require signed commits (a ruleset), so an unverified
  commit fails the push instead of landing.

## Plan the batch

Planning happens with the user, before anything runs.

1. List the candidate issues (`gh issue list --milestone <name>`) and read each one.
2. Group issues that will change the same files or behavior, using the code paths
   the issues cite and a search of the code. Order each group bottom-up: what others
   depend on first, then smaller changes. Stack only issues that really overlap;
   independent issues get their own group, since a stack merges bottom-up and a
   rejected lower layer holds back every layer above it.
3. Leave out, and say why:
   - issues the user did not open, or that someone else edited (the launcher refuses
     them anyway, because their text could steer an unattended agent);
   - issues likely to change `.github/workflows/`, since pushing those needs the user;
   - issues whose outcome or verification is unclear, which belong in an interactive
     session first.
4. Size the run: one group for a first run in a repository, then a few groups at a
   time. Each group is a long agent session with its own model usage, and the test
   suites run concurrently on one machine.
5. Present the plan as a table (group, issues in order, files touched, why grouped)
   and launch only after the user approves it.

## Launch

Each argument is a group, issues comma-separated, bottom of the stack first:

```shell
python3 <skill-dir>/scripts/parallel_issues.py launch --dry-run 14,27 13
python3 <skill-dir>/scripts/parallel_issues.py launch 14,27 13
```

The dry run checks every issue and prints each group's branches and prompt without
creating anything. The launch creates, per group, a branch from the default branch in
a Herdr-managed worktree and workspace, starts the agent there (`omp --advisor`; change
it with `--kind <herdr-kind> -- <agent args>`), and submits the prompt. It also loads
the agent signing key into a private ssh-agent for 12 hours, routes the agents' pushes
over HTTPS through `gh`, and keeps the Mac awake for the same period.

A group that fails a check is reported and skipped; the others still launch.

## While it runs

- `parallel_issues.py status` lists each group's agent state and its pull requests.
- `herdr agent read <agent> --source recent-unwrapped --lines 120` shows an agent's
  recent output. The user can also open the workspace in Herdr and talk to the agent.
- Each agent ends by running `parallel_issues.py record`. It fails unless GitHub shows
  every commit of each pull request as verified, since the default branch's ruleset
  does not cover pull request branches. Otherwise it stores the commit each pull
  request was opened with, which `clean` relies on. `status` shows a group whose
  agent stopped without recording.

## After the run

1. **Review.** Each pull request gets the review the `github-workflow` skill describes.
   Changes to a lower layer happen in an interactive session: fix it, then
   `gh stack rebase --upstack`, and force push only with the user's agreement.
2. **Merge.** Merge as the `github-workflow` skill describes, bottom-up.
3. **Clean.** Run `clean --dry-run`, then `clean`. A group's worktree, workspace, and
   branches are removed only when every branch still points at the commit `record`
   stored, each of those pull requests is merged, the worktree has no uncommitted
   changes, and no other Herdr workspace uses it. Anything else is kept with the
   reason, for the user to resolve.

## What the safeguards do not cover

The agents act as the user on GitHub. The launcher's issue checks, the prompt's
instructions not to read comments or follow linked pages, and the rule against pushing
workflow changes reduce what can steer an agent, but an agent that ignores its prompt
can still do anything the user's `gh` login allows. The signing key cannot push or log
in; it can only make commits that verify, until it expires or is removed from GitHub.
