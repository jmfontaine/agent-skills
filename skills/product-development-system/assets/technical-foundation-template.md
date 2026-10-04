# Technical Foundation

<!-- Adapt relevant sections to actual settled choices. Remove unused sections, prompts, and these comments. Keep unresolved and slice-local choices in the Slice Brief; preserve consequential rationale in Decision Records. -->

## Engineering principles

[Record adopted durable engineering preferences. Prompts include simple mature
technology, maintainability, operational simplicity, interoperability, useful
automation, and observable and testable behavior.]

## Application shape

[State the actual or committed shape: CLI, library, web app, service, desktop app,
worker, or a necessary combination.]

## Language, runtime, and tooling

[Record chosen languages and versions, major frameworks, package manager, formatting,
linting, type checking, and code generation where established.]

## Repository structure

[Describe useful navigation conventions. Link existing contributor and agent guidance
rather than duplicating it.]

## Supported platforms

[State verified platforms and architecture or runtime constraints. Distinguish tested
support from intentions.]

## Persistence and storage

[Record settled storage choices and applicable migration, backup, and integrity
expectations.]

## APIs and integrations

[Record established interface, format, compatibility, authentication, error, and
machine-readable access conventions. Do not design unused interfaces.]

## Testing

[State the baseline for meaningful behavior checks, system boundaries, primary
workflows, regressions, and supported platforms.]

## Observability and diagnostics

[Record applicable logging, metrics, tracing, or diagnostic expectations, scaled to this
project.]

## Security and secrets

[State applicable secret handling, privilege, sensitive data, dependency, and
authorization expectations. Never include credentials.]

## Packaging and distribution

[State committed build artifacts, versioning, installation and publishing channels, and
signing requirements where applicable.]

## CI/CD and automation

[Record established required checks, build/test matrix, and release or dependency
automation.]

## AI and agent support

[Record the actual role of coding agents, agent users or operators, machine-readable
interfaces, and deterministic or independently verifiable boundaries.]

## Dependency policy

[Record adopted rules for dependency selection, version constraints, maintenance burden,
and infrastructure additions.]

## Architectural constraints

[State durable cross-cutting constraints that future slices may assume. Link Decision
Records for consequential rationale.]

## Current Technical Baseline

<!-- Finish with a short summary of actual choices, consistent with the sections retained above. Omit entries that do not apply. -->

- **Application shape:** [Choice]
- **Language/runtime:** [Choice]
- **Persistence:** [Choice]
- **Supported platforms:** [Verified support]
- **Testing:** [Baseline]
- **Distribution:** [Choice]
- **Key constraints:** [Durable constraints]
