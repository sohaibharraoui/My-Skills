---
name: manage-agent-skills
description: Use when creating, updating, or maintaining skills, plugins, and configs in the agent-skills repository — enforces authoring standards, plugin conventions, and the mandatory push-to-remote synchronization protocol.
---

# Agent Skills Management & Synchronization Protocol

Standard operating procedure for authoring, modifying, testing, and synchronizing skills, plugins, and developer configurations across all development environments.

---

## ⚡ The Mandatory Golden Rule

> [!IMPORTANT]
> **Zero Local-Only State**: Whenever any skill, plugin manifest, MCP tool definition, or developer configuration is created, modified, or deleted on any machine, the agent MUST immediately execute the **Sync Protocol** and push changes to `origin main` before concluding the task.

---

## 📂 Repository File Placement Conventions

All customizations belong in `~/.config/agent-skills/`:

| Change Type | Target Location | Requirement |
| :--- | :--- | :--- |
| **New skill in existing plugin** | `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` | Follow YAML frontmatter standard |
| **New standalone plugin** | `plugins/<plugin-name>/` | Must include `plugin.json` manifest + `skills/` or `mcp_config.json` |
| **Submodule documentation** | `plugins/<submodule-name>/` | Add via `git submodule add <repo-url>` |
| **Tool sessions / credentials** | `config/<tool-name>/` | Move into repo and establish symlink `~/.config/<tool-name>` |
| **Global MCP configuration** | `plugins/<plugin-name>/mcp_config.json` | Encapsulate inside the relevant plugin |

---

## ✍️ Skill Authoring Standards

### 1. YAML Frontmatter Specification
Every `SKILL.md` MUST start with valid YAML frontmatter containing:
- `name`: Kebab-case identifier matching the directory name (e.g. `prod-gcp`, `manage-agent-skills`).
- `description`: 1-3 sentences in the third person stating **what the skill does** and **when the agent should trigger it** (e.g., `Use when diagnosing cluster issues, checking pods/deployments...`).

```markdown
---
name: my-new-skill
description: Comprehensive runbook for XYZ. Use when performing task A, troubleshooting B, or reviewing C.
---
```

### 2. Body Structure & Quality Guidelines
- **Concise & Actionable**: Provide concrete CLI commands, YAML examples, and step-by-step triage flows.
- **Markdown Links**: Link symbols and files using GitHub-style markdown.
- **Progressive Disclosure**: When referencing large documentation trees, point to index maps (e.g., `content/index.md`) rather than duplicating massive text blocks.
- **Alerts**: Use `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]` to highlight critical guidance.

---

## 🔄 The 5-Step Synchronization Protocol

Execute these exact steps whenever creating or updating skills:

```bash
# Step 1: Ensure you are in the agent-skills repository
REPO_DIR="$HOME/.config/agent-skills"

# Step 2: Update README.md file table & architecture if a new plugin or skill was added
# (Verify README.md reflects the new file tree)

# Step 3: Run the idempotent setup script to refresh links and submodules
$REPO_DIR/setup.sh

# Step 4: Check out a feature branch
git -C "$REPO_DIR" checkout -b feat/<skill-name>

# Step 5: Stage, review diff, and commit with Conventional Commits format
git -C "$REPO_DIR" add .
git -C "$REPO_DIR" commit -m "feat(skills): add <skill-name> covering <purpose>"

# Step 6: Push feature branch to remote (Never push directly to main!)
git -C "$REPO_DIR" push -u origin feat/<skill-name>

# Step 7: Open a Pull Request for human review
gh pr create --title "feat(skills): add <skill-name>" --body "..."

# Step 8: Verify CI and trigger automated bot review
gh pr checks
```

---

## 🔄 Submodule Update Protocol (e.g., `internal_docs`)

When updating an external submodule repository:

```bash
# 1. Pull the latest commits in the submodule directory
git -C ~/.config/agent-skills/plugins/internal-docs pull origin main

# 2. Record the updated submodule commit pointer
git -C ~/.config/agent-skills commit -am "chore(submodules): bump internal-docs to latest commit"

# 3. Push to remote
git -C ~/.config/agent-skills push origin main
```
