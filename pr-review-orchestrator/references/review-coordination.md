# Review Coordination Notes

Use this reference when the review needs multiple agents.

## Handoff payload

Pass each reviewer only the context it needs:

- repository and PR identity;
- base and head commit;
- task and acceptance criteria;
- changed-file inventory;
- relevant project instructions;
- specialist perspective;
- read-only requirement;
- requested output contract.

Avoid passing the coordinator's conclusions to specialists. This preserves independent reasoning.

## Parallel worker layout

When parallel review is selected, use one shared immutable scope and launch workers together:

- `review-agent`: general defect-first review;
- correctness and behavior reviewer;
- performance and operations reviewer;
- style and quality reviewer;
- security and trust reviewer;
- project-integrity reviewer.

Do not require every role for every PR. The orchestration assessment chooses the smallest set that covers the actual risk. The role descriptions are prompts, not closed checklists.

The general worker must explicitly use the installed `review-agent` skill by name. Do not reference a host-specific filesystem path. Other workers can use the same base review instructions with a bounded perspective prompt.

## Uniform result

Every worker should return the same finding fields:

```json
{
  "title": "Short finding title",
  "severity": "Blocker | Major | Minor | Question",
  "file": "path/to/file",
  "line": 42,
  "problem": "What is wrong",
  "evidence": "Why the code proves it",
  "impact": "What can happen",
  "fix": "Concrete fix direction",
  "confidence": "high | medium | low",
  "tests": "Verification recommendation",
  "fingerprint": "stable semantic issue key"
}
```

The coordinator deduplicates by semantic issue, affected behavior, and evidence. It keeps one final finding per distinct failure mode and retains the clearest evidence from the workers.

## Shared state

Prefer a small structured result from each specialist rather than long conversational summaries. Preserve exact file paths, line numbers, commands, and evidence pointers.

## Failure handling

- If a specialist fails, record the failure and continue with the remaining review when safe.
- If context, credentials, runtime, or diff size prevents complete review, mark the affected area as not covered.
- Do not retry indefinitely; use a bounded retry or fall back to one coordinator review.
- Never convert an unverified suspicion into a finding merely because a specialist reported it.

## Anti-sycophancy

Require specialists to state what they checked and what they rejected. Do not use simple majority voting. The coordinator verifies candidates against code, tests, contracts, and project requirements.
