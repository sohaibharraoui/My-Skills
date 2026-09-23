---
name: pr-review-orchestrator
description: Orchestrate an adaptive, read-only, evidence-based review of a pull request or code diff using specialized subagents when they add material value. Use for PR review, regression analysis, or requests to find bugs, security risks, performance problems, and project-wide impacts. Never modify code or GitHub state.
---

# Pull Request Review Orchestrator

Review the actual repository and task context before deciding how to review. Do not use a fixed checklist as a substitute for engineering judgment. Specialists are perspectives, not rigid boundaries: each reviewer must investigate risks relevant to the repository, technology, architecture, and change.

## Hard safety gates

- Read-only review only. Never edit files, stage, commit, push, checkout, rebase, reset, comment, approve, close, or merge.
- Run read-only Git and GitHub inspection commands directly without a conversational confirmation.
- Merging is never allowed by this skill.
- ALWAYS fetch all existing PR review comments (`gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate`) before launching review workers. NEVER list already flagged issues in review output. Reviewers must focus strictly on spotting BRAND-NEW issues.
- Every reported finding must include a minimal exact code snippet from the
  frozen PR changes that contains its changed-line anchor. Reject a candidate
  that cannot meet this requirement; never quote a secret or credential.
- Distinguish verified facts, reasoned inference, uncertainty, and product questions.
- Use the installed `review-agent` skill and the host's native subagent mechanism. If scope cannot be frozen, stop and report that limit. If a selected worker fails after scope is frozen, record its coverage as incomplete and continue with the remaining workers when safe.

## Review workflow

### 1. Establish scope

Read enough metadata to identify:

- repository and PR;
- base and head commits;
- issue or task requirements;
- changed files and diff size;
- project instructions;
- relevant tests, contracts, migrations, and deployment constraints.

Use read-only commands such as:

```bash
gh pr view <number> --json number,title,body,headRefName,baseRefName,files,commits,statusCheckRollup
gh pr diff <number>
git diff <base>...<head> --stat
```

Freeze the scope before launching reviewers: record the base and head SHA,
changed-file inventory and changed-line ranges for the commit under review,
ALWAYS fetch existing PR review comments (`gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate`)
and provide them as an exclusion list to workers. Reviewers must NEVER list or report already
flagged issues, focusing 100% of their effort on spotting brand-new unflagged defects.

### 2. Run an orchestration assessment

Launch exactly one read-only assessment subagent. Give it the scope identity, changed-file inventory, requirements, risk signals, and environment limits.

Require this decision:

```text
Single reviewer OR parallel specialists
Rationale
Risk dimensions
Proposed partitions
Expected overlap
Verification needs
```

Use parallel specialists when the PR is large, security-sensitive, cross-cutting, or has multiple independent risk dimensions. For small, narrow, low-risk changes, one reviewer may be enough. Do not equate more agents with a better review.

### 3. Launch reviewers in parallel

When the assessment selects parallel review, launch the selected read-only workers together against the same frozen scope. Do not make one specialist wait for another unless the assessment identifies a real dependency.

Always launch the installed `review-agent` skill as the general defect-first
worker when review is selected. Refer to it by skill name, never by a
filesystem path. Give every worker the same frozen scope of the commit under review
and no conclusions from peers. Workers must review independently: strictly focus
on the changes introduced in this commit to prevent duplicate issues. Ask the general
worker to inspect correctness, security, performance, maintainability, tests, and
regressions without modifying Git state.

For additional perspectives, use the specialist roles below as task prompts. They do not need separate installed skills unless a future workflow requires reusable domain-specific instructions.

### 4. Select adaptive specialists

When parallel review is justified, assign bounded but non-rigid perspectives. The reviewers must discover the relevant concerns from the repository rather than limit themselves to the examples below.

- Correctness and behavior: logic, state, data flow, APIs, edge cases, regressions, and requirements.
- Performance and operations: runtime behavior, resource use, queries, concurrency, caching, scalability, timeouts, and deployment impact.
- Style, quality, and tests: project conventions, readability, maintainability, duplication, error handling, behavioral tests, and design fit. For Python, use `~/clean_code.md` when available, but let repository conventions override it.
- Security and trust: all security risks relevant to the system, including trust boundaries, identity, access, input handling, data exposure, dependencies, filesystem or network effects, and unexpected attack paths.
- Project-wide integrity: callers, consumers, integrations, migrations, compatibility, configuration, observability, generated artifacts, and effects outside the changed lines.

