---
name: python-coding-style
description: Coding standards, style guide, and review conventions for Python development. Use when writing, refactoring, or reviewing Python code to ensure type safety, clean architecture, robust testing, and adherence to Ostorlab conventions.
---

# Python Coding Style Guide & Development Principles

Definitive coding standards, modern language idioms (Python 3.10–3.13+), architectural rules, testing patterns, and review principles for Python codebases across Ostorlab.

---

## 📦 1. Import Rules & Module Architecture

### Top-Level Imports Only
All imports must **ALWAYS** be located at the top of the file. Local imports (imports inside functions, classes, methods, or conditional blocks) are strictly prohibited and must **NEVER** be used.
> [!IMPORTANT]
> The only rare exception is resolving circular dependencies that cannot be refactored away. Even in those cases, you must make every effort to avoid them by restructuring modules and decoupling dependencies.

### One Import Per Symbol (Never Group Imports from the Same Module)
Imports should be **one line per symbol**. Never group multiple symbols in parentheses from the same module.
```python
# BAD
from my_package.module import (Alpha, Beta, Gamma)
from os.path import join, split, dirname

# GOOD
from my_package.module import Alpha
from my_package.module import Beta
from my_package.module import Gamma
from os.path import dirname
from os.path import join
from os.path import split
```

### No Relative Imports
Never use relative imports (`.` or `..`). Always use absolute package imports:
```python
# BAD
from .models import Scan
from ..utils import format_report

# GOOD
from my_package.models import Scan
from my_package.utils import format_report
```

### No Direct Class Imports (Except for Type Hinting)
To maintain clear namespace provenance and readability, never import classes directly for runtime instantiation. Always import the module and reference `module.ClassName`. Direct class imports are allowed **only** when used strictly in type annotations / type hints.
```python
# BAD (for runtime instantiation)
from my_package.scanner import VulnerabilityScanner

scanner = VulnerabilityScanner()

# GOOD (runtime instantiation)
import my_package.scanner

scanner = my_package.scanner.VulnerabilityScanner()

# ACCEPTABLE (only when used exclusively for type hints)
from my_package.scanner import VulnerabilityScanner

def process_scan(scanner: VulnerabilityScanner) -> None:
    ...
```

### Standard 3-Tier Grouping
Separate import blocks with a single blank line in the following order:
1. Standard library imports (`os`, `sys`, `typing`, `datetime`)
2. Third-party library imports (`pydantic`, `pytest`, `graphene`, `django`)
3. Local/first-party application imports (`from my_app.models import ...`)

### Forward References & No Wildcards
- Always use `from __future__ import annotations` at the top of files to enable lazy evaluation of type annotations and forward references.
- **Never** use wildcard imports (`from module import *`).

---

## 🔍 2. Explicit Logic & Condition Checks (No Implicit Truthiness)

Avoid implicit boolean truthiness checks on objects, collections, integers, and optional values. Always use explicit typed checks:

| Scenario | Anti-Pattern (Implicit Truthiness) | Clean Explicit Pattern |
| :--- | :--- | :--- |
| **Booleans** | `if is_active:` | `if is_active is True:` / `if is_active is False:` |
| **Optional / None** | `if value:` or `if not value:` | `if value is not None:` / `if value is None:` |
| **Collections / Lists** | `if items:` or `if not items:` | `if len(items) > 0:` / `if len(items) == 0:` |
| **Dictionaries** | `if data:` | `if len(data) > 0:` / `if len(data) == 0:` |
| **Type Checking** | `if type(x) == int:` | `if isinstance(x, int) is True:` or `if isinstance(x, int):` |

```python
# BAD
def process_records(records, user_id=None, is_admin=False):
    if user_id:
        fetch_user(user_id)
    if is_admin:
        grant_all()
    if records:
        for r in records:
            save(r)

# GOOD
def process_records(
    records: list[Record], 
    user_id: int | None = None, 
    is_admin: bool = False
) -> None:
    if user_id is not None:
        fetch_user(user_id)
    if is_admin is True:
        grant_all()
    if len(records) > 0:
        for r in records:
            save(r)
```

