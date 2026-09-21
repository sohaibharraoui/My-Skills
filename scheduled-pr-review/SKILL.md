---
name: scheduled-pr-review
description: Use when configuring or executing a recurring cron job to discover open Pull Requests across organization repositories, track reviewed commit SHAs, and perform automated code reviews using the standalone pr-review skill.
---

# Scheduled PR Review (Hourly Cron Workflow)

## Overview

Automates organization-wide pull request discovery and code review execution on a recurring hourly schedule. Discovers open Pull Requests across target repositories, deduplicates against previously reviewed commit SHAs to prevent redundant evaluations, and performs high-signal macro and micro code reviews using the standalone `pr-review` skill.

---

## When to Use / When NOT to Use

### When to Use
- Configuring a background standing agent or cron schedule to monitor organization repositories (e.g., `Ostorlab`) continuously for pull requests needing review.
- Batch reviewing all new and updated pull requests across multiple repositories in a single scheduled pass.
- Keeping GitHub review comments synchronized as developers push new commits to existing branches, while preventing duplicate reviews on untouched PRs.

### When NOT to Use
- Single on-demand reviews of an individual PR, branch, or local diff (use the standalone `pr-review` skill directly in the active session).
- Interactive authoring, fixing, or pushing of pull requests (use `creating-pr`).
- Continuous integration checks that must run inside GitHub Actions CI/CD pipelines rather than agent/system cron scheduling.

---

## Architecture & Workflow Diagram

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             RECURRING TRIGGER (HOURLY)                           │
│  Antigravity schedule daemon (CronExpression="0 * * * *") OR system crontab      │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     1. DISCOVERY & STATE DEDUPLICATION                           │
│  Run scripts/find_and_review_prs.py:                                             │
│    • Queries GitHub GraphQL / REST API for open PRs across organization          │
│    • Compares PR head_sha against ~/.gemini/antigravity/pr_review_cache.json     │
│    • Filters out drafts, bots, closed PRs, and unchanged head commits            │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     2. REVIEW PIPELINE (STANDALONE pr-review)                    │
│  For each candidate PR:                                                          │
│    • Fetch unified diff (gh pr diff) & existing review comments                  │
│    • Macro Review: Architecture, blast radius across repo via ripgrep (rg)       │
│    • Micro Review: Diff quality, null safety, clean code rules, edge cases       │
│    • Filter duplicates: Validate comments (suppress valid, flag invalid findings)│
│    • Structure findings: Exact Diff + Technical Explanation + Ready-to-Post      │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     3. STATE COMMIT & CONSOLIDATED REPORTING                     │
│    • Update ~/.gemini/antigravity/pr_review_cache.json with latest head_sha      │
│    • Output structured markdown run report: summary table, PR details, findings  │
│    • Post inline comments / review summaries if running in active publish mode   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Activating the Recurring 1-Hour Cron Job

### Antigravity Schedule Tool Call (Standing Background Daemon)
In Antigravity, schedule a recurring background cron job using the `schedule` tool with `IsDaemon=true`:

```json
{
  "CronExpression": "0 * * * *",
  "IsDaemon": true,
  "Prompt": "Execute scheduled PR review across Ostorlab repositories: run python3 /home/sohaib-harraoui/Desktop/workspace/My-Skills/scheduled-pr-review/scripts/find_and_review_prs.py --org Ostorlab --limit 10, then perform standalone pr-review evaluations for all candidate PRs with changed head SHAs. Filter out existing review comments, verify repo-wide blast radius with rg, and report consolidated findings.",
  "toolAction": "Scheduling hourly PR review cron",
  "toolSummary": "Hourly PR review cron job"
}
```

> [!NOTE]
> `CronExpression="0 * * * *"` (or `0 */1 * * *`) fires at minute 0 of every hour. `IsDaemon=true` indicates this is an independent standing background job that continues running across tasks.

### System Cron / CLI Alternative
To execute independently of the interactive agent session via Linux `crontab`:

```bash
crontab -e
```

Add the following hourly entry (runs at minute 0 of every hour):

```cron
0 * * * * cd /home/sohaib-harraoui/Desktop/workspace/My-Skills/scheduled-pr-review && /usr/bin/python3 scripts/find_and_review_prs.py --org Ostorlab --limit 10 >> ~/.gemini/antigravity/scheduled_pr_review.log 2>&1
```

---

## 2. Open PR Discovery & State Deduplication

### Why Tracking `head_sha` is Critical
Executing hourly reviews without state persistence causes severe review spam and token waste by re-analyzing identical, unmodified pull requests every 60 minutes.

The deduplication state cache is stored locally at:
`~/.gemini/antigravity/pr_review_cache.json`

Each entry maps repository PR keys (`owner/repo#number`) to their reviewed head commit SHA:

```json
{
  "Ostorlab/agent_auto_exploit#42": {
    "head_sha": "a1b2c3d4e5f67890123456789abcdef012345678",
    "last_reviewed_at": "2026-09-10T14:00:00+00:00",
    "title": "fix: prevent SSRF bypass in multi-url parameter handling",
    "author": "developer-username"
  }
}
```

