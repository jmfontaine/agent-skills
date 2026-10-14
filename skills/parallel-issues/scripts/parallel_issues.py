#!/usr/bin/env python3
"""Run one coding agent per group of GitHub issues, each group as a stack of PRs.

    parallel_issues.py launch --dry-run 14,27 13
    parallel_issues.py launch 14,27 13 [--kind omp] [-- AGENT_ARGS...]
    parallel_issues.py record          # run by the agent, inside its worktree
    parallel_issues.py status [--wait [--interval SECONDS] [--timeout HOURS] | --ack]
    parallel_issues.py clean [--dry-run]

Each ``launch`` argument is a group: comma-separated issue numbers, bottom of the
stack first. Run ``launch``, ``status`` and ``clean`` from a Herdr pane inside a
clone of the GitHub repository.

``launch`` refuses issues that are not open, not written by the authenticated
GitHub user, or edited by anyone else. For each group it creates a Herdr-managed
worktree on the first issue's branch, starts the agent there with
``assets/prompt.md``, and records the group in
``<git common dir>/parallel-issues.json``.
The issue text and the user's own comments go into the prompt; nothing else from
the issue does.

Agents run unattended, so ``launch`` prepares everything that would prompt:

- Signing, which is mandatory. ``commit.gpgsign`` must be true, and git config
  ``agent.signingKey`` must hold a 1Password reference (``op://...``) to an SSH
  private key whose public key is in ``gpg.ssh.allowedSignersFile`` for the
  repository's ``user.email``. The key is loaded into a private ssh-agent for
  ``KEY_HOURS``; agents sign through ``ssh-keygen``, and the key is never written
  to disk.
- Pushing. Agents reach GitHub over HTTPS through ``gh auth git-credential``.
- Sleep. On macOS, ``caffeinate -i`` keeps the machine awake for ``KEY_HOURS``.

Each launch records its caffeinate process and ssh-agent socket in
``STATE_DIR/RUNS_FILE`` so that ``clean`` can stop them.

Every check fails hard: an issue that fails one is not launched.

``record`` stores, for each branch of the agent's group, the PR number and the
commit that PR was opened with, but only when the PR's head on GitHub equals the
local branch and GitHub shows every commit of the PR as verified; otherwise it exits
nonzero. The default branch's ruleset does not cover PR branches, so this is the
check that catches an unverified commit before review.

``clean`` removes a merged group's worktree, closes its Herdr workspace (stopping
its agent) even when the worktree is already gone, deletes its local and ``origin``
branches, and drops it from the state. A branch is deleted only at the commit
``record`` stored or the head its pull request was merged with; any other commit,
an unmerged pull request, uncommitted changes, a working agent, or a workspace in
use keeps the group. Once no group of the repository is left, it stops the
recorded caffeinate processes and the signing ssh-agent unless another
repository's run records it. It then reports, as leftovers, launch workspaces,
issue worktrees and merged issue branches that no group accounts for, and exits
nonzero while anything is kept or left over.

``status`` classifies each group launched in this Herdr session as ``working``,
``needs-you`` (Herdr reports the agent blocked, or its recent output says "This
needs you", even when everything is recorded), ``done`` (Herdr reports it idle or
done, every branch recorded, and its PR merged or still at the recorded commit),
``stopped`` (any other agent state, or work unrecorded) or ``gone``
(no Herdr agent of that name). ``status --wait`` polls until a group that is not
working has a state its last report did not cover, prints the report, marks it
acknowledged and exits 0. A group seen working loses its acknowledgement, so its next
idle state is always reported. It exits 2 on timeout, and 3 when two polls, the
second ``IDLE_RECHECK`` seconds after the first, find nothing working and nothing
new (the pause covers a watcher started just after messaging an agent). A poll that
fails (``gh`` or Herdr erroring) is reported on stderr and retried, each pause twice
the last up to ``FAILED_POLL_MAX_PAUSE`` (never shorter than the interval); once polls
have failed in a row for ``FAILED_POLL_LIMIT`` seconds it exits 1 with the last error.
``status --ack`` acknowledges the current state without waiting. After a ``--wait``
report, git config ``agent.notifyCommand`` is run (``NOTIFY_TIMEOUT`` seconds at
most) with the title as its last argument and the report on stdin, unless
``--no-notify`` is given: a session supervising the run reports to the user itself.
``notify TITLE`` runs the same command with ``TITLE`` (prefixed with the repository
name) and standard input as the message, so that session can tell the user when it
needs them; it exits 1 when the command is not set or fails.

``launch`` of an ``omp`` agent adds ``--config <file>`` for git config
``agent.ompConfig`` (an omp config overlay) unless the agent arguments have one.

Python 3.10+, standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from collections.abc import Generator
from pathlib import Path
from string import Template
from typing import Any

USAGE = "Run one coding agent per group of GitHub issues, each group as a stack."
SCRIPT = Path(__file__).resolve()
PROMPT_TEMPLATE = SCRIPT.parent.parent / "assets" / "prompt.md"
STATE_FILE = "parallel-issues.json"
RUNS_FILE = "parallel-issues-runs.json"
# Branch names the launcher creates (see branch_prefix and slugify).
ISSUE_BRANCH = re.compile(r"[a-z]+/issue-\d+-[a-z0-9-]*")
REQUIRED_TOOLS = ("git", "gh", "herdr")
# Herdr agent kinds take the agent's own CLI flags after `--`.
DEFAULT_AGENT_ARGS = {"omp": ["--advisor"]}
# Branches follow the git-branch skill: <type>/issue-<N>-<slug>, where <type> is the
# Conventional Commits type of the change. An issue's labels are the only type signal
# the launcher has. They are matched most specific first, so the result never depends
# on the order GitHub lists them in: a label named after a commit type, then a label
# that stands for one type, then GitHub's generic defaults.
COMMIT_TYPES = (
    "feat",
    "fix",
    "docs",
    "test",
    "refactor",
    "perf",
    "build",
    "ci",
    "chore",
)
LABEL_PREFIXES = (
    *((commit_type, commit_type) for commit_type in COMMIT_TYPES),
    ("tests", "test"),
    ("performance", "perf"),
    ("documentation", "docs"),
    ("bug", "fix"),
    ("enhancement", "feat"),
    ("feature", "feat"),
)
DEFAULT_PREFIX = "fix"
SLUG_WORDS = 4
STOPWORDS = frozenset(
    {"a", "an", "and", "at", "by", "for", "from", "in", "is", "it", "of", "on"}
    | {"or", "so", "the", "to", "when", "with"}
)
AGENT_NAME_MAX = 32  # Herdr: [a-z][a-z0-9_-]{0,31}
AGENT_START_TIMEOUT_MS = "60000"
# A new pane's shell may still be starting (direnv, a slow rc file) when the agent is
# started; Herdr then answers `agent_pane_busy`. Retry for this long.
PANE_READY_SECONDS = 30.0
PANE_READY_PAUSE = 1.0
MAX_ITEMS = 100  # issue comments and edits fetched in one query
SIGNING_KEY_SETTING = "agent.signingKey"
KEY_HOURS = 12
# Seconds between polls of `status --wait`. A poll is one `gh pr list` per recorded
# branch, one Herdr agent list, and one output read per agent that is not working,
# so the supervising session learns that an agent finished within this many seconds.
# At 30 branches that is 3,600 GitHub API calls an hour, within the 5,000 allowed.
WAIT_INTERVAL = 30.0
WAIT_TIMEOUT_HOURS = 13.0
EXIT_TIMEOUT = 2
EXIT_NOTHING_TO_WAIT = 3
EXIT_POLL_FAILED = 1
# GitHub outages and rate limits (secondary limits included) usually clear within
# minutes; a watcher that gives up sooner needs a restart by hand.
FAILED_POLL_LIMIT = 30 * 60.0  # seconds of failing polls before exit 1
FAILED_POLL_MAX_PAUSE = 300.0  # longest pause between failing polls
IDLE_RECHECK = 30.0  # seconds before exit 3 is confirmed
NOTIFY_TIMEOUT = 30  # seconds the notify command may run
READ_LINES = "120"  # recent agent output searched for NEEDS_YOU
NEEDS_YOU = "This needs you"
# Herdr agent states after a turn ends. `blocked` means the agent waits for input
# or hit a provider failure; any other unknown state is never treated as finished.
FINISHED_STATUSES = {"idle", "done"}
BLOCKED_STATUS = "blocked"
HEAD_MOVED = "PR head moved since record"
# Report order and wording of the notification title.
STATE_LABELS = {
    "done": "done",
    "needs-you": "needs you",
    "stopped": "stopped",
    "gone": "gone",
}
NOTIFY_SETTING = "agent.notifyCommand"
OMP_CONFIG_SETTING = "agent.ompConfig"
STATE_DIR = (
    Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "agent"
)
ISSUE_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    issue(number: $number) {
      title state body
      author { login }
      labels(first: 20) { nodes { name } }
      userContentEdits(first: 100) { totalCount nodes { editor { login } } }
      comments(first: 100) { totalCount nodes { author { login } body } }
    }
  }
}
"""


