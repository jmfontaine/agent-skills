# Release planning

Choose what the next release delivers. The release plan is a GitHub milestone named
`vX.Y.Z`; its issues are the committed work. The roadmap is the Now / Next / Later
section of the [Product Map](product-map.md). Do not create a separate tracking system.

Review the Manifesto, the Product Map, the previous release review, the Architecture
section and ADRs that constrain the work, and the Parking Lot when available.
User-reported issues are input to triage, not automatic commitments. Contributors must
still be able to plan from canonical artifacts without private context.

## Choose what goes into the next milestone

Prefer “a user can archive one source and later verify its integrity” to “implement the
database layer.” Find the smallest meaningful end-to-end outcome that advances product
intent or tests an important assumption. Explain why it is useful now and what makes it
demonstrable.

A milestone holds one or a few related outcomes. For each, keep a brief description, its
Product Map capability, essential dependencies, and what would demonstrate success. Do
not invent work to fill a release.

If an outcome is too large, split it into smaller end-to-end releases or narrow
supported inputs, platforms, or variations. Keep necessary technical work inside the
outcome it enables. An exceptional enabling task needs a concrete consumer and bounded
purpose; it must not become a speculative architecture release.

## Set the appetite

Write the appetite in the milestone description. An appetite is how much effort the user
is willing to invest, not a prediction or a guaranteed delivery date. Use an established
budget or propose one explicitly; do not treat an agent's estimate as an agreed
commitment. A brief may set a narrower appetite for its own work.

When appetite is exceeded, first defer variations, integrations, optimizations, or
generalization while preserving a useful end-to-end outcome. Present the tradeoff if
meaningful delivery still does not fit; the user decides whether to change the appetite
or the outcome.

## Commit the work

The milestone description states the outcomes, the appetite, and links to the Product
Map section and to any [brief](brief.md). Create issues only for work committed to the
milestone, and give each the milestone. An issue without a milestone is accepted, not
committed. Do not decompose Next or Later into issues; they stay as roadmap entries.

Issues cite the brief's acceptance criteria rather than copying them. The
`github-workflow` skill, if installed, covers milestones, issue format, and labels. See
[artifact lifecycle](artifact-lifecycle.md) for promotion and triage rules.

## Update Now / Next / Later

When the milestone is created, move its outcomes into Now and shift the rest of the
roadmap: Next becomes the following one or two releases, and Later keeps the intended
capabilities. Keep Next to what is actually planned. Do not list more future releases
than there is known work for.

## Replan

After a [release review](release-review.md), reassess the next outcome before starting
it. Reorder, split, combine, or remove roadmap entries based on evidence. Update product
intent in Git where justified, then create the next milestone and, if the work needs it,
its brief.
