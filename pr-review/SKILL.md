---
name: pr-review
description: Fast, standalone, evidence-based Pull Request and code diff review. Mandatory for initial PR reviews AND all follow-up review prompts, specialized angle requests (e.g. focusing on technical, logical, obvious issues, quality, security, performance, edge cases), or subsequent review turns. Always fetches existing PR review comments and discussion threads, strictly suppresses already flagged issues, and focuses 100% on spotting new, unflagged issues and refuting invalid bot comments. Evaluates changes for both the macro big-picture (architectural intent, repo-wide blast radius, caller breaks, operational safety) and micro diff quality (security vulnerabilities, logic bugs, contract breaks, test regressions, clean code conventions). Strictly enforces reporting every finding using the mandatory 3-part format: exact PR diff, detailed technical explanation, and ready-to-post PR comment matching Ostorlab senior review style. Never falls back to unstructured conversational bullets or essay sections. Use whenever reviewing a PR, PR URL, commit diff, or handling any follow-up prompt, specialized angle, deep dive, or critique on a PR.
---

# Fast Standalone PR Review (Macro & Micro)

Perform a rapid, high-signal, evidence-based code review of a pull request or local git diff.

This skill audits both the **Big Picture (Macro: architectural intent, systemic blast radius, broken callers across the repo)** and the **Diff Quality (Micro: logic bugs, null safety, exception handling, clean code conventions)** directly in standalone mode without slow subagents.

---

## Hard Rules & Principles

1. **Zero Subagents:** Review directly in the active session. Never spawn subagents or delegate to child processes.
2. **Strictly Read-Only:** Never edit files, stage commits, push, or merge during a review.
3. **The Big-Picture First (Macro Assessment):**
   * **Goal & Intent:** Does the PR actually solve the root problem described in the PR description / ticket, or does it only mask a symptom?
   * **Systemic Blast Radius:** When a public function, method signature, model field, or return type changes, use fast `rg` to audit all callers across the entire repository—not just the files in the diff.
   * **Architectural Cohesion & Simplicity:** Ensure the change aligns with existing patterns in the codebase and adheres to Occam's engineering principle (favor the simplest viable solution, avoid speculative abstractions).
4. **Mandatory Existing Comments Fetching & Deduplication (Zero Re-flagging):**
   * **Always Fetch Existing PR Comments:** ALWAYS fetch all existing review comments and threads before reviewing (`gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate`). Build an index of all lines, code hunks, and issues already flagged by humans or bots.
   * **Never List Already Flagged Issues:** NEVER repeat, re-list, summarize, or include issues that have already been commented on or flagged on the PR. If an issue has already been raised, completely suppress it from your findings list and output report. Re-flagging known issues creates noise and wastes review bandwidth.
   * **Always Focus on Spotting New Issues:** Direct 100% of analytical effort toward spotting brand-new, unspotted issues: logic flaws, unhandled exceptions, security vulnerabilities, broken repo-wide callers, unstated assumptions, or invalid bot comments that require explicit technical refutation.
   * **Current Commit Diff Scope:** When reviewing a specific commit or PR update, anchor new findings to lines changed in that commit while tracing blast radius across the repository.
5. **Formatters vs. Clean Code:** 
   * **Skip Mechanical Formatting:** Do not comment on whitespace, line lengths, or indentation (`ruff format` / linters enforce those).
   * **Enforce Clean Code & Conventions:** Audit architecture, encapsulation, explicit typing, boolean checks, and error handling against authoritative standards (`~/clean_code.md`).
