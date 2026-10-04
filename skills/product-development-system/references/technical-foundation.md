# Technical foundation

Record what technical choices and constraints future slices may safely assume today. This is the project's current baseline, not a design of the full future architecture.

## Instantiate and adapt

If the project already has a Technical Foundation document in its repository (see the artifact locations in SKILL.md), read it first. When creating a new one, use `assets/technical-foundation-template.md` from the skill root.

Copy only relevant sections, replace prompts and defaults with actual project choices, and remove inapplicable sections. Defaults are decision prompts, not mandatory standards. The resulting Technical Foundation document must stand on its own and describe the project's current reality.

Finish the instantiated document with a short Current Technical Baseline describing actual choices. Keep that summary consistent with the body. Do not include template instructions, unresolved options, or claims of platform support that have not been verified.

## Decide where a choice belongs

| Kind of information | Home |
| --- | --- |
| A settled technical choice that multiple future slices can assume without reopening | Technical Foundation |
| A local implementation choice or question needed only for the current slice | Slice Brief |
| Rationale, alternatives, and tradeoffs behind a consequential choice | Decision Record |
| A possible future mechanism with no current commitment | Private Parking Lot |

These homes can complement each other: the Foundation states the current choice and links a Decision Record for its rationale. Avoid copying the full rationale into both.

Ask whether the next meaningful vertical slice requires a decision now. If it does not, defer it. A baseline can be very small initially. Consider only relevant choices about application shape, language/runtime, platforms, persistence, interfaces, tooling, tests, diagnostics, security, packaging, dependencies, and cross-cutting constraints.

Decide deliberately how agents participate as contributors, users, or operators; preserve deterministic and verifiable boundaries where needed. Do not introduce AI architecture solely because coding agents are used.

## Maintain from evidence

Review the Foundation after each meaningful slice. Promote choices when evidence makes them durable; revise or remove statements that are no longer true. Preserve consequential rationale by adding or superseding a Decision Record. Template updates do not automatically change a project's established baseline.

The Foundation is ready when it is concise, self-contained, consistent with the current project, and sufficient for the next slice without choosing the whole future stack.
