# Milestone planning

Turn the Product Map into a small rolling sequence of coherent user outcomes. A milestone describes a capability, not a work breakdown or necessarily a GitHub Milestone object.

Review the Manifesto, Product Map, previous slice's evidence, relevant Technical Foundation constraints, and private Parking Lot when available. User-reported issues are input to triage, not automatic commitments. Contributors must still be able to plan from canonical artifacts without private context.

## Choose outcomes

Prefer “a user can archive one source and later verify its integrity” to “implement the database layer.” Find the smallest meaningful end-to-end capability that advances product intent or tests an important assumption. Explain why it is useful now and what makes it demonstrable.

Keep a few upcoming milestones visible, typically 3–6 when there is enough known work. This is a useful horizon, not a quota. Treat only the next milestone as strongly committed; later milestones remain provisional and coarse. Do not invent future work to fill the plan.

For each planned outcome, retain a brief description, its Product Map connection, essential dependencies, and what would demonstrate success. Give the next outcome an appetite and refine it into the active slice's boundary. An appetite is how much effort the user is willing to invest, not a prediction or guaranteed delivery date. Use an established budget or propose one explicitly; do not treat an agent's estimate as an agreed commitment.

If an outcome is too large, split it into smaller end-to-end slices or narrow supported inputs, platforms, or variations. Keep necessary technical work inside the outcome it enables. An exceptional enabling task should have a concrete consumer and bounded purpose, not become a speculative architecture milestone.

## Keep the plan in GitHub Projects

Use project items for milestones and sequencing; a milestone need not be an issue. Reuse existing fields and views. Roadmap, Now / Next, and Active Work views can help when needed; do not create a custom tracking system by default.

Create internal issues only for actionable work in an active or deliberately committed near-term slice. Do not decompose distant milestones into issues. Consult the artifact-lifecycle reference for promotion and intake rules before changing work items.

When appetite is exceeded, first defer variations, integrations, optimizations, or generalization while preserving a useful vertical outcome. Present the tradeoff if meaningful delivery still does not fit; the user decides whether to change the appetite or outcome.

## Replan

After a slice review, reassess the next outcome before starting it. Reorder, split, combine, or remove milestones based on evidence. Update product intent in Git where justified and status or sequencing in GitHub Projects. Prepare a detailed Slice Brief only for the selected current increment.
