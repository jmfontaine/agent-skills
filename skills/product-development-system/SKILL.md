---
name: product-development-system
description: Guide product development from manifesto and product map through releases, optional briefs, and release review. Use to draft, review, challenge, or simplify a manifesto, vision statement, product charter, or principles document; map capabilities and keep the Now / Next / Later roadmap; decide what goes into the next release; write a brief for multi-issue work; or reconcile learning and artifacts after a release. Does not replace coding guidance for ordinary implementation tasks.
---

# Product Development System

Specify the whole product coarsely and the next release precisely. Help the user make
product decisions; do not turn the process into an automatic pipeline of documents or
approvals.

Use **product** for what users receive: vision, capabilities, scope, roadmap, and
outcomes. Use **project** for the implementation context: repository, contributors,
tooling, architecture, and execution environment.

## Orient and route

Read the relevant existing artifacts and agent instruction files (AGENTS.md, CLAUDE.md).
Identify the current work, what is authoritative, what is already decided, and the next
unresolved decision. Use established paths and conventions. Missing documents are not an
instruction to manufacture a complete set before helping.

The usual flow is:

`Manifesto → Product Map → Milestone → Brief (when needed) → Build → Release review → Replan`

A milestone is a GitHub milestone: one release (`vX.Y.Z`) whose issues are the committed
work. The Product Map holds the roadmap as Now / Next / Later. A brief is optional: the
issue is the spec by default. The Architecture section of AGENTS.md carries the
project's technical baseline across releases. Establish only what the next release
needs, then update it as choices become durable.

Reusable guidance and templates live in this skill. Load only the reference needed for
the task. Add shared references when their conditions apply; do not load every file in
advance. Reference and template paths are relative to this skill directory.

| Current task | Read |
| --- | --- |
| Draft, challenge, or simplify vision, a manifesto, or product principles | [Manifesto refinement](references/manifesto.md) |
| Map the intended product, find missing capabilities and boundaries, or update Now / Next / Later | [Product map](references/product-map.md) |
| Choose the next release's outcomes, set its appetite, or replan | [Release planning](references/release-planning.md) |
| Decide whether work needs a brief, write one, or assess readiness to build | [Brief](references/brief.md) |
| Review a finished milestone and decide what changes next | [Release review](references/release-review.md) |
| Establish or revise the project's technical baseline | [Architecture section](references/architecture-section.md) |
| Promote an artifact, resolve conflicting sources, place an idea, create work items, or preserve a decision | [Artifact lifecycle](references/artifact-lifecycle.md) |
| Author, edit, or comment on an artifact; reconcile prior feedback | [Collaboration conventions](references/collaboration-conventions.md) |

For “what next?”, locate the earliest unresolved decision that affects the requested
work, explain its implication, and load that reference. Revisit earlier artifacts when
evidence challenges them. Continue within the user's authorized scope; do not silently
expand into the next phase.

## Artifact locations

Use these default locations unless the project already has established conventions.
Repository paths are relative to the project's repository root.

| Artifact | Typical home or location |
| --- | --- |
| Manifesto | Repository: `docs/manifesto.md` |
| Product Map, with Now / Next / Later | Repository: `docs/product-map.md` |
| Briefs | Repository: `docs/briefs/NNNN-<name>.md`, linked from the milestone description |
| ADRs | Repository: `docs/decisions/` |
| Architecture section | Repository: the Architecture section of AGENTS.md |
| Release plan | GitHub milestones, one per release |
| Committed work and user-reported issues (untriaged until triaged) | GitHub issues |
| Parking Lot | GitHub Discussions, category “Ideas” (public repository), else private Notion |

If the repository's `docs/` directory is published user documentation, put the
Manifesto, Product Map, briefs, and ADRs under `docs/product/` instead
(`docs/product/manifesto.md`, `docs/product/briefs/`, `docs/product/decisions/`, and
so on).

## Shared constraints

- **Git** holds canonical durable artifacts. **GitHub milestones and issues** hold the
  release plan and committed work. The **Parking Lot** holds uncommitted ideas;
  **private Notion** also holds exploration and project-specific context. After
  promotion, edit the Git artifact; an older private draft cannot override it.
- Contributors and coding agents must be able to work without access to or awareness of
  private Notion. Keep project documents self-contained.
- Keep distant work coarse and current work precise. Prefer thin, end-to-end work that
  delivers something useful over isolated horizontal subsystems. Use an appetite to
  bound effort; reduce scope first when work no longer fits.
- Trace meaningful implementation work through its issue, the milestone (and brief, when
  there is one), the Product Map capability, and the Manifesto. A broken link needs
  investigation, not invented justification.
- Consider AI and agents explicitly: how they help build the product and whether they
  belong in its runtime, interfaces, or user model. Do not assume one implies the other.
- Prefix agent-authored comments and replies with `[AgentName]`, using the established
  name. Use restrained formatting that reflects conceptual hierarchy.
- Working material for a task in progress (drafts, plans, research exports) is scratch:
  keep it in the scratch directory the agent instruction files name, else an ignored
  `.scratch/`, and delete it once its content is filed or the task is done.

During Build, work from the issue, the brief if there is one, the relevant higher-level
artifacts, ADRs, and repository guidance. Keep implementation bounded; surface
discoveries that change scope or durable decisions. This skill adds no separate
implementation framework and does not restate GitHub mechanics; follow the
`github-workflow` skill, if installed, for issues, pull requests, reviews, milestones,
and labels.

## Templates, only when creating the corresponding artifact

- [Brief template](assets/brief-template.md): tailor it to the work at hand and
  existing repository conventions.
- [ADR template](assets/adr-template.md): use only when consequential rationale needs
  preserving.
- [Architecture section template](assets/architecture-section-template.md): adapt it to
  the project's actual technical choices when creating the AGENTS.md section.

End with what changed or was decided, any material unresolved question, and the next
useful step. Say when an artifact is good enough; avoid indefinite polishing.
