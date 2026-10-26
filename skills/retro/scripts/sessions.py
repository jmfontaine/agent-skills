#!/usr/bin/env python3
"""List and digest omp session transcripts for a retrospective.

    sessions.py list   --since 2026-10-24 --until 2026-10-25 [--project myapp]
    sessions.py digest --since 2026-10-24 --until 2026-10-25 --out .scratch/retro

Dates are local calendar days, inclusive; a time (``2026-10-24T18:00``) is local
time too. A session is in the window when any of its messages is. ``--project``
keeps sessions whose working directory contains the text (repeatable).

``digest`` writes one Markdown file per session to ``--out`` (the user's prompts,
the agent's last text before each prompt, tool counts and failed tool results)
and ``summary.md`` with what usually points at friction: short confirmations and
the question they answered, retries, corrections, and recurring tool errors.
Times in the output are local. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

SESSIONS_DIR = Path.home() / ".omp" / "agent" / "sessions"
PROMPT_CHARS = 2500
REPLY_CHARS = 1500
CONFIRM = re.compile(r"^(yes|yep|ok(ay)?|do (it|that)|proceed|go ahead|run it|merge|commit|push|amend)\b", re.I)
RETRY = re.compile(r"^(try again|retry|resume|again)\b", re.I)
CORRECTION = re.compile(
    r"^(no\b|why\b|i meant|what i mean|aren't|isn't|don't|that's not|actually|wait\b|you (seem|forgot|missed))",
    re.I,
)
SHORT = 80


@dataclass
class Session:
    path: Path
    id: str = ""
    cwd: str = ""
    title: str = ""
    first: datetime | None = None
    last: datetime | None = None
    prompts: list[tuple[datetime, str, str]] = field(default_factory=list)  # (time, prompt, reply before)
    final_reply: str = ""
    tools: Counter[str] = field(default_factory=Counter)
    errors: list[tuple[str, str]] = field(default_factory=list)


def text_of(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()


def load(path: Path) -> Session:
    session = Session(path)
    reply = ""
    with path.open(encoding="utf-8") as lines:
        for line in lines:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = entry.get("type")
            if kind == "session":
                session.id, session.cwd = entry.get("id", ""), entry.get("cwd", "")
            elif kind in ("title", "title_change"):
                session.title = entry.get("title", session.title)
            if kind != "message":
                continue
            when = parse_time(entry["timestamp"])
            session.first = session.first or when
            session.last = when
            message = entry.get("message", {})
            role = message.get("role")
            if role == "user":
                session.prompts.append((when, text_of(message.get("content")).strip(), reply))
                reply = ""
            elif role == "assistant":
                for part in message.get("content", []):
                    if isinstance(part, dict) and part.get("type") == "toolCall":
                        session.tools[part.get("name", "?")] += 1
                reply = text_of(message.get("content")).strip() or reply
            elif role == "toolResult" and message.get("isError"):
                session.errors.append((message.get("toolName", "?"), text_of(message.get("content")).strip()))
    session.final_reply = reply
    return session


def bound(value: str, end: bool) -> datetime:
    when = datetime.fromisoformat(value)
    if len(value) == 10 and end:
        when += timedelta(days=1)
    return when.astimezone()


def select(args: argparse.Namespace) -> list[Session]:
    since, until = bound(args.since, False), bound(args.until or args.since, True)
    chosen = []
    for path in sorted(Path(args.sessions_dir).glob("*/*.jsonl")):
        if datetime.fromtimestamp(path.stat().st_mtime).astimezone() < since:
            continue
        session = load(path)
        if not session.first or session.last < since or session.first >= until:
            continue
        if args.project and not any(p in session.cwd for p in args.project):
            continue
        chosen.append(session)
    return sorted(chosen, key=lambda s: s.first)


def stamp(when: datetime) -> str:
    return when.strftime("%a %Y-%m-%d %H:%M")


def short_id(session: Session) -> str:
    return session.id[:13] or session.path.stem[-36:][:13]


def digest(session: Session) -> str:
    out = [f"# {short_id(session)} {session.title}", f"{session.cwd}", f"{stamp(session.first)} → {stamp(session.last)}", f"File: {session.path}", ""]
    for when, prompt, reply in session.prompts:
        if reply:
            out += ["**Agent:**", "", reply[:REPLY_CHARS], ""]
        out += [f"**User {when:%a %H:%M}:**", "", prompt[:PROMPT_CHARS], ""]
    if session.final_reply:
        out += ["**Agent (last):**", "", session.final_reply[:REPLY_CHARS], ""]
    out += ["## Tools", "", ", ".join(f"{k} {v}" for k, v in session.tools.most_common()) or "none", ""]
    if session.errors:
        out += ["## Failed tool results", ""]
        out += [f"- {tool}: {err[:300]!r}" for tool, err in session.errors]
    return "\n".join(out) + "\n"


def signature(error: str) -> str:
    first = next((line for line in error.splitlines() if line.strip()), "")
    return re.sub(r"\d+", "N", first.strip())[:100]


def summary(sessions: list[Session]) -> str:
    out = ["# Sessions", "", "| Session | Start | End | Prompts | Tool calls | Errors | Directory | Title |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in sessions:
        out.append(
            f"| {short_id(s)} | {stamp(s.first)} | {stamp(s.last)} | {len(s.prompts)} | {sum(s.tools.values())} | {len(s.errors)} | {s.cwd} | {s.title} |"
        )
    groups = {"Confirmations (what did the agent ask?)": CONFIRM, "Retries": RETRY, "Corrections and questions back": CORRECTION}
    for heading, pattern in groups.items():
        hits = [(s, w, p, r) for s in sessions for w, p, r in s.prompts if pattern.match(p) and (len(p) <= SHORT or pattern is CORRECTION)]
        out += ["", f"# {heading}: {len(hits)}", ""]
        for s, when, prompt, reply in hits:
            asked = " ".join(reply.split())[-240:]
            out.append(f"- {short_id(s)} {when:%a %H:%M} “{' '.join(prompt.split())[:200]}” ← …{asked}")
    repeated = Counter(" ".join(p.lower().split()) for s in sessions for _, p, _ in s.prompts if 3 < len(p) <= SHORT)
    out += ["", "# Repeated prompts", ""]
    out += [f"- {n}× “{p}”" for p, n in repeated.most_common() if n > 1]
    tools = Counter(tool for s in sessions for tool, _ in s.errors)
    sigs = Counter(f"{tool}: {signature(err)}" for s in sessions for tool, err in s.errors)
    out += ["", "# Tool errors", "", ", ".join(f"{k} {v}" for k, v in tools.most_common()) or "none", ""]
    out += [f"- {n}× {sig}" for sig, n in sigs.most_common(25)]
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["list", "digest"])
    parser.add_argument("--since", required=True, help="local date or date-time")
    parser.add_argument("--until", help="local date or date-time, inclusive day (default: --since)")
    parser.add_argument("--project", action="append", help="keep sessions whose directory contains this")
    parser.add_argument("--out", type=Path, help="digest output directory")
    parser.add_argument("--sessions-dir", default=str(SESSIONS_DIR))
    args = parser.parse_args()
    sessions = select(args)
    if args.command == "list":
        for s in sessions:
            print(f"{short_id(s)}  {stamp(s.first)} → {stamp(s.last)}  {len(s.prompts):3} prompts  {s.cwd}  {s.title}")
        return 0
    if not args.out:
        parser.error("digest needs --out")
    args.out.mkdir(parents=True, exist_ok=True)
    for s in sessions:
        (args.out / f"{short_id(s)}.md").write_text(digest(s), encoding="utf-8")
    (args.out / "summary.md").write_text(summary(sessions), encoding="utf-8")
    print(f"{len(sessions)} sessions → {args.out}/summary.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
