# Release review

Close the learning loop before the next release. When a milestone's work is done, or the
user calls the release, compare what was delivered with what was planned, then
reconcile the affected artifacts. A retrospective document alone is not the outcome.

The release review is one pull request. Its body holds the assessment; its diff holds
the artifact updates. If an artifact needs no change, say so in the body rather than
touching it.

Read the milestone description, its brief if there is one, the acceptance criteria,
relevant implementation or demo evidence, test results, and user feedback. Merged pull
requests, their reviews, and the milestone's issues are evidence too. Distinguish
observed behavior from assumptions and missing evidence. Do not claim a release is
complete just because issues were closed.

## Check openly before closing

When the user asks whether to do more before a release, and before proposing to close a
milestone, evaluate the question openly. The plan so far is input, not the answer.
Check:

- small known bugs and review findings from this release;
- Next outcomes that would make the release clearly more useful;
- what a user would miss in this version.

Answer with options and a recommendation, not a defense of the plan.

## Review four areas

| Area | Questions |
| --- | --- |
| Product | Did the release solve the intended user problem? Which criteria passed, failed, or remain unverified? What capability was missing or unnecessary? Which Product Map scenarios did it deliver or change? |
| Architecture | Which choices and abstractions proved useful or premature? What should remain simple? What is now durable enough for the Architecture section? Is any technical debt worth addressing now? |
| Manifesto | Did evidence challenge a principle, boundary, or AI/agent assumption? Is this a real direction change or a local implementation issue? |
| Planning | Is the planned next outcome still best? Should Now / Next / Later change? What did the release teach us about scope and about where the user's checkpoints fell? |

Recommend Manifesto changes only for evidence that materially challenges product
direction. Avoid rewriting the north star to rationalize implementation drift.

## Reconcile and replan

For each meaningful finding, name the evidence, implication, and destination:

- Product intent, newly understood capabilities or scenarios, or roadmap changes →
  Product Map (including Now / Next / Later) in Git.
- Durable technical reality → Architecture section of AGENTS.md in Git.
- Consequential rationale → new or superseding ADR in Git.
- Scope or acceptance learning for the work just done → the brief in Git, when there is
  one.
- Justified direction change → Manifesto in Git.
- Actionable follow-up within committed scope → issue in the next milestone;
  uncommitted idea → Parking Lot.

Update the artifacts only where the evidence justifies it. Apply changes the user
already authorized. Separate product choices still requiring a decision from mechanical
updates. Preserve unresolved acceptance gaps in the brief or in linked issues, and
report unverified results honestly.

Decide explicitly what happens to each issue still open in the milestone: finish it now,
move it to a later milestone, or close it as not planned. Then close the milestone.

Record the actual durations in the review body: agent time and the user's time,
separately. [Release planning](release-planning.md) estimates from them.

Finish with the delivery assessment, material learning, changes made or proposed, and
the next recommended outcome. Continue with [release planning](release-planning.md) for
the next milestone. If an external system is unavailable, prepare exact proposed updates
and state what remains unapplied. The `github-workflow` skill, if installed, covers pull
request and milestone mechanics.
