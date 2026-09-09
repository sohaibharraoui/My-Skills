---
name: pr-review
description: Fast, standalone, evidence-based Pull Request and code diff review. Evaluates pull requests for both the macro big-picture (architectural intent, repo-wide blast radius, caller breaks, operational safety) and micro diff quality (security vulnerabilities, logic bugs, contract breaks, test regressions, clean code conventions). Checks existing PR review threads to avoid duplicate comments and expand on unaddressed issues. Outputs exact diff snippets, detailed technical explanations, and ready-to-post PR comments matching Ostorlab senior review style. Use whenever reviewing a PR, PR URL, or local git diff.
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
4. **Check Existing PR Comments (Zero Echoes & Value-Add):**
   * **Fetch Existing Threads:** When reviewing a GitHub PR, check existing review comments (`gh api repos/{owner}/{repo}/pulls/{number}/comments`).
   * **Never Duplicate:** If an issue or convention violation has already been pointed out by another human or bot reviewer, **do NOT re-flag the exact same comment**.
   * **Enrich & Deepen Incomplete Threads:** If an existing reviewer flagged an issue but missed a critical secondary bug, suggested an incomplete/flawed fix, or if follow-up commits failed to resolve the thread, provide additive value: reference the thread (`Building on @user's comment...`), explain what remains broken, and provide the complete fix.
5. **Formatters vs. Clean Code:** 
   * **Skip Mechanical Formatting:** Do not comment on whitespace, line lengths, or indentation (`ruff format` / linters enforce those).
   * **Enforce Clean Code & Conventions:** Audit architecture, encapsulation, explicit typing, boolean checks, and error handling against authoritative standards (`~/clean_code.md`).
6. **Mandatory 3-Part Finding Structure:** Every reported finding MUST include:
   * **Exact PR Diff:** The exact diff hunk from the PR showing the problematic line(s).
   * **Detailed Explanation:** In-depth technical reasoning detailing why this fails or violates clean code.
   * **Ready-to-Post PR Comment:** A concise, punchy 1–2 sentence inline comment written in Ostorlab senior review style, ready to copy-paste directly into GitHub with optional ```suggestion diff.
7. **Concrete Evidence Only:** Report an issue only if you can demonstrate concrete failure modes, convention violations, or architectural code smells on changed lines. If a concern is speculative, **stay silent**.

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
│ 1. MACRO: INTENT, SCOPE & EXISTING COMMENTS                            │
│    • Read PR title, description, and target branch                     │
│    • Fetch review comments: gh api repos/.../pulls/<number>/comments   │
│    • Extract diff (gh pr diff <number> / git diff <base>...HEAD)       │
│    • Filter out lockfiles, generated assets, minified bundles          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. MACRO: SYSTEMIC BLAST RADIUS & CALLER AUDIT                         │
│    • For modified public functions/models, run fast ripgrep (rg)       │
│      to verify whether external callers across the repo are broken     │
│    • Check data physics: N+1 queries, unbounded memory, race states    │
│    • Check architectural simplicity vs over-engineering (Occam's razor│
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. MICRO: BOUNDED CONTEXT & CONVENTION AUDIT                           │
│    • Inspect enclosing function/class (10–30 lines surrounding diff)   │
│    • Trace inputs, nullability, exception paths, and callees          │
│    • Cross-check against existing comments (filter out duplicate nits) │
│    • Check typing, encapsulation, and clean code conventions           │
│    • Verify test assertions and public API coverage under tests/       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. REPORT: ARCHITECTURAL SUMMARY + 3-PART FINDINGS                     │
│    • Architectural & Big-Picture assessment                            │
│    • Exact PR Diff + Detailed Explanation + Ready-to-Post Comment      │
│    • Thread Additions for unaddressed or incomplete existing reviews   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Review Hierarchy (Priority Order)

Evaluate the diff against these core tiers:

### 1. 🌐 Big Picture & Systemic Architecture
- **Root Cause vs. Symptom:** Does the implementation actually address the core objective, or is it a band-aid?
- **Unupdated Callers (Blast Radius):** Public function signature or return type changes that break downstream callers across other packages.
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
- **Narrow Exception Handling:**
  - Never catch generic `Exception` — catch specific exceptions (`requests.Timeout`, `KeyError`).
  - Keep `try` blocks minimal (ideally wrapping only the line that can raise).
  - Use flat `except` clauses (never catch a tuple only to branch on `isinstance(e, ...)` inside).
- **Simplicity Over Complexity:**
  - Flat is better than nested: use guard clauses and early returns to reduce cyclomatic complexity.
  - Short functions with single responsibility.
  - Replace opaque compound types (e.g. `dict[str, dict[str, Any]]`) with `TypedDict` or `@dataclasses.dataclass`.
  - Zero private/underscored attribute tampering across external library boundaries (`_state`, `_internal`, `__dict__`).
- **Import Rules:** Absolute imports only, import modules rather than classes directly (except `typing`), no wildcard imports.

### 5. 🧪 Test Integrity & Regressions
- **Test Function Naming:** Follow `testWhat_whenCondition_shouldBehavior`.
- **Meaningful Assertions:** Flag tests that assert nothing (`assert True`), assert only mocks, or mock the actual bug away.
- **Public API Coverage:** Test behavior through public methods; never unit-test private `_` functions directly. Error-handling paths must be tested.

---

## 📋 Output Format Specification

Every review MUST follow this layout:

```markdown
## PR Review Summary
- **Verdict:** `APPROVED` | `CHANGES REQUESTED`
- **Scope:** `<file-count> files reviewed (<total-insertions>+ / <total-deletions>-)`
- **Existing Threads:** `<N> existing review comments checked (0 duplicated)`

### 🌐 Big-Picture & Architecture Assessment
- **Goal Alignment:** `<1-2 sentences on whether the change correctly addresses the root problem>`
- **Blast Radius & Callers:** `<Assessment of repo-wide caller safety, migration risks, and data physics>`
- **Architectural Fit:** `<Assessment of simplicity vs over-engineering>`

---

### Findings (If any)

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

### Additions to Existing Threads (If applicable)

#### [THREAD ENRICHMENT] In response to @reviewer on `path/to/file.py:88`
##### 1. Relevant PR Diff & Thread Context
- **Thread:** @reviewer flagged missing timeout on `requests.get()`.
- **Follow-up Commit Diff:**
```diff
+ response = requests.get(url, timeout=30)
```

##### 2. Detailed Technical Explanation
While the commit added `timeout=30`, it leaves `requests.exceptions.RequestException` unhandled. If the remote host drops the connection or DNS resolution fails, the worker process terminates abnormally without retrying.

##### 3. Ready-to-Post PR Comment
> `Building on @reviewer's comment: while timeout=30 prevents hanging, connection resets and DNS errors remain unhandled and will terminate the worker. Wrap in a try/except handling requests.RequestException.`
> ```suggestion
>     try:
>         response = requests.get(url, timeout=30)
>     except requests.RequestException as e:
>         logger.error("Failed fetching %s: %s", url, e)
>         return None
> ```

---

*(If no issues are found)*:
> **Result: APPROVED**  
> All changed lines and external callers verified against architectural intent, security, runtime safety, test coverage, and clean-code conventions. No new defects found and existing threads addressed.
```
