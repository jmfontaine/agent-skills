---
name: manifesto-refinement
description: Iteratively refine an early product or project vision into a concise, durable manifesto that guides later specifications. Use when drafting, reviewing, challenging, or simplifying a manifesto, vision statement, product charter, or principles document, including clarifying target users, capabilities, principles, non-goals, scope, and the role of AI and software agents.
---

# Manifesto Refinement

Help the user turn an early product or project vision into a concise, coherent manifesto that can guide later specifications and implementation decisions.

The goal is **not** to produce a detailed specification. The goal is to expose and resolve important product decisions, make boundaries explicit, and then simplify the result into a durable north-star document.

## Core Philosophy

A strong manifesto should make clear:

- what is being created;
- who it is primarily for;
- what it should enable;
- which principles should guide future decisions;
- what is deliberately outside scope;
- what conceptual model best explains the project;
- what role AI and software agents should play, if any;
- what future specifications should be judged against.

The process should be **iterative and conversational**, not a one-shot rewrite.

First expand understanding. Then compress expression.

## Working Style

Act as a skeptical product and architecture partner, not merely an editor.

Look for:

- hidden assumptions;
- ambiguity or contradictions;
- accidental scope expansion;
- missing boundaries;
- vague or inconsistent terminology;
- implied but unstated capabilities;
- decisions with long-term product or architectural consequences.

When the user accepts a recommendation and asks for an edit, make the smallest complete change that incorporates it.

Do not keep reopening issues that later changes have already resolved. Reassess earlier feedback against the latest document.

### Formatting and Hierarchy

Use formatting to reveal meaning, not decorate the document.

Prefer:

- headings for real conceptual sections;
- short introductory prose for umbrella concepts;
- bullets for true peer items;
- concise bold labels for principles or categories;
- consistent formatting at equivalent levels.

Avoid excessive heading depth, decorative callouts, overuse of emphasis, or flat lists that hide conceptual hierarchy.

A reader should be able to skim the headings and emphasized labels and understand the document's structure.

## Workflow

### 1. Establish the Document's Role

Determine whether the document is a vision, manifesto, product charter, principles document, or specification.

If it is intended as a manifesto or north star, resist implementation detail. It should guide specifications rather than become one.

### 2. Review the Whole Document

Evaluate it through these lenses.

#### Vision

- Is the central idea clear and distinctive?
- Can it be expressed in one or two sentences?
- Is the practical or emotional payoff clear?
- Does it describe a coherent product rather than a feature list?

Ask:

> What is this project really about if we ignore the current implementation?

#### Target Users

- Who is it primarily for?
- Are profiles distinct, or is one actually an umbrella category?
- Are they defined by jobs and motivations rather than demographics?

Prefer functional profiles over elaborate personas.

#### Capabilities

- What does the product enable?
- Are these user outcomes rather than mechanisms?
- Are important capabilities missing?
- Are several bullets describing the same underlying outcome?

Aim for a small number of clear capabilities.

#### Product Model

Look for a simple workflow, lifecycle, hierarchy, or mental model that explains the product.

Examples:

`Acquire → Preserve → Analyze → Compare → Share`

`Capture → Understand → Decide → Act`

Do not force a pipeline if none naturally exists.

#### Principles

Identify decisions that should remain true even if implementation changes.

Potential themes include usability, trust, simplicity, privacy, openness, portability, reliability, interoperability, accessibility, user control, extensibility, transparency, performance, and longevity.

Only keep principles that materially constrain future decisions.

#### AI and Agent Role

Consider AI for every project, but do not assume it belongs in the shipped product.

Determine whether AI is:

- a building tool;
- a product capability;
- an interaction model;
- a secondary or primary user;
- an autonomous actor;
- or deliberately excluded from core runtime behavior.

Ask:

> If agents become important users later, would today's design support them?

> Is AI essential, assistive, or only part of how the project is built?

> Which responsibilities must remain deterministic, verifiable, or under human control?

If the answers materially affect the product, reflect them in the manifesto.

#### Scope and Ownership

Ask:

> What adjacent product could this accidentally become?

> What should this product own, and what should remain external?

Prefer integration over unnecessary duplication. Add **Non-goals** when they protect the project's identity.

#### Terminology and Hierarchy

Check for overloaded or inconsistent terms and for lists where umbrella concepts are presented as peers with their subtypes.

Ensure the visual hierarchy matches the conceptual hierarchy.

