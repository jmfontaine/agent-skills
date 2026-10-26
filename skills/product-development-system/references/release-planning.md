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
database layer.” Size a release by what is worth shipping to a user, not by the
smallest outcome that can be demonstrated. Explain why each outcome is useful now and
what makes it demonstrable.

A milestone holds two to four related outcomes from Next. For each, keep a brief
description, its Product Map capability, essential dependencies, and what would
demonstrate success. Do not invent work: work that does not trace to the Product Map
does not belong in a release. Pulling in Next outcomes, or bugs found during the
release, is not invented work. Fix small bugs found during a release in that release,
unless the user says otherwise.

If an outcome is too large to ship in one release, narrow supported inputs, platforms,
or variations. Keep necessary technical work inside the outcome it enables. An
exceptional enabling task needs a concrete consumer and bounded purpose; it must not
become a speculative architecture release.

## Set scope and the user's checkpoints

Write the scope boundary (in scope, out of scope) in the milestone description, with
the cut order: what to cut first if scope grows, preserving a useful end-to-end
outcome. A brief may set a narrower scope and cut order for its own work.

List what needs the user, in this order: product decisions, checks only the user can do
(by-hand checks), and merges and releases. The user's attention is the scarce resource,
so name each of these up front.

Give open-ended work (a spike, method research, an approach not yet settled) a stop
rule: the condition at which the agent stops and reports, for example “stop and report
if the method is not settled after the spike.”

When scope grows, first defer variations, integrations, optimizations, or
generalization while preserving a useful end-to-end outcome. Present the tradeoff if
meaningful delivery still does not fit; the user decides whether to change the scope or
the outcome.

## Estimate

When the user asks how long something will take, estimate from the recorded durations of
past milestones; [release reviews](release-review.md) record them. Give agent time and
the user's time separately. Never estimate as if a person were writing the code.

## Commit the work

The milestone description states the outcomes, the scope and cut order, what needs the
user, and links to the Product Map section and to any [brief](brief.md). Create issues
only for work committed to the milestone, and give each the milestone. An issue without
a milestone is accepted, not committed. Do not decompose Next or Later into issues;
they stay as roadmap entries.

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
