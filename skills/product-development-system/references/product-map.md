# Product map development

Map the whole intended product at low resolution. Preserve coherence across slices without designing the entire system or promising every possibility.

Start from the Manifesto and known user workflows. For an existing product, compare documented intent with observed behavior and identify gaps rather than rewriting intent to match whatever was built.

## Build the map

- Group major capabilities by user outcome. Distinguish umbrella capabilities from their parts and remove duplicates.
- Sketch the main user journeys or lifecycle stages connecting those capabilities.
- Surface cross-cutting product concerns and external ownership or integration boundaries.
- Keep important future capability areas visible when they are part of product intent. Leave speculative ideas in the private Parking Lot.
- Connect capability areas to the Manifesto's capabilities, principles, or boundaries. Links or named sections are sufficient; do not invent an identifier system merely for traceability.

A compact document can use capability groups, key journeys, cross-cutting concerns, and boundaries. Add a diagram only if it clarifies relationships. Distinguish intended capabilities from those already delivered when useful, but leave live sequencing and execution status to GitHub Projects.

Exclude database schemas, API details, exact file formats, algorithms, CLI flags, detailed acceptance criteria, and task breakdowns. A mechanism may expose a missing capability; translate it back into the outcome before adding it.

## Challenge and finish

Use the agent as a systems thinker: find omissions, overlaps, and inconsistent boundaries. Ask whether a missing area was deliberately excluded or simply overlooked. Check that the main journeys make sense end to end and that the map follows the Manifesto.

The map is ready when it gives enough context to choose a coherent next outcome without designing distant work. Promote a clean version to Git when it begins guiding implementation, then use milestone planning to choose what happens next. Do not turn each map entry into an issue.
