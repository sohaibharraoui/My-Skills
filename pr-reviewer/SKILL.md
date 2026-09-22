---
name: pr-reviewer
description: Use when preparing, reviewing, or iterating on pull requests (PRs) before submitting, creating, or merging, to conduct rigorous automated code reviews ensuring multi-tenancy isolation, defect prevention, and code convention compliance.
---

# PR Reviewer Skill

## Overview
This skill provides a rigorous, automated, and convention-enforcing code review process inspired by Ostorlab's `pr_review_agent`.

**MANDATORY RULE:** Before any Pull Request (PR) is created, updated, or merged, the changes must be reviewed by the PR Reviewer subagent (or using this review skill workflow). All findings must be addressed iteratively until an explicit **`APPROVED`** verdict is achieved.

---

## Review Process & Iteration Loop

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. Generate git diff against base branch (e.g. master) │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. Inspect full changed files in context               │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. Run PR Reviewer against the Defect Hierarchy        │
  └──────────────────────────┬─────────────────────────────┘
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
        [CHANGES REQUESTED]           [APPROVED]
               │                           │
               ▼                           ▼
  ┌─────────────────────────┐     ┌─────────────────┐
  │ 4. Fix issues in code   │     │ Ready for merge │
  │    & tests; re-run ruff │     │ / PR submission │
  └────────────┬────────────┘     └─────────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │ 5. Commit & repeat step │
  └─────────────────────────┘