class StepError(Exception):
    """A check or command failed; for one group, the other groups still run."""


def run(
    args: list[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    stdin: str | None = None,
) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise StepError(f"`{' '.join(args[:4])}` exited {result.returncode}: {detail}")
    return result.stdout


def run_json(args: list[str], *, cwd: str | None = None) -> Any:
    return json.loads(run(args, cwd=cwd))


def git_config(key: str, *, cwd: str | None = None) -> str | None:
    result = subprocess.run(
        ["git", "config", "--get", key],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or None


class Herdr:
    def __init__(self, session: str | None) -> None:
        self.session = session
        self._prefix = ["herdr", "--session", session] if session else ["herdr"]

    def call(self, *args: str) -> dict[str, Any]:
        return run_json([*self._prefix, *args])["result"]

    def read(self, agent: str) -> str:
        """The agent's recent terminal output; unlike ``call``, plain text."""
        return run(
            [
                *self._prefix,
                *("agent", "read", agent, "--source", "recent-unwrapped"),
                *("--lines", READ_LINES),
            ]
        )


def common_dir() -> str:
    return run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"]
    ).strip()


@contextlib.contextmanager
def locked_json(path: Path) -> Generator[dict[str, Any], None, None]:
    """Yield the JSON object in ``path`` under an exclusive lock, then save it.

    Several agents may run ``record`` at once, so every change is a locked
    read-modify-write of the whole file.
    """
    with open(path.with_suffix(".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        entries = json.loads(path.read_text()) if path.exists() else {}
        yield entries
        path.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n")


def state() -> contextlib.AbstractContextManager[dict[str, dict[str, Any]]]:
    """The recorded groups of this repository, keyed by agent name."""
    return locked_json(Path(common_dir()) / STATE_FILE)


def runs() -> contextlib.AbstractContextManager[dict[str, dict[str, Any]]]:
    """What each repository's launches left running, keyed by git common dir.

    ``caffeinate`` holds the process ids that keep the Mac awake and ``sockets`` the
    ssh-agent sockets holding the signing key. Agents of every repository share one
    ssh-agent per key, so this lives outside any one repository.
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    return locked_json(STATE_DIR / RUNS_FILE)


def slugify(title: str) -> str:
    words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOPWORDS]
    return "-".join(words[:SLUG_WORDS])


def agent_name(repo: str, number: int) -> str:
    suffix = f"-{number}"
    stem = re.sub(r"[^a-z0-9_-]+", "-", repo.lower()).strip("-_")
    if not stem[:1].isalpha():
        stem = f"r{stem}"
    return stem[: AGENT_NAME_MAX - len(suffix)].rstrip("-_") + suffix


def branch_prefix(labels: list[str]) -> str:
    names = {label.lower() for label in labels}
    return next(
        (prefix for label, prefix in LABEL_PREFIXES if label in names), DEFAULT_PREFIX
    )


def parse_groups(values: list[str]) -> list[list[int]]:
    groups, seen = [], set()
    for value in values:
        try:
            group = [int(part) for part in value.split(",")]
        except ValueError:
            raise StepError(
                f"bad group {value!r}: use issue numbers like 14,27"
            ) from None
        if len(set(group)) != len(group) or seen.intersection(group):
            raise StepError(f"issue listed twice in {' '.join(values)}")
        seen.update(group)
        groups.append(group)
    return groups


def fetch_issue(owner: str, name: str, number: int, me: str) -> dict[str, Any]:
    """Return the issue if it is safe to hand to an unattended agent."""
    data = run_json(
        ["gh", "api", "graphql", "-f", f"query={ISSUE_QUERY}"]
        + ["-F", f"owner={owner}", "-F", f"name={name}", "-F", f"number={number}"]
    )
    issue = data["data"]["repository"]["issue"]
    if issue is None:
        raise StepError(f"#{number} is not an issue")
    if issue["state"] != "OPEN":
        raise StepError(f"#{number} is {issue['state'].lower()}")
    author = (issue["author"] or {}).get("login")
    if author != me:
        raise StepError(f"#{number} was opened by {author}, not {me}")
    edits = issue["userContentEdits"]
    editors = {(e["editor"] or {}).get("login") for e in edits["nodes"]}
    if edits["totalCount"] > MAX_ITEMS or editors - {me}:
        raise StepError(f"#{number} was edited by someone other than {me}")
    comments = issue["comments"]
    if comments["totalCount"] > MAX_ITEMS:
        raise StepError(f"#{number} has over {MAX_ITEMS} comments; work on it by hand")
    issue["own_comments"] = [
        c["body"] for c in comments["nodes"] if (c["author"] or {}).get("login") == me
    ]
    return issue


def existing_branches(number: int) -> list[str]:
    patterns = [
        f"refs/heads/*/issue-{number}-*",
        f"refs/remotes/origin/*/issue-{number}-*",
    ]
    return run(["git", "for-each-ref", "--format=%(refname:short)", *patterns]).split()


def issue_block(number: int, branch: str, issue: dict[str, Any]) -> str:
    lines = [
        f"### #{number}: {issue['title']}",
        "",
        f"Branch: `{branch}`",
        "",
        "Issue text:",
        "",
        issue["body"].strip() or "(empty)",
    ]
    for index, body in enumerate(issue["own_comments"], 1):
        lines += ["", f"Comment {index} by the issue's author:", "", body.strip()]
    return "\n".join(lines)


def allowed_blobs(path: str, email: str) -> set[str]:
    """Key blobs that ``path`` (an allowed_signers file) allows for ``email``."""
    blobs = set()
    for line in Path(path).expanduser().read_text().splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if email in fields[0].split(","):
            # principals [options] keytype blob [comment]
            for i, field in enumerate(fields[1:-1], 1):
                if field.startswith(("ssh-", "ecdsa-", "sk-")):
                    blobs.add(fields[i + 1])
                    break
    return blobs


def load_signing_key(
    reference: str, email: str, allowed_signers: str
) -> tuple[str, Path]:
    """Load the key behind ``reference`` into its own ssh-agent.

    Return the public key and the agent socket. Each reference gets its own agent,
    so loading one scope's key never disturbs agents signing with another.
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    STATE_DIR.chmod(0o700)
    digest = hashlib.sha256(reference.encode()).hexdigest()[:12]
    socket = STATE_DIR / f"ssh-agent-{digest}.sock"
    env = {**os.environ, "SSH_AUTH_SOCK": str(socket)}
    probe = subprocess.run(["ssh-add", "-l"], env=env, capture_output=True, check=False)
    if probe.returncode == 2:  # 0: keys loaded, 1: running but empty, 2: no agent
        socket.unlink(missing_ok=True)
        run(["ssh-agent", "-a", str(socket)])
    # Read through the 1Password app, which can reach personal vaults, rather than
    # a service account the shell may export for other tools.
    app_env = {k: v for k, v in os.environ.items() if k != "OP_SERVICE_ACCOUNT_TOKEN"}
    key = run(["op", "read", reference], env=app_env)
    if "PRIVATE KEY" not in key:
        raise StepError(f"{SIGNING_KEY_SETTING} does not point at an SSH private key")
    # Re-adding a loaded key restarts its lifetime.
    run(["ssh-add", "-q", "-t", f"{KEY_HOURS}h", "-"], env=env, stdin=key)
    loaded = run(["ssh-add", "-L"], env=env).splitlines()
    if len(loaded) != 1:
        raise StepError(f"{socket} holds {len(loaded)} keys; expected 1")
    public = loaded[0]
    if public.split()[1] not in allowed_blobs(allowed_signers, email):
        run(["ssh-add", "-D"], env=env)  # this agent holds only this key
        raise StepError(
            f"the agent key is not in {allowed_signers} for {email}, so its"
            " signatures would not verify"
        )
    return public, socket


def agent_env(public: str, socket: Path) -> dict[str, str]:
    """Environment that lets an agent sign and push without prompting."""
    config = [
        ("url.https://github.com/.insteadOf", "git@github.com:"),
        ("url.https://github.com/.insteadOf", "ssh://git@github.com/"),
        # The empty value drops inherited helpers before adding gh's.
        ("credential.https://github.com.helper", ""),
        ("credential.https://github.com.helper", "!gh auth git-credential"),
        ("gpg.format", "ssh"),
        ("gpg.ssh.program", "ssh-keygen"),
        ("user.signingkey", f"key::{public}"),
        ("commit.gpgsign", "true"),
    ]
    env = {"SSH_AUTH_SOCK": str(socket), "GIT_CONFIG_COUNT": str(len(config))}
    for index, (key, value) in enumerate(config):
        env[f"GIT_CONFIG_KEY_{index}"] = key
        env[f"GIT_CONFIG_VALUE_{index}"] = value
    return env


def keep_awake() -> int | None:
    """Keep the Mac awake for ``KEY_HOURS``; return the process to stop afterwards."""
    if not shutil.which("caffeinate"):
        return None
    return subprocess.Popen(
        ["caffeinate", "-i", "-t", str(KEY_HOURS * 3600)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).pid


def submit(herdr: Herdr, agent: str) -> None:
    """Make sure the prompt started a turn.

    omp shows a long paste as an attachment and can leave it in the input box, so
    when no turn starts the prompt gets one more Enter. Waiting for the turn to end
    would block for hours; reaching ``working`` is enough.
    """
    for attempt in range(2):
        try:
            herdr.call(
                "agent", "wait", agent, "--until", "working", "--timeout", "15000"
            )
            return
        except StepError:
            if attempt == 0:
                herdr.call("agent", "send-keys", agent, "enter")
    raise StepError(f"{agent} did not start working after the prompt; check its pane")


def start_agent(
    herdr: Herdr, agent: str, kind: str, pane: str, agent_args: list[str]
) -> None:
    """Start ``agent`` in ``pane``, waiting while the pane's shell is still starting."""
    deadline = time.monotonic() + PANE_READY_SECONDS
    while True:
        try:
            herdr.call(
                "agent",
                "start",
                agent,
                "--kind",
                kind,
                "--pane",
                pane,
                "--timeout",
                AGENT_START_TIMEOUT_MS,
                "--",
                *agent_args,
            )
            return
        except StepError as exc:
            if "agent_pane_busy" not in str(exc) or time.monotonic() >= deadline:
                raise
            time.sleep(PANE_READY_PAUSE)


def with_omp_config(kind: str, agent_args: list[str]) -> list[str]:
    """Add the omp config overlay named by ``agent.ompConfig`` to ``agent_args``."""
    setting = git_config(OMP_CONFIG_SETTING) if kind == "omp" else None
    if not setting or any(
        arg == "--config" or arg.startswith("--config=") for arg in agent_args
    ):
        return agent_args
    path = Path(setting).expanduser().resolve()
    if not path.is_file():
        raise StepError(f"{OMP_CONFIG_SETTING} is {setting}, which is not a file")
    return [*agent_args, "--config", str(path)]


def launch(
    values: list[str], kind: str, agent_args: list[str], herdr: Herdr, dry_run: bool
) -> int:
    groups = parse_groups(values)
    agent_args = with_omp_config(kind, agent_args)
    if dry_run:
        print(f"agent command: {kind} {shlex.join(agent_args)}")
    template = Template(PROMPT_TEMPLATE.read_text())
    repo = run_json(
        ["gh", "repo", "view", "--json", "owner,name,nameWithOwner,defaultBranchRef"]
    )
    owner, name = repo["owner"]["login"], repo["name"]
    base = f"origin/{repo['defaultBranchRef']['name']}"
    me = run(["gh", "api", "user", "--jq", ".login"]).strip()
    top = run(["git", "rev-parse", "--show-toplevel"]).strip()
    run(["git", "fetch", "--quiet", "origin"])

    email = git_config("user.email")
    if not email:
        raise StepError("no user.email for this repository; check your git config")
    # Every agent commit must be signed and verify on GitHub, so there is no
    # unsigned mode: a missing piece stops the launch.
    reference = git_config(SIGNING_KEY_SETTING)
    allowed_signers = git_config("gpg.ssh.allowedSignersFile")
    if git_config("commit.gpgsign") != "true" or not reference or not allowed_signers:
        raise StepError(
            f"agents sign every commit: set commit.gpgsign=true, {SIGNING_KEY_SETTING}"
            " and gpg.ssh.allowedSignersFile for this repository"
        )
    live_agents: set[str] = set()
    env_flags: list[str] = []
    if not dry_run:
        public, socket = load_signing_key(reference, email, allowed_signers)
        env_flags = [
            flag
            for key, value in agent_env(public, socket).items()
            for flag in ("--env", f"{key}={value}")
        ]
        live_agents = {a.get("name") for a in herdr.call("agent", "list")["agents"]}
        awake = keep_awake()
        # Recorded so that `clean` can stop both once this repository's groups are
        # gone, instead of leaving them to their timeouts.
        with runs() as recorded:
            mine = recorded.setdefault(common_dir(), {"caffeinate": [], "sockets": []})
            if awake:
                mine["caffeinate"].append(awake)
            if str(socket) not in mine["sockets"]:
                mine["sockets"].append(str(socket))

    failures = 0
    for group in groups:
        label = ",".join(f"#{n}" for n in group)
        try:
            branches, blocks = [], []
            for number in group:
                issue = fetch_issue(owner, name, number, me)
                if taken := existing_branches(number):
                    raise StepError(f"#{number} already has {', '.join(taken)}")
                prefix = branch_prefix([n["name"] for n in issue["labels"]["nodes"]])
                branch = f"{prefix}/issue-{number}-{slugify(issue['title'])}"
                branches.append(branch)
                blocks.append(issue_block(number, branch, issue))
            agent = agent_name(name, group[0])
            if agent in live_agents:
                raise StepError(f"a live Herdr agent is already named {agent}")
            with state() as entries:
                if agent in entries:
                    raise StepError(f"{agent} is already recorded; run clean first")
            prompt = template.substitute(
                repo=repo["nameWithOwner"],
                base=base,
                trunk=repo["defaultBranchRef"]["name"],
                email=email,
                branches=", ".join(f"`{b}`" for b in branches),
                bottom=branches[0],
                issues="\n\n".join(blocks),
                record=f"python3 {SCRIPT} record",
            )
            if dry_run:
                print(f"{label}: would create {branches[0]} from {base}, agent {agent}")
                print("-" * 72, prompt.rstrip(), "-" * 72, sep="\n")
                continue

            workspace_label = f"{name} {label}"
            created = herdr.call(
                "worktree",
                "create",
                "--cwd",
                top,
                "--branch",
                branches[0],
                "--base",
                base,
                "--label",
                workspace_label,
                "--no-focus",
            )
            workspace = created["workspace"]
            path = os.path.realpath(workspace["worktree"]["checkout_path"])
            with state() as entries:
                entries[agent] = {
                    "issues": group,
                    "branches": branches,
                    "path": path,
                    "workspace_id": workspace["workspace_id"],
                    "label": workspace_label,
                    "herdr_session": herdr.session,
                    "submitted": {},
                }
            # A failure from here on leaves the recorded worktree for inspection.
            # `worktree create` takes no environment, so the agent runs in a pane
            # split with one, and the original pane goes away.
            root_pane = created["root_pane"]["pane_id"]
            pane = herdr.call(
                "pane",
                "split",
                root_pane,
                "--direction",
                "right",
                "--cwd",
                path,
                *env_flags,
                "--no-focus",
            )["pane"]["pane_id"]
            herdr.call("pane", "close", root_pane)
            start_agent(herdr, agent, kind, pane, agent_args)
            herdr.call("agent", "prompt", agent, prompt)
            submit(herdr, agent)
            live_agents.add(agent)
            print(f"{label}: {agent} started on {branches[0]}")
        except StepError as exc:
            failures += 1
            print(f"{label}: FAILED: {exc}", file=sys.stderr)
    return 1 if failures else 0


def ref_head(ref: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or None


def branch_head(branch: str) -> str | None:
    return ref_head(f"refs/heads/{branch}")


def unverified_commits(repo: str, number: int) -> list[str]:
    """Commits of pull request ``number`` that GitHub does not show as verified.

    GitHub lists at most 250 commits of a pull request, so a longer one cannot be
    checked this way and counts as unverified.
    """
    total = int(run(["gh", "api", f"repos/{repo}/pulls/{number}", "--jq", ".commits"]))
    lines = run(
        ["gh", "api", "--paginate", f"repos/{repo}/pulls/{number}/commits"]
        + [
            "--jq",
            '.[] | "\\(.sha[0:7]) \\(.commit.verification.verified)'
            ' \\(.commit.verification.reason)"',
        ]
    ).splitlines()
    if len(lines) != total:
        return [f"only {len(lines)} of {total} commits could be checked"]
    return [
        f"{sha} {reason}"
        for sha, verified, reason in (line.split(" ", 2) for line in lines)
        if verified != "true"
    ]


def record() -> int:
    top = os.path.realpath(run(["git", "rev-parse", "--show-toplevel"]).strip())
    repo = run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]
    )
    with state() as entries:
        found = [(a, e) for a, e in entries.items() if e["path"] == top]
        if not found:
            raise StepError(f"{top} is not a recorded worktree")
        entry = found[0][1]
        problems = 0
        for branch in entry["branches"]:
            head = branch_head(branch)
            prs = run_json(
                ["gh", "pr", "list", "--head", branch, "--state", "open"]
                + ["--json", "number,headRefOid,url"]
            )
            if head is None or not prs:
                print(f"not submitted  {branch}")
                continue
            pr = prs[0]
            if pr["headRefOid"] != head:
                problems += 1
                print(f"MISMATCH       {branch}: local {head[:7]}, PR {pr['url']}")
                continue
            # Only the default branch's ruleset rejects unsigned pushes, so a
            # pull request branch has to be checked commit by commit.
            if bad := unverified_commits(repo.strip(), pr["number"]):
                problems += 1
                print(f"UNVERIFIED     {branch} {pr['url']}: {'; '.join(bad)}")
                continue
            entry["submitted"][branch] = {"pr": pr["number"], "oid": head}
            print(f"recorded       {branch} {head[:7]} {pr['url']}")
    return 1 if problems else 0


def branch_report(branch: str, entry: dict[str, Any]) -> dict[str, Any]:
    """What GitHub shows for ``branch``, against what ``record`` stored for it.

    ``submitted`` means the recorded PR is merged, or open at the recorded commit.
    An open PR that has moved on counts too when the local branch is still at the
    recorded commit: GitHub rebased the layer after a partial stack merge, and the
    agent did not push.
    """
    recorded = entry["submitted"].get(branch)
    prs = run_json(
        ["gh", "pr", "list", "--head", branch, "--state", "all"]
        + ["--json", "number,state,url,headRefOid"]
    )
    wanted = recorded["pr"] if recorded else None
    pr = (
        next((p for p in prs if p["number"] == wanted), None)
        or next((p for p in prs if p["state"] == "OPEN"), None)
        or next(iter(prs), None)
    )
    submitted, note = False, None
    if recorded and pr and pr["number"] == recorded["pr"]:
        if pr["state"] == "MERGED":
            submitted = True
        elif pr["state"] == "OPEN":
            moved = pr["headRefOid"] != recorded["oid"]
            note = HEAD_MOVED if moved else None
            submitted = not moved or branch_head(branch) == recorded["oid"]
    return {
        "branch": branch,
        "recorded": bool(recorded),
        "oid": recorded["oid"] if recorded else None,
        "pr": pr["number"] if pr else None,
        "pr_state": pr["state"] if pr else None,
        "pr_head": pr["headRefOid"] if pr else None,
        "url": pr["url"] if pr else None,
        "submitted": submitted,
        "note": note,
    }


def inspect_group(
    agent: str, entry: dict[str, Any], live: dict[str, Any] | None, herdr: Herdr
) -> dict[str, Any]:
    """Classify one group; ``signature`` identifies its state for acknowledging.

    A working agent is never ``done``, whatever was recorded before it resumed, and
    neither is a blocked one: Herdr reports ``blocked`` when the agent waits for the
    user or a provider failed, so it needs the user even if its old records are
    complete. Only an agent Herdr reports as finished can be ``done``.
    """
    branches = [branch_report(branch, entry) for branch in entry["branches"]]
    agent_status = live.get("agent_status") if live else None
    if live is None:
        state_name = "gone"
    elif agent_status == "working":
        state_name = "working"
    elif agent_status == BLOCKED_STATUS or NEEDS_YOU in herdr.read(agent):
        state_name = "needs-you"
    elif agent_status in FINISHED_STATUSES and all(b["submitted"] for b in branches):
        state_name = "done"
    else:
        state_name = "stopped"
    signature = {
        "state": state_name,
        "branches": [
            [b["branch"], b["oid"], b["pr"], b["pr_state"], b["pr_head"]]
            for b in branches
        ],
    }
    return {"state": state_name, "branches": branches, "signature": signature}


def recorded_groups() -> dict[str, dict[str, Any]]:
    with state() as entries:
        return dict(entries)


def inspect_groups(
    herdr: Herdr, groups: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Report on the groups launched in this Herdr session, by issue order."""
    agents = {a.get("name"): a for a in herdr.call("agent", "list")["agents"]}
    return {
        agent: inspect_group(agent, entry, agents.get(agent), herdr)
        for agent, entry in sorted(groups.items(), key=lambda item: item[1]["issues"])
        if entry.get("herdr_session") == herdr.session
    }


def render(reports: dict[str, dict[str, Any]], changed: set[str]) -> str:
    lines = []
    for agent, report in reports.items():
        lines.append(
            f"{agent}: {report['state']}{' (changed)' if agent in changed else ''}"
        )
        for b in report["branches"]:
            pr = f"{b['pr_state'].lower()} {b['url']}" if b["pr"] else "no PR"
            recorded = "recorded" if b["recorded"] else "not recorded"
            note = f"; {b['note']}" if b["note"] else ""
            lines.append(f"  {b['branch']}: {pr} ({recorded}{note})")
    return "\n".join(lines)


def acknowledge(reports: dict[str, dict[str, Any]]) -> None:
    """Store each group's current signature as the one the reader has seen."""
    with state() as entries:
        for agent, report in reports.items():
            if agent in entries:
                entries[agent]["acknowledged"] = report["signature"]


def run_notify_command(title: str, text: str) -> str | None:
    """Run ``agent.notifyCommand`` with ``title`` and ``text``; return the problem."""
    setting = git_config(NOTIFY_SETTING)
    if not setting:
        return f"{NOTIFY_SETTING} is not set"
    try:
        command = shlex.split(setting)
        command[0] = os.path.expanduser(command[0])
        result = subprocess.run(
            [*command, title],
            input=text,
            capture_output=True,
            text=True,
            check=False,
            timeout=NOTIFY_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"{NOTIFY_SETTING} timed out after {NOTIFY_TIMEOUT} s"
    except (OSError, ValueError, IndexError) as exc:
        return f"{NOTIFY_SETTING} could not run: {exc}"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return f"{NOTIFY_SETTING} exited {result.returncode}: {detail}"
    return None


def notify(reports: dict[str, dict[str, Any]], changed: set[str], text: str) -> None:
    """Send a ``status --wait`` report, titled with a count of the changed states."""
    if not git_config(NOTIFY_SETTING):
        return
    counts = [reports[agent]["state"] for agent in changed]
    summary = ", ".join(
        f"{counts.count(name)} {label}"
        for name, label in STATE_LABELS.items()
        if name in counts
    )
    if problem := run_notify_command(
        f"{Path(common_dir()).parent.name}: {summary}", text
    ):
        print(f"warning: {problem}", file=sys.stderr)


def notify_user(title: str) -> int:
    """Send ``title`` and standard input through ``agent.notifyCommand``."""
    text = sys.stdin.read() if not sys.stdin.isatty() else ""
    problem = run_notify_command(f"{Path(common_dir()).parent.name}: {title}", text)
    if problem:
        print(f"FAILED: {problem}", file=sys.stderr)
        return 1
    return 0


def poll(
    herdr: Herdr,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Return (recorded groups, their reports); forget acknowledgements of workers.

    A group seen working has moved on, so the state it ends in is news even when it
    equals the one that was acknowledged.
    """
    groups = recorded_groups()
    reports = inspect_groups(herdr, groups)
    resumed = [
        agent
        for agent, report in reports.items()
        if report["state"] == "working" and "acknowledged" in groups[agent]
    ]
    if resumed:
        with state() as entries:
            for agent in resumed:
                if agent in entries:
                    entries[agent].pop("acknowledged", None)
        for agent in resumed:
            groups[agent].pop("acknowledged", None)
    return groups, reports


def wait_for_change(
    herdr: Herdr, interval: float, hours: float, send_notification: bool
) -> int:
    """Poll until a group that is not working has a state nobody was told about.

    Exits ``EXIT_NOTHING_TO_WAIT`` once two polls in a row, the second
    ``IDLE_RECHECK`` seconds after the first, find nothing working and nothing new:
    an agent just messaged may not show as working yet, and a watcher started again
    after a finished run must not spin. Polls that fail are retried with a growing
    pause; once they have failed in a row for ``FAILED_POLL_LIMIT`` seconds, the last
    error ends the wait.
    """
    deadline = time.monotonic() + hours * 3600
    idle_polls = failed_polls = 0
    failing_since = 0.0
    while True:
        pause = interval
        try:
            groups, reports = poll(herdr)
        except StepError as exc:
            if not failed_polls:
                failing_since = time.monotonic()
            failed_polls += 1
            idle_polls = 0
            failing_for = time.monotonic() - failing_since
            print(
                f"warning: poll failed ({failed_polls} in a row, "
                f"{failing_for // 60:.0f} of {FAILED_POLL_LIMIT / 60:.0f} min): {exc}",
                file=sys.stderr,
            )
            if failing_for >= FAILED_POLL_LIMIT:
                print(f"FAILED: {exc}", file=sys.stderr)
                return EXIT_POLL_FAILED
            # Never retry sooner than a healthy poll would run.
            pause = min(
                interval * 2 ** (failed_polls - 1),
                max(interval, FAILED_POLL_MAX_PAUSE),
            )
        else:
            failed_polls = 0
            changed = {
                agent
                for agent, report in reports.items()
                if report["state"] != "working"
                and report["signature"] != groups[agent].get("acknowledged")
            }
            if changed:
                text = render(reports, changed)
                print(text)
                acknowledge(reports)
                if send_notification:
                    notify(reports, changed, text)
                return 0
            if any(report["state"] == "working" for report in reports.values()):
                idle_polls = 0
            else:
                idle_polls += 1
                if idle_polls >= 2:
                    print(
                        "Nothing to wait for: no agent is working and nothing is new."
                    )
                    return EXIT_NOTHING_TO_WAIT
                pause = min(interval, IDLE_RECHECK)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print(f"Timed out after {hours:g} h; nothing new.")
            return EXIT_TIMEOUT
        time.sleep(min(pause, remaining))


def status(herdr: Herdr, ack: bool) -> int:
    groups = recorded_groups()
    if not groups:
        print("No recorded groups.")
        return 0
    reports = inspect_groups(herdr, groups)
    for agent, entry in sorted(groups.items(), key=lambda item: item[1]["issues"]):
        if agent not in reports:
            print(f"{agent}: launched in Herdr session {entry.get('herdr_session')}")
    if reports:
        print(render(reports, set()))
    if ack:
        acknowledge(reports)
        print(f"Acknowledged {len(reports)} group(s).")
    return 0


def inside(path: str | None, root: str) -> bool:
    if not path:
        return False
    real = os.path.realpath(path)
    return real == root or real.startswith(root + os.sep)


def worktree_branches() -> dict[str, str]:
    """Map each worktree path to the branch checked out there."""
    found, path = {}, ""
    for line in run(["git", "worktree", "list", "--porcelain"]).splitlines():
        if line.startswith("worktree "):
            path = os.path.realpath(line.removeprefix("worktree "))
        elif line.startswith("branch refs/heads/"):
            found[path] = line.removeprefix("branch refs/heads/")
    return found


def blockers(
    agent: str,
    entry: dict[str, Any],
    herdr: Herdr,
    worktrees: dict[str, str],
    panes: list[dict[str, Any]],
    workspaces: dict[str, dict[str, Any]],
    agents: dict[str | None, dict[str, Any]],
) -> tuple[list[str], str | None, dict[str, set[str]]]:
    """Return (reasons to keep the group, owned workspace id, removable heads).

    A branch, local or on origin, may be deleted only at a commit its merged pull
    request accounts for: the one ``record`` stored, or the head the pull request
    was merged with. Anything else is work that would be lost.
    """
    if entry.get("herdr_session") != herdr.session:
        return [f"launched in Herdr session {entry.get('herdr_session')}"], None, {}
    reasons, removable = [], {}
    for branch in entry["branches"]:
        heads = {branch: branch_head(branch), f"origin/{branch}": remote_head(branch)}
        if not any(heads.values()):
            continue
        submitted = entry["submitted"].get(branch)
        if not submitted:
            reasons.append(f"{branch}: not recorded as submitted")
            continue
        pr = run_json(
            ["gh", "pr", "view", str(submitted["pr"]), "--json", "state,headRefOid"]
        )
        if pr["state"] != "MERGED":
            reasons.append(f"{branch}: PR #{submitted['pr']} is {pr['state'].lower()}")
            continue
        removable[branch] = {submitted["oid"], pr["headRefOid"]}
        for name, head in heads.items():
            if head and head not in removable[branch]:
                reasons.append(
                    f"{name} is at {head[:7]}, a commit PR #{submitted['pr']} did not"
                    " merge"
                )

    path = entry["path"]
    if path in worktrees:
        if worktrees[path] not in entry["branches"]:
            reasons.append(f"worktree has {worktrees[path]} checked out")
        elif os.path.isdir(path) and run(["git", "status", "--porcelain"], cwd=path):
            reasons.append("worktree has uncommitted changes")
    # The workspace is owned whether or not its worktree still exists: removing a
    # worktree by hand leaves the workspace, and the agent in it, behind.
    workspace = workspaces.get(entry["workspace_id"])
    checkout = ((workspace or {}).get("worktree") or {}).get("checkout_path")
    owned = None
    if (
        workspace
        and workspace.get("label") == entry["label"]
        and inside(checkout, path)
    ):
        owned = entry["workspace_id"]
    if owned and owned == os.environ.get("HERDR_WORKSPACE_ID"):
        reasons.append(
            f"clean runs inside its Herdr workspace {owned}; run it from the main"
            " checkout's workspace"
        )
    live = agents.get(agent)
    if live and live.get("agent_status") in {"working", BLOCKED_STATUS}:
        reasons.append(f"agent {agent} is still {live['agent_status']}")
    others = sorted(
        {
            p["workspace_id"]
            for p in panes
            if p["workspace_id"] != owned
            and (inside(p.get("cwd"), path) or inside(p.get("foreground_cwd"), path))
        }
    )
    if others:
        reasons.append(f"worktree is in use by Herdr workspace {', '.join(others)}")
    return reasons, owned, removable


def remote_head(branch: str) -> str | None:
    return ref_head(f"refs/remotes/origin/{branch}")


def open_workspaces(herdr: Herdr) -> dict[str, dict[str, Any]]:
    return {w["workspace_id"]: w for w in herdr.call("workspace", "list")["workspaces"]}


def remove_group(
    entry: dict[str, Any],
    herdr: Herdr,
    worktrees: dict[str, str],
    owned: str | None,
    removable: dict[str, set[str]],
) -> None:
    """Remove the worktree, close the workspace and its agent, delete the branches."""
    path = entry["path"]
    if path in worktrees:
        if owned:
            # Refuses a dirty worktree, and then leaves the workspace open.
            herdr.call("worktree", "remove", "--workspace", owned)
        else:
            run(["git", "worktree", "remove", path])
    if owned and owned in open_workspaces(herdr):
        herdr.call("workspace", "close", owned)
    for branch, allowed in removable.items():
        # The agent may have committed or pushed before its workspace closed.
        if (head := branch_head(branch)) is not None:
            if head not in allowed:
                raise StepError(f"{branch} moved during removal; kept")
            run(["git", "branch", "-D", branch])
        if (head := remote_head(branch)) is not None:
            if head not in allowed:
                raise StepError(f"origin/{branch} moved during removal; kept")
            run(["git", "push", "--quiet", "origin", "--delete", branch])


def running(pid: int, command: str) -> bool:
    """Whether process ``pid`` is still the ``command`` that was started."""
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip().startswith(command)


def terminate(pid: int) -> None:
    """Stop ``pid`` and wait briefly for it to exit, so later checks do not see it."""
    with contextlib.suppress(ProcessLookupError):
        os.kill(pid, signal.SIGTERM)
        for _ in range(40):
            time.sleep(0.05)
            os.kill(pid, 0)


def stop_signing_agent(socket: str) -> None:
    env = {**os.environ, "SSH_AUTH_SOCK": socket}
    subprocess.run(["ssh-add", "-D"], env=env, capture_output=True, check=False)
    command = f"ssh-agent -a {socket}"
    for line in run(["ps", "-axo", "pid=,command="]).splitlines():
        pid, _, args = line.strip().partition(" ")
        if args.strip() == command:
            terminate(int(pid))
    Path(socket).unlink(missing_ok=True)


def release_run(dry_run: bool) -> None:
    """Stop what this repository's launches left running: caffeinate, signing key.

    An ssh-agent another repository's run still records is left alone, since its
    agents may still be signing with it.
    """
    common = common_dir()
    with runs() as recorded:
        mine = recorded.get(common)
        if not mine:
            return
        shared = {
            s for key, e in recorded.items() if key != common for s in e["sockets"]
        }
        awake = [pid for pid in mine["caffeinate"] if running(pid, "caffeinate ")]
        sockets = [s for s in mine["sockets"] if s not in shared]
        summary = f"caffeinate {awake or 'none running'}, signing agent {sockets}"
        if dry_run:
            print(f"stop    {summary}")
            return
        for pid in awake:
            terminate(pid)
        for socket in sockets:
            stop_signing_agent(socket)
        del recorded[common]
    print(f"stopped {summary}")


def leftovers(herdr: Herdr, repo_name: str, entries: dict[str, Any]) -> list[str]:
    """What a launch created that no recorded group accounts for any more.

    These are typically the remains of a cleanup done by hand: a workspace whose
    worktree was deleted, a branch that was never removed or that gained commits
    after its pull request merged, or a launch's caffeinate or signing agent that
    nothing recorded.
    """
    found = []
    workspace_ids = {e["workspace_id"] for e in entries.values()}
    for workspace in open_workspaces(herdr).values():
        label = workspace.get("label", "")
        if (
            label.startswith(f"{repo_name} #")
            and workspace["workspace_id"] not in workspace_ids
        ):
            found.append(
                f"Herdr workspace {workspace['workspace_id']} ({label}) belongs to no"
                " recorded group; close it once nothing in it is needed"
            )
    paths = {e["path"] for e in entries.values()}
    branches = {b for e in entries.values() for b in e["branches"]}
    for path, branch in worktree_branches().items():
        if ISSUE_BRANCH.fullmatch(branch) and path not in paths:
            found.append(f"worktree {path} on {branch} belongs to no recorded group")
    refs = run(
        ["git", "for-each-ref", "--format=%(refname)"]
        + ["refs/heads/*/issue-*", "refs/remotes/origin/*/issue-*"]
    ).split()
    for ref in refs:
        branch = ref.removeprefix("refs/heads/").removeprefix("refs/remotes/origin/")
        name = branch if ref.startswith("refs/heads/") else f"origin/{branch}"
        if branch in branches or not ISSUE_BRANCH.fullmatch(branch):
            continue
        # An unmerged branch may be work in progress; only merged ones are judged.
        prs = run_json(
            ["gh", "pr", "list", "--head", branch, "--state", "merged"]
            + ["--json", "number,headRefOid"]
        )
        if not prs:
            continue
        number, head = prs[0]["number"], ref_head(ref) or ""
        if head == prs[0]["headRefOid"]:
            found.append(f"{name} is merged (PR #{number}) but was not deleted")
        else:
            found.append(
                f"{name} is at {head[:7]}, a commit PR #{number} did not merge; keep"
                " or drop it with the user"
            )
    if not entries:
        found += unrecorded_processes()
    return found


def unrecorded_processes() -> list[str]:
    """Caffeinate and signing agents a launch started that no run records.

    Launches made before the launcher recorded them, or whose record was lost, are
    otherwise never stopped.
    """
    with runs() as recorded:
        pids = {p for e in recorded.values() for p in e["caffeinate"]}
        sockets = {s for e in recorded.values() for s in e["sockets"]}
    awake = f"caffeinate -i -t {KEY_HOURS * 3600}"
    agent = f"ssh-agent -a {STATE_DIR / 'ssh-agent-'}"
    found = []
    for line in run(["ps", "-axo", "pid=,command="]).splitlines():
        pid, _, args = line.strip().partition(" ")
        args = args.strip()
        if args == awake and int(pid) not in pids:
            found.append(
                f"caffeinate {pid} looks like a launch's and no run records it; stop"
                f" it with `kill {pid}` unless another run needs it"
            )
        elif args.startswith(agent):
            socket = args.removeprefix("ssh-agent -a ")
            if socket in sockets:
                continue
            found.append(
                f"ssh-agent {pid} ({socket}) holds a launch's signing key and no run"
                f" records it; stop it with `kill {pid}` unless another run's agents"
                " still sign with it"
            )
    return found


def clean(herdr: Herdr, dry_run: bool) -> int:
    """Remove every merged group, then whatever its launch left running.

    Exits nonzero while anything is kept or left over, so a clean run is one that
    prints no ``keep``, ``FAILED`` or ``leftover`` line.
    """
    repo_name = run_json(["gh", "repo", "view", "--json", "name"])["name"]
    run(["git", "fetch", "--quiet", "--prune", "origin"])
    if not dry_run:
        # Forget worktrees whose directory was deleted by hand before judging them.
        run(["git", "worktree", "prune"])
    with state() as entries:
        groups = dict(entries)
    worktrees = worktree_branches()
    panes = herdr.call("pane", "list")["panes"]
    workspaces = open_workspaces(herdr)
    agents = {a.get("name"): a for a in herdr.call("agent", "list")["agents"]}

    problems = 0
    remaining = dict(groups)
    parents = set()
    for agent, entry in sorted(groups.items(), key=lambda item: item[1]["issues"]):
        try:
            reasons, owned, removable = blockers(
                agent, entry, herdr, worktrees, panes, workspaces, agents
            )
            if reasons:
                problems += 1
                print(f"keep    {agent}")
                for reason in reasons:
                    print(f"          {reason}")
                continue
            if dry_run:
                print(f"remove  {agent} (workspace {owned or 'already closed'})")
                del remaining[agent]
                continue
            remove_group(entry, herdr, worktrees, owned, removable)
            with state() as entries:
                del entries[agent]
            del remaining[agent]
            parents.add(os.path.dirname(entry["path"]))
            print(f"removed {agent}")
        except StepError as exc:
            problems += 1
            print(f"{agent}: FAILED: {exc}", file=sys.stderr)

    if not dry_run:
        run(["git", "worktree", "prune"])
        # Herdr keeps each repository's worktrees in one directory; drop it when the
        # last of them is gone.
        for parent in parents:
            with contextlib.suppress(OSError):
                os.rmdir(parent)
    if not remaining:
        release_run(dry_run)
    for leftover in leftovers(herdr, repo_name, remaining if not dry_run else groups):
        problems += 1
        print(f"leftover  {leftover}")
    if not groups and not problems:
        print("Nothing to clean.")
    return 1 if problems else 0


def main() -> None:
    argv = sys.argv[1:]
    agent_args: list[str] | None = None
    if "--" in argv:
        split = argv.index("--")
        argv, agent_args = argv[:split], argv[split + 1 :]

    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "--herdr-session",
        metavar="NAME",
        help="target this named Herdr session instead of the one this pane is in",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    launch_parser = commands.add_parser("launch", help="start one agent per group")
    launch_parser.add_argument(
        "groups", nargs="+", metavar="GROUP", help="issues, bottom first: 14,27"
    )
    launch_parser.add_argument(
        "--kind", default="omp", help="Herdr agent kind to start (default: omp)"
    )
    launch_parser.add_argument(
        "--dry-run", action="store_true", help="check issues and print prompts only"
    )
    commands.add_parser("record", help="record submitted PRs (run by the agent)")
    status_parser = commands.add_parser(
        "status", help="show agent and PR state per group"
    )
    mode = status_parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--wait",
        action="store_true",
        help="wait until a group is done, needs you, stopped or gone (exit 0), "
        f"timed out ({EXIT_TIMEOUT}), nothing is left to wait for "
        f"({EXIT_NOTHING_TO_WAIT}) or polls kept failing for "
        f"{FAILED_POLL_LIMIT / 60:.0f} minutes ({EXIT_POLL_FAILED})",
    )
    mode.add_argument(
        "--ack", action="store_true", help="mark the current state as seen"
    )
    status_parser.add_argument(
        "--interval",
        type=float,
        default=WAIT_INTERVAL,
        metavar="SECONDS",
        help=f"seconds between polls (default: {WAIT_INTERVAL:g})",
    )
    status_parser.add_argument(
        "--timeout",
        type=float,
        default=WAIT_TIMEOUT_HOURS,
        metavar="HOURS",
        help=f"give up after this long (default: {WAIT_TIMEOUT_HOURS:g})",
    )
    status_parser.add_argument(
        "--no-notify",
        action="store_true",
        help=f"with --wait, do not run {NOTIFY_SETTING} (a supervising session "
        "reports to the user itself)",
    )
    notify_parser = commands.add_parser(
        "notify",
        help=f"send TITLE and standard input to the user through {NOTIFY_SETTING}",
    )
    notify_parser.add_argument("title", metavar="TITLE")
    clean_parser = commands.add_parser("clean", help="remove merged groups")
    clean_parser.add_argument(
        "--dry-run", action="store_true", help="print what would be removed"
    )
    args = parser.parse_args(argv)
    if agent_args is not None and args.command != "launch":
        parser.error("agent arguments after `--` apply to launch only")
    if args.command == "status" and (args.interval <= 0 or args.timeout <= 0):
        parser.error("--interval and --timeout must be positive")
    if args.command == "status" and args.no_notify and not args.wait:
        parser.error("--no-notify applies to --wait only")

    if missing := [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]:
        sys.exit(f"Missing tools: {', '.join(missing)}")
    needs_herdr = args.command in ("status", "clean") or (
        args.command == "launch" and not args.dry_run
    )
    if needs_herdr and not args.herdr_session and os.environ.get("HERDR_ENV") != "1":
        sys.exit("Run this from a Herdr pane, or pass --herdr-session NAME.")

    herdr = Herdr(args.herdr_session)
    try:
        if args.command == "launch":
            if agent_args is None:
                agent_args = DEFAULT_AGENT_ARGS.get(args.kind, [])
            code = launch(args.groups, args.kind, agent_args, herdr, args.dry_run)
        elif args.command == "record":
            code = record()
        elif args.command == "notify":
            code = notify_user(args.title)
        elif args.command == "status":
            if args.wait:
                code = wait_for_change(
                    herdr, args.interval, args.timeout, not args.no_notify
                )
            else:
                code = status(herdr, args.ack)
        else:
            code = clean(herdr, args.dry_run)
    except StepError as exc:
        sys.exit(f"FAILED: {exc}")
    sys.exit(code)


if __name__ == "__main__":
    main()