### 3. Refine Incrementally

Do not immediately rewrite the entire manifesto.

When an important issue appears:

1. explain it;
2. explain why it matters;
3. propose concise wording or a principle;
4. let the user react;
5. edit the document when requested.

Important decisions often emerge through discussion of examples and edge cases.

### 4. Apply Domain-Specific Lenses When Relevant

Do not impose the same concerns on every manifesto.

Examples:

- **Data/analytics:** provenance, reproducibility, uncertainty, evidence vs. interpretation, data longevity.
- **Developer tools/infrastructure:** composability, automation, portability, deterministic behavior, operational complexity.
- **Consumer products:** trust, privacy, accessibility, user control, onboarding friction.
- **Platforms/ecosystems:** extensibility, compatibility, governance, openness, stable contracts.
- **Preservation systems:** durability, integrity, recoverability, provenance, future readability.
- **AI-heavy products:** agent access, delegation, permissions, explainability, deterministic boundaries, fallbacks.

These are prompts, not a checklist. Use only what exposes meaningful decisions.

### 5. Review Comments and Prior Feedback

If the source document has comments or annotations, review them as part of the process.

For each comment:

- determine whether it is still valid;
- check whether later changes resolved it;
- agree when appropriate rather than defending existing wording;
- remove redundant content when the comment reveals duplication.

Comments like these are especially useful:

- "Is this necessary?"
- "This feels messy."
- "Isn't this already covered?"
- "This sounds like scope creep."
- "These don't feel like peers."

When the agent adds a source-document comment, prefix it with the agent's own name:

`[AgentName] Comment text`

Use a configured or established agent name consistently. Prefer it over a generic prefix such as `[AI]`. If the user specifies a prefix, use that.

Never leave an agent-authored comment without clear authorship.

### 6. Structural Pass

Once the ideas stabilize, prefer a compact structure such as:

1. Vision
2. Target Users
3. What the Product Enables
4. Principles
5. Non-goals

The exact structure may differ, but every section should have durable value.

Avoid an **Open Questions** section unless the unresolved questions genuinely affect the vision. Implementation questions belong elsewhere.

### 7. Simplification and Consistency Pass

Do this only after the exploratory phase.

Review for:

- duplicated principles;
- overlapping capabilities;
- umbrella concepts presented as peers;
- inconsistent terminology;
- contradictions between principles and non-goals;
- temporary project facts that should become durable positions;
- inconsistent or decorative formatting.

Every sentence should earn its place.

Do not remove distinctions that materially affect future product or architecture decisions merely to shorten the document.

### 8. Final Challenge Pass

Before declaring the manifesto finished, ask:

> Could this document reject a plausible but off-mission feature?

> Could it resolve a future design disagreement?

> Does it say what the project must protect even if implementation changes?

> Is anything important still only present in the conversation?

> Have we made a deliberate decision about AI's role?

> Can a reader understand the hierarchy by skimming it?

Only recommend further changes if they materially improve those answers.

Stop when remaining changes are mostly wording or formatting preferences.

## Editing Behavior

When direct editing tools are available:

- read the latest version first;
- make the smallest complete edit;
- preserve unrelated content;
- preserve or improve meaningful formatting hierarchy;
- re-read after structural or multi-part edits;
- verify that the change did not introduce contradictions, duplication, or inconsistent formatting.

If direct editing is unavailable, provide exact replacement text.

## Common Failure Modes

Avoid:

- rewriting everything too early;
- simplifying before important decisions surface;
- turning the manifesto into a specification;
- vague marketing language;
- elaborate persona theater;
- treating non-peer concepts as peers;
- redundant principles;
- narrowing scope by blocking useful integration;
- adding AI language without deciding what role AI actually plays;
- ambiguous comment authorship;
- decorative or inconsistent formatting;
- retaining implementation questions after they stop affecting the vision;
- polishing indefinitely after the product decisions are settled.

## Quality Standard

A finished manifesto should be:

- short enough to reread regularly;
- specific enough to guide decisions;
- broad enough to survive implementation changes;
- opinionated enough to reject scope creep;
- clear about what the product owns and does not own;
- deliberate about AI and agents where relevant;
- internally consistent;
- visually easy to scan;
- free of accidental implementation detail.

The best test is whether future work can be challenged with:

> Does this advance the manifesto?

> Does it contradict a principle?

> Is this complexity necessary?

> Are we quietly building something listed as a non-goal?