6. **Mandatory 3-Part Finding Structure:** Every reported finding MUST include:
   * **Exact PR Diff:** The exact diff hunk from the PR showing the problematic line(s).
   * **Detailed Explanation:** In-depth technical reasoning detailing why this fails or violates clean code.
   * **Ready-to-Post PR Comment:** A concise, punchy 1–2 sentence inline comment written in Ostorlab senior review style, ready to copy-paste directly into GitHub with optional ```suggestion diff.
7. **Concrete Evidence Only:** Report an issue only if you can demonstrate concrete failure modes, convention violations, or architectural code smells on changed lines. If a concern is speculative, **stay silent**.
8. **Agent Prompt & Behavioral Contract Parity (Prompt-to-Code Parity):**
   * In autonomous agent repositories, system instructions and tool docstrings are operational specifications that dictate LLM actions.
   * Whenever prompt text or tool documentation changes, audit every claim with universal or absolute quantifiers (`every`, `all`, `automatically`, `always`, `never`, `any`) against the underlying backend implementation:
     - *Size & memory caps:* (e.g. 5MB file sync limit, token truncation).
     - *Exclusions & blacklists:* (e.g. `site-packages`, internal storage roots, `__pycache__`).
     - *Format & transport constraints:* (e.g. GraphQL string UTF-8 constraints vs raw binary payloads).
     - *Concurrency & lifecycle:* (e.g. background processes still writing after task completion).
   * If a prompt promises persistence, tracking, or behavior that the backend filters, drops, or defers, flag it as a prompt-contract defect.
9. **Zero-Tolerance Exception Scrutiny (No Exemption for Teardown or `finally:`):**
   * Clean code rules on exception handling are non-negotiable. Never give a pass to `except Exception:` on the grounds that "it's just a cleanup / teardown / background block".
   * Catching bare `Exception` in teardown silences typos, `AttributeError`, `TypeError`, or logic defects in the cleanup routine itself. Always require catching specific operational exceptions (e.g., `(OSError, requests.RequestException)`).
   * Trace domain exception hierarchies: never assume standard library exceptions (e.g. `OSError`) cover domain path or workspace resolution failures (such as `RepositoryWorkspaceError` inheriting from `RuntimeError`).
10. **Mock Contract Symmetry (Signatures & Types):**
    * In unit tests using test doubles, mocks, or fakes, ensure that every replacement callable or side-effect function (`record_*`, `fake_*`) strictly matches the parameter types and return type annotations of the real method being mocked (`WorkspaceDeltaSync.sync_delta() -> list[pathlib.Path]`, NOT `list[str]`).
    * Dynamic mocking (`mocker.patch.object`) hides type divergence from static type checkers; reviewers must audit signature symmetry manually.
11. **Orchestrator Integration Rigor & Deletion Auditing:**
    * *Wiring Integration Tests:* When an architectural base class or orchestrator (e.g. `ExecutorAgent`) wires a new subsystem or collaborator into its core execution lifecycle, verifying only mock call sequences (`["snapshot", "execute", "sync_delta"]`) is insufficient. Require at least one concrete integration test that runs the orchestrator with real collaborators producing actual artifacts to verify end-to-end data flow.
    * *Deep Deletion Audit:* When tests or code are deleted under the justification of being "obsolete", verify that deleted tests do not remove the sole coverage for fallback branches, legacy paths, or error handling that remain active in production code.
12. **Mandatory Session Continuity & Follow-Up Review Contract (Zero Unstructured Findings):**
    * **Continuous Review Lifecycle:** The PR review does NOT end after the initial review response. Any follow-up request from the user to inspect, refine, drill down, re-evaluate, or focus on specific aspects of the PR (such as *"focus on technical, logical, obvious issues, and quality"*, *"look into edge cases"*, *"check security"*, *"audit file X"*, *"what did you miss?"*) is a direct continuation of the PR review.
    * **Strict Prohibition on Free-Form Conversational Output:** The agent MUST NEVER drop out of the `pr-review` skill or revert to generic conversational bullet points, numbered essay sections, or casual chat when presenting issues or critiques.
    * **Enforce the Mandatory 3-Part Finding Format for Every Single Issue:** Every technical flaw, logical bug, real-world limitation, convention violation, or quality defect identified during any turn of the review MUST be reported using the canonical 3-part finding layout:
      - `#### [SEVERITY] <Short Descriptive Title>`
      - `- **Location:** path/to/file.ext:line`
      - `- **Category:** <Category>`
      - `##### 1. Relevant PR Diff`
      - `##### 2. Detailed Technical Explanation`
      - `##### 3. Ready-to-Post PR Comment` (with GitHub markdown suggestion block where applicable).
    * Even when answering targeted follow-up prompts, all findings must be delivered in this exact actionable format so the user can immediately copy/paste them or review them directly on GitHub.


