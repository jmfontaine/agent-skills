# Architecture section template

<!-- Section skeleton for AGENTS.md: copy everything below this comment into AGENTS.md as its "## Architecture" section. Keep the entries that apply, replace prompts with actual settled choices, and delete the rest and these comments. Keep choices local to one piece of work in its brief or issue; link an ADR for consequential rationale instead of repeating it. -->

## Architecture

### Shape

[State the actual or committed shape: CLI, library, web app, service, desktop app,
worker, or a necessary combination. Name the main components in a sentence or two.]

### Language, runtime, and tooling

[Record chosen languages and versions, major frameworks, package manager, formatting,
linting, type checking, and code generation where established. State supported
platforms only when verified.]

### Structure

[Describe useful navigation conventions: where code, tests, and documentation live.
Link existing contributor guidance rather than duplicating it.]

### Testing

[State the baseline for meaningful behavior checks: system boundaries, primary
workflows, regressions, and supported platforms. Name the command that runs them.]

### Distribution

[State committed build artifacts, versioning, installation and publishing channels, and
signing requirements where applicable.]

### CI

[Record required checks, the build/test matrix, and release or dependency automation.]

### Agent support

[Record the actual role of coding agents, agent users or operators, machine-readable
interfaces, and deterministic or independently verifiable boundaries.]

### Durable constraints

[State cross-cutting constraints that future work may assume, such as persistence,
compatibility, security, or dependency rules. Link ADRs for consequential rationale.]
