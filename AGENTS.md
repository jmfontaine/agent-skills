# Agent Skills

## Project Overview

Skills targeting, in order of priority, omp, Claude, ChatGPT, Claude Code, and Codex,
following the [Agent Skills specification](https://agentskills.io/specification). Other
agents are neither targeted nor tested. Skills install with
`npx skills add jmfontaine/agent-skills`, or are uploaded to Claude and ChatGPT.

**Repository:** <https://github.com/jmfontaine/agent-skills>

## Project Structure

```text
docs/
└── workflow.md                  # The shared workflow, glossary, and setup
skills/
├── git-branch/                  # Git branch naming guidelines
├── git-commit/                  # Git commit guidelines
├── github-workflow/             # GitHub issues, pull requests, and reviews
├── parallel-issues/             # Unattended agents on GitHub issues in parallel
├── product-development-system/  # Product development lifecycle and focused resources
├── project-review/              # Project file review
├── python-codebase-review/      # Whole-codebase Python review
├── review-verification/         # Verify an existing review file's findings
└── uv/                          # Python package management with uv
```

Each skill is a directory containing a `SKILL.md` (YAML frontmatter plus Markdown
instructions) and optional `scripts/`, `references/`, or `assets/` directories.

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md` with `name` (identical to the directory name)
   and `description` (what the skill does and when to use it) in the frontmatter.
2. Add the skill to the list in `README.md`.

## Development

[rumdl](https://rumdl.dev) formats and lints Markdown, wrapping prose at 88 columns
(`.rumdl.toml`). [CSpell](https://cspell.org) checks spelling against the word list in
`cspell.json`, which the VS Code Code Spell Checker extension reads too: add words with
its "Add Word to CSpell Configuration" command. [prek](https://prek.j178.dev) runs both
with general file checks as pre-commit hooks (`.pre-commit-config.yaml`). Recipes live
in the `justfile`:

- `just setup`: Install the Git pre-commit hook.
- `just format`: Format Markdown. Run after editing any Markdown file.
- `just spell`: Check spelling (the `cspell` hook).
- `just qa`: Check formatting, lint, spelling, and retired terms (the `banned-terms`
  hook).
- `just package`: Zip each skill into `dist/<skill-name>.zip` for Claude and ChatGPT.

The QA workflow (`.github/workflows/qa.yml`) runs the same hooks on pushes and pull
requests to `main`. Dependabot updates the pinned actions and hook revisions weekly.

## Gotchas

- Keep skills flat at `skills/<skill-name>/SKILL.md`. omp does not discover nested
  category directories.
- `name` allows lowercase letters, digits, and single hyphens, up to 64 characters.
  `description` allows up to 1024 characters.
- Avoid names that collide with agent built-ins. For example, Claude Code's `/review`
  alias shadows a skill named `review`.
- `allowed-tools` is optional and experimental: a space-separated list of Claude Code
  permission rules (e.g., `Bash(git add:*) Bash(git commit:*)`). Support varies by
  agent.
- Write skill bodies for every target agent where practical, omp first. Say
  "agent instruction files (AGENTS.md, CLAUDE.md)" instead of naming one agent's file.
  When a skill relies on one agent's features, such as omp's `task` subagents, say so in
  its `compatibility` field.
- `npx skills add` copies the whole skill directory, so keep files the skill does not
  need at runtime out of `skills/<skill-name>/`.
- Skills have no version field. `npx skills update` detects changes from the skill
  folder's contents.
- Use the glossary in `docs/workflow.md` for workflow terms. The `banned-terms` hook
  rejects retired terms under `skills/`.

## Shared workflow

This repository follows the shared workflow: the `github-workflow` skill's repository
setup describes its GitHub settings, rulesets, labels and templates. Those settings are
managed as code outside this repository; change them there, never with `gh api` or the
GitHub web UI.

It is a straight-to-main repository: commit directly on `main`, with no branches or
pull requests.

### Deviations from the shared workflow

None.

## Key Files

- `skills/*/SKILL.md`: Skill definitions
- `README.md`: Installation instructions and skill list
- `justfile`: Formatting, linting, and pre-commit recipes
