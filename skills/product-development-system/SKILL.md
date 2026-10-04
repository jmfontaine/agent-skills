---
name: product-development-system
description: Guide product development from manifesto and product map through technical foundation, rolling milestone planning, slice briefs, and review. Use to draft, review, challenge, or simplify a manifesto, vision statement, product charter, or principles document; decide what to build next; bound an implementation slice; or reconcile learning and artifacts. Does not replace coding guidance for ordinary implementation tasks.
---

# Product Development System

Specify the whole product coarsely and the next increment precisely. Help the user make product decisions; do not turn the process into an automatic pipeline of documents or approvals.

Use **product** for what users receive: vision, capabilities, scope, roadmap, and outcomes. Use **project** for the implementation context: repository, contributors, tooling, technical foundation, and execution environment.

## Orient and route

Read the relevant existing artifacts and agent instruction files (AGENTS.md, CLAUDE.md). Identify the current work, what is authoritative, what is already decided, and the next unresolved decision. Use established paths and conventions. Missing documents are not an instruction to manufacture a complete set before helping.

The usual flow is:

`Manifesto → Product Map → Milestones → Slice Brief → Build → Review → Replan`

The Technical Foundation supports this flow across slices. Establish only what the next meaningful slice needs, then update it as choices become durable.

Reusable guidance and templates live in this skill. Load only the reference needed for the task. Add shared references when their conditions apply; do not load every file in advance. Reference and template paths are relative to this skill directory.

| Current task | Read |
| --- | --- |
| Draft, challenge, or simplify vision, a manifesto, or product principles | [Manifesto refinement](references/manifesto.md) |
| Map the intended product or find missing capabilities and boundaries | [Product map](references/product-map.md) |
| Establish or revise the project's durable technical baseline | [Technical foundation](references/technical-foundation.md) |
| Select outcomes, sequence milestones, or replan | [Milestone planning](references/milestone-planning.md) |
| Bound the current vertical slice or assess readiness to build | [Slice brief](references/slice-brief.md) |
| Review delivered work and decide what changes next | [Slice review](references/slice-review.md) |
| Promote an artifact, resolve conflicting sources, place an idea, create work items, or preserve a decision | [Artifact lifecycle](references/artifact-lifecycle.md) |
| Author, edit, or comment on an artifact; reconcile prior feedback | [Collaboration conventions](references/collaboration-conventions.md) |

For “what next?”, locate the earliest unresolved decision that affects the requested work, explain its implication, and load that reference. Revisit earlier artifacts when evidence challenges them. Continue within the user's authorized scope; do not silently expand into the next phase.

## Artifact locations

Use these default locations unless the project already has established conventions. Repository paths are relative to the project's repository root.

| Artifact | Typical home or location |
| --- | --- |
| Manifesto | Repository: `docs/manifesto.md` |
| Product Map | Repository: `docs/product-map.md` |
| Technical Foundation | Repository: `docs/technical-foundation.md` |
| Slice Briefs | Repository: `docs/slices/` |
| Decision Records | Repository: `docs/decisions/` |
| Rolling milestone plan | GitHub Projects |
| User intake and actionable work | GitHub Issues |
| Exploration and Parking Lot | Private Notion |

## Shared constraints

- **Private Notion** holds exploration, project-specific context, and the Parking Lot. **Git** holds canonical durable artifacts. **GitHub Projects** holds the rolling plan. **GitHub Issues** holds user-reported intake and actionable committed work. After promotion, edit the Git artifact; an older private draft cannot override it.
- Contributors and coding agents must be able to work without access to or awareness of private Notion. Keep project documents self-contained.
- Keep distant work coarse and current work precise. Prefer a thin, useful end-to-end slice over isolated horizontal subsystems. Use an appetite to bound effort; reduce scope first when work no longer fits.
- Trace meaningful implementation work through the slice requirement, milestone, Product Map capability, and Manifesto. A broken link needs investigation, not invented justification.
- Consider AI and agents explicitly: how they help build the product and whether they belong in its runtime, interfaces, or user model. Do not assume one implies the other.
- Prefix agent-authored comments and replies with `[AgentName]`, using the established name. Use restrained formatting that reflects conceptual hierarchy.

During Build, work from the current canonical Slice Brief, relevant higher-level artifacts, Decision Records, and repository guidance. Keep implementation bounded; surface discoveries that change scope or durable decisions. This skill adds no separate implementation framework.

## Templates, only when creating the corresponding artifact

- [Technical Foundation template](assets/technical-foundation-template.md): adapt it to the project's actual technical choices.
- [Slice Brief template](assets/slice-brief-template.md): tailor it to the current slice and existing repository conventions.
- [Decision Record template](assets/decision-record-template.md): use only when consequential rationale needs preserving.

End with what changed or was decided, any material unresolved question, and the next useful step. Say when an artifact is good enough; avoid indefinite polishing.
