---
name: dependency-alternatives
description: Audit a repository's dependencies (runtime packages, dev and QA tools, build backends, task runners, CI actions, container images) and research alternatives to the ones the user picks. Maps which features the repository actually uses, compares candidates on feature coverage, project health, adoption and risk with cited and dated sources, rates migration effort, and recommends switch, consider, or keep. Read-only. Use for "what could replace httpx", "are there better alternatives to our dependencies", "is black still the best formatter for us", "which of our tools are abandoned", or `/dependency-alternatives [name]`. Not for upgrading or adding dependencies (uv) or for reviewing the code itself (python-codebase-review).
compatibility: Needs web access (search and page fetching) for current health and adoption data. An authenticated gh CLI gives more precise GitHub metrics but is optional. Subagents (omp's task, Claude Code's subagents) speed up research on several dependencies but are optional.
---

# Dependency Alternatives

Find out whether the repository's dependencies are still the right choices, and what
replacing one would cost. A dependency is judged by what this repository uses it for,
not by its full feature list: an alternative that lacks a feature nobody here calls is
still a full replacement.

"Keep the current dependency" is a valid and common outcome. The goal is an honest
comparison, not a list of switches.

## Scope

- Read-only. Never modify code, configuration, manifests, or lockfiles, and never run
  commands that do: installs into the project's environment, `uv lock`, `npm install`,
  formatters or linters with `--fix`. Reading files, searching, and querying registries
  and APIs are fine.
- When a claim needs a probe (does candidate X support feature Y?), run it in a
  temporary directory outside the repository and delete it afterwards.
- The report goes in chat. Write a file only when the user asks for one.
- Establish today's date first (`date +%F`, or the date the agent's context gives).
  It is the research date in the report, and "the last 12 months" counts back from it.

## Invocation

- **No argument:** run the whole workflow, steps 1 to 5.
- **A dependency name** (`/dependency-alternatives httpx`): skip discovery and
  selection. Confirm the repository actually uses it: declared in a manifest, a tool
  configuration, a workflow, or an image reference, and used in code, configuration,
  or a command. Account for names that differ between the registry and the import
  (`beautifulsoup4` and `bs4`, `pyyaml` and `yaml`) and for separator variants
  (`ruamel-yaml`, `ruamel.yaml`). Then:
  - not found: say so, name any close matches, and stop;
  - declared, but no usage found (see step 1): say so, name the places you searched,
    point out that it may be removable, and stop;
  - several matches (`pytest` and `pytest-cov`): list them and ask which one;
  - used: run steps 3 to 5 for that dependency only.

## 1. Discover dependencies

Inventory every direct dependency, not just runtime packages. Check what applies:

- **Manifests and lockfiles:** `pyproject.toml` (project, optional and dependency
  groups, build-system), `requirements*.txt`, `setup.cfg`, `setup.py`, `Pipfile`,
  `poetry.lock`, `uv.lock`, `package.json`, and the equivalents of other ecosystems
  (`Cargo.toml`, `go.mod`, `Gemfile`, …). Use lockfiles only to resolve versions and to
  tell direct dependencies from transitive ones.
- **Development and QA tooling:** test runners and their plugins, linters, formatters,
  type checkers, coverage, spell checkers, and `.pre-commit-config.yaml` hooks.
- **Build and tasks:** build and packaging backends; task runners (`Makefile`,
  `tox.ini`, `noxfile.py`, `justfile`) and the tools they call without declaring them,
  such as `uvx`, `npx`, or `pipx run` invocations.
- **CI/CD:** GitHub Actions workflows and composite actions, including every
  third-party action in `uses:`, and other pipeline configurations.
- **Containers and infrastructure:** `Dockerfile` base images, `docker-compose`
  services, and other image references.

A dependency is something the repository declares, or something its code, scripts,
tasks, or CI import or run without declaring it. A tool that only appears in prose,
such as a prerequisite the README tells readers to install, is not one. Leave out
transitive dependencies, except one the code imports directly: list it, and note that
it is undeclared.

