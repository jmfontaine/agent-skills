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

The point of a batch is that the user starts it and goes off to do something else. So
ask for everything the run will need while the user is still there, and always tell
them plainly whether they can leave now and what will call them back.

The launcher is `scripts/parallel_issues.py` (path relative to this skill directory).
Run it from the repository's main checkout. The agents follow `assets/prompt.md`, the
`github-workflow` and `git-commit` skills, and the repository's agent instruction files
(AGENTS.md, CLAUDE.md). Keep repository-specific rules, such as tests that must not
run concurrently, in those instruction files rather than in the prompt.

## When the user is needed

Gather every question before the first unattended step, ask them together, and start
only once all are answered. A question that surfaces after the user has left blocks
the work until they return, which defeats the batch.

- **Planning and launch: needed.** Approving the plan, labels or exclusions to fix,
  and the 1Password prompt that reads the signing key, once per 24 hours (see Signing
  key).
- **While the agents run: not needed.** Agents never ask; they take the conservative
  option and note it in the pull request.
- **After the run: needed only for decisions.** Merging, a force push after a rebase,
  pushing a change only the user may push, and anything a `keep` or `leftover` line
  from `clean` asks them to resolve. Ask these together as well, before a long merge,
  release, or cleanup sequence.

End every turn with one of these, stated in so many words:

- "I need you for: …", listing each item and why; or
- "You can go AFK now. Nothing needs you until …", naming what will need them next
  (the agents finishing, a merge decision, the next 1Password prompt), or "until I
  report back" when nothing will.

Say it right after the launch prints every group as started, and again whenever a
step that needed the user is done.

Notifications come from this session only, and only when the user is needed. Whenever
a turn ends with "I need you for: …" while the user may be away, also send that list:
`parallel_issues.py notify "<short title>"` with the list on standard input. Never let
the watcher or the agents ping the user: the watcher runs with `--no-notify` (see
While it runs), and the agents' own notifications are off through `agent.ompConfig`.

Ask the user to send decisions for an agent through this session, not by typing in
the agent's Herdr pane: this session cannot see those messages, and an agent's pane is
removed by `clean`.

## Before the first run

Check each item and fix what is missing with the user; the launcher refuses to start
otherwise.

- This session runs in a Herdr pane (`HERDR_ENV=1`). For agent status to be accurate,
  Herdr's integration for the agent must be installed (`herdr integration status`).
- `gh extension list` shows `github/gh-stack`.
- `gh auth status` lists the `workflow` scope: agents push changes under
  `.github/workflows/` like any other, and GitHub rejects such a push without it
  (`gh auth refresh -h github.com -s workflow` adds it). The launcher does not check
  this one.
- Agents sign every commit with their own key, never the user's:
  - `git config commit.gpgsign` is `true` in the repository.
  - `git config agent.signingKey` holds a 1Password reference to the agent's SSH
    private key, such as `op://Private/Agent signing/private key`. It can differ per
    directory tree through `includeIf`.
  - The agent's public key is in `gpg.ssh.allowedSignersFile` for the repository's
    `user.email`, and is added to the user's GitHub account as a **Signing** key.
  - The user is present when the key is read from 1Password (see Signing key).
- The default branch should require signed commits (a ruleset), so an unverified
  commit fails the push instead of landing.
- Optional, through git config:
  - `agent.ompConfig`: an omp config overlay that the launcher passes to every omp
    agent with `--config`, for settings only unattended agents should get, such as a
    model from another family for their pre-commit reviewer, so that review does not
    share the author's blind spots. It should also set
    `completion.notify`, `ask.notify` and `error.notify` to `"off"` (quoted), or every
    agent notifies the user at the end of each turn.
  - `agent.notifyCommand`: a command that sends the user a notification, with a title
    as its argument and the message on standard input, for example a script that
    sends a phone notification. `parallel_issues.py notify` runs it, and so does
    `status --wait` when no session supervises the run.
  - `agent.sshProgram`: the program agents sign with, in place of `ssh-keygen`. It
    takes `ssh-keygen`'s arguments, so it can be a wrapper that runs an extra check
    before signing. The agents and `env` get it as `gpg.ssh.program`.

