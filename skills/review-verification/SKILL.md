---
name: review-verification
description: Check every finding in an existing review or plan file (REVIEW.md or similar) against the current code or a named dependency version, mark each confirmed, partially confirmed, or false positive with evidence, and add important omissions. Edits only that file, with no branches, commits, issues, or pull requests. Use for "check every finding in REVIEW.md", "verify the review", or "which findings still hold against v0.7.0". Not for writing a new review (python-codebase-review) or filing issues from one (github-workflow).
---

# Review Verification

Check an existing review file finding by finding, so that whoever acts on it next works
only from claims that hold. A wrong finding costs more than a missing one: it becomes
an issue, then a pull request, before anyone notices.

## Scope

- The only file you change is the review file itself. Do not create branches, commits,
  issues, or pull requests, even when the repository's instructions say finished work
  is committed: the review file is a scratch input, not a deliverable.
- Throwaway probes and environments go under `/tmp` and are removed at the end.
- Record what you verified against at the top of the file: the commit SHA, or the
  dependency version, installed in an isolated environment rather than the project's
  own one.

## 1. Inventory

List every item the file asserts: numbered findings, quick wins, table rows, rejected
proposals, migration mappings. Keep the list, so you can check at the end that every
item got a verdict.

## 2. Verify

- **P0 and P1:** read the code path and prove or disprove the claim with a throwaway
  script or test. Name the triggering input and the observed result.
- **P2 and P3:** read the code. Probe when it is cheap or the claim is surprising.
- **Proposed fixes:** check them too. A correct finding with a fix that would break
  something else needs a corrected fix, not just a verdict.
- With more than about 40 items, split them by area across parallel reviewers that all
  use the verdict format below, then spot-check their false positives yourself.

## 3. Annotate

Under each item, add one line with the verdict (Confirmed, Partially confirmed, or
False positive) and its evidence: `file:line`, or the probe you ran and its output.

```markdown
**Verdict:** False positive. `cache.py:88` closes only caches the client created.
```

For a partial confirmation, say which sub-claim fails. Keep the original text, so the
reader can see what changed.

## 4. Add omissions

Add important problems the review missed as N1, N2, … in the same format as its
findings, each with evidence of the same standard. Report only what you confirmed.

## 5. Report

Reply in chat with:

- a table of counts by verdict;
- each false positive with a one-line reason;
- the added items;
- what you did not run again, such as the baseline checks.
