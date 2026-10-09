# Review

A pull request gets two complementary reviews before the user's final one:

| Review | Question | Reviewer |
| --- | --- | --- |
| Bug finding | Is the diff correct and safe? | A hosted review bot, or an agent when no bot runs |
| Spec check | Does the PR deliver its issue's outcome and verification, within the issue's and brief's scope? | An agent using this skill, in a session that did not write the PR |

Hosted bots read the diff and repository guidance but not linked issues or briefs, so
they cannot do the spec check. The user then reads both reviews and the diff, and
merges.

## Run a spec check

Independence matters: an author rarely spots what they already rationalized. Prefer a
fresh session, ideally a different model from the author's. If this session wrote the
pull request, say so in the review.

1. **Gather.** Read the PR
   (`gh pr view <n> --json title,body,closingIssuesReferences,files,commits,isDraft`),
   the diff (`gh pr diff <n>`), the checks (`gh pr checks <n>`), and existing reviews
   and comments (`gh pr view <n> --comments`). Read each linked issue, its parent, the
   linked brief, and the relevant agent instruction files. When the PR changes the
   brief, read both versions.
2. **Verify.** Run the issue's verification against the PR head in a separate worktree,
   so the user's working tree stays untouched:
   `git fetch origin pull/<n>/head && git worktree add --detach <dir> FETCH_HEAD`.
   Remove it with `git worktree remove <dir>` when done.
3. **Assess.**
   - **Outcome:** mark each verification item passed, with evidence; failed; or
     unverified.
   - **Scope:** changes outside the issue or the brief, missing parts of the outcome,
     and undeclared changes to canonical artifacts.
   - **Correctness:** bugs and missing failure behavior on the changed paths. Do not
     repeat a bot's findings; mention one only to disagree or to raise its severity.
   - **Consistency:** documentation, agent instructions, or the brief left stale by the
     change, and commits that break the repository's history rules.
   - Skip anything CI already enforces, such as formatting and lint.
4. **Classify.** A finding is blocking when the outcome or verification fails, the work
   leaves scope, or it introduces a bug. Everything else is non-blocking. Give each
   finding its location, evidence, consequence, and a suggested fix. Label inferences
   that you could not confirm.

## Post the review

Report in chat unless the user asked you to post on GitHub. Post a single review with
the comment event. Never approve or request changes: the agent acts through the user's
account, so its approval would be the user's, and GitHub rejects both events from the
PR's author.

For a summary-only review, write the body to a file and run
`gh pr review <n> --comment --body-file <file>`. To attach findings to lines, create the
review through the REST API instead:

```shell
gh api repos/{owner}/{repo}/pulls/<n>/reviews --input <file>
```

The file contains:

```json
{
  "event": "COMMENT",
  "body": "[AgentName] Spec review ...",
  "comments": [
    { "path": "src/verify.ts", "line": 42, "side": "RIGHT", "body": "[AgentName] ..." }
  ]
}
```

Inline comments attach only to lines in the diff, with paths relative to the repository
root. Put findings about other lines, such as stale documentation the PR did not touch,
in the review body.

Shape the body as:

```markdown
[AgentName] Spec review of #<issue>

**Verdict:** Ready for human review | Needs changes (<count> blocking)

**Verification**
- Passed: <item>: <evidence>
- Failed: <item>: <evidence>
- Unverified: <item>: <reason>

**Blocking**
1. <finding>

**Non-blocking**
1. <finding>
```

Omit empty sections. On a re-review, check the previous findings and the new changes
only; do not raise fresh nits on unchanged code.

## Configure a hosted review bot

Each bot reads its own guidance file. Keep it to consequential, repository-specific
rules, and leave mechanical checks to CI.

| Bot | Trigger | Guidance |
| --- | --- | --- |
| Codex | Automatic, or comment `@codex review` | `## Code Review Rules` section in AGENTS.md |
| Claude Code Review | Per-repository setting, or comment `@claude review` | `REVIEW.md`, plus CLAUDE.md |
| Copilot code review | Automatic ruleset, or request Copilot as a reviewer | `.github/copilot-instructions.md` |

## The user's final review

The user reads the bot and spec reviews and the diff, then merges. GitHub does not let
an author approve their own pull request, and pull requests opened by an agent through
the user's account are authored by the user. In a single-maintainer repository, a
branch protection rule that requires approvals would therefore block every merge; rely
on required status checks instead. Never present an agent review as an approval.