---

## 💬 Ostorlab PR Comment Style Guide (Ready-to-Post)

Comments posted on GitHub PR lines must sound like a senior peer engineer, not an AI bot. Follow this canonical formula:

### The Formula: [Optional Severity:] + Trigger/Cause + Consequence + Prescriptive Action / Precedent

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [minor:] <Function/Line> <condition/defect>, <consequence/failure>.    │
│ <Exact prescriptive fix, repository precedent, or missing test paths>.│
│                                                                        │
│ ```suggestion                                                          │
│ <drop-in replacement code if applicable>                              │
│ ```                                                                    │
└────────────────────────────────────────────────────────────────────────┘
```

### Style Rules:
- **No Artificial Headers in Comments:** Do NOT put bullet headers like `**Issue:** ... **Failure Mode:** ... **Convention:** ...` inside the inline comment. Write a single cohesive, high-density note.
- **Ultra-Concise (1–2 Sentences):** Keep comments between 25 and 60 words. State the trigger, the failure mode, and the exact remedy.
- **Reference Precedents & Specifics:** Cite exact model names (`PlanNg`), exceptions (`MissingPlanError`), parameters (`organisation=organisation`), and precedent functions in the repo (`like scan_follow_with_account_journey does`).
- **Severity Prefixes:** Use `minor:` for non-blocking clean-code/readability nits; omit prefix for functional, security, or testing blockers.
- **Always Include Drop-In Suggestions When Line-Local:** Use GitHub's ```suggestion syntax whenever the fix is local to the diff hunk.

### Canonical Examples from Real Reviews:
* **Multi-Tenancy / Security:**
  > `build_renewal_context() accepts organisation but queries PlanNg by plan_id alone without scoping to the organisation, allowing cross-tenant plan retrieval. Scope the query by adding organisation=organisation to get() so foreign plan IDs raise MissingPlanError.`
* **Unhandled Exception / Engine Precedent:**
  > `build_renewal_context raises MissingPlanError when plan_id has no PlanNg row and it bubbles to the engine catch-all so the reminder stops sending. Catch it locally like scan_follow_with_account_journey does with MissingScanError.`
* **Prompt vs. Implementation Boundary Contract:**
  > `BaseExecutor and Bash prompts claim that every new or modified file in /workspace is automatically persisted to scan memory, but WorkspaceDeltaSync skips files >5MB, ignores ROOT_EXCLUDED_DIRS, and drops binary files from ScanStore. Qualify the prompt instructions with these limits so the LLM does not rely on persistence for dropped artifacts.`
* **Clean Code / Narrow Exception in Teardown:**
  > `Catch specific workspace-sync exceptions (such as OSError) instead of generic Exception in the finally block, otherwise internal programming errors (e.g. AttributeError, TypeError) in sync_delta are silently masked.`
* **Mock Return Type Annotation Mismatch:**
  > `record_sync_delta is annotated as returning list[str], but WorkspaceDeltaSync.sync_delta returns list[pathlib.Path]. Update the mock annotation to list[pathlib.Path] to match the collaborator's type contract.`
* **Missing Integration Test for Orchestrator Wiring:**
  > `The new tests only assert the call sequence of mocked snapshot and sync methods. Add a concrete integration test executing a task that creates a file and asserting it reaches both ScanStoreMemory and the message queue.`
* **Customer-Facing Logic / Fallback:**
  > `minor: if last_payment_cached is None, expiry_date stays empty and the email ships a blank expiry date. Fall back to the plan end date since displaying that date is the whole point.`
