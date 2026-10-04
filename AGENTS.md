# Agent Skills

## Project Overview

A collection of agent-agnostic skills following the [Agent Skills specification](https://agentskills.io/specification). Skills install with `npx skills add jmfontaine/agent-skills` into Claude Code, Codex, omp, and other agents, or are uploaded to Claude and ChatGPT.

**Repository:** https://github.com/jmfontaine/agent-skills

## Project Structure

```
skills/
├── git-branch/            # Git branch naming guidelines
├── git-commit/            # Git commit guidelines
├── manifesto-refinement/  # Product manifesto refinement
├── project-review/        # Project file review
└── uv/                    # Python package management with uv
```

Each skill is a directory containing a `SKILL.md` (YAML frontmatter plus Markdown instructions) and optional `scripts/`, `references/`, or `assets/` directories.

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md` with `name` (identical to the directory name) and `description` (what the skill does and when to use it) in the frontmatter.
2. Add the skill to the list in `README.md`.

## Gotchas

- Keep skills flat at `skills/<skill-name>/SKILL.md`. omp does not discover nested category directories.
- `name` allows lowercase letters, digits, and single hyphens, up to 64 characters. `description` allows up to 1024 characters.
- Avoid names that collide with agent built-ins. For example, Claude Code's `/review` alias shadows a skill named `review`.
- `allowed-tools` is optional and experimental: a space-separated list of Claude Code permission rules (e.g., `Bash(git add:*) Bash(git commit:*)`). Support varies by agent.
- Write skill bodies for any agent. Say "agent instruction files (AGENTS.md, CLAUDE.md)" instead of naming one agent's file.
- `npx skills add` copies the whole skill directory, so keep files the skill does not need at runtime out of `skills/<skill-name>/`.
- Skills have no version field. `npx skills update` detects changes from the skill folder's contents.
- `CLAUDE.md` only imports this file for Claude Code versions that don't read `AGENTS.md`. Edit `AGENTS.md`.

## Key Files

- `skills/*/SKILL.md`: Skill definitions
- `README.md`: Installation instructions and skill list
