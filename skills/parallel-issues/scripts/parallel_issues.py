#!/usr/bin/env python3
"""Run one coding agent per group of GitHub issues, each group as a stack of PRs.

    parallel_issues.py launch --dry-run 14,27 13
    parallel_issues.py launch 14,27 13 [--kind omp] [-- AGENT_ARGS...]
    parallel_issues.py record          # run by the agent, inside its worktree
    parallel_issues.py status
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

Every check fails hard: an issue that fails one is not launched.

``record`` stores, for each branch of the agent's group, the PR number and the
commit that PR was opened with, but only when the PR's head on GitHub equals the
local branch and GitHub shows every commit of the PR as verified; otherwise it exits
nonzero. The default branch's ruleset does not cover PR branches, so this is the
check that catches an unverified commit before review. ``clean`` removes a group's
worktree, workspace and branches only
when every branch is at its recorded commit and its PR is merged, the worktree has
no uncommitted changes, and no other Herdr workspace uses it. Anything else is kept
and reported.

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
import shutil
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path
from string import Template
from typing import Any

USAGE = "Run one coding agent per group of GitHub issues, each group as a stack."
SCRIPT = Path(__file__).resolve()
PROMPT_TEMPLATE = SCRIPT.parent.parent / "assets" / "prompt.md"
STATE_FILE = "parallel-issues.json"
REQUIRED_TOOLS = ("git", "gh", "herdr")
# Herdr agent kinds take the agent's own CLI flags after `--`.
DEFAULT_AGENT_ARGS = {"omp": ["--advisor"]}
# Branches follow the git-branch skill: <type>/issue-<N>-<slug>, where <type> is the
# Conventional Commits type of the change. An issue's labels are the only type signal
# the launcher has. They are matched most specific first, so the result never depends
# on the order GitHub lists them in: a label named after a commit type, then a label
# that stands for one type, then GitHub's generic defaults.
COMMIT_TYPES = ("feat", "fix", "docs", "test", "refactor", "perf", "build", "ci", "chore")
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
MAX_ITEMS = 100  # issue comments and edits fetched in one query
SIGNING_KEY_SETTING = "agent.signingKey"
KEY_HOURS = 12
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


@contextlib.contextmanager
def state() -> Generator[dict[str, dict[str, Any]], None, None]:
    """Yield the recorded groups, keyed by agent name, under an exclusive lock.

    Several agents may run ``record`` at once, so every change is a locked
    read-modify-write of the whole file.
    """
    common = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"])
    path = Path(common.strip()) / STATE_FILE
    with open(path.with_suffix(".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        entries = json.loads(path.read_text()) if path.exists() else {}
        yield entries
        path.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n")


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


def keep_awake() -> None:
    if shutil.which("caffeinate"):
        subprocess.Popen(
            ["caffeinate", "-i", "-t", str(KEY_HOURS * 3600)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


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


def launch(
    values: list[str], kind: str, agent_args: list[str], herdr: Herdr, dry_run: bool
) -> int:
    groups = parse_groups(values)
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
        keep_awake()

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
            herdr.call("agent", "prompt", agent, prompt)
            submit(herdr, agent)
            live_agents.add(agent)
            print(f"{label}: {agent} started on {branches[0]}")
        except StepError as exc:
            failures += 1
            print(f"{label}: FAILED: {exc}", file=sys.stderr)
    return 1 if failures else 0


def branch_head(branch: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or None


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


def status(herdr: Herdr) -> int:
    with state() as entries:
        groups = dict(entries)
    if not groups:
        print("No recorded groups.")
        return 0
    agents = {a.get("name"): a for a in herdr.call("agent", "list")["agents"]}
    for agent, entry in sorted(groups.items(), key=lambda item: item[1]["issues"]):
        live = agents.get(agent)
        print(f"{agent}: {live['agent_status'] if live else 'gone'}")
        for branch in entry["branches"]:
            prs = run_json(
                ["gh", "pr", "list", "--head", branch, "--state", "all"]
                + ["--json", "state,url"]
            )
            pr = " ".join(f"{p['state'].lower()} {p['url']}" for p in prs) or "no PR"
            recorded = "recorded" if branch in entry["submitted"] else "not recorded"
            print(f"  {branch}: {pr} ({recorded})")
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
    entry: dict[str, Any],
    herdr: Herdr,
    worktrees: dict[str, str],
    panes: list[dict[str, Any]],
    workspaces: dict[str, dict[str, Any]],
) -> tuple[list[str], str | None]:
    """Return (reasons to keep the group, owned workspace id)."""
    if entry.get("herdr_session") != herdr.session:
        return [f"launched in Herdr session {entry.get('herdr_session')}"], None
    reasons = []
    for branch in entry["branches"]:
        head = branch_head(branch)
        if head is None:
            continue
        submitted = entry["submitted"].get(branch)
        if not submitted:
            reasons.append(f"{branch}: not recorded as submitted")
            continue
        if head != submitted["oid"]:
            reasons.append(f"{branch}: moved since it was submitted")
            continue
        pr = run_json(["gh", "pr", "view", str(submitted["pr"]), "--json", "state"])
        if pr["state"] != "MERGED":
            reasons.append(f"{branch}: PR #{submitted['pr']} is {pr['state'].lower()}")

    path = entry["path"]
    owned = None
    if path in worktrees:
        if worktrees[path] not in entry["branches"]:
            reasons.append(f"worktree has {worktrees[path]} checked out")
        elif run(["git", "status", "--porcelain"], cwd=path).strip():
            reasons.append("worktree has uncommitted changes")
        workspace = workspaces.get(entry["workspace_id"])
        checkout = (workspace or {}).get("worktree", {}).get("checkout_path")
        if (
            workspace
            and workspace.get("label") == entry["label"]
            and inside(checkout, path)
        ):
            owned = entry["workspace_id"]
        others = sorted(
            {
                p["workspace_id"]
                for p in panes
                if p["workspace_id"] != owned
                and (
                    inside(p.get("cwd"), path) or inside(p.get("foreground_cwd"), path)
                )
            }
        )
        if others:
            reasons.append(f"worktree is in use by Herdr workspace {', '.join(others)}")
    return reasons, owned


def clean(herdr: Herdr, dry_run: bool) -> int:
    with state() as entries:
        groups = dict(entries)
    if not groups:
        print("No recorded groups.")
        return 0
    worktrees = worktree_branches()
    panes = herdr.call("pane", "list")["panes"]
    workspaces = {
        w["workspace_id"]: w for w in herdr.call("workspace", "list")["workspaces"]
    }

    failures = 0
    for agent, entry in sorted(groups.items(), key=lambda item: item[1]["issues"]):
        try:
            reasons, owned = blockers(entry, herdr, worktrees, panes, workspaces)
            if reasons:
                print(f"keep    {agent}")
                for reason in reasons:
                    print(f"          {reason}")
                continue
            if dry_run:
                print(f"remove  {agent} (workspace {owned or 'already closed'})")
                continue
            if owned:
                # Refuses a dirty worktree, and then leaves the workspace open.
                herdr.call("worktree", "remove", "--workspace", owned)
            elif entry["path"] in worktrees:
                run(["git", "worktree", "remove", entry["path"]])
            for branch in entry["branches"]:
                head = branch_head(branch)
                if head is None:
                    continue
                # The agent may have committed before its workspace closed.
                if head != entry["submitted"][branch]["oid"]:
                    raise StepError(f"{branch} moved during removal; kept")
                run(["git", "branch", "-D", branch])
            with state() as entries:
                del entries[agent]
            print(f"removed {agent}")
        except StepError as exc:
            failures += 1
            print(f"{agent}: FAILED: {exc}", file=sys.stderr)
    return 1 if failures else 0


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
    commands.add_parser("status", help="show agent and PR state per group")
    clean_parser = commands.add_parser("clean", help="remove merged groups")
    clean_parser.add_argument(
        "--dry-run", action="store_true", help="print what would be removed"
    )
    args = parser.parse_args(argv)
    if agent_args is not None and args.command != "launch":
        parser.error("agent arguments after `--` apply to launch only")

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
        elif args.command == "status":
            code = status(herdr)
        else:
            code = clean(herdr, args.dry_run)
    except StepError as exc:
        sys.exit(f"FAILED: {exc}")
    sys.exit(code)


if __name__ == "__main__":
    main()
