---
name: long-memory
description: Git-backed long-term developer memory for Antigravity. Use when searching past playbooks, recording architectural decisions (ADRs), storing troubleshooting solutions, or managing user preferences across projects.
---

# Git-Backed Long Memory System

Comprehensive guide for storing, retrieving, curating, and synchronizing long-term developer memory in Antigravity (`agy`).

---

## 🧠 Memory Taxonomy

All memory records are version-controlled Markdown files with YAML frontmatter stored in `~/.config/agent-skills/plugins/long-memory/memory/<category>/`:

| Category | Target Folder | Purpose | Example |
| :--- | :--- | :--- | :--- |
| **`preferences`** | `memory/preferences/` | Coding preferences, linters, tooling conventions | Preferred typing flags, linter configs |
| **`playbooks`** | `memory/playbooks/` | Incident triage, bug resolutions, recurring fixes | GKE Ingress 502, PG deadlock resolution |
| **`architecture`** | `memory/architecture/` | ADRs, system topologies, API contracts | Auth flow design, event pipeline schema |
| **`domain`** | `memory/domain/` | Domain terms, business rules, org structure | Vulnerability scoring definitions |
| **`scratchpad`** | `memory/scratchpad/` | Draft learnings awaiting refinement | Raw debugging notes |

---

## 🛠️ MCP Tools Usage

The `long-memory` MCP server provides the following tools:

### 1. `search_memory`
Search across titles, tags, content, and categories:
```json
{
  "ServerName": "long-memory",
  "ToolName": "search_memory",
  "Arguments": {
    "query": "GKE ingress 502",
    "category": "playbooks",
    "tags": ["gke", "networking"]
  }
}
```

### 2. `store_memory`
Record a new structured memory with automatic Git commit:
```json
{
  "ServerName": "long-memory",
  "ToolName": "store_memory",
  "Arguments": {
    "title": "GKE Ingress HTTP 502 with BackendConfig timeout",
    "category": "playbooks",
    "content": "### Problem\nIngress 502 during pod restart.\n\n### Fix\nSet timeoutSec to 60 in BackendConfig.",
    "tags": ["gke", "ingress", "502"],
    "related_projects": ["prod-gcp"],
    "confidence": "verified"
  }
}
```

### 3. `get_memory`
Retrieve full content and YAML metadata for a specific memory ID or file path:
```json
{
  "ServerName": "long-memory",
  "ToolName": "get_memory",
  "Arguments": {
    "memory_id_or_path": "MEM-20260824-..."
  }
}
```

### 4. `update_memory`
Refine an existing memory record or bump its confidence:
```json
{
  "ServerName": "long-memory",
  "ToolName": "update_memory",
  "Arguments": {
    "memory_id_or_path": "MEM-20260824-...",
    "content": "### Problem\n...\n### Updated Fix\n...",
    "confidence": "verified"
  }
}
```

### 5. `list_memories`
List all stored records grouped by category:
```json
{
  "ServerName": "long-memory",
  "ToolName": "list_memories",
  "Arguments": {
    "category": "architecture"
  }
}
```

---

## 🔄 Git Synchronization Protocol

When memory is created or modified:
1. The memory engine automatically creates an atomic local Git commit.
2. Changes synchronize with remote `origin main` during the standard 5-step `agent-skills` synchronization protocol.
