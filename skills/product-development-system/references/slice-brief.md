# Slice brief creation

Specify exactly what is being built now: a bounded vertical slice producing a useful
end-to-end outcome. Use the agent as a specification reviewer to expose ambiguity,
contradictions, and accidental complexity.

Read the selected milestone, relevant Product Map and Manifesto sections, current
Technical Foundation, relevant Decision Records, and agent instruction files. Use
`assets/slice-brief-template.md` from the skill root if no suitable repository format
exists.

## Shape the brief

- State the goal and primary user scenario from input or trigger through useful output
  and verification.
- Define in-scope behavior and explicit exclusions. Ask “does this slice need it?”
  rather than “might the product eventually need it?”
- Include only necessary requirements, relevant constraints, and technical decisions.
  Keep unproven choices local to this brief.
- Retain only questions that materially block this implementation. Move future
  possibilities to their appropriate home.
- Define observable acceptance criteria, including important failure behavior. Avoid
  vague criteria such as “works well.”
- State the agreed appetite and the first things to cut if scope grows. Preserve a
  meaningful end-to-end result when cutting.
- Explain alignment with the Manifesto and link the milestone and Product Map
  capability.

Trace meaningful work as:

`Implementation task → Slice requirement → Milestone → Product Map capability → Manifesto`

Use existing links and identifiers, or concise named references. If the chain fails,
investigate whether the work is premature, accidental complexity, or evidence that a
higher-level artifact needs a deliberate change. Do not invent alignment to keep a
desired task.

## Assess readiness

The slice is ready when its scenario is end to end, scope and exclusions are clear,
acceptance is observable, appetite is agreed, and blocking product or technical
questions are resolved. The brief and any necessary baseline must be canonical in Git
before implementation starts. If a required decision is unresolved, identify it and
continue independent preparation rather than filling it in as fact.

A contributor should be able to implement from repository context without private Notion
discussion. Create actionable internal issues only after work has this context and is
part of the committed active or near-term plan; a brief does not require an issue for
every requirement. Each issue links the brief and the requirement or acceptance
criterion it covers rather than copying them, and sits under the slice's parent issue.

## During implementation

Treat the current brief as the scope boundary. When a discovery affects acceptance,
appetite, or a durable constraint, surface the tradeoff and update the relevant artifact
through Git within the user's authorization. Do not quietly expand scope or mark
criteria complete without evidence. Promote product-wide technical choices to the
Foundation when durable, with consequential rationale in Decision Records.

Keep artifact changes reviewable apart from the code. A clarification that leaves scope
unchanged goes in its own commit. A change to scope, acceptance criteria, or appetite
goes in its own pull request, merged before the implementation that depends on it.
