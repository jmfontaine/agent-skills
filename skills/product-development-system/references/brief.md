# Brief

A brief is an optional spec for work that spans several issues or needs product
decisions settled first. By default the issue is the spec: its Context, Acceptance
criteria, Verification, and Out of scope are enough for one bounded change.

## Decide whether to write one

Write a brief when at least one of these holds:

- The work spans several issues that must fit together.
- Product decisions (scenario, scope, exclusions) must be settled before issues can be
  written.
- The work needs its own cut order, user checkpoints, or stop rule, separate from the
  milestone's.

Skip it when one issue, or a few independent ones, can state the acceptance criteria
directly. Do not write a brief to restate an issue. The milestone groups the issues;
no umbrella issue is needed.

## Shape the brief

Read the milestone, the relevant Product Map and Manifesto sections, the Architecture
section, relevant ADRs, and agent instruction files. Use
[`assets/brief-template.md`](../assets/brief-template.md) if no suitable repository
format exists. Briefs live in `docs/briefs/NNNN-<name>.md` and are linked from the
milestone description. `NNNN` is the next unused four-digit number (`0001`, `0002`, …),
so briefs sort in creation order; a number never changes, even when the work moves to
another release.

- State the goal and primary user scenario from input or trigger through useful output
  and verification. Prefer thin, end-to-end work over isolated horizontal subsystems.
  The scenario refines one of the Product Map's key scenarios, or part of one; link it.
  If none matches, the map is missing a scenario or the work has drifted from it.
- Define in-scope behavior and explicit exclusions. Ask “does this work need it?” rather
  than “might the product eventually need it?”
- Include only necessary requirements, relevant constraints, and technical decisions.
  Keep unproven choices local to this brief.
- Retain only questions that materially block this implementation. Move future
  possibilities to their appropriate home.
- Number the acceptance criteria (AC1, AC2, …) so issues can cite them. Make them
  observable, including important failure behavior. Avoid vague criteria such as “works
  well.”
- State the first things to cut if scope grows, preserving a meaningful end-to-end
  result when cutting. List what needs the user, in order: product decisions, checks
  only the user can do (by-hand checks), and merges and releases. Give open-ended work
  (a spike, method research, an approach not yet settled) a stop rule: the condition at
  which the agent stops and reports.
- Explain alignment with the Manifesto and link the milestone, Product Map capability,
  and Product Map scenario.

Trace meaningful work as:

`Issue → Acceptance criterion → Milestone → Product Map capability → Manifesto`

Use existing links and identifiers, or concise named references. If the chain fails,
investigate whether the work is premature, accidental complexity, or evidence that a
higher-level artifact needs a deliberate change. Do not invent alignment to keep a
desired task.

## Assess readiness

The work is ready when its scenario is end to end, scope and exclusions are clear,
acceptance criteria are observable, the cut order and what needs the user are stated,
and blocking product or technical questions are resolved. The brief must be on the
default branch before implementation starts. If a required decision is unresolved,
identify it and continue independent preparation rather than filling it in as fact.

A contributor should be able to implement from repository context without private Notion
discussion. Create issues only after the work has this context and belongs to the
milestone. A brief does not require an issue for every requirement. Each issue links the
brief and the acceptance criteria it covers (for example “covers AC2 and AC3”) rather
than copying them.

## During implementation

Treat the brief as the scope boundary. Decide how to record a discovery by what it
changes:

- **A clarification that leaves scope and acceptance criteria unchanged** goes in the
  same pull request as the implementation, under its Scope notes. Update the brief in
  that pull request only if it would otherwise be left stale.
- **A change to scope or acceptance criteria is a product decision.** Stop and ask the
  user. If they agree, make the change in its own pull request, branched from the
  default branch and merged first. Then update the implementation pull request by
  merging the default branch into it. The two pull requests need not be stacked.

Do not quietly expand scope or mark criteria complete without evidence. Promote
project-wide technical choices to the Architecture section when durable, with
consequential rationale in an ADR. The `github-workflow` skill, if installed, covers
pull request mechanics.
