---
name: type-hinting
description: Add Python3 type hinting to legacy codebases.
---

# Python Type Hinting Skill

## Purpose

This skill configures the agent to act as a **Python 3 static type-hinting assistant**.

When invoked, the agent will:
- Take existing Python 3 code.
- Add or improve static type hints (annotations) without changing behavior.
- Follow a consistent, modern typing style suitable for Python 3.10–3.13+.
- Eliminate dynamic reflection anti-patterns (`getattr`, `hasattr`) by introducing proper Protocols, ABCs, or explicit model fields.

---

## Usage

Ask the agent something like:

> "Use the **Python Type Hinting Skill** to add type hints to this code. Output only the updated code."

and then paste your Python code.

You can also say:

- "Annotate this file using the Python typing skill."
- "Add Python 3.10+ type hints according to our typing conventions."

---

## Typing Rules

### 1. General Style

- Target **Python 3.10+** (leveraging Python 3.12+ PEP 695 type parameter syntax where applicable).
- Prefer **modern type syntax**:
  - Use built-in generics (PEP 585): `list[int]`, `dict[str, Any]`, `set[str]`, `tuple[int, str]`.
  - Use union types as `X | Y` (PEP 604) instead of `Union[X, Y]`.
  - Use `type Alias = ...` (PEP 695) and `def func[T](items: list[T]) -> T:` syntax.
- Add `from __future__ import annotations` at the top of the file if it is not already present.
- Add or update `typing` imports as needed (e.g., `from typing import Any, Callable, Protocol, TypeIs, runtime_checkable`).

### 2. Strict Prohibition on `getattr()` and `hasattr()`

> [!CAUTION]
> **Do not introduce or preserve `getattr()` / `hasattr()` to bypass type checking.**
> If dynamic attribute access exists in the code because typing information was missing:
> 1. Define an explicit `typing.Protocol` with `@runtime_checkable` or subclass `abc.ABC`.
> 2. Add the missing attributes to the Pydantic model / Dataclass.
> 3. Use `typing.cast(TargetType, obj)` at external library boundaries.

### 3. What to Annotate

The agent should **always** annotate:

- **Function and method parameters**
  - Including optional parameters and parameters with default values.
  - Mark `self` and `cls` as unannotated (normal Python convention) unless existing style dictates otherwise.
- **Return types**
  - Every function and method gets a return type.
  - Use `-> None` for functions that do not explicitly return a value.
- **Class and instance attributes**
  - Add explicit attribute types when they can be reasonably inferred from initialization or usage.
  - Use class-level annotations or `self.attr: Type = ...` in `__init__`.

### 4. Inference vs `Any`

- **Prefer specific types** whenever they can be confidently inferred from:
  - Literals (`[]`, `{}`, `0`, `""`, etc.).
  - Operations on variables (e.g., list methods, dictionary access).
  - Typical usage and naming (e.g., `count` is likely `int`).
- **Use `Any`** when:
  - The type truly cannot be determined from context.
  - The design is intentionally dynamic or generic.
- Avoid overusing `Any`. Use it as a fallback, not the default.

### 5. Optional / `None` Handling

- When a value can be missing or explicitly `None`, use:
  - `T | None` (e.g., `str | None`, `int | None`).
- For parameters with a default of `None`, annotate accordingly:
  - `def find_user(id: int | None = None) -> User | None: ...`

### 6. Containers and Collections

- Use built-in generic syntax:
  - `list[int]`, `list[str]`, `list[MyModel]`
  - `dict[str, Any]`, `dict[str, int]`
  - `set[str]`, `set[int]`
  - `tuple[int, str]`, `tuple[str, ...]` for variable-length homogeneous tuples.
- For mapping-like objects with unknown values, prefer `dict[str, Any]` or `Mapping[str, Any]` depending on usage.

### 7. Structural Subtyping (`typing.Protocol`)

- Define explicit protocols for duck-typed objects:
  ```python
  from typing import Protocol, runtime_checkable

  @runtime_checkable
  class Closable(Protocol):
      def close(self) -> None: ...
  ```

### 8. Unions and Complex Returns

- If a function can return multiple specific types, annotate explicitly with a union:
  - `str | None`, `User | Error`, `Response | dict[str, Any]`
- Avoid `Any` when the valid set of types is known.
- Do **not** change the business logic; reflect the existing behavior accurately with static types.

---

## Code-Style Requirements

- **Do not change behavior or control flow.**
  - Only add or refine type hints and necessary imports.
- Preserve:
  - Existing **formatting and layout** as much as possible.
  - Existing **comments** and **docstrings**.
- Do **not** remove correct existing annotations.
  - Extend, refine, or align them with the chosen style if needed.

---

## Imports

When adding type hints, the agent may:

- Add:

  ```python
  from __future__ import annotations
  ```

- Add or update `typing` imports, such as:

  ```python
  from typing import Any, Callable, Protocol, TypeIs, runtime_checkable
  ```

- Use `if TYPE_CHECKING:` for heavy or circular imports when it improves performance or avoids runtime issues:

  ```python
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from mypackage.models import User
  ```

---

## Output Rules

When this skill is invoked, the agent should:

- **Output only the updated code**, as a single code block.
- Not include surrounding explanations, unless the user explicitly asks for them.
- Keep the code ready to paste back into a Python file.
