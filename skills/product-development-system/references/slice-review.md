# Slice review

Close the learning loop before starting the next slice. Compare delivered behavior with the canonical brief and available evidence, then reconcile affected artifacts. A retrospective document alone is not the outcome.

Read the current brief and acceptance criteria, relevant implementation or demo evidence, test results, and user feedback. Distinguish observed behavior from assumptions and missing evidence. Do not claim a slice is complete just because tasks were closed.

## Review four areas

| Area | Questions |
| --- | --- |
| Product | Did the slice solve the intended user problem? Which criteria passed, failed, or remain unverified? What capability was missing or unnecessary? |
| Architecture | Which choices and abstractions proved useful or premature? What should remain simple? What is now durable enough for the Technical Foundation? Is any technical debt worth addressing now? |
| Manifesto | Did evidence challenge a principle, boundary, or AI/agent assumption? Is this a real direction change or a local implementation issue? |
| Planning | Is the planned next outcome still best? Should milestones be reordered, split, combined, or removed? What did appetite teach us about scope? |

Recommend Manifesto changes only for evidence that materially challenges product direction. Avoid rewriting the north star to rationalize implementation drift.

## Reconcile and replan

For each meaningful finding, name the evidence, implication, and destination:

- Product intent or newly understood capabilities → Product Map in Git.
- Durable technical reality → Technical Foundation in Git.
- Consequential rationale → new or superseding Decision Record in Git.
- Justified direction change → Manifesto in Git.
- Sequence, commitment, or status → GitHub Projects.
- Actionable follow-up within committed scope → issue; uncommitted internal idea → private Parking Lot.

Apply changes already authorized by the user. Separate product choices still requiring a decision from mechanical updates. Preserve unresolved acceptance gaps in the brief or linked work, and report unverified results honestly. Avoid a new report format when a short review attached to the slice or an existing review location is enough.

Update affected canonical artifacts and reassess the milestone plan before committing to the next slice. If an external system is unavailable, prepare exact proposed updates and state what remains unapplied. Finish with the delivery assessment, material learning, changes made or proposed, and next recommended outcome.
