---
name: project-review
description: Review project files for consistency, completeness, correctness, and simplicity. Use when asked to review, audit, check, validate, or simplify project configuration files (justfile, Makefile, CI workflows, pre-commit config, pyproject.toml, Dockerfile, docker-compose, etc.) or documentation files (README, AGENTS.md, CLAUDE.md, CONTRIBUTING, etc.). Flags accidental complexity such as duplication, indirection, and dead or redundant settings. Supports both single-file review and cross-file checks.
---

# Project File Review

Review project files across four dimensions, then suggest fixes and improvements.

## Dimensions

- **Consistency**: Naming conventions, formatting, patterns, and style are uniform within and across files.
- **Completeness**: Nothing is missing. All referenced targets, commands, variables, and dependencies exist. All expected sections are present.
- **Correctness**: Syntax is valid. Commands work. Paths exist. Versions are compatible. Logic is sound.
- **Simplicity**: No accidental complexity, meaning complexity the project's needs do not require. Look for:
  - Dead weight: unused targets, variables, dependencies, stages, hooks, and documentation for removed features.
  - Redundancy within the file: settings that restate tool defaults, duplicated steps or blocks that could share a definition, and sections that repeat each other. Report duplication across files in Phase 2 instead.
  - Needless indirection: wrappers that only forward arguments, targets that only call one other target, scripts that reimplement what a tool already does.
  - Over-engineering: parameters, matrix entries, environment variables, or abstractions with a single use or no use.
  - Convoluted processes: multi-step instructions or workflows that a single command or built-in tool feature could replace.

  Every simplification must preserve required behavior. When a simplification drops something (a platform, a version, a workflow), state what is lost so the user can decide.

## Workflow

### Phase 1: Individual File Review

Review each file separately. For each file:

1. Read the file fully.
2. Evaluate against all four dimensions.
3. Report findings grouped by dimension.
4. Suggest specific fixes with code snippets.

### Phase 2: Cross-File Alignment

When multiple files are provided, or after individual reviews, check alignment across files:

1. Verify shared references match (e.g., target names in justfile match CI workflow steps, Python version in pyproject.toml matches CI matrix and Dockerfile).
2. Check that documented commands in README match actual targets/scripts.
3. Confirm dependency lists are synchronized (e.g., pyproject.toml vs requirements files vs CI install steps).
4. Ensure agent instruction files (AGENTS.md, CLAUDE.md) reflect the actual project structure and tooling.
5. Find duplication across files that could collapse to a single source of truth (e.g., a Python version repeated in four files instead of read from one, CI steps reimplementing justfile recipes instead of calling them, CLAUDE.md copying AGENTS.md instead of importing it). Skip overlap that serves different readers, such as README and AGENTS.md both listing setup commands, unless one file can reference the other.

### Discovery Mode

When reviewing a file, suggest other project files that should be cross-checked. Common relationships:

- **justfile / Makefile** <-> CI workflows, README, pre-commit config
- **pyproject.toml** <-> Dockerfile, CI workflows, pre-commit config
- **README** <-> AGENTS.md, CLAUDE.md, justfile, CI workflows
- **Dockerfile** <-> docker-compose, CI workflows, pyproject.toml
- **pre-commit config** <-> CI workflows, pyproject.toml

Offer to review related files the user hasn't mentioned yet.

## Output Format

For each file, report:

```
### <filename>

#### Consistency
- [finding + suggested fix]

#### Completeness
- [finding + suggested fix]

#### Correctness
- [finding + suggested fix]

#### Simplicity
- [complexity + simpler alternative + anything lost]
```

After all individual reviews, add a cross-file section:

```
### Cross-File Alignment
- [inconsistency or duplication + which files + suggested fix]
```

Omit empty sections. Prioritize actionable findings over nitpicks.
