---
name: llm-council
description: Run decisions, subagent outputs, or bugfix proposals through a 5-advisor panel (Contrarian, First Principles, Executor, Architect, Outsider) for rapid stress-testing and synthesis. Use when deciding between architectures or trade-offs ('council this', 'council decision'), evaluating subagent iterations ('council subagent'), or comparing competing bug fixes ('council fix').
---

# LLM Council

One model's first answer often suffers from agreeable confirmation bias. If you ask "should I use approach A?", it produces 5 reasons in favor. If you ask "why is approach A bad?", it produces 5 reasons against.

**The LLM Council fixes this.** It runs the problem through 5 distinct cognitive lenses operating in creative tension, cross-examines their arguments, and delivers a decisive verdict: where they agree, where they clash, what blind spots they caught, and exactly what to do next.

Adapted from Andrej Karpathy's LLM Council methodology, streamlined for **Antigravity** and **Codex** to deliver fast, low-friction judgments in daily engineering workflows.

---

## 🎯 The Three Core Engineering Scenarios

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        LLM COUNCIL SCENARIOS                           │
├────────────────────────────────────────────────────────────────────────┤
│ 1. DECISIONS           Architecture, libraries, schema, API contracts  │
│ 2. SUBAGENT ITERATION  Reviewing subagent plans, diffs, and findings   │
│ 3. PROPOSING FIXES     Competing bug fixes, symptom vs root cause      │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Technical Decisions (`council decision`, `council this`)
- Evaluating trade-offs between competing technologies (e.g., Redis Streams vs Kafka, Polling vs Webhooks).
- Structuring core domain abstractions, data models, or breaking schema changes.
- Deciding whether to adopt a third-party dependency or build a minimal internal utility.

### 2. Subagent Iteration (`council subagent`)
- Evaluating a subagent's proposed plan, code changes, or test output before applying.
- Checking for hallucinated assumptions, incomplete requirements, or subtle behavioral regressions.
- Cross-examining edge cases when an autonomous agent claims a complex task is "complete".

