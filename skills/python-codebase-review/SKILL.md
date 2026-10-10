---
name: python-codebase-review
description: Deep, whole-codebase review of a Python project that produces REVIEW.md, a verified and prioritized list of fixes and improvements. Splits the code into slices and fans out parallel reviewer subagents, plus cross-cutting and security passes, on top of a ruff/type-checker/pytest baseline. Use this whenever the user wants to review, audit, assess, or find bugs and improvements across a Python repository, package, or service as a whole, even if they just say "review this codebase", "what should we fix in this project", or "audit the code quality". Do not use it for reviewing a diff, branch, commit, or PR (use /review), or for a single file.
---

# Python Codebase Review

Review an entire Python codebase and write `REVIEW.md` at the repository root: bugs to
fix and improvements to make, each with location, impact, and a concrete fix. The value
of this review is that every reported item is real and actionable, so verification
matters more than volume.

The review is read-only. Do not edit, format, or commit source files; the only file you
write in the repository is `REVIEW.md`. Running tools and throwaway scripts under `/tmp`
is fine. If the user passed arguments (a path to limit scope, or a focus such as
"performance"), apply them to every phase.

## 1. Baseline

Run the bundled script from the repository root:

```sh
bash <skill-dir>/scripts/baseline.sh
```

It prints a summary and, on the last line, the output directory containing
`inventory.txt` (Python lines per directory), `ruff.txt`, `types.txt`, and `tests.txt`
(results plus coverage). It uses the project's uv environment or `.venv` when present
and the project's configured type checker, falling back to basedpyright.

Read the summary, the inventory, the test result tail, and enough of the ruff and type
output to know its shape. A failing or uncollectable test suite is itself a finding.
Reviewers get these paths so they do not re-report mechanical diagnostics; they should
cite one only when it points at a real behavioral bug.

If `git status` shows uncommitted changes, mention it in the final report, since
findings may refer to code that is not committed yet.

## 2. Map the project

Read `README`, `pyproject.toml` (or `setup.cfg`/`setup.py`), `AGENTS.md`/`CLAUDE.md` if
present, the entry points (console scripts, `__main__`, app factories, CLI modules), and
the test layout. Write a project brief of about 15 lines: purpose, runtime (CLI, web
service, library, data pipeline), Python version, key dependencies, packages and their
roles, entry points, conventions, and what the baseline showed. Every reviewer receives
this brief, so it is worth getting right.

## 3. Plan slices

Split the code into review slices of roughly 3-8k lines each, along package or module
boundaries so each reviewer sees code that belongs together. Size the plan to the
codebase: a 2k-line project needs one or two reviewers, not ten. Keep generated code,
vendored code, and migrations out of slices unless the user asks for them.

Add cross-cutting reviewers, each covering the whole codebase through its own lens:

- **Architecture**: module boundaries, dependency direction, import cycles, global
  state, layering leaks, abstractions that do not pay for themselves.
- **Errors and resources**: exception handling and propagation, swallowed errors,
  retries, cleanup of files, connections, subprocesses, and temporary state.
- **Concurrency**: async correctness, blocking calls in async code, threads, shared
  mutable state, locks, task cancellation. Skip it if the project has none.
- **Tests**: what is untested (use the coverage report), weak assertions, tests coupled
  to implementation details, flaky patterns, missing edge cases on critical paths.
- **Dead code and simplification**: unused modules, functions, parameters, settings, and
  dependencies; duplicated logic; needless indirection.

Add one `security-reviewer` for the whole repository when the code handles untrusted
input, network, files, auth, secrets, subprocesses, deserialization, or SQL.

## 4. Fan out

Launch every reviewer in a single `task` call so they run in parallel. Use the
`reviewer` agent for slice and cross-cutting reviews. Give every task the contents of
`references/finding-schema.json` as its `outputSchema`, so the findings can be merged
mechanically.

Put in the shared `context`: the project brief, the baseline output paths, the read-only
rule, the output contract (below), and the checklist from
`references/python-checklist.md`. Each task names its slice (exact paths) or its lens,
and anything specific you noticed during mapping.

Output contract for reviewers:

- Report a finding only after tracing the code path that makes it real. Name the
  triggering input or state and the consequence. A plausible-sounding guess costs the
  user time to disprove.
- `kind: fix` means behavior is wrong today; `kind: improvement` means it works but
  should change.
- Do not report formatting or naming nits, issues already present in the baseline
  output, or "consider adding" suggestions with no concrete defect or payoff.
- When the same problem repeats across files, report it once and list the other
  locations in `problem`.
- Prefer a short snippet in `fix` over a description of a snippet.

## 5. Verify and merge

When all reviewers return:

1. Merge findings and remove duplicates: same root cause in overlapping lines is one
   finding; keep the clearest write-up and the highest justified priority.
2. Verify every P0 and P1 yourself by reading the code. Where it is cheap, prove it with
   a throwaway script or test under `/tmp`. Drop findings you cannot confirm, and
   downgrade ones whose impact was overstated.
3. Drop findings with confidence below 0.5 unless they are P0. Spot-check a sample of
   P2/P3 findings; if a reviewer's samples are often wrong, re-check the rest of that
   reviewer's findings.
4. Group systemic issues (the same pattern in many places) into one finding with a list
   of locations.

## 6. Write REVIEW.md

Use this structure:

```markdown
# Code review: <project>

<date> · <commit sha> · <lines of Python reviewed>
Baseline: ruff <n> issues, <checker> <n> errors, tests <pass/fail>, coverage <n>%

## Summary
3-6 sentences: overall health, the most important risks, and where to start.

## Quick wins
Up to 10 high-value fixes with effort S, one line each, linking to their entries below.

## Fixes
### P0
#### F1. <title>
`path/to/file.py:12-20` · category · effort S/M/L
**Problem:** what is wrong, what triggers it, and the impact.
**Evidence:** how it was confirmed.
**Fix:** concrete change, with a snippet when useful.

### P1 / P2 / P3 (same format)

## Improvements
Same format, numbered I1, I2, ..., ordered by priority then effort.

## Baseline diagnostics
Counts by rule or error code for ruff and the type checker, with a one-line
recommendation for each large group (for example, "enable rule X", "fix with ruff
--fix"). Do not list every diagnostic.

## Not reviewed
Paths excluded and why, and any reviewer that failed.
```

Omit empty sections. Then reply in chat with the path to `REVIEW.md`, the count of
findings by priority, and the top five items.

## After the review

Suggest fixing in batches by priority in a new session ("fix the P0 items in REVIEW.md,
one commit each, with a regression test for each"), then running `/review` on the
resulting diff. For a second opinion, ask a model from another family to check REVIEW.md
for false positives and misses.