---

## 🔒 3. Modern Type Annotations & Static Typing (Python 3.10–3.13+)

*References: [Robust Python](https://learning.oreilly.com/library/view/-/9781098100650/?orm_source=mcp) (Patrick Viafore) & [Effective Python, 3rd Ed.](https://learning.oreilly.com/library/view/-/9780138172398/?orm_source=mcp) (Brett Slatkin)*

### Built-in Generics & Union Syntax (PEP 585 & PEP 604)
- **Built-in Generics**: Never import `List`, `Dict`, `Set`, `Tuple`, `Optional`, or `Union` from `typing`. Use built-in types: `list[str]`, `dict[str, int]`, `set[bytes]`, `tuple[int, ...]`.
- **Union Pipe Syntax**: Use `X | Y` and `T | None` instead of `Union[X, Y]` and `Optional[T]`.

### Python 3.12+ Generic Syntax (PEP 695)
Use first-class `type` alias statements and bracketed parameter lists `[T]` instead of legacy `TypeVar` and `TypeAlias`:
```python
# Modern type alias
type JSONScalar = str | int | float | bool | None
type JSONDict = dict[str, JSONScalar | list[JSONScalar]]

# Generic functions & classes using PEP 695 syntax
def first_or_default[T](items: list[T], default: T) -> T:
    if len(items) > 0:
        return items[0]
    return default

class CacheStore[K, V]:
    def __init__(self) -> None:
        self._store: dict[K, V] = {}
```

### Protocols & Structural Subtyping (Duck Typing)
Avoid rigid class inheritance. Use `typing.Protocol` with `@runtime_checkable` for flexible interface contracts:
```python
from collections.abc import Sequence
from typing import Protocol
from typing import runtime_checkable

@runtime_checkable
class Exportable(Protocol):
    def to_json(self) -> dict[str, object]: ...

def export_all(items: Sequence[Exportable]) -> list[dict[str, object]]:
    return [item.to_json() for item in items]
```

### Type Narrowing with `TypeIs` / `TypeGuard` (PEP 742 / Python 3.13)
When validating dynamic payloads or union types, use `TypeIs` to enable static type checkers to narrow types accurately across conditional branches:
```python
from typing import TypeIs

type RawPayload = dict[str, object]

def is_user_dict(payload: RawPayload) -> TypeIs[dict[str, str]]:
    name = payload.get("username")
    return isinstance(name, str)
```

### Abstract Interfaces for Arguments vs Concrete Return Types
- Use abstract container types from `collections.abc` (`Sequence[T]`, `Iterable[T]`, `Mapping[K, V]`, `Callable[..., R]`) for function arguments to accept any valid container.
- Use concrete types (`list[T]`, `dict[K, V]`) for return types.

---

## ⚡ 4. Structured Concurrency & Asyncio (PEP 654, Python 3.11+)

*References: [Python Concurrency with asyncio](https://learning.oreilly.com/library/view/-/9781617298660/?orm_source=mcp) (Matthew Fowler) & [Effective Python, 3rd Ed.](https://learning.oreilly.com/library/view/-/9780138172398/?orm_source=mcp) (Brett Slatkin)*

### Structured Concurrency with `asyncio.TaskGroup`
Replace unmanaged `asyncio.gather()` and fire-and-forget `asyncio.create_task()` with `async with asyncio.TaskGroup() as tg:`. If one task fails, all sibling tasks are cancelled cleanly before exiting the context.

```python
import asyncio

async def fetch_telemetry(endpoint: str) -> dict[str, float]:
    async with asyncio.timeout(5.0):
        await asyncio.sleep(0.05)
        return {"endpoint": endpoint, "latency": 0.012}

async def collect_telemetry(endpoints: list[str]) -> list[dict[str, float]]:
    results: list[dict[str, float]] = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_telemetry(ep)) for ep in endpoints]

    for t in tasks:
        results.append(t.result())
    return results
```

### Context-Managed Timeouts (`asyncio.timeout`)
Always use `async with asyncio.timeout(seconds):` instead of `asyncio.wait_for()` to prevent task cancellation leakage.

### Exception Groups & `except*` (PEP 654)
Handle multiple concurrent exceptions from task groups cleanly:
```python
async def run_pipeline():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task_db())
            tg.create_task(task_api())
    except* ConnectionError as eg:
        for exc in eg.exceptions:
            logger.error("Connection failed: %s", exc)
    except* TimeoutError as eg:
        logger.error("Timeouts encountered across %d tasks", len(eg.exceptions))
```

### Non-Blocking Async Execution
Never execute blocking CPU-bound code or blocking synchronous I/O in the async event loop. Offload to threads or process pools:
```python
# Offload blocking operations to thread pool
digest = await asyncio.to_thread(synchronous_heavy_computation, payload)
```

---

## 🏎️ 5. High-Performance Data Modeling & Control Flow

*References: [Fluent Python, 2nd Edition](https://learning.oreilly.com/library/view/-/9781492056348/?orm_source=mcp) (Luciano Ramalho) & [High Performance Python, 3rd Edition](https://learning.oreilly.com/library/view/-/9781098165956/?orm_source=mcp) (Micha Gorelick & Ian Ozsvald)*

### High-Performance Dataclasses (`slots=True`, `frozen=True`, `kw_only=True`)
Use `slots=True` to eliminate dynamic instance `__dict__` overhead, achieving 40–50% memory savings and faster attribute resolution.
```python
from dataclasses import dataclass
from enum import StrEnum

class VulnerabilityStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

@dataclass(slots=True, frozen=True, kw_only=True)
class VulnerabilityRecord:
    id: str
    title: str
    risk_rating: str
    status: VulnerabilityStatus = VulnerabilityStatus.OPEN
```

### Structural Pattern Matching (`match / case`)
Use structural pattern matching for concise, type-safe payload decomposition and guarded dispatch:
```python
def handle_event(event: dict[str, object]) -> None:
    match event:
        case {"type": "scan_complete", "scan_id": str(scan_id), "vulns": list(vulns)} if len(vulns) > 0:
            logger.info("Scan %s finished with %d findings", scan_id, len(vulns))
        case {"type": "scan_complete", "scan_id": str(scan_id)}:
            logger.info("Scan %s finished with zero findings", scan_id)
        case {"type": "ping"}:
            logger.debug("Received heartbeat ping")
        case _:
            logger.warning("Unrecognized event structure: %s", event)
```

### Methods Without `self` Belong Outside the Class (Module-Level Private Functions)
If a method within a class does not access instance state (`self`), do NOT define it as an instance method (or `@staticmethod`) inside the class. Extract it as a module-level private function (prefixed with `_`) outside the class.
- **Why**: Keeps class contracts minimal, focused, and trivial to review and understand. It cleanly separates stateful class behavior from pure helper/transformation logic and avoids cluttering class namespaces.

```python
# BAD: cluttering class definition with helper methods that don't need `self`
class MemoryManager:
    def _is_safe_path(self, category: str, target: str) -> bool:
        # Does not use self!
        return not (".." in category or "/" in category)

    def _extract_repo_name(self, url: str) -> str:
        # Does not use self!
        return url.split("/")[-1]

# GOOD: extracted as private module-level functions outside the class
def _is_safe_path(category: str, target: str) -> bool:
    return not (".." in category or "/" in category)


def _extract_repo_name(url: str) -> str:
    return url.split("/")[-1]


class MemoryManager:
    def sync(self) -> bool:
        ...
```

---

## 🚫 6. Strict Prohibition on `getattr()` and `hasattr()`

> [!CAUTION]
> **`getattr()` and `hasattr()` are strictly prohibited in favor of good static typing.**
> Dynamic attribute reflection is almost always an anti-pattern masking missing or incomplete static typing. It blinds `mypy`/`pyright`, breaks IDE navigation, and hides runtime errors.

### Why They Are Prohibited:
1. **Masks Incomplete Types**: Checking `hasattr(obj, "field")` or using `getattr(obj, "field", default)` indicates the object contract is underspecified. Use explicit `@runtime_checkable` `typing.Protocol`, concrete classes, or subclass `abc.ABC`.
2. **Breaks Static Analysis**: Type checkers cannot verify method signatures or return types dynamically looked up via `getattr`.
3. **Polymorphic Model Anti-Pattern**: Never use `getattr(target, "field", None)` to probe polymorphic models (e.g., Django `Target` or `Asset`). Use explicit `isinstance(target, ConcreteModel)` checks with type narrowing and direct attribute access.
4. **Django Models Gotcha**: **NEVER** use `hasattr()` or `getattr()` to check for related models, `ForeignKey`, or `OneToOne` relations. Access the typed attribute directly: `model.relation`. Check for `None` on optional fields (`if model.relation is not None:`). If accessing a reverse OneToOne that might not exist, use an explicit `try...except RelatedObjectDoesNotExist:` block.

### Alternatives Table:
| Anti-Pattern (Forbidden) | Clean Type-Safe Alternative |
| :--- | :--- |
| `if hasattr(obj, "run"): obj.run()` | Define `@runtime_checkable class Runnable(Protocol): def run(self) -> None: ...` and check `isinstance(obj, Runnable)`. |
| `pkg = getattr(target, "package_name", None)` | Use explicit `isinstance` branches: `if isinstance(target, AndroidStoreTarget): return target.package_name`. |
| `val = getattr(model, "score", 0)` | Model `score: int = 0` directly on the Pydantic model / Dataclass, or use `model.score`. |
| `owner = getattr(asset, "owner", None)` | Direct attribute access: `owner = asset.owner if asset is not None else None`. |
| `getattr(third_party_obj, "data")` | Define a typed wrapper or use `typing.cast(ExpectedType, third_party_obj).data`. |
| Dynamic key lookup on arbitrary object | Use a typed dictionary (`dict[str, Any]`, `TypedDict`) with `.get("key")`. |

---

## 🧪 7. Testing Standards & Test Quality (pytest)

*References: [Python Testing with pytest, 2nd Edition](https://learning.oreilly.com/library/view/-/9781680509427/?orm_source=mcp) (Brian Okken) & [Test-Driven Development with Python, 3rd Edition](https://learning.oreilly.com/library/view/-/9781098148706/?orm_source=mcp) (Harry Percival)*

### Strict 1-to-1 File-Matching Test Architecture
- Every source file (`path/to/xxx.py`) **MUST** have a matching test file in `tests/path/to/xxx_test.py`.
- **Strict Prohibition on Ad-Hoc Feature Test Files**: Never create separate, arbitrarily named test files for specific features, tickets, or sub-components. Tests must live in the corresponding file's test module (`types_test.py` or `authenticated_test.py`).

### Pytest Function Naming Convention
Test function names must follow the `testAction_conditionCamelCase_expectedResult` convention:
```python
def testCalculateRiskScore_whenVulnerabilitiesEmpty_returnsZero():
    ...

def testParseFeed_whenXmlIsMalformed_raisesFeedParsingError():
    ...

def testAuthenticateUser_whenTokenIsExpired_raisesAuthenticationError():
    ...
```

### No Useless Unit Tests & No Tautological Mocking
> [!IMPORTANT]
> **Avoid Useless Unit Tests**:
> - Never write unit tests that mock a dependency and only assert on the mock's call status (`mock.assert_called_once()`) or assert on the mock's configured return value without exercising real production code or verifying actual logic/state transitions.
> - **Never mock the unit or system under test itself** (the actual function, method, or class being tested), as this makes the test completely useless.
> - Always prefer using real, concrete objects, state verification, and integration tests over excessive mocking. Only mock out-of-process boundaries (network calls, external databases, third-party APIs).

### Test Optimization & Fixture Discipline
- **Never Test or Mock Private Methods**: Do not mock or test methods starting with a leading underscore (`_private_method`). Test through the public interface.
- **Fast Tests & Retry Disabling**: If the code under test uses `tenacity` for retries, disable retry delays in the test:
  ```python
  func.retry.wait = tenacity.wait_none()
  ```
- **Mock `time.sleep`**: If the code performs a sleep, always mock `time.sleep`:
  ```python
  def testExecute_whenRateLimited_retries(mocker):
      mocker.patch("time.sleep")
      func()
  ```
- **Dead Fixtures**: Use `pytest-deadfixtures` to identify and remove unused fixtures. Deduplicate fixtures across root and app `conftest.py`.

---

## 🧱 8. Error Handling & Exception Architecture

### Module/Package Base Exception Hierarchy
Every package or domain module should define a top-level `Error` base class inheriting from `Exception`. All specialized domain exceptions must inherit from this base `Error`:
```python
class Error(Exception):
    """Base exception for all errors in this module."""

class ScanExecutionError(Error):
    """Raised when scan execution fails."""

class InvalidScanProfileError(ScanExecutionError):
    """Raised when an invalid scan profile is specified."""
```

### Exception Guidelines
- **CapWords Naming**: Use `CapWords` naming ending in `Error` for all exception classes.
- **No Catch-All `except Exception:`**: Never catch generic `Exception` without specific justification and logging.
  > [!TIP]
  > **MCP Tools Exception**: Top-level `except Exception:` blocks in MCP tool handlers are permitted and encouraged when logging exceptions internally and returning sanitized, user-friendly error strings to prevent leaking stack traces or internal secrets to LLMs.
- **Flat Exception Handling (No `isinstance` in `except`)**: Never catch multiple exceptions in a tuple only to inspect or re-raise based on `isinstance(e, ...)` inside the handler. Let Python's native exception dispatcher handle types across separate `except` clauses:
  ```python
  # BAD
  except (UsageLimitExceeded, UsageLimitExceededError) as e:
      if isinstance(e, UsageLimitExceededError):
          raise
      raise UsageLimitExceededError from e

  # GOOD
  except UsageLimitExceededError:
      raise
  except UsageLimitExceeded as e:
      raise UsageLimitExceededError from e
  ```
- **Zero Tampering with Private/Underscored Library Internals**: Never reach into private attributes (e.g. `obj._state.usage = ...`) of third-party or framework objects across module boundaries. Always leverage public parameters (e.g. `Agent.run(..., usage=initial_usage)`), public methods, or immutable constructors.
- **Base Class Polymorphism Over Orchestrator Type Branching**: When managing execution lifecycles, warning horizons, or error recovery across domain entities, implement the behavior directly on the base domain class (e.g. `AIAgent.run()`). Avoid wrapper layers or runner loops that branch on object types with `isinstance(obj, AIAgent)`.

---

## 📝 9. Code Cleanliness, Tooling & Modern Ecosystem

- **Unified Configuration**: Use `pyproject.toml` (PEP 621) for project dependencies, tool configurations, and metadata.
- **Simplicity First & Anti-Overengineering (Occam's Principle)**:
  - Always search for the simplest viable solution before building complex machinery, custom parsers, regex mutation engines, or new architectural layers.
  - In agentic/LLM systems, evaluate whether a clear prompt or skill instruction solves the problem before writing redundant backend parsing pipelines.
  - Reuse existing data pipelines, models, and helper utilities whenever possible rather than creating parallel mechanisms.
  - Minimize blast radius: smaller, direct diffs are more reliable, easier to review, and less prone to regressions.
- **Linter & Formatter (`ruff`)**: Rely on `ruff` for all formatting and linting (pyupgrade, flake8-bugbear, isort). Do not nitpick purely mechanical formatting in PR reviews.
- **Package Management (`uv`)**: Standardize on `uv` for fast, deterministic dependency resolution.
- **Static Typing (`mypy` / `pyright`)**: Run static type checkers in strict mode (`--strict`).
- **No Unnecessary Wrappers**: Do not create wrapper functions that simply forward calls to another function without transforming data or adding logic.
- **Accurate Function Naming**: Ensure function and method names accurately describe what the body implementation does.
- **Single Responsibility & Function Length**: Split large functions into smaller, focused functions. The code should read like simple prose to clearly convey its intention.
- **No Maximum Line Length Restriction**: Do not artificially wrap lines based on an arbitrary character limit; keep logical units and expressions together.
- **Strings & Resources**:
  - Use f-strings for string interpolation (except in logging where parameterized formatting is preferred).
  - Use context managers (`with` statements) and `contextlib.closing()` for all resource lifecycles.
  - Include issue tracker references in all `TODO` comments (`# TODO(#1234): ...`).

---

## 🌐 10. API Classification & Architecture

Use standardized filenames to classify API access and authorization tiers:
- `public.py`: Non-authenticated, publicly accessible endpoints and schemas.
- `authenticated.py`: Authenticated access (MUST enforce authorization and tenant isolation).
- `robot.py`: Privileged internal system communication and service-to-service endpoints.

---

## 🛡️ 11. Security, Multi-Tenancy & Platform Integrity

- **Vulnerability DNA & Deduplication Immutability**:
  - **NEVER** modify, strip, or sanitize URL schemes, default ports (`:80`, `:443`), or paths inside functions named `_build_url`, `_stable_dna_location`, `dna`, or functions creating `VulnerabilityLocation` objects. Modifying these strings corrupts historical finding deduplication hashes across the Ostorlab scanning platform.
- **Multi-Tenancy Access Logic**:
  - In Ostorlab backend services, `has_object_level_access = False` grants organization-wide access for organization API keys; owner scoping is only enforced when `has_object_level_access = True`.
- **Dev / CI / Mock Settings**:
  - Do not flag hardcoded dummy secrets or passwords in `settings_dev.py`, `settings_ci.py`, `settings_test.py`, conftest fixtures, or test mocks.
  - Do not suggest dynamic random tokens (e.g., `secrets.token_urlsafe()`) in development settings as they break CSRF and session persistence on process restart.

---

## 🕵️ 12. Code Review & Autonomous Verification Protocol

- **Strict Ban on "Please Verify / Check" Comments**:
  - Reviewers and AI agents must investigate issues autonomously using available inspection tools (`get_file_content`, search, callers/callees) to confirm defects before commenting.
  - **Never** ask the PR author to "verify", "check", "ensure", or "confirm" whether something works. Asking the author to verify is NOT a review comment.
  - If a defect is confirmed, state the finding assertively with concrete evidence. If an issue cannot be confirmed, remain silent.
- **Severity Calibration (Definition of Critical)**:
  - `Critical` is strictly reserved for catastrophic defects: fatal crashes on primary workflows, critical security vulnerabilities (auth bypass, RCE), or permanent data corruption/loss.
  - Unhandled exceptions that might never happen in practice, rare theoretical edge cases, missing defensive checks, or speculative failure modes must **NEVER** be classified as `Critical` or `Major`. Classify them as `Minor` / `Maintainability` ("can be improved").
- **Exhaustive Review**: Deliver all verified findings and review comments at once in a single comprehensive review. Never cap or withhold comments due to PR size.