```

---

## Defect Hierarchy (Prioritized Verification)

When conducting the review, evaluate code strictly in this prioritized order:

### 1. Multi-Tenancy & Security Isolation (Blocker)
- **Tenant Scoping:** All database queries, filters, resolvers, and mutations MUST scope by `organisation=organisation` or verify object-level access.
- **Cross-Tenant Prevention:** Relational inputs (e.g., tickets, members, leads, assets) MUST be validated against the active organisation. Never allow attaching cross-tenant IDs.
- **Object-Level Access (OLA):** When `organisation.settings.has_object_level_access` is `True`, non-admin users and non-admin API keys must only access and modify entities present in access caches (`cached_user_accesses`, `cached_api_key_accesses`). On update mutations, inaccessible entities already linked must be preserved rather than stripped.
- **RBAC & Authorization:** Every GraphQL mutation must have `@authorization.authorize(action=PermissionAction.WRITE)` and be registered in `authorization_test.py`.
- **Audit Logging:** Every mutating action must call `audit_common.audit_action` inside the transaction, supporting both `org_user` and masked API keys (`api_auth.mask_api_key`).

### 2. Transaction Atomicity & Data Consistency (Blocker)
- **Atomic Operations:** Wrap database creations, updates, M2M set operations, deletions, and audit logging inside `with transaction.atomic():`.
- **Pre-capture Values:** Capture model attributes (like `ticket_stream.name`) before deletion or mutation to avoid post-save / post-delete inconsistencies.

### 3. Coding Conventions & Best Practices (Quality)
- **Simplicity & Minimal Diff Footprint (Occam's Principle):** Reject over-engineered abstractions, excessive defensive machinery, runtime heuristics, or speculative multi-layered handlers when a clean, targeted 1-line change or configuration parameter achieves the exact same result. Code must be elegant, readable, and direct.
- **Strict Prohibition on `getattr()` and `hasattr()` in Favor of Good Typing:** Do NOT use `getattr()` or `hasattr()` on models, relations, or input objects. Enforce explicit static typing: direct attribute access (`obj.field`), explicit `isinstance()` type-narrowing for polymorphic models, and `@runtime_checkable` `typing.Protocol` definitions. Check for `None` directly on optional fields (`if obj.field is not None:`).
- **Explicit Condition Checks:**
  - `if len(items) > 0:` instead of `if items:`
  - `if len(text.strip()) == 0:` instead of `if not text.strip():`
  - `if value is None:` or `if value is not None:`
  - `if condition is True:` or `if condition is False:`
- **Zero Generic `Exception` in Teardown/Cleanup & Domain Exception Tracing:** Never catch generic `Exception` inside `finally:`, `__del__:`, or background cleanup blocks. Require catching specific operational exceptions (e.g., `(OSError, requests.RequestException)`). Trace domain exception hierarchies (e.g. `RepositoryWorkspaceError` subclassing `RuntimeError`) so domain failures are not missed.
- **Agent Prompt & Behavioral Contract Parity:** In autonomous agent systems, system prompts and tool docstrings are functional contracts. When prompts contain absolute claims (*"every file"*, *"always persists"*, *"tracks all changes"*), verify them against the actual code constraints (size limits like `MAX_SYNC_BYTES = 5MB`, excluded directories like `site-packages`, transport restrictions like UTF-8 GraphQL String vs raw binary).
- **Resolver Query Efficiency:** Never call `.filter()` on prefetched relations in child resolvers (which triggers N+1 SQL queries); filter in Python memory or leverage cached relations.
- **Constants:** Use defined constants (e.g., `DEFAULT_NUMBER_ELEMENTS`) instead of magic numbers.

### 4. Test Suite Fidelity & Naming (Verification)
- **Naming Convention:** All test functions MUST follow:
  ```python
  def testAction_conditionCamelCase_expectedResult():
  ```
  *Examples:*
  - `testCreateTicketStream_whenNameIsEmpty_raisesGraphQLError`
  - `testUpdateTicketStream_whenForeignOrg_raisesGraphQLError`
  - `testDeleteTicketStream_whenApiKeyProvided_deletesStreamAndLogsApiKeyAudit`
- **Real Database Models & Sinks:** Use real Django model instances in tests (`@pytest.mark.django_db`) rather than mock objects for database queries.
- **Mock Contract Symmetry (Types & Signatures):** In unit tests using test doubles, mocks, or fakes, ensure that every replacement callable or side-effect function (`record_*`, `fake_*`) strictly matches the parameter types and return type annotations of the real method being mocked (`sync_delta() -> list[pathlib.Path]`, NOT `list[str]`).
- **Orchestrator Wiring Integration Tests:** For base class orchestrators wiring new subsystems or collaborators into their core execution lifecycle (e.g. `ExecutorAgent`), testing only mock call order (`["snapshot", "execute", "sync_delta"]`) is insufficient. Require at least one concrete integration test that runs the orchestrator with real collaborators producing actual artifacts to verify end-to-end data flow.
- **Deep Deletion Audit:** When tests or code are deleted under the justification of being "obsolete", verify that deleted tests do not remove the sole coverage for fallback branches, legacy paths, or error handling that remain active in production code.
- **High-Value Assertions:** Verify actual database persistence, relation sets, audit log calls, and GraphQL error messages. Do NOT write tautological or assert-true mock tests.
- **Full Coverage:** Test happy paths, edge cases (empty strings, whitespace, naive datetimes, null elements in lists, non-positive page counts), and cross-tenant isolation.

---

## Output Format

The review report must follow this template:

```markdown
# Pull Request Review: PR <Number> (<Branch Name>)

## Verdict: [APPROVED | CHANGES_REQUESTED]

### Executive Summary
<Brief description of the PR scope and overall assessment>

### Key Review Areas & Findings
1. **Multi-Tenancy & Security Isolation**: <Status and findings>
2. **Transaction Atomicity & Audit Logging**: <Status and findings>
3. **Architecture & Coding Conventions**: <Status and findings>
4. **Test Fidelity & Edge Case Coverage**: <Status and findings>

### Required Changes (if CHANGES_REQUESTED)
- [ ] Item 1: <Detailed description with file:// link and required fix>
- [ ] Item 2: <Detailed description with file:// link and required fix>

### Non-blocking Suggestions (if any)
- <Optional polish recommendations>
```