**Deduplication Decision Matrix:**
- **PR not in cache:** Mark as candidate (`New open pull request needing initial review`).
- **PR in cache with matching `head_sha`:** Skip silently (`No changes since last reviewed commit`).
- **PR in cache with different `head_sha`:** Mark as candidate (`Head commit updated from previous_sha to new_sha`).

### Helper Script: `find_and_review_prs.py`
The helper script located at [`scripts/find_and_review_prs.py`](file:///home/sohaib-harraoui/Desktop/workspace/My-Skills/scheduled-pr-review/scripts/find_and_review_prs.py) automates GitHub CLI interaction, cache management, and candidate discovery.

#### CLI Syntax & Flags
```bash
python3 scripts/find_and_review_prs.py [OPTIONS]
```

- `--org <name>`: Organization name to search pull requests for (default: `Ostorlab`).
- `--repos <repo1> <repo2>`: Restrict search to specific repositories (e.g. `--repos agent_auto_exploit agent_threat_intelligence`).
- `--limit <int>`: Maximum candidate open PRs to process per run (default: `10`). Prevents context exhaustion during initial runs on backlogged repositories.
- `--ignore-drafts` / `--no-ignore-drafts`: Skip draft PRs (default: `--ignore-drafts`).
- `--ignore-authors <author1> ...`: Skip automated bot PRs (default: `dependabot`, `renovate`, etc.).
- `--dry-run`: Identify candidates and display diff summaries without updating the JSON cache.
- `--json`: Emit candidate list as machine-readable JSON for agent consumption.
- `--cache-path <path>`: Custom cache file location (default: `~/.gemini/antigravity/pr_review_cache.json`).

#### Typical Execution Workflow
```bash
# 1. Discover candidates in JSON format
python3 scripts/find_and_review_prs.py --org Ostorlab --limit 5 --json

# 2. Dry-run inspection with human-readable summary
python3 scripts/find_and_review_prs.py --org Ostorlab --limit 5 --dry-run
```

---

## 3. Review Execution Pipeline with `/pr-review`

For each candidate PR identified by `find_and_review_prs.py`, execute the review using the standalone `pr-review` skill rules:

### 1. Standalone Execution (Zero Subagents)
- **Review Directly in Active Session:** Never spawn subagents or delegate tasks to child processes.
- **Strictly Read-Only:** Never edit source files, commit, push, or merge during code review.

### 2. Macro Assessment (The Big Picture First)
- **Goal & Intent:** Does the PR solve the underlying problem described in the PR description, or merely mask a symptom?
- **Systemic Blast Radius (`rg`):** When public functions, classes, signatures, model fields, or return types change, execute fast `rg` across the entire codebase to detect broken callers outside the diff.
- **Architectural Cohesion:** Ensure alignment with repository precedents, Occam's engineering principle (simplest viable solution), and zero speculative over-engineering.

### 3. Micro Review (Diff Quality & Conventions)
- **Ignore Noise:** Skip lockfiles (`poetry.lock`, `package-lock.json`), minified files, generated schemas, and mechanical formatting (whitespace/indentation handled by `ruff format`).
- **Security & Multi-Tenancy:** Verify tenant scoping (`organisation=...`), parameter sanitization, permission decorators, and secret handling.
- **Logic & Null Safety:** Verify None/null guards, collection bounds, unhandled exceptions, and race conditions.
- **Clean Code (`~/clean_code.md`):**
  - Prohibit `getattr()`, `hasattr()`, and `setattr()` in favor of direct typing and `isinstance` narrowing.
  - Move methods without `self` outside classes as module-level functions (`_foo()`).
  - Explicit boolean checks (`is True`, `is None`, `len(items) == 0`).
  - Flat, narrow exception handling without branching on `isinstance(e, ...)` inside `except`.

### 4. Existing Comment Cross-Check (Strict Zero-Echo Rule)
- Fetch active PR review comments:
  ```bash
  gh api repos/{owner}/{repo}/pulls/{number}/comments
  ```
- **Strict Prohibition on Echoing:** NEVER copy, summarize, or regurgitate pre-existing reviewer or bot comments as your own review findings. 
- **Genuine Independent Scrutiny:** Review the full code diff independently for new bugs, missed edge cases, unhandled exceptions, type regressions, performance bottlenecks, or boundary conditions.
- **Enrich Incomplete Threads:** If an existing reviewer flagged an issue but missed a secondary defect, or follow-up commits left the defect partially unresolved, reference the thread explicitly (`Building on @user's comment...`) and provide the complete fix.

### 5. Mandatory 3-Part Finding Format
Every finding reported MUST strictly follow the 3-part Ostorlab senior review standard:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. EXACT PR DIFF                                                       │
│    The exact diff hunk from the PR showing the problematic line(s).    │
├────────────────────────────────────────────────────────────────────────┤
│ 2. DETAILED TECHNICAL EXPLANATION                                      │
│    In-depth rationale: failure mode, affected callers, and convention. │
├────────────────────────────────────────────────────────────────────────┤
│ 3. READY-TO-POST PR COMMENT                                            │
│    Concise 1–2 sentence senior engineer comment with a drop-in         │
│    ```suggestion code replacement block.                               │
└────────────────────────────────────────────────────────────────────────┘
```

For PRs where no defects are found (`APPROVED`), the reviewer MUST explicitly document the concrete invariants verified (e.g. multi-tenant isolation, null-safety guards, caller blast radius across the repository, error handling boundaries) rather than a generic one-sentence rubber stamp.

### 6. Submitting Reviews to GitHub (Publishing Findings)
To post findings directly to the PR on GitHub:
- Via `find_and_review_prs.py`:
  ```bash
  python3 scripts/find_and_review_prs.py \
    --post-review "Ostorlab/repo#123" \
    --review-event "COMMENT" \
    --review-body-file "/path/to/findings.md"
  ```
- Via `gh` CLI directly:
  ```bash
  gh pr review 123 --repo Ostorlab/repo --comment --body "..."
  ```
- After review is delivered or posted, update the state cache:
  ```bash
  python3 scripts/find_and_review_prs.py --mark-reviewed "Ostorlab/repo#123" "<HEAD_SHA>"
  ```

---

## 4. Output & Reporting Specification

Consolidate the results of each scheduled review sweep into a clear, high-density Markdown report:

### Run Report Structure

```markdown
# Scheduled PR Review Run Report - YYYY-MM-DD HH:MM UTC

## Sweep Summary
- **Organization / Repositories:** Ostorlab
- **Total Open PRs Scanned:** 14
- **Candidate PRs Reviewed:** 2
- **Skipped (Unchanged Head SHA):** 10
- **Skipped (Drafts / Bot Authors):** 2
- **Review Cache Updated:** `~/.gemini/antigravity/pr_review_cache.json`

## Candidates Reviewed
| Repository | PR # | Author | Head SHA | Review Status | Findings Count |
|---|---|---|---|---|---|
| `Ostorlab/agent_auto_exploit` | #42 | dev_user | `a1b2c3d` | Action Required | 2 findings (1 blocker, 1 nit) |
| `Ostorlab/reporting_engine` | #189 | eng_lead | `f8e9d0a` | Approved (Clean) | 0 findings |

---

## Detailed Findings per PR

### [Ostorlab/agent_auto_exploit#42: fix: prevent SSRF bypass](https://github.com/Ostorlab/agent_auto_exploit/pull/42)
**Author:** @dev_user | **Head SHA:** `a1b2c3d` | **Reason:** Head commit updated

#### Finding 1: Unscoped Plan Lookup (Blocker)
- **Exact PR Diff:**
  ```diff
  @@ -45,2 +45,2 @@ def fetch_plan(plan_id: str, organisation: Organization) -> Plan:
  -    return Plan.objects.get(id=plan_id, org=organisation)
  +    return Plan.objects.get(id=plan_id)
  ```
- **Detailed Technical Explanation:**
  Querying `Plan` by `id` without filtering on `org=organisation` breaks multi-tenant isolation, allowing cross-tenant plan retrieval if an attacker guesses a valid UUID.
- **Ready-to-Post PR Comment:**
  > `fetch_plan() accepts organisation but queries Plan by id alone without scoping to the organisation, allowing cross-tenant plan retrieval. Scope the query by adding org=organisation to get() so foreign plan IDs raise MissingPlanError.`
  > ```suggestion
  >     return Plan.objects.get(id=plan_id, org=organisation)
  > ```

---

## Skipped Unchanged PRs
- `Ostorlab/agent_threat_intelligence#88` (SHA `b5c6d7e` unchanged)
- `Ostorlab/agent_threat_intelligence_stream#104` (SHA `1234abc` unchanged)
```

---

## 5. Common Mistakes & Failure Modes

| Mistake / Failure Mode | Why It Fails | Correct Procedure |
|---|---|---|
| **Re-reviewing identical PRs every hour** | Causes duplicate review notifications, noise for engineers, and wasted token budget. | Always verify `head_sha` against `~/.gemini/antigravity/pr_review_cache.json` before initiating review. |
| **Spawning child subagents during review** | Violates the standalone `pr-review` principle, introduces process orchestration overhead, and risks context fragmentation. | Review candidates sequentially and directly within the active session. |
| **Duplicating existing review comments** | Comments on issues already flagged by humans or linters irritate PR authors without adding value. | Query `gh api repos/{owner}/{repo}/pulls/{number}/comments` and verify prior threads before posting. |
| **Reviewing lockfiles & generated files** | Lockfiles (`poetry.lock`, `package-lock.json`) and minified code contain thousands of auto-generated lines that obscure actual logic changes. | Filter out lockfiles, asset bundles, and compiled schemas from diff inspection. |
| **Missing repo-wide blast radius** | Catching bugs in the diff alone misses un-updated external callers across the codebase when public APIs change. | Run fast `rg -n '\bfunction_name\b'` across the repository to verify all callers. |
| **Writing verbose AI-style review comments** | Long conversational paragraphs with artificial subheadings are ignored by senior developers. | Follow Ostorlab senior review style: 1–2 punchy sentences stating condition, failure consequence, and prescriptive fix. |