While finding each dependency's role, note any declared one with no usage found.
Some usage never shows up as an import. Count these as used:

- a plugin that loads through an entry point or configuration (pytest, mkdocs,
  Flake8), when the repository runs its host tool;
- a type stub package (`types-requests`), when the code imports the package it types;
- a driver or optional extra selected by a connection string or another package
  (`psycopg` behind a SQLAlchemy URL, `uvicorn[standard]`);
- a build backend named in the build configuration, and a tool that a system outside
  the repository runs, such as a deployment system, when the repository documents it.

Flag the rest as "no usage found", never "unused": the search can still miss
something, such as a developer running the tool by hand.

Group the dependencies by category: runtime, testing, linting and formatting, typing,
build, CI, infrastructure, and other for anything that fits none. Omit empty
categories. List a dependency once, even when several places declare or pin it.

## 2. Let the user choose

Present one numbered list, numbered continuously across the category headings. The
list is for choosing, so keep each entry to the name and a few words on its role in
this repository: no versions, file counts, or configuration details, which belong in
step 3. For a dependency with no usage found, the entry says so instead:

```markdown
**Runtime**

1. httpx: HTTP client for the GitHub API
2. pydantic: validates the configuration and API responses
3. requests: no usage found

**Testing**

4. pytest: test runner
5. pytest-cov: coverage report in CI

**CI**

6. actions/setup-python: installs Python in CI
```

When some dependencies have no usage found, list their numbers in one line above the
question, with the places searched, and say they may be removable. Keep them
selectable. Then ask which numbers
to research. Accept ranges (`1-4`), comma-separated values (`1,3,7`), a mix of both,
or `all`. Do no research until the user answers.

## 3. Map actual feature usage

For each selected dependency, find which of its features the repository uses. Search:

- imports and API calls, including attributes, classes, and keyword arguments that
  carry behavior (`httpx.AsyncClient`, `follow_redirects=True`, retries, timeouts);
- CLI invocations in task runners, CI, scripts, and documentation of the dev workflow,
  with their flags;
- configuration sections (`[tool.ruff]`, `.coveragerc`, `jest.config.js`), the rules
  or options enabled, and plugins;
- for actions, the inputs used; for images, the runtime version, OS packages,
  architecture, and anything the build relies on from the image.

Record each feature with evidence: file paths and one or two representative usages.
Count the files that touch the dependency; migration effort depends on it. This
feature list is the baseline for comparison. Features of the current dependency that
the repository does not use are irrelevant.

When the user selects a dependency with no usage found, search again with these
methods. If the baseline is still empty, skip step 4 for it: in step 5, give the
places searched instead of the baseline and comparison, and recommend Remove.

## 4. Research alternatives

Find candidates in the ecosystem's comparison articles, curated lists, the current
dependency's issue tracker (users often name what they moved to), and registries.
Consider two candidates that are easy to miss: the standard library or no dependency
at all, and a dependency the repository already has that could absorb this one's job
(one tool replacing a linter, a formatter, and an import sorter).

Run the same health check on the current dependency, so the comparison is fair.

For each candidate, collect:

- **Feature coverage:** each baseline feature as full, partial (name the workaround),
  or missing. Exclude a candidate that misses a baseline feature with no reasonable
  workaround, and record why.
- **Project health** as of the research date: latest release date, commits over the
  last 12 months, active maintainers (people who committed or merged in that period),
  open and closed issues and pull requests, and response time (median time to a first
  maintainer reply on a sample of recent issues; give the sample size and ignore bot
  replies).
- **Adoption and community:** downloads, GitHub stars, notable users, documentation
  quality, and the ecosystem of plugins and integrations.
- **Risk factors:** license compatibility with the repository's license, supported
  language and runtime versions against the repository's own constraints, known
  security advisories, and the risk of a single maintainer or of a company abandoning
  the project.