## Plan the batch

Planning happens with the user, before anything runs.

1. List the candidate issues (`gh issue list --milestone <name>`) and read each one.
   Check its labels as well: they are the launcher's only signal for the branch type
   (see Launch). Add the commit-type label when the generic ones would mislead.
2. Group issues that will change the same files or behavior, using the code paths
   the issues cite and a search of the code. Order each group bottom-up: what others
   depend on first, then smaller changes. Stack only issues that really overlap;
   independent issues get their own group, since a stack merges bottom-up and a
   rejected lower layer holds back every layer above it. Then compare the groups with
   each other: two groups that edit the same files, including shared ones such as
   test fixtures and configuration, command registries, help text, or the
   documentation index, conflict when the first one merges, and every later one pays
   a merge round. Stack them, or run them in separate waves.
3. Leave out, and say why:
   - issues the user did not open, or that someone else edited (the launcher refuses
     them anyway, because their text could steer an unattended agent);
   - issues whose outcome or verification is unclear, which belong in an interactive
     session first.
4. Size the run knowing that each group is a long agent session with its own model
   usage, and that the test suites run concurrently on one machine.
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
a Herdr-managed worktree and workspace, starts the agent there (`omp --advisor`, plus
`--config` when `agent.ompConfig` is set; change it with
`--kind <herdr-kind> -- <agent args>`), and submits the prompt. It also routes the
agents' pushes over HTTPS through `gh`, and keeps the Mac awake for 24 hours. It
reuses the agent signing key already loaded in its private ssh-agent, and reads the
key from 1Password only when none is loaded or it has under 8 hours left.

Worktrees contain only tracked files. When the repository's instruction files point
agents at gitignored reference material (for example `docs/discogs/api/`), send each
agent its absolute path in the main checkout right after the launch
(`herdr agent prompt <agent> "<message>"`), or the agents will not find it.

Branch names follow the `git-branch` skill in every repository, whatever its
instruction files or earlier branches say: `<type>/issue-<N>-<slug>`. The type comes
from the issue's labels, the most specific one winning whatever their order: a label
named after a commit type (`feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`,
`ci`, `chore`), then `tests` → `test`, `performance` → `perf`, `documentation` →
`docs`, then `bug` → `fix` and `enhancement`/`feature` → `feat`. With none of these it
is `fix`. Between two labels of the same tier, the first in that list wins (`feat` +
`fix` gives `feat`, `bug` + `enhancement` gives `fix`). So a test-only issue labelled
`enhancement` gets `test/` once it also carries a `test` label; the dry run shows the
branch each issue will get.

A group that fails a check is reported and skipped; the others still launch.

## Signing key

Reading the agent key asks the user through 1Password, and the prompt fails after a
minute when nobody approves it. So read it only while the user is there. It then
stays loaded for 24 hours, across waves and `clean`, and every launch reuses it.

- `python3 <skill-dir>/scripts/parallel_issues.py key` prints when the key expires
  and until when launches reuse it (8 hours before it expires). A launch after that
  reads the key again.
- Before ending a turn with "You can go AFK", run `key`. When a launch the plan still
  needs may come after that time, or no key is loaded, run `key --load` first, while
  the user is there: it reads the key and restarts its 24 hours.
- `key --unload` removes the key. Run it only when no agent is working.
- This session's own git commands that sign or reach GitHub (commit, fetch, pull,
  push, `gh stack` commands that push) also use the agent key and HTTPS, never the
  user's SSH agent, which asks for an approval that cannot come while they are away.
  Run them in a subshell with the launcher's environment, assigned first so that a
  failed `env` stops the command. `env` never prompts; it fails when no key is loaded.

  ```shell
  ( e=$(python3 <skill-dir>/scripts/parallel_issues.py env) && eval "$e" && git push )
  ```

