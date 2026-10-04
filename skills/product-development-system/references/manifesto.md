# Manifesto refinement

Turn an early vision into a concise, durable north star that guides later specifications. First expand understanding, then compress expression. Keep implementation detail in later artifacts.

## Explore the product decisions

Read the whole current document and relevant comments before proposing changes. Establish whether it is a manifesto, charter, principles document, or specification; preserve its intended role. Act as a skeptical product and architecture partner. Look for hidden assumptions, contradictions, missing boundaries, ambiguous terms, and accidental scope expansion.

Use these lenses where they reveal a real decision:

| Lens | Questions that matter |
| --- | --- |
| Vision | Can the central idea and practical or emotional payoff be expressed in one or two sentences? Does it describe a coherent product beyond the present implementation? |
| Target users | Who is it primarily for, and what jobs or motivations distinguish them? Is one profile an umbrella for another? Prefer functional profiles to elaborate personas. |
| Capabilities | What outcomes does the product enable? Which are missing or overlapping? Separate outcomes from implementation mechanisms. |
| Product model | Does a workflow, lifecycle, or hierarchy explain the product? Use a model such as capture → understand → decide → act only when it naturally fits. |
| Principles | Which positions materially constrain future decisions even if implementation changes? Remove aspirations that cannot guide a tradeoff. |
| Scope and ownership | What adjacent product could this accidentally become? What should it own, integrate with, or leave external? Use non-goals to protect identity without blocking useful integration. |
| Terminology | Are terms consistent? Do headings and peer lists reflect the actual conceptual hierarchy? |

Consider AI for every product, without assuming it belongs in the shipped runtime. Distinguish AI as a building tool, product capability, interaction model, primary or secondary user, or autonomous actor; deliberate runtime exclusion is also valid. Ask what must remain deterministic, independently verifiable, or under human control. Consider whether future agent users would be supported by today's model. Put the answer in the manifesto when it materially affects product direction.

Apply domain lenses selectively: provenance and uncertainty for analytics; composability and portability for developer tools; trust and accessibility for consumer products; stable contracts and governance for platforms; integrity and recoverability for preservation; delegation boundaries and fallbacks for AI-heavy products. These are prompts, not a mandatory checklist.

## Refine conversationally

For a material unresolved issue, explain the issue and consequence, propose concise wording or alternatives, and let the user resolve the product choice. When an edit is already authorized or a decision accepted, make the smallest complete change without another confirmation. Do not rewrite everything at the start or simplify away distinctions before they are understood.

Reassess prior comments against the latest text. Acknowledge valid feedback; do not defend obsolete wording or reopen resolved questions. Shared editing and comment rules are in [collaboration conventions](collaboration-conventions.md).

Once ideas stabilize, a useful structure is:

1. Vision
2. Target users
3. What the product enables
4. Principles
5. Non-goals

Adapt this structure to the product. Keep open questions here only when they affect the vision; move implementation questions to the relevant later artifact.

## Simplify and challenge

Remove duplicate principles, overlapping capabilities, temporary project facts, decorative formatting, and vague marketing language. Preserve distinctions that affect future product or architecture decisions. Check that principles and non-goals agree and that umbrella concepts are not peers of their subtypes.

Before calling the manifesto ready, ask:

- Could it reject a plausible off-mission feature and resolve a future design disagreement?
- Does it say what the product must protect when implementation changes?
- Is an important decision still present only in conversation?
- Have we deliberately considered AI's role?
- Can a reader understand the hierarchy by skimming?

Stop when it is short enough to reread, specific enough to guide decisions, broad enough to survive implementation changes, and remaining edits are preferences. Promote it according to the artifact-lifecycle rules when it begins directing implementation.