* **Type Annotations / Style Guide:**
  > `Per style guide, specify inner generic types for collection type annotations, such as using dict[str, object] | None instead of bare dict | None.`
* **Missing Test Coverage:**
  > `The new expiry calculation branches for monthly billing, leap year anniversaries, fallback frequency, and missing subscription data lack unit test coverage. Please add unit tests in utils_test.py covering these branching paths.`

---

## ⚡ 4-Step Review Workflow

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. MACRO: INTENT, EXISTING COMMENTS & COMMIT SCOPE                     │
│    • Read PR title, description, and target branch                     │
│    • ALWAYS fetch existing review comments:                            │
│      gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate    │
│    • Index already flagged lines/issues to ensure zero duplication     │
│    • Extract diff of commit (git show <sha> / commit diff)             │
│    • Filter out lockfiles, generated assets, minified bundles          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. MACRO: SYSTEMIC BLAST RADIUS & CALLER AUDIT                         │
│    • For modified public functions/models, run fast ripgrep (rg)       │
│      to verify whether external callers across the repo are broken     │
│    • Check prompt contracts: verify claims against backend limits/caps │
│    • Check data physics: N+1 queries, unbounded memory, race states    │
│    • Check architectural simplicity vs over-engineering (Occam's razor│
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. MICRO: BOUNDED CONTEXT & CONVENTION AUDIT                           │
│    • Inspect enclosing function/class (10–30 lines surrounding diff)   │
│    • Trace inputs, nullability, exception paths, and callees          │
│    • Zero-tolerance exception audit: reject broad Exception in finally │
│    • Check typing, encapsulation, and clean code conventions           │
│    • Verify mock type signature symmetry and test deletion coverage    │
│    • Verify test assertions and public API coverage under tests/       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. REPORT: ARCHITECTURAL SUMMARY + BRAND-NEW 3-PART FINDINGS           │
│    • Architectural & Big-Picture assessment                            │
│    • Filter out ALL already flagged issues (never list them)           │
│    • Focus exclusively on reporting brand-new, unflagged findings      │
│    • Exact PR Diff + Detailed Explanation + Ready-to-Post Comment      │
│    • Flag invalid bot comments if they mislead the PR author           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Review Hierarchy (Priority Order)

Evaluate the diff against these core tiers:

### 1. 🌐 Big Picture & Systemic Architecture
- **Root Cause vs. Symptom:** Does the implementation actually address the core objective, or is it a band-aid?
- **Unupdated Callers (Blast Radius):** Public function signature or return type changes that break downstream callers across other packages.
- **Agent Prompt & Behavioral Contract Parity:** Audit modified prompt strings and tool docstrings against implementation invariants (`MAX_SYNC_BYTES`, excluded dirs, encoding/transport constraints). Ensure the prompt does not promise persistence or behavior that the backend filters or drops.
- **Architectural Over-Engineering:** Introducing speculative abstractions, duplicate helper layers, or unnecessary state machines when a simpler change suffices.
- **Operational & Data Physics:** N+1 queries introduced into hot loops, unbounded in-memory list growth, non-atomic multi-step transactions, or backwards-incompatible migrations.

### 2. 🚨 Security & Multi-Tenancy (Blockers)
- **Tenant Isolation:** Queries, mutations, or API endpoints missing tenant scoping (`organisation=...`), allowing cross-tenant data access.
- **Injection:** Unsanitized parameters in SQL, shell, regex, or HTML templates.
- **Auth & Permissions:** Endpoints or mutations missing authorization decorators or role checks.
- **Credential / Information Leaks:** Exposing sensitive secrets, tokens, or raw internal stack traces.

### 3. 💥 Logic, Runtime & Edge-Case Crashes
- **Null / None Dereference:** Calling attributes or methods on potentially `None` / `undefined` values without checks or optional chaining.
- **Unhandled Exceptions:** Network I/O, file operations, JSON parsing, or database lookups lacking error handling or fallback rescues.
- **Off-by-One & Loop Boundaries:** Incorrect slice indices, empty list assumptions (`list[0]` without length check), off-by-one loops.
- **State Corruption & Concurrency:** Race conditions, mutating shared in-place collections, un-awaited async calls.

### 4. 🧹 Clean Code & Code Conventions (Authoritative: `~/clean_code.md`)
- **Strict Prohibition on `getattr()` / `setattr()` / `hasattr()`:** Access attributes directly via type narrowing (`isinstance`) and typed contracts; never use dynamic attribute reflection.
- **Methods Without `self`:** If a method does not access instance state (`self`), move it outside the class as a private module-level function (prefixed with `_`).
- **Encapsulation & Private Members:** Attributes and helper functions not part of the public API must be prefixed with `_`. Expose read-only state via `@property`.
- **Explicit Boolean Checks:** Use explicit comparisons (`is True`, `is None`, `is not None`, `len(items) == 0`) rather than implicit truthiness (`if not items:`, `if items:`).
- **Narrow Exception Handling & Domain Exceptions:**
  - Never catch generic `Exception` — catch specific exceptions (`requests.Timeout`, `KeyError`, `OSError`).
  - **No Teardown/Cleanup Exemption:** Never rationalize `except Exception:` inside `finally:`, `__del__:`, or background cleanup blocks. Generic catches silently swallow programming bugs, typos, and syntax errors.
  - **Trace Domain Exception Hierarchies:** Audit repository-defined domain exceptions (e.g., `RepositoryWorkspaceError` subclassing `RuntimeError`). Never assume standard library `OSError` covers domain path or workspace resolution errors.
  - Keep `try` blocks minimal (ideally wrapping only the line that can raise).
  - Use flat `except` clauses (never catch a tuple only to branch on `isinstance(e, ...)` inside).
- **Simplicity Over Complexity:**
  - Flat is better than nested: use guard clauses and early returns to reduce cyclomatic complexity.
  - Short functions with single responsibility.
  - Replace opaque compound types (e.g. `dict[str, dict[str, Any]]`) with `TypedDict` or `@dataclasses.dataclass`.
  - Zero private/underscored attribute tampering across external library boundaries (`_state`, `_internal`, `__dict__`).
- **Import Rules:** Absolute imports only, import modules rather than classes directly (except `typing`), no wildcard imports.

### 5. 🧪 Test Integrity & Regressions
- **Test Function Naming:** Follow `testAction_condition_expectedResult` (e.g. `testCreateTicketStream_whenNameIsEmpty_raisesGraphQLError`).
- **Meaningful Assertions:** Flag tests that assert nothing (`assert True`), assert only mocks, or mock the actual bug away.
- **Mock Contract Symmetry (Types & Signatures):** In unit tests using test doubles, mocks, or fakes, ensure that every replacement callable or side-effect function (`record_*`, `fake_*`) strictly matches the parameter types and return type annotations of the real method being mocked (`WorkspaceDeltaSync.sync_delta() -> list[pathlib.Path]`, NOT `list[str]`). Dynamic mocking (`mocker.patch.object`) hides type divergence from static type checkers; reviewers must audit signature symmetry manually.
- **Orchestrator Integration Testing vs. Pure Mock Isolation:** When an architectural base class or orchestrator wires a new subsystem or collaborator into its core execution lifecycle (e.g. `ExecutorAgent`), testing only mock call order (`snapshot -> execute -> sync_delta`) is insufficient. Require at least one concrete integration test that runs the orchestrator with real collaborators producing actual artifacts to verify end-to-end data flow.
- **Deep Deletion & Deprecation Audit:** When tests or code are deleted under the claim of being "obsolete", audit the deleted tests against the remaining codebase. Ensure deleted tests do not remove the sole coverage for fallback branches, legacy paths, or error handling that remain active in production code.
- **Public API Coverage:** Test behavior through public methods; never unit-test private `_` functions directly. Error-handling paths must be tested.

---

## 📋 Output Format Specification

Every review MUST follow this layout:

```markdown
## PR Review Summary
- **Verdict:** `APPROVED` | `CHANGES REQUESTED`
- **Scope:** `<file-count> files reviewed in commit <sha> (<total-insertions>+ / <total-deletions>-)`
- **Existing Comments:** `<N> existing review comments fetched (already flagged issues strictly suppressed, 100% focused on new issues)`

### 🌐 Big-Picture & Architecture Assessment
- **Goal Alignment:** `<1-2 sentences on whether the change correctly addresses the root problem>`
- **Blast Radius & Callers:** `<Assessment of repo-wide caller safety, migration risks, and data physics>`
- **Architectural Fit:** `<Assessment of simplicity vs over-engineering>`

---

### New Findings (Zero Already-Flagged Issues)

#### [CRITICAL | MAJOR | MINOR | CONVENTION] <Short Descriptive Title>
- **Location:** `path/to/file.py:123`
- **Category:** `Big Picture/Blast Radius` | `Security` | `Logic/Crash` | `Clean Code & Conventions` | `Tests`

##### 1. Relevant PR Diff
```diff
@@ -40,6 +40,8 @@ def process_asset(asset_id: str) -> None:
     record = fetch_record(asset_id)
+    user = get_user(record.user_id)
+    user.sync_permissions()
```

##### 2. Detailed Technical Explanation
`get_user()` returns `None` if the user ID does not exist in the database. Calling `.sync_permissions()` directly on `user` will raise an unhandled `AttributeError: 'NoneType' object has no attribute 'sync_permissions'` in production.

##### 3. Ready-to-Post PR Comment
*(Copy and paste directly into GitHub review comment on line 42)*

> `get_user()` returns `None` when the user does not exist, causing an unhandled `AttributeError` on `.sync_permissions()`. Add an explicit None check before syncing permissions.
> ```suggestion
>     user = get_user(record.user_id)
>     if user is not None:
>         user.sync_permissions()
> ```

---

*(If no issues are found)*:
> **Result: APPROVED**  
> All changed lines in this commit and external callers verified against architectural intent, security, runtime safety, test coverage, and clean-code conventions. No defects found in this commit.
```

### Follow-Up Review / Specialized Angle Iteration Layout

When the user asks follow-up questions, requests specialized focus (e.g. *"focus on technical, logical, obvious issues, and quality"*, *"look into security"*, *"check edge cases"*, *"audit file X"*), or continues the review across multiple conversation turns:

The agent MUST NEVER revert to free-form conversation, generic bullet points, or informal prose.
The output MUST strictly follow this layout:

```markdown
## PR Review Follow-Up: <Focus Area / User Angle>
- **Scope / Angle:** `<Brief 1-line statement of the focus area requested by the user>`
- **Total New Issues Identified:** `<N>`

---

### New Findings

#### [CRITICAL | MAJOR | MINOR | CONVENTION] <Short Descriptive Title>
- **Location:** `path/to/file.ext:line`
- **Category:** `Technical / Logic` | `Domain Accuracy` | `Quality / Polish` | `Security` | `Clean Code`

##### 1. Relevant PR Diff
```diff
<diff hunk showing the problematic code>
```

##### 2. Detailed Technical Explanation
<In-depth technical explanation of the flaw, why it is problematic, real-world edge cases or domain inaccuracies>

##### 3. Ready-to-Post PR Comment
*(Copy and paste directly into GitHub review comment on line X)*

> <1-2 punchy senior peer sentences with exact issue, consequence, and remedy>
> ```suggestion
> <suggested replacement if line-local>
> ```

---

*(If no issues are found in this angle/focus)*:
> **Result: NO ADDITIONAL ISSUES IDENTIFIED**  
> Audited <focus area / files> thoroughly against all technical, logical, and quality constraints. No new defects spotted.
```