## While it runs

- Right after the launch, and after every relaunch or message to an agent, start
  `parallel_issues.py status --wait --no-notify` as a background job with no time
  limit. After a message, first wait until that agent works again
  (`herdr agent wait <agent> --until working --timeout 15000`). The watcher polls
  every 30 seconds and exits as soon as a group changes to a state not reported yet:
  `needs-you` (Herdr reports the agent blocked, or it finished and its last closing
  line starts with "This needs you"), `done` (agent finished, every branch recorded at
  the current pull request head), `stopped` (finished without recording everything),
  or `gone`. A closing line counts only at the start of a line, so a message to an
  agent may quote the two closing sentences mid-line but must never start a line with
  one. A group is reported `done` only once it has stayed done for two minutes: the
  agent's final reviewer posts its concern up to about 100 seconds after the agent
  finishes, and a concern starts one more turn. Until then a report lists it as
  `settling`; start the watcher again to get its state. A group that stays blocked is
  reported once; one that resumes counts as working again and is reported when it
  next stops. On exit it prints every group's state, and runs `agent.notifyCommand`
  unless `--no-notify` is given. Exit code 3 means nothing is running and nothing new
  happened. A failed poll (a GitHub outage or rate limit, a Herdr error) is retried
  with a growing pause; exit code 1 means polls kept failing for 30 minutes, so check
  `gh` and Herdr before starting it again.
- When the watcher exits with a report, check the reported pull requests (checks,
  review state), report to the user without waiting to be asked, and start the watcher
  again while any group is still working.
- Detect that agents finished only with this watcher, never with `herdr agent wait`
  or a status loop of your own. Herdr reports a finished agent as `idle`, not `done`,
  and `herdr agent wait` matches the state it observes, so it can return at once on
  an agent that has not started yet or never return for one already finished. The
  watcher checks before it sleeps and uses the launcher's states. Use
  `herdr agent wait --until working` only for the step above: confirming that a
  messaged agent resumed.
- `parallel_issues.py status` prints the same states once. `herdr agent read <agent>
  --source recent-unwrapped --lines 120` shows an agent's recent output.
- Each agent ends by running `parallel_issues.py record`. It fails unless GitHub shows
  every commit of each pull request as verified, since the default branch's ruleset
  does not cover pull request branches. Otherwise it stores the commit each pull
  request was opened with, which `clean` relies on. A `gh` call that fails
  transiently (a rate limit, an HTTP 5xx, a timeout) is retried like a failed poll,
  for up to 30 minutes, so one `record` call is enough. `status` shows a group whose
  agent stopped without recording.

## After the run

1. **Review.** Each pull request gets the spec check the `github-workflow` skill
   describes. Run the checks from this session as `task` subagents, one per pull
   request or stack, launched in one batch. The pre-commit reviewer already looked for
   defects; the spec check asks whether the delivery matches the issue, and a batch of
   `reviewer` subagents would spend the costly model that agent defaults to. Changes
   to a lower layer go back to the group's agent, or are made in an interactive
   session, as the `git-commit` skill describes (Updating Layers).
