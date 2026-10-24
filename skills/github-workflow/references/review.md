# Review

A pull request gets up to three reviews, in this order:

| Review | Question | Reviewer |
| --- | --- | --- |
| Agent review | Does the PR deliver its issue's acceptance criteria and verification, within scope, correctly, and consistently with the rest of the repository? | An agent using this skill, with a fresh context that did not write the PR |
| Bot review | Is the diff correct and safe? Optional. | A hosted review bot |
| Maintainer review | Is it right to merge? | The maintainer, who then merges |

Hosted bots read the diff and repository guidance but not linked issues or briefs, so
they cannot judge acceptance criteria or scope. The agent review does. One agent review
covers a pull request, or a whole stack. Agents never approve or request changes.

## Run an agent review

Independence matters: an author rarely spots what they already rationalized. Use a
fresh context: a subagent the author starts counts, as does a new session. Prefer a
different model from the author's. Give the reviewer the pull request number, not the
author's reasoning. When the author started the reviewer, say so in the review.

1. **Gather.** Read the PR
   (`gh pr view <n> --json title,body,closingIssuesReferences,files,commits,isDraft`),
   the diff (`gh pr diff <n>`), the checks (`gh pr checks <n>`), and existing reviews
   and comments (`gh pr view <n> --comments`). Read each linked issue, the linked brief
   if there is one, and the relevant agent instruction files. When the PR changes the
   brief, read both versions.
2. **Verify.** Run the issue's verification against the PR head in a separate worktree,
   so the maintainer's working tree stays untouched:
   `git fetch origin pull/<n>/head && git worktree add --detach <dir> FETCH_HEAD`.
   Remove it with `git worktree remove <dir>` when done.
3. **Assess.**
   - **Acceptance criteria:** mark each verification item passed, with evidence;
     failed; or unverified.
   - **Scope:** changes outside the issue or the brief, missing acceptance criteria,
     and undeclared changes to canonical artifacts.
   - **Correctness:** bugs and missing failure behavior on the changed paths. Do not
     repeat a bot's findings; mention one only to disagree or to raise its severity.
   - **Consistency:** documentation, agent instructions, or the brief left stale by the
     change, and commits that break the repository's history rules.
   - Skip anything CI already enforces, such as formatting and lint.
4. **Classify.** A finding is blocking when the acceptance criteria or verification
   fail, the work leaves scope, or it introduces a bug. Everything else is
   non-blocking. Give each finding its location, evidence, consequence, and a suggested
   fix. Label inferences that you could not confirm.

## Post the review

During a delivery (see the pull requests reference), post the review on the pull request
once the fixes are in, as one review of the final head. When the user asks for a review
on its own, report in chat unless they ask you to post it. Post a single review with
the comment event. Never approve or request changes: the agent acts through the
maintainer's account, so its approval would be the maintainer's, and GitHub rejects
both events from the PR's author.

Inline comments carry only the findings still open: blocking ones left after the last
round, non-blocking ones not fixed, and those the author rejected. The author replies to
each rejected finding's comment with its reason. Findings fixed during the delivery go
in the body, each with the commit that fixed it.

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
  "body": "[AgentName reviewer] Agent review ...",
  "comments": [
    {
      "path": "src/verify.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "[AgentName reviewer] ..."
    }
  ]
}
```

Inline comments attach only to lines in the diff, with paths relative to the repository
root. Put findings about other lines, such as stale documentation the PR did not touch,
in the review body. Keep the body file in the scratch directory and delete it after
posting.

Shape the body as:

```markdown
[AgentName reviewer] Agent review of #<issue>

**Verdict:** Ready for maintainer review | Needs changes (<count> blocking)

**Verification**
- Passed: <item>: <evidence>
- Failed: <item>: <evidence>
- Unverified: <item>: <reason>

**Blocking**
1. <finding>

**Non-blocking**
1. <finding>

**Fixed during delivery**
1. <finding>: <commit>
```

Omit empty sections. On a re-review, check the previous findings and the commits pushed
since the posted review only; do not raise fresh nits on unchanged code.

## Configure a hosted review bot

Each bot reads its own guidance file. Keep it to consequential, repository-specific
rules, and leave mechanical checks to CI.

| Bot | Trigger | Guidance |
| --- | --- | --- |
| Codex | Automatic, or comment `@codex review` | `## Code Review Rules` section in AGENTS.md |
| Claude Code Review | Per-repository setting, or comment `@claude review` | CLAUDE.md only |
| Copilot code review | Automatic ruleset, or request Copilot as a reviewer | `.github/copilot-instructions.md` |

Never create a REVIEW.md for a bot. REVIEW.md is always a scratch file.

## Maintainer review

The maintainer reads the agent review, the bot review if any, and the diff, then
merges. GitHub does not let an author approve their own pull request, and pull requests
opened by an agent through the maintainer's account are authored by the maintainer. In a
single-maintainer repository, a rule that requires approvals would therefore block every
merge: require no approvals and rely on required status checks instead. Never present an
agent review as an approval.
