# LLM Council — Antigravity & Codex Skill

Stop relying on agreeable, single-angle AI responses. Run decisions, subagent outputs, and bugfix proposals through a 5-advisor panel operating in creative tension to reach an evidence-backed verdict.

Based on [Andrej Karpathy's LLM Council](https://x.com/karpathy/status/1962263486196867115) methodology, streamlined for engineering environments (Antigravity & Codex).

---

## 🎯 When to Use

1. **Decisions (`council decision`, `council this`)**: Architecture, database/cache selection, API contract design, build vs buy.
2. **Subagent Iteration (`council subagent`)**: Multi-perspective verification of a subagent's plan, diff, or completed task before accepting it.
3. **Proposing Fixes (`council fix`)**: Competing bugfix proposals, evaluating minimal diff vs deep refactor, blast radius assessment.

---

## 👥 The 5 Advisors

- 🥊 **The Contrarian**: Blast radius, failure modes, security, edge cases.
- 📐 **The First Principles Thinker**: Root cause vs symptoms, Occam's razor, 1-line/zero-code solutions.
- ⚡ **The Pragmatic Executor**: Actionability, minimal diff, rollback ease, immediate execution.
- 🏗️ **The Systems Architect**: Longevity, contracts, multi-tenancy, technical debt.
- 👁️ **The Outsider**: Developer experience (DX), fresh eyes, readability, curse of knowledge.

---

## ⚡ Modes

- **Inline Council (Default / Fast)**: Immediate single-turn 5-lens stress-test directly in terminal conversation.
- **Deep Council (Parallel Subagents)**: Dispatches 5 subagents in parallel for high-stakes architectural pivots.

---

## 💻 Triggers

- `council this: <query>`
- `council fix: <options or bug scenario>`
- `council subagent: <plan or output>`
- `run the council on <topic>`
- `pressure-test this`
- `debate this`