2. **Merge.** Merge as the `github-workflow` skill describes. When several pull requests
   are ready, suggest merging them in one request; never require it. On a repository
   that squash-merges, merge a single pull request with `gh pr merge <n> --squash`,
   and a whole stack by running `gh stack merge --yes --squash` with no number from the
   group's worktree, where the stack is checked out. GitHub signs the squash commits
   and rebases what is left of a partly merged stack. GitHub's **Rebase and merge**
   button fails on a repository that requires signed commits; that is expected.

   Every merge moves `main`, so check the next pull request with
   `gh pr view <n> --json mergeStateStatus` before merging it. While it reads
   `UNKNOWN`, GitHub is still computing it after the previous merge: query again a few
   seconds later until it changes. Act on the value it settles on:
   - **`BEHIND`, on a repository whose ruleset requires up-to-date branches:** run
     `gh pr update-branch <n>` for a single pull request. GitHub adds a merge commit
     that it signs, and the squash drops it. A stacked pull request refuses it (HTTP
     403); treat it as the next case. Without that ruleset, `BEHIND` needs nothing.
   - **`DIRTY` (a conflict), or a stack that must be updated, on a squash-merging
     repository:** hand it back to its agent, since only the agent's key may sign its
     commits. Tell it to fetch `main` over HTTPS, merge it into the bottom branch,
     then merge each layer into the next one up, and push normally: no rebase, no
     force push, so no decision from the user.
   - **A repository that fast-forwards** (rebase merges only, signed commits
     required): every merge after the first needs the next branch rebased by its
     agent and force pushed, which needs the user's agreement. Suggest enabling squash
     merges to the user instead.

   When you hand a branch back, tell the agent to rerun the repository's checks on
   every layer it changed. When there were conflicts, it also has a fresh reviewer
   check only the resolutions (`git show --remerge-diff <merge>`, or `git range-diff`
   against the old head after a rebase); an update without conflicts gets no review.
   Hand a group its update only after the merges already decided for other groups
   have landed, so one round covers them all.
3. **Clean.** Run it from the main checkout's Herdr workspace, never from an agent's
   workspace, once no agent is working: `clean --dry-run`, then `clean`. Never remove a
   worktree, branch, or workspace by hand: that leaves the Herdr workspace and its idle
   agent behind, and neither caffeinate nor the signing agent is stopped. First,
   `clean` fetches with `--prune` and prunes worktrees whose directory is gone. Then,
   for every group whose pull requests are all merged, it:
   1. removes the worktree through Herdr and closes its workspace, which stops the
      agent, even when the worktree is already gone;
   2. deletes the local branches and their `origin` branches, if GitHub has not
      already deleted them;
   3. drops the group from the launcher's state.

   It then removes Herdr's empty worktree directory for the repository. Once no group
   of the repository is left, it stops the caffeinate processes its launches started.
   It stops the ssh-agent holding the signing key only once the key has expired and
   no other repository's run still records that agent: a loaded key stays for the
   next wave, and `clean` prints until when. Agents keep their scratch files in their
   worktree's git directory, so nothing outside the worktree needs removing.

   A group is kept, with the reason printed, when:
   - a pull request is not merged or the group was never recorded;
   - a branch, local or on `origin`, is at a commit its merged pull request did not
     merge, such as a follow-up pushed after the merge;
   - the worktree has uncommitted changes or another branch checked out;
   - its agent is still working;
   - another Herdr workspace uses it, or `clean` runs inside its workspace;
   - it was launched in another Herdr session.

   A `leftover` is something a launch created that no recorded group accounts for,
   usually the trace of a cleanup done by hand:
   - a workspace labelled like a launch;
   - an issue worktree;
   - an issue branch, local or on `origin`, whose pull request merged, either still
     at the merged commit or carrying commits the merge did not include;
   - once no group is left, a caffeinate or signing ssh-agent a launch started that no
     run records, which includes launches made before the launcher recorded them.

   `clean` exits nonzero while it prints any `keep`, `FAILED`, or `leftover` line.
   Resolve each line with the user, then run `clean` again until it exits 0.

## What the safeguards do not cover

The agents act as the user on GitHub. The launcher's issue checks and the prompt's
instructions not to read comments or follow linked pages reduce what can steer an
agent, but an agent that ignores its prompt can still do anything the user's `gh` login
allows, including pushing a workflow that runs with the repository's Actions secrets.
The signing key cannot push or log in; it can only make commits that verify, until it
expires or is removed from GitHub.
