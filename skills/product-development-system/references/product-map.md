# Product map development

Map the whole intended product at low resolution. Preserve coherence across releases
without designing the entire system or promising every possibility.

Start from the Manifesto and known user workflows. For an existing product, compare
documented intent with observed behavior and identify gaps rather than rewriting intent
to match whatever was built.

## Build the map

- Group major capabilities by user outcome. Distinguish umbrella capabilities from their
  parts and remove duplicates.
- Write the key scenarios: how a Manifesto target user reaches an outcome across
  capabilities. Each names the user and what they are trying to achieve, the trigger,
  the steps across capabilities, the outcome, and the Manifesto principle it
  illustrates, when one applies. Keep scenarios at the outcome level; concrete commands
  and outputs belong in briefs or user documentation.
- Surface cross-cutting product concerns and external ownership or integration
  boundaries.
- Keep important future capability areas visible when they are part of product intent.
  Leave speculative ideas in the Parking Lot.
- Connect capability areas to the Manifesto's capabilities, principles, or boundaries.
  Links or named sections are sufficient; do not invent an identifier system merely for
  traceability.

A compact document can use capability groups, key scenarios, cross-cutting concerns, and
boundaries. Add a diagram only if it clarifies relationships. Distinguish intended
capabilities from those already delivered when useful, but leave issue-level status and
execution detail to GitHub milestones and issues.

Exclude database schemas, API details, exact file formats, algorithms, CLI flags,
detailed acceptance criteria, and task breakdowns. A mechanism may expose a missing
capability; translate it back into the outcome before adding it.

## Keep Now / Next / Later

The Product Map ends with the roadmap, a short Now / Next / Later section in the same
file:

| Column | Holds | Precision |
| --- | --- | --- |
| Now | The outcomes of the current milestone | Precise; matches the milestone description |
| Next | Outcomes planned for the next one or two milestones | Coarse; provisional |
| Later | Intended capabilities with no release yet | One line each, tied to a capability |

Each entry names a user outcome and its capability, not a task. The roadmap has no
dates and no status; a milestone's issues carry execution status. Only Now is
committed, and only because a milestone exists for it.

Move entries left as evidence supports it: Later → Next when a release is in sight,
Next → Now when the user creates its milestone (see
[release planning](release-planning.md)). Update the section during
[release review](release-review.md), not whenever a thought arrives. An entry that stays
in Later without a release is still part of product intent; an idea that is not yet
intent belongs in the Parking Lot.

## Challenge and finish

Use the agent as a systems thinker: find omissions, overlaps, and inconsistent
boundaries. Ask whether a missing area was deliberately excluded or simply overlooked.
Check that the key scenarios make sense end to end and that the map follows the
Manifesto.

The map is ready when it gives enough context to choose a coherent next outcome without
designing distant work. Promote a clean version to Git when it begins guiding
implementation, then use release planning to choose what goes into the next milestone.
Do not turn each map entry into an issue.
