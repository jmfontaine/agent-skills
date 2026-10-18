# Artifact lifecycle and source of truth

Use one canonical home per kind of information. Authority follows the artifact's
purpose; a newer timestamp or a planning item does not silently override product intent.

| Home | Authoritative for | Boundaries |
| --- | --- | --- |
| Skill package | Reusable process guidance and templates | Project documents record adapted project choices |
| Git | Durable product intent (Manifesto, Product Map with Now / Next / Later), briefs, ADRs, the Architecture section, contributor and agent guidance | Change through pull requests and review as diffs after promotion |
| GitHub milestones and issues | The release plan (one milestone per release), committed work and its execution status, user-reported issues | Planned work, not a collection of vague possibilities; user-reported issues stay untriaged until triaged |
| Discussions or Notion | Parking Lot (uncommitted ideas), exploration, research, rough drafts, private discussion. Discussions “Ideas” category on a public repository; private Notion otherwise | Never a dependency for contributors or the authority over promoted Git artifacts |

## Promote cleanly

Promote an artifact when it materially affects what contributors or coding agents should
build. Use the artifact locations in SKILL.md unless the repository already has its own
conventions; do not create a parallel structure.

Read the latest source and any existing canonical version. Extract settled decisions
into clean, self-contained Markdown. Remove private conversation, sensitive context,
template instructions, and dependencies on private links. Preserve reasoning needed by
contributors in the Git artifact or a linked ADR.

A brief, when there is one, must be canonical in Git before implementation. After
promotion, future edits must happen in Git and be reviewable as diffs. Notion may retain
exploration history, but do not maintain two competing editable authorities or require
contributors to know that history exists.

When sources conflict, use Git for promoted intent and baseline, GitHub milestones for
the current release plan, and issues for reported behavior or scoped work. Treat new
reports and private discussion as evidence that may justify a deliberate update, not an
automatic override. Explain a material conflict instead of silently resolving product
judgment by recency.

## Move possibilities into commitments deliberately

The usual internal path is:

`Parking Lot → Product Map → Milestone → Brief (when needed) → Issue`

This is a promotion model, not a requirement to create an artifact at every step. An
idea can be rejected, deferred, or absorbed into existing work. Important intended
future capabilities belong on the coarse Product Map; uncommitted possibilities stay in
the Parking Lot. Do not put speculative ideas into milestones or issues to avoid
deciding where they belong.

User-reported issues are an exception to the internal promotion path: bugs and requests
may arrive before acceptance or scheduling. Triage them for relevance, evidence,
duplication, and product boundaries. Do not interpret their existence as a commitment,
erase a valid report for being unplanned, or automatically move every report onto the
roadmap. A triaged issue without a milestone is accepted; giving it a milestone commits
it.

For an internal issue, ensure there is a concrete actionable outcome, a link to its
milestone (and to the brief, when there is one, citing the acceptance criteria it
covers), and a way to verify completion. Do not turn Next or Later into speculative
issue trees. The `github-workflow` skill, if installed, covers issue format and
mechanics.

## Preserve consequential rationale

Use a lightweight ADR (Architecture Decision Record) when a future contributor could
unknowingly reverse an important choice. Architecture, ownership, compatibility,
lifecycle, interfaces, and invariants often qualify; ordinary coding choices usually do
not.

- ADRs live in `docs/decisions/`, one file per decision. Use the existing decision log
  format, or `assets/adr-template.md` from the skill root.
- Record context, the choice, material alternatives and tradeoffs, and consequences.
  Link affected artifacts.
- Never rewrite an accepted ADR. When a decision changes, add a new ADR that supersedes
  it, mark the old one superseded with a link to the replacement, and keep the
  Architecture section's current facts up to date.
- The Architecture section states the current choice and links the ADR for its
  rationale. Do not copy the rationale into both.

## Work within available tools and scope

Use available tools to carry out requested changes. These conventions do not themselves
authorize publishing private material, sending messages, creating external work items,
or changing a product decision. Follow the user's existing authorization without adding
routine approval gates.

If a system is unavailable, continue useful local work and provide exact proposed
updates with their intended destination. Do not claim that a local draft changed Notion
or GitHub, and do not quietly turn a fallback file into a second permanent source of
truth.
