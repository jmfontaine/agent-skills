# Artifact lifecycle and source of truth

Use one canonical home per kind of information. Authority follows the artifact's
purpose; a newer timestamp or a planning item does not silently override product intent.

| Home | Authoritative for | Boundaries |
| --- | --- | --- |
| Skill package | Reusable process guidance and templates | Project documents record adapted project choices |
| Private Notion | Exploration, research, rough drafts, private discussion, project-specific context, Parking Lot | Never a dependency for contributors or the authority over promoted Git artifacts |
| Git | Durable product intent, project baseline, Slice Briefs, consequential decisions, contributor and agent guidance | Change through Git and review as diffs after promotion |
| GitHub Projects | Rolling milestone plan, current/next slices, execution status and sequencing | Planned work, not a collection of vague possibilities |
| GitHub Issues | User-reported intake and actionable committed implementation work | Intake may be untriaged; internally created issues represent deliberate planning decisions |

## Promote cleanly

Promote an artifact when it materially affects what contributors or coding agents should
build. Use the artifact locations in SKILL.md unless the repository already has its own
conventions; do not create a parallel structure.

Read the latest source and any existing canonical version. Extract settled decisions
into clean, self-contained Markdown. Remove private conversation, sensitive context,
template instructions, and dependencies on private links. Preserve reasoning needed by
contributors in the Git artifact or a linked Decision Record.

The active Slice Brief must be canonical in Git before implementation. After promotion,
future edits must happen in Git and be reviewable as diffs. Notion may retain
exploration history, but do not maintain two competing editable authorities or require
contributors to know that history exists.

When sources conflict, use Git for promoted intent and baseline, Projects for current
planning state, and Issues for reported behavior or scoped work. Treat new reports and
private discussion as evidence that may justify a deliberate update, not an automatic
override. Explain a material conflict instead of silently resolving product judgment by
recency.

## Move possibilities into commitments deliberately

The usual internal path is:

`Private Parking Lot → Product Map / Milestone → Slice Brief → Actionable issue`

This is a promotion model, not a requirement to create an artifact at every step. An
idea can be rejected, deferred, or absorbed into existing work. Important intended
future capabilities belong on the coarse Product Map; uncommitted possibilities remain
in the private Parking Lot. Do not put speculative ideas into Projects or Issues to
avoid deciding where they belong.

User-reported issues are an exception to the internal promotion path: bugs and requests
may arrive before acceptance or scheduling. Triage them for relevance, evidence,
duplication, and product boundaries. Do not interpret their existence as a commitment,
erase valid intake for being unplanned, or automatically move every report onto the
roadmap.

For an internal issue, ensure there is a concrete actionable outcome, a link to its
committed active or near-term slice, and a way to verify completion. Do not turn distant
milestones into speculative issue trees.

## Preserve consequential rationale

Use a lightweight Decision Record when a future contributor could unknowingly reverse an
important choice. Architecture, ownership, compatibility, lifecycle, interfaces, and
invariants often qualify; ordinary coding choices usually do not.

Use the existing decision log format, or `assets/decision-record-template.md` from the
skill root. Record context, the choice, material alternatives and tradeoffs, and
consequences. Link affected artifacts. When a decision changes, preserve its historical
rationale and mark it superseded with a link to the replacement; keep the Foundation's
current facts up to date.

## Work within available tools and scope

Use available tools to carry out requested changes. These conventions do not themselves
authorize publishing private material, sending messages, creating external work items,
or changing a product decision. Follow the user's existing authorization without adding
routine approval gates.

If a system is unavailable, continue useful local work and provide exact proposed
updates with their intended destination. Do not claim that a local draft changed Notion
or GitHub, and do not quietly turn a fallback file into a second permanent source of
truth.
