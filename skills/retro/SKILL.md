---
name: retro
description: Review recent coding-agent sessions (a weekend, a week, a project's last few days) for friction, mistakes and wasted effort, trace each problem to the skill, agent instruction file, project file or tool that caused it, and propose evidence-backed changes for approval, then make the approved ones. Use for "review the sessions from the past weekend", "retro on this week's agent work", "why did the agents keep asking me X", "how can we make the agents more autonomous", or whenever the user wants to refine skills or AGENTS.md from what actually happened in sessions. Not for reviewing code (python-codebase-review) or a single pull request (github-workflow).
compatibility: Written for omp, whose transcripts are JSONL files under ~/.omp/agent/sessions; scripts/sessions.py reads them with Python 3.10+ and no dependencies. Other agents need their own transcript location. Read-only subagents (omp's scout) speed up the analysis but are optional.
---

# Retro

Find out what got in the user's way in real sessions, and change the skills and
instructions so it doesn't happen again. Sessions are the evidence: a retro says what
happened, where, and which file let it happen, never what agents "tend to" do.

A retro has two phases, with the user's approval between them: **review** (answer and
stop) and **apply** (make the approved changes).

## 1. Scope

- **Period:** turn the user's words into local dates. "The weekend" is Saturday and
  Sunday in the user's timezone; transcripts store UTC.
- **Projects:** every project unless the user names some.
- **Focus:** note what the user already suspects ("reviews were inconsistent", "it kept
  asking me"). Treat it as a hypothesis to test, not a finding.
- **Recent changes:** list commits to the skills and agent instruction files since the
  period started. A session that ran after a change shows whether the change worked;
  one before it shows the problem the change was meant to fix.

## 2. Collect

Digest the sessions into the scratch directory:

```shell
python3 <skill-dir>/scripts/sessions.py digest --since 2026-10-24 --until 2026-10-25 \
  --out .scratch/retro
```

`summary.md` lists the sessions and pre-sorts the user's short replies, which carry
most of the signal:

- **Confirmations** ("Yes", "Do it", "Commit") and the question each one answered: an
  agent asking permission it could have assumed, or asking one question at a time.
- **Retries** ("Try again"): an environment or tool failure the agent could not
  recover from, such as a signing prompt that timed out.
- **Corrections and questions back** ("Why…?", "I meant…", "Aren't they at…?"): a
  silent decision, a misread request, or something the agent should have known.
- **Repeated prompts:** the user doing by hand what the workflow could do, such as
  "What should we work on next?" after every release.
- **Recurring tool errors:** the same failure across sessions.

Read each session's digest for context, and the raw transcript (the `File:` line) for
anything you will cite. Digests truncate long messages.

## 3. Analyze

For each problem, record:

- **Evidence:** session id, local time, and a short quote.
- **Root cause:** the exact place that allowed it: a skill section (`file:line`),
  agent instruction files, a project file, a template, a tool or a setting. Read the
  current text before claiming a gap: the rule may exist and have been ignored, which
  calls for a different fix than a missing rule.
- **Fix:** what to change, and where.
- **Severity:** high (wrong result, public mistake, user blocked), medium (repeated
  friction), low (one-off).

Look for these patterns in particular:

- the agent waited for the user when it had what it needed, or stopped for one
  question while other work could continue;
- the user supplied a fact they had given in an earlier session, which means it was
  never written where the next session reads;
- an assumption the plan or a skill bakes in that the sessions contradict, such as
  estimates far from the time the work actually took;
- several sessions doing one change separately, colliding in a shared checkout or
  needing an order nobody owned;
- environment state leaking between steps, such as exported variables in a persistent
  shell.

Prefer fixes that remove a cause over fixes that add a procedure. When two repositories
must change in step, removing the coupling is better than documenting the order.
Before proposing a change in some file, check that the file is really where that thing
is managed: a setting may live in an infrastructure repository, a rule in a template.

With more than about ten sessions, give groups of related sessions to parallel
read-only subagents, with this section as their rubric and the digest and transcript
paths. Verify every high-severity finding they report against the transcript and the
current files yourself: subagents misattribute sessions and invent gaps.

Also record what worked and should be kept, so a later change doesn't remove it.

## 4. Report, then stop

Reply in chat, without editing anything:

- findings, highest severity first, each with evidence, root cause and fix;
- what worked;
- items that need a decision from the user, with your recommendation.

The user often adds observations ("the estimates were always far off"). Check each
against the sessions, say what the data shows, and fold it into the recommendations.
When the user asks for the list, group the changes by target (skills, the user's own
agent instruction files, project repositories, infrastructure), mark the decisions, and
say how each will ship.

## 5. Apply

Once the user approves:

- Change each target by its own rules: skills in their source repository, checked with
  its QA recipe, then synced to the installed copies; agent instruction files at their
  source (a dotfiles manager, for example); project repositories through their usual
  workflow (the `github-workflow` skill, if installed), in worktrees, never in a main
  checkout that may hold the user's work.
- Independent targets can go to parallel subagents. Give each the exact change, the
  shared contracts (a check name, a section's wording), and the rule that it edits only
  its own files.
- Write every change as a standalone rule in the target file's own voice. Committed
  files never cite the retro, session ids, scratch files, or when the user was active.
- Respect the user's working-hours and publishing rules for commits and anything posted.

Delete `.scratch/retro/` when the retro is done.