- **New possibilities:** capabilities beyond the baseline that would meaningfully help
  this repository, such as performance, typing, async support, or simpler
  configuration. Tie each one to something in the repository, not to the candidate's
  marketing.

Useful sources, each to cite with a link:

- Registries: `https://pypi.org/pypi/<name>/json`, `https://registry.npmjs.org/<name>`,
  Docker Hub, the GitHub Marketplace for actions.
- Downloads: `https://pypistats.org/api/packages/<name>/recent`,
  `https://api.npmjs.org/downloads/point/last-month/<name>`, Docker Hub pull counts.
- GitHub, through `gh api` when it is authenticated: `repos/<owner>/<repo>`, its
  releases, `stats/commit_activity` (it can answer 202 while GitHub computes it; retry
  once, then use the commits endpoint with `since=`), and `search/issues` queries for
  open and closed counts.
- Advisories: [OSV](https://osv.dev), the GitHub Advisory Database (`gh api advisories`
  with `ecosystem` and `affects`).
- Runtime support schedules: [endoflife.date](https://endoflife.date).

A metric you could not verify is marked `unverified` with the reason (rate limit, no
public repository, no download data for actions). Never estimate one.

With several dependencies selected, research them in parallel: one subagent per
dependency, given steps 3 and 4 of this skill, the research date, and the report format
of step 5. Check their strongest claims yourself before reporting them: a project
called abandoned, a security advisory, or a feature called missing.

## 5. Report

Use this structure:

````markdown
# Dependency alternatives: <repository>

Researched on <YYYY-MM-DD>. Health metrics go stale; check them again before acting.

## <dependency> (<category>)

**Role:** what it does in this repository.

**Baseline features:**

| Feature | Evidence |
| --- | --- |
| Async requests | `src/app/client.py:42` `httpx.AsyncClient(...)`, 6 files |

**Health:** one paragraph, with the same metrics as the table below.

### Comparison

| | Current: <name> | <candidate A> | <candidate B> |
| --- | --- | --- | --- |
| <baseline feature 1> | Full | Full | Partial: <workaround> |
| Latest release | | | |
| Commits, last 12 months | | | |
| Active maintainers | | | |
| Issues open / closed | | | |
| Pull requests open / closed | | | |
| Median first response | | | |
| Downloads per month | | | |
| GitHub stars | | | |
| License | | | |
| Runtime support | | | |
| Known advisories | | | |

**Excluded:** <candidate C>: no support for <feature>, and no workaround.

### <candidate A>

- **Pros:**
- **Cons:**
- **New possibilities:**
- **Migration effort:** Low, Medium, or High, with the number of affected files, the
  API differences, the configuration changes, and the impact on tests.

**Recommendation:** Switch to <A>, Consider <A>, or Keep <current>, with the reason.

**Sources:** numbered links, referenced from the table and text.

## Summary

| Rank | Change | Recommendation | Value | Effort | Why |
| --- | --- | --- | --- | --- | --- |

Kept: <dependencies>.
````

- Give the pros, cons, new possibilities, and migration effort for each recommended
  alternative, not for every viable one.
- **Migration effort:** Low for a drop-in or configuration-only change in a few files;
  Medium for API differences across several modules, or test changes; High for
  pervasive use, behavior that differs in ways tests may not catch, or a change that
  forces other dependencies to move.
- **Switch:** a clear improvement that is worth scheduling. **Consider:** a real gain
  with a tradeoff or a condition, which the recommendation names. **Keep:** no
  candidate is better enough to justify the migration. When no viable alternative
  exists at all, say so. **Remove:** no usage found after the step 3 search; name what
  would confirm it, such as removing it and running the tests and CI.
- In the summary, rank only the switch, consider, and remove recommendations, by value
  to effort, the most worthwhile first. Kept dependencies never get a row: list them
  in the "Kept" line. When every recommendation is keep, leave out the table and give
  only that line.
