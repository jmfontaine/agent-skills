# Repository setup

Every repository uses the same GitHub configuration, so the rest of this skill can rely
on it. This reference states the rules; it ships no configuration files. Check a
repository against them with the drift checklist at the end.

A repository deviates only for a reason recorded in its AGENTS.md, under the section
"Deviations from the shared workflow". Without a recorded reason, a difference from
these rules is drift: report it, and fix it only when the user asks. When agent
instruction files say the repository's GitHub settings are managed as code, change
them there through a pull request, never with `gh api` or the web UI.

## Why squash merges

Squash merges are the only GitHub merge method that keeps the default branch linear
with every commit signed and verified: commits on the branch are signed by the
maintainer or the agent's key, and GitHub signs the squash commit. Rebase merges,
preferred for granular history, cannot be signed, because GitHub rewrites the commits.
Merge commits keep signatures but make history non-linear and land work-in-progress
commits.

Because only the squash commit lands, only the pull request title matters. Branch
commits are free-form but always signed. Before merging, check that the repository
allows squash merges; if not, stop and ask.

## Merge settings

- Allow squash merging only. Disable merge commits and rebase merging.
- Default squash commit title: the pull request title.
- Default squash commit message: blank. The commit on the default branch is then the
  title plus `(#123)`.
- Delete the head branch automatically after merge.

## Rulesets

Three repository rulesets, split by who may bypass them:

| Ruleset | Targets | Rules | Bypass |
| --- | --- | --- | --- |
| Signed commits | All branches | Require signed commits | The admin role, for pull request merges only (`bypass_mode: pull_request`) |
| Default branch history | Default branch | Block deletion, block force pushes, require linear history | None |
| Required checks | Default branch | Require `CI passed` from GitHub Actions; omitted when the repository has no CI | The admin role, always |

- **No pull request rule.** The maintainer may push straight to the default branch, and
  straight-to-main repositories have no pull requests at all. Agents still work through
  pull requests, as the rest of this skill describes.
- **No required approvals:** GitHub does not let an author approve their own pull
  request, and agents open pull requests through the maintainer's account.
- **The signed-commits bypass** lets the maintainer merge an external pull request whose
  commits are unsigned; GitHub signs the squash commit. **The required-checks bypass**
  lets the maintainer push straight to the default branch, before any check has run.
- **Agents never use either bypass.** They ask the maintainer to merge an external pull
  request with unsigned commits, and never pass `--admin`.
- **One required check.** The pull request CI workflow has a `CI passed` job (job id
  `ci-passed`) that needs every other job of the workflow, runs with `if: always()`, and
  fails when any of them failed or was cancelled. Rulesets require only that check, so
  adding, renaming or dropping a job or a matrix entry, such as a Python version, needs
  no ruleset change. A new job joins the summary job's `needs`.

Internal commits (the maintainer's and agents') are always signed. CONTRIBUTING.md asks
external contributors to sign when they can; edits in GitHub's web editor are signed by
GitHub. Commits by Dependabot and other external tools keep their own identity as the
squash commit's author. Agents are tools, so no commit carries a `Co-authored-by`
trailer for one.

## Labels

Every repository has exactly these labels and no others, unless a deviation documents
more:

| Group | Labels |
| --- | --- |
| Change type | `bug`, `build`, `chore`, `ci`, `documentation`, `enhancement`, `perf`, `refactor`, `test` |
| State | `triage` |
| Topic | `security` |
| Dependabot | `dependencies` |
| GitHub housekeeping | `duplicate`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix` |

An issue has exactly one change-type label once triaged. The label sets the branch type
and the pull request title type; the `git-branch` skill owns that mapping. Never create
a label outside the baseline; ask the user instead.

## Templates

- **Issue forms** under `.github/ISSUE_TEMPLATE/` add the `triage` label to every issue
  they create. Triage removes it (see the issues reference).
- **Pull request template** at `.github/pull_request_template.md`: the `Closes #N` line,
  Summary, Verification, and Scope notes, as in `assets/pull-request-template.md`.

## Dependabot

In `.github/dependabot.yml`, every update entry sets:

- `commit-message.prefix: build`, with no scope, so squash-merged updates read
  `build: bump ...`;
- `labels: [dependencies, build]`. Setting labels explicitly replaces Dependabot's
  default, so list both.

## Milestones

A milestone is one release, named `vX.Y.Z`. Its issues are the committed work for that
release. Link the brief, if there is one, from the milestone description, which also
states the scope and what needs the user. Do not use GitHub Projects to plan work.

## Ideas without a commitment

On public repositories, enable GitHub Discussions with an "Ideas" category: it is the
Parking Lot for ideas nobody has committed to. Private repositories keep the Parking
Lot in private Notion instead.

## Straight-to-main repositories

A repository whose agent instruction files allow or require committing straight to the
default branch has no branches or pull requests, and its merge settings go unused. The
rulesets above already allow direct pushes. Everything else here still applies:
labels, issue forms, milestones, signed commits.

## Drift checklist

Run these read-only commands, compare with the rules above, and report each
difference. Change nothing unless the user asks (and never through `gh api` when the
settings are managed as code).

```shell
gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed
gh repo view --json deleteBranchOnMerge,isPrivate,hasDiscussionsEnabled
gh api repos/{owner}/{repo} \
  --jq '{title: .squash_merge_commit_title, message: .squash_merge_commit_message}'
gh api repos/{owner}/{repo}/rulesets
gh api repos/{owner}/{repo}/rulesets/<id>
gh label list --limit 200 --json name
gh api "repos/{owner}/{repo}/milestones?state=all" --jq '.[].title'
gh api graphql -f query='{ repository(owner: "<owner>", name: "<repo>") {
  discussionCategories(first: 20) { nodes { name } } } }'
```

Compare each result with the rules:

1. **Merge settings.** Squash allowed; merge commits and rebase merging not allowed;
   branches deleted on merge; squash title `PR_TITLE`, message `BLANK`.
2. **Rulesets.** The three rulesets above exist (take each `<id>` from the list), with
   those targets, rules and bypass modes, and no other ruleset targets the repository.
3. **Labels.** The names match the baseline exactly. Report missing and extra labels.
4. **Templates.** In the checkout, `.github/pull_request_template.md` exists and every
   form under `.github/ISSUE_TEMPLATE/` adds `triage`.
5. **Dependabot.** In the checkout, every entry of `.github/dependabot.yml` sets the
   prefix and labels above.
6. **Milestones.** Every title is `vX.Y.Z`.
7. **Ideas.** On a public repository, Discussions are enabled and the category list
   includes "Ideas".
8. **Deviations.** When anything above differs, AGENTS.md has a "Deviations from the
   shared workflow" section that records the reason for each difference.