These are starting perspectives, not exhaustive checklists. A reviewer may raise any repository-relevant concern and must explain why it matters.

### 5. Specialist contract

Each specialist returns the same structured result. JSON is preferred for machine aggregation:

```json
{
  "title": "Short finding title",
  "rating": "Critical | High | Medium | Low",
  "classification": "Bug | Security | Performance | Maintainability",
  "file": "path/to/file",
  "line": 42,
  "changed_line_anchor": "path/to/file:42",
  "snippet_anchor": "path/to/file:40-46",
  "changed_code_snippet": "exact frozen-diff code, 3-12 lines, including line 42",
  "problem": "What is wrong",
  "evidence": "Why the code proves it",
  "impact": "What can happen",
  "suggested_fix": "Optional; include only for a small, unambiguous correction",
  "confidence": "high | medium | low",
  "verification": "Verification recommendation",
  "fingerprint": "stable semantic issue key"
}
```

Also return `role`, `coverage`, `dismissed_candidates`,
`blind_spots`, `commands_or_tests_run`, and `worker_status`.
`worker_status` is `complete`, `incomplete`, or `scope_unavailable`.

Specialists must not change the repository or communicate with GitHub.

### 6. Coordinator synthesis and deduplication

Collect all worker results before synthesis when possible. The coordinator must independently re-read the relevant code and evidence for every candidate that could enter the final report. Then:

1. group worker candidates by semantic fingerprint, affected behavior, and evidence—not only matching wording;
2. merge duplicate worker findings and preserve the strongest evidence;
3. compare each candidate against the fetched PR review comments and completely suppress any issue that has already been flagged (never list already flagged issues in the output report); focus 100% on reporting brand-new defects;
4. verify that every finding is strictly anchored to lines changed in the target commit (preventing duplicate issues on unmodified code);
5. reject unsupported claims;
6. resolve disagreements explicitly;
7. separate defects from product questions;
8. identify missing tests and uncovered areas;
9. assign final rating based on impact and evidence;
10. state whether the review is complete or incomplete.

Do not let a majority vote decide correctness. Evidence and authoritative behavior take priority.

## Review depth

Trace beyond changed lines when risk can propagate through callers, shared utilities, state, persistence, migrations, validation, trust boundaries, retries, concurrency, public APIs, configuration, dependencies, deployment, and tests. This list is a guide, not a closed checklist. Follow the evidence and project context.

## Finding contract

Use one rating for every finding:

- `Critical`: proven authentication or authorization bypass, remote code
  execution, irreversible data loss/corruption, or a guaranteed primary
  production outage.
- `High`: confirmed core behavior, data-integrity, or reliability failure with
  a realistic production trigger.
- `Medium`: confirmed but bounded functional, security, performance, or
  maintainability defect.
- `Low`: confirmed low-impact defect or narrowly scoped maintainability gap.

Do not create an unrated `Question` finding. Put genuine product-intent gaps in
a separate questions section instead.

Each finding should include:

- rating: `Critical`, `High`, `Medium`, or `Low`;
- concise title;
- location or behavior path;
- `changed_code_snippet`: exact, minimal frozen-head code from the PR diff;
- `snippet_anchor`: path and inclusive head line range. Keep snippets to 3-12
  lines when possible, include the changed-line anchor, and never replace code
  with an ellipsis. If quoting would expose a secret, do not report the finding
  until it can be safely evidenced without revealing the secret;
- what the code does;
- why it is a problem;
- expected behavior basis;
- optional suggested fix, only for a small, unambiguous correction;
- confidence;
- verification or test recommendation.

## Final report

Return GitHub-style comments only. Do not include a review summary, decision,
second-pass section, research narrative, coverage essay, test-gap section, or
blind-spot section. State `No new comments.` when there are no reportable new
findings.

```markdown
### Comments

#### [High] Concise title — `path/to/file:42`

```python
exact changed code from the frozen PR diff
```

The comment explains the confirmed problem and concrete impact.

Suggested fix: Include only when a small, unambiguous correction is known.
```

Every new comment must contain its rating, file/line, exact changed-code
snippet, and review text. Omit `Suggested fix` otherwise. Each finding must be
strictly anchored to a changed line in the commit under review.
