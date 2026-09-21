---
name: cxpak
description: Codebase AST dependency intelligence, token-budgeted context packing, blast radius analysis, architecture exploration, and data layer introspection across 43 languages. Use when onboarding to a repository, planning refactors, analyzing dependency graphs, tracing call graphs, checking blast radius, inspecting schemas/migrations, or packing context bundles for complex tasks.
---

# cxpak Code Intelligence & Context Packing Guide

`cxpak` indexes codebases using tree-sitter across 43 languages, builds typed dependency graphs, and produces token-budgeted context bundles. It spends CPU cycles upfront to provide high-density briefing packets rather than unbudgeted file dumps.

---

## ⚡ When to Use `cxpak`

| Scenario | Recommended Approach | Tool / Command |
| :--- | :--- | :--- |
| **New Repo Onboarding / Architecture Overview** | Generate structured summary, risk ranking, and module signatures | `cxpak overview <folder>` |
| **Pre-Refactor Blast Radius** | Find all downstream files/symbols affected by a proposed change | `cxpak graph path` / `cxpak graph neighbors` |
| **Path / Dependency Tracing** | Find how file A connects to file B or trace call hierarchies | `cxpak graph path --from A --to B <folder>` |
| **Task Context Packing** | Pack minimal, highest-relevance context for an instruction | `cxpak trace "<task_or_symbol>" <folder>` |
| **Review / Diff Inspection** | Contextual diff with dependency awareness | `cxpak diff <folder>` |
| **Visual Architecture Dashboard** | Offline interactive D3 dependency graph & risk treemap | `cxpak visual <folder>` |

---

## 🚀 Spawning MCP On-Demand for a Specific Project Folder

`cxpak` is designed to be spawned directly against the specific project repository you are actively working in.

### 1. Workspace-Scoped MCP (`.mcp.json` or `.agents/mcp_config.json`)
To enable `cxpak` MCP tools (`cxpak_context`, `cxpak_graph`, `cxpak_data`, `cxpak_review`, `cxpak_insight`) inside a specific project, create `.mcp.json` (or `.agents/mcp_config.json`) in that project's root:

```json
{
  "mcpServers": {
    "cxpak": {
      "command": "cxpak",
      "args": ["serve", "--mcp", "."]
    }
  }
}
```

When Antigravity or Claude Code opens that workspace folder, `cxpak serve --mcp .` will spawn inside that project root and index its AST dependency graph in the background.

### 2. Direct On-Demand CLI (No Daemon Required)
You can run `cxpak` on any folder at any time without running a persistent daemon:

```bash
# Overview for the current working directory
cxpak overview . --tokens 20k

# Overview for any specific repository
cxpak overview /path/to/repo --tokens 20k

# Blast radius / graph neighbors for a file
cxpak graph neighbors --id src/core/engine.rs /path/to/repo

# Trace a function or error through the call graph
cxpak trace "handle_request" /path/to/repo

# Token-budgeted contextual diff
cxpak diff /path/to/repo
```

---

## 🛠 MCP Tool Operations (5 Intent Tools)

When `cxpak` is running as an MCP server for your project workspace:

### 1. `cxpak_context` — Token-Budgeted Context Bundling
* **`op: "overview"`**: Structured repo summary (health dial, top risks, git context, module signatures).
  * *Parameters:* `tokens` (e.g. `"20k"`), `focus` (subdirectory filter).
* **`op: "context_for_task"`**: Packs the most relevant AST fragments for a specific task prompt.
  * *Parameters:* `task` (string description), `limit` (max files), `focus`.
* **`op: "briefing"`**: Produces a concise architectural briefing for a feature or bugfix.
  * *Parameters:* `task`, `tokens`, `focus`.
* **`op: "search"`**: Iterative retrieval over AST symbol index.
  * *Parameters:* `pattern`, `limit`, `focus`, `context_lines`.
* **`op: "retrieval"`**: Sub-selector retrieval (`retrieval_op: "search" | "references" | "expand"`).

### 2. `cxpak_graph` — Dependency Graph Queries
* **`op: "blast_radius"`**: Traces downstream impact of changing one or more files.
  * *Parameters:* `files` (array of repo-relative paths), `depth` (integer, default 2), `focus`.
* **`op: "graph"`**: Direct graph queries (`graph_op: "nodes" | "node" | "neighbors" | "path" | "subgraph"`).
  * *Parameters:* `from`, `to`, `seeds`, `depth`.
* **`op: "call_graph"`**: Computes function-level caller/callee trees.
  * *Parameters:* `target` (symbol name), `depth`, `focus`.
* **`op: "dead_code"`**: Discovers unreferenced symbols and unreachable exports.
  * *Parameters:* `limit`, `focus`, `workspace`.
* **`op: "api_surface"`**: Enumerates exported public endpoints, functions, and interfaces.

### 3. `cxpak_data` — Data Layer & Schema Introspection
* **`op: "data"`**: Analyzes SQL schemas, ORM models (Django, SQLAlchemy, Prisma, ActiveRecord), migration sequences, and column-level references.

### 4. `cxpak_review` — Code Review & Verification
* **`op: "diff"`**: Token-budgeted change summary with dependency context.
  * *Parameters:* `git_ref` (default `HEAD`), `tokens`, `focus`.
* **`op: "review"`**: Analyzes working tree or branch changes for architectural drift and risk.
* **`op: "verify"`**: Checks integrity of AST references across changes.

### 5. `cxpak_insight` — Health, Risk & Architecture
* **`op: "health"`**: Codebase maintainability, complexity, and coupling scores.
* **`op: "risks"`**: Ranked list of highest-risk files (complexity + churn + coupling).
* **`op: "architecture"`**: High-level module boundaries, layer violations, and dependency cycles.
* **`op: "conventions"`**: Extracted codebase conventions and naming patterns.
* **`op: "security_surface"`**: Attack surface map, auth middleware boundaries, and input sinks.

---

## 💻 CLI Quick Reference

```bash
# Repo overview within a token budget
cxpak overview . --tokens 20k

# Diff with dependency context
cxpak diff .

# Query graph nodes and neighbors
cxpak graph nodes .
cxpak graph neighbors --id src/core/engine.rs .
cxpak graph path --from src/api/routes.rs --to src/db/schema.rs .
cxpak graph subgraph --seeds src/auth/mod.rs --depth 2 .

# Trace error or function through call tree
cxpak trace "AuthError::InvalidToken" .

# Generate self-contained offline visual dashboard (HTML)
cxpak visual .

# Clean cache
cxpak clean .
```

---

## 📋 Best Practices

> [!TIP]
> **Use Before Large Refactors**: Always run `cxpak graph neighbors --id <file>` or `cxpak_graph(op="blast_radius")` before renaming methods, changing schemas, or refactoring shared utilities to ensure no caller is overlooked.

> [!NOTE]
> **Monorepos**: Use `--workspace <path>` to scope analysis to a sub-package while maintaining root git context.