### 3. Proposing Fixes (`council fix`)
- Diagnosing a recurring bug or production incident with multiple competing fix approaches.
- Comparing a quick defensive fallback vs a root-cause refactor (Occam's engineering principle: minimal blast radius vs systemic fix).
- Concurrency, race condition, caching invalidation, or memory leak resolution.

---

## 👥 The Five Advisor Lenses

Each advisor brings a dedicated perspective that creates natural checks and balances:

| Advisor | Cognitive Focus | Key Question |
| :--- | :--- | :--- |
| 🥊 **The Contrarian** | Blast radius, failure modes, security, edge cases | *"How will this break in production or under scale?"* |
| 📐 **The First Principles Thinker** | Root cause, assumptions, Occam's razor | *"Are we solving the real problem or patching a symptom?"* |
| ⚡ **The Pragmatic Executor** | Actionability, minimal diff, developer ergonomics | *"What is the cleanest, smallest diff we can ship right now?"* |
| 🏗️ **The Systems Architect** | Longevity, multi-tenancy, contracts, technical debt | *"How does this evolve over the next 12 months?"* |
| 👁️ **The Outsider** | Developer experience (DX), fresh eyes, cognitive load | *"Would a new engineer understand this in 5 minutes without context?"* |

---

## ⚡ Execution Modes: Simple & Pragmatic

Do not overcomplicate the council. Choose the mode matching task gravity:

### Mode A: Quick Inline Council (Default / Fast)
Use for standard decisions, routine fix evaluation, and quick subagent sanity checks. The agent assumes the 5 advisor lenses directly in a single turn without waiting for external round trips.

```text
User: "council fix: Should we wrap the Redis call in a retry decorator or catch RedisError in the worker loop?"
  │
  ▼
[Agent performs inline 5-lens stress-test & Chairman synthesis directly in response]
```

### Mode B: Deep Parallel Council (High Stakes / Multi-Agent)
Use for architectural pivots, large refactors, or critical security vulnerabilities.
1. The agent dispatches 5 parallel subagents (`invoke_subagent` in Antigravity or Codex subagents).
2. Each subagent runs one advisor lens with the framed prompt.
3. The parent agent collects the responses, anonymizes them for peer evaluation, and synthesizes the Chairman verdict.

---

## 🔄 Step-by-Step Workflow

### Step 1: Context Enrichment
Before running the council, gather local context:
- Scan `AGENTS.md`, project guidelines, and relevant source files.
- Inspect recent git diffs, failing test traces, or subagent logs.
- Identify the exact trade-off, constraints, and non-negotiables.

### Step 2: Frame the Decision / Fix
Express the dilemma neutrally in 3-4 bullet points:
- **Core Dilemma**: The specific choice to make (Option A vs Option B).
- **Context & Constraints**: System requirements, SLA, deadlines, dependencies.
- **Stakes**: What breaks if we make the wrong choice?

### Step 3: Run the 5 Perspectives
For each advisor, extract concise, punchy takes (2-4 sentences or bullet points each):
- **Contrarian**: Uncovers failure modes and silent side effects.
- **First Principles**: Challenges the premise; looks for a zero-code or 1-line solution.
- **Executor**: Assesses implementation effort, testability, and rollback ease.
- **Architect**: Checks compatibility, modularity, and future maintainability.
- **Outsider**: Flags unnecessary complexity, cryptic naming, or obscure APIs.

### Step 4: Synthesize the Chairman Verdict
Format the final verdict using the standard terminal-friendly layout:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          LLM COUNCIL VERDICT                           │
├────────────────────────────────────────────────────────────────────────┤
│ Question / Choice: [Short description of the decision or fix]          │
│ Alignment:         [Unanimous | Majority A | Majority B | Split]       │
│ Top Pick:          [Clear, unambiguous choice]                         │
│ Fatal Flaw / Trap: [Top pitfall flagged by Contrarian / Outsider]      │
│ Next Step:         [Immediate concrete action to execute]              │
└────────────────────────────────────────────────────────────────────────┘
```

Follow the box with structured synthesis sections:
1. **Consensus (Where the Council Agrees)**: Common ground established across lenses.
2. **Clashes (Genuine Tensions)**: Conflicting tradeoffs and why reasonable engineers disagree.
3. **Blind Spots Caught**: Non-obvious risks or simplifications revealed during review.
4. **The Recommendation**: A definitive decision with technical rationale (never say "it depends").
5. **Immediate Next Action**: The single concrete step to execute next.

---

## 📋 Concrete Examples

### Example 1: Evaluating a Bugfix Proposal (`council fix`)

**Context**: Worker crashes intermittently with `ConnectionResetError` during peak loads.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          LLM COUNCIL VERDICT                           │
├────────────────────────────────────────────────────────────────────────┤
│ Question / Choice: Retry decorator vs Connection Pool health checks    │
│ Alignment:         Majority Pool Health Check                          │
│ Top Pick:          Add pre-ping health check to pool configuration     │
│ Fatal Flaw / Trap: Retrying resets floods Redis during a network blip  │
│ Next Step:         Configure `health_check_interval=30` in pool init   │
└────────────────────────────────────────────────────────────────────────┘
```

- **Contrarian**: Wrapping individual calls in retries causes thundering herd when Redis restarts, amplifying downtime.
- **First Principles**: The connection was dropped by the OS firewall because of idle timeout. Retrying in application logic treats a transport lifecycle issue as a business logic error.
- **Executor**: A 1-line configuration change `health_check_interval=30` in the connection pool avoids wrapping 20 call sites.
- **Architect**: Centralizes connection reliability at the driver layer rather than leaking retry semantics into worker domain code.
- **Outsider**: Decorating every database/cache call makes the codebase noisy and masks underlying infrastructure degradation.

---

### Example 2: Subagent Iteration Check (`council subagent`)

**Context**: Subagent generated a 200-line custom token bucket rate limiter for an API endpoint.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          LLM COUNCIL VERDICT                           │
├────────────────────────────────────────────────────────────────────────┤
│ Question / Choice: Accept custom token bucket vs Use existing redis-ratelimit │
│ Alignment:         Unanimous Reject & Replace                          │
│ Top Pick:          Use standard redis-based limiter                    │
│ Fatal Flaw / Trap: In-memory token bucket fails across multi-pod deploys│
│ Next Step:         Instruct subagent to adopt `limits` library         │
└────────────────────────────────────────────────────────────────────────┘
```

- **Contrarian**: In-memory token bucket does not synchronize across Kubernetes replicas. Attackers can bypass limits simply by spraying round-robin pods.
- **First Principles**: Why write custom token math when Redis atomic commands (`INCR` + `EXPIRE`) or standard libraries (`limits`) already provide tested race-condition safety?
- **Executor**: Replace 200 lines of custom subagent code with 8 lines of standard dependency calls.
- **Architect**: Avoids maintaining bespoke state-machine tests and concurrency locks in application code.
- **Outsider**: Custom math is clever but creates maintenance overhead for the next developer debugging rate limits.

---

## 📌 Summary of Triggers

Trigger the skill whenever multi-angle validation is required:
- `council this: <decision / proposal>`
- `council fix: <competing fixes or bug scenario>`
- `council subagent: <subagent output or draft plan>`
- `run the council on <topic>`
- `pressure-test this`
- `debate this`
