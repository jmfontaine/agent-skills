# Architecture section

Record what technical choices and constraints future work may safely assume today. The
Architecture section of AGENTS.md is the project's current technical baseline, not a
design of the full future architecture. It lives in the agent instruction file so
contributors and coding agents read it with every task.

## Write or revise the section

If AGENTS.md already has an Architecture section, read it first. When creating one, use
[`assets/architecture-section-template.md`](../assets/architecture-section-template.md).

Keep only the entries that apply, replace prompts with actual project choices, and
delete the rest. Defaults are decision prompts, not mandatory standards. The section
must describe the project's current reality, be self-contained, and stay short enough
that an agent reads it every time. Link longer material (an ADR, a design note) instead
of inlining it. Do not include template instructions, unresolved options, or claims of
platform support that have not been verified.

If a repository has both AGENTS.md and CLAUDE.md, put the section where the repository
already keeps shared guidance, and make the other file point to it.

## Decide where a choice belongs

| Kind of information | Home |
| --- | --- |
| A settled technical choice that future work can assume without reopening | Architecture section |
| A local implementation choice or question needed only for one piece of work | Brief, or the issue |
| Rationale, alternatives, and tradeoffs behind a consequential choice | ADR |
| A possible future mechanism with no current commitment | Parking Lot |

These homes complement each other: the Architecture section states the current choice
and links an ADR for its rationale. Avoid copying the full rationale into both.

Ask whether the next release requires a decision now. If it does not, defer it. A
baseline can be very small initially. Consider only relevant choices about application
shape, language/runtime, tooling, repository structure, testing, distribution, CI,
agent support, and durable constraints.

Decide deliberately how agents participate as contributors, users, or operators;
preserve deterministic and verifiable boundaries where needed. Do not introduce AI
architecture solely because coding agents are used.

## Maintain from evidence

Review the section during each [release review](release-review.md). Promote choices when
evidence makes them durable; revise or remove statements that are no longer true.
Preserve consequential rationale by adding or superseding an ADR. Template updates do
not automatically change a project's established baseline.

The section is ready when it is concise, consistent with the current project, and
sufficient for the next release without choosing the whole future stack.
