---
name: user-journey-design
description: Design, map, audit, and optimize website user journeys, interactive product tours, information architectures, and conversion funnels based on authoritative UX literature (Kalbach, Rosenfeld, Podmajersky, Krug). Use when structuring homepage flows, evaluating product walkthroughs, aligning value propositions with user mental models, or auditing SaaS conversion journeys.
---

# User Journey & Experience Architecture Design

A battle-tested methodology for engineering user journeys, information architectures, interactive product tours, and high-conversion landing pages grounded in the foundational principles of:
- **James Kalbach** (*Mapping Experiences: A Complete Guide to Creating Value Through Journeys, Blueprints, and Diagrams*)
- **Louis Rosenfeld, Peter Morville & Jorge Arango** (*Information Architecture: For the Web and Beyond*)
- **Torrey Podmajersky** (*Strategic Writing for UX*)
- **Steve Krug** (*Don't Make Me Think!*)

---

## 🧭 The 4-Stage Experience Architecture Framework

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      The End-to-End User Journey Lifecycle                             │
├───────────────────┬───────────────────┬───────────────────┬────────────────────────────┤
│ 1. Frame & Align  │ 2. Map & Model    │ 3. Architect & UX │ 4. Convert & Measure       │
│ • Point of View   │ • Chronology      │ • Progressive     │ • Primary vs Secondary CTA │
│ • Mental Model    │ • Touchpoints     │   Disclosure      │ • Friction Removal (FAQ)   │
│ • Dual-Path Need  │ • Moments of Truth│ • IA Labeling     │ • Proof & Trust Anchors    │
└───────────────────┴───────────────────┴───────────────────┴────────────────────────────┘
```

---

## 1. Frame & Point of View (Kalbach & Krug)

### The First-Time Visitor Mental Model
Before presenting features or technology, every digital journey MUST answer the visitor's chronological questions in strict order:

1. **"What is this?"** *(Category definition & core purpose)*
2. **"Why should I care / What makes it different?"** *(Core differentiator & unfair advantage)*
3. **"How does it actually work?"** *(Operating model & mechanics)*
4. **"Does it fit my specific environment/stack?"** *(Coverage, frameworks & integrations)*
5. **"Who else trusts this?"** *(Proof-grade evidence, customer validation, case studies)*
6. **"Is anything stopping me?"** *(Friction elimination & FAQ)*
7. **"What do I do right now?"** *(Clear, unfragmented conversion actions)*

### The Dual-Path Strategy (Self-Serve + Enterprise)
Every modern technical product page must maintain two non-conflicting paths:
- **Product-Led Path (Bottom-Up):** Frictionless, zero-setup immediate value (e.g., `FREE Mobile Scan`, instant sandbox, interactive CLI).
- **Evaluation Path (Top-Down):** Structured walkthrough for engineering leads, CISOs, and enterprise evaluators (`Interactive Journey → Solutions → Book a Demo`).

---

## 2. Journey Mapping & Touchpoint Anatomy (Kalbach)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Anatomy of an Alignment Step                                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Action Name:      Concise verb-noun identifying the phase (e.g., "Discover")         │
│ • User Intent:      What the user aims to accomplish at this juncture                  │
│ • Capabilities:     The concrete features/products enabling this action                │
│ • Frontstage Touch: What the user sees (UI state, interactive preview, artifact)       │
│ • Backstage Engine: What the system executes (agents, APIs, scans, data pipelines)     │
│ • Moment of Truth:  The specific breakthrough or proof point that creates confidence   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Principles for Operating Models:
1. **Single-Container Interactive Surface:** Rather than forcing visitors to scroll through 7 disjointed sections, consolidate the operating model into a single interactive stage that updates state dynamically.
2. **Distinct Steps vs. Cross-Cutting Layers:**
   - **Linear Steps:** Sequence atomic actions cleanly (`Discover → Test → Monitor → Control → Contain / Fix → Measure`).
   - **Cross-Cutting Enablers:** Explicitly designate systemic layers (e.g., `Automate`, `API / MCP / Webhooks`, `Integrations`) as pervasive capabilities rather than an artificial final step.
3. **Show Concrete Artifacts:** Anchor each step in tangible proof (e.g., real proof-grade exploit verification, SARIF logs, code diffs, Jira tickets) rather than abstract marketing illustrations.

---

## 3. Information Architecture & Labeling (Rosenfeld & Morville)

### Progressive Disclosure
- **Top-Level (30 Seconds):** Category claim, core differentiation headline, and primary CTA.
- **Mid-Level (3 Minutes):** Unified interactive journey showcasing the 6-7 operating pillars.
- **Deep-Level (30 Minutes):** Specialized solution pages (Healthcare, Banking, Gaming, High-Tech), API docs, and compliance matrices.

### Labeling Discipline:
- **Never Combine Unrelated Verbs:** Keep discovery distinct from testing, and code remediation distinct from ticket delivery.
- **Avoid Ambiguous Industry Buzzwords:** Anchor terms in standard developer and security terminology (e.g., "Agentic Deep Scan", "Proof-backed exploitability", "SARIF", "MCP Server").
- **Strict Scope Boundaries:** Exclude unreleased or non-GA capabilities (e.g., Network pentesting) to preserve trust and messaging fidelity.

---

## 4. Strategic UX Writing & Microcopy (Podmajersky)

### Headline & Lead-in Formulation
- Lead with the **benefit and outcome**, followed immediately by the **mechanism**:
  * *Strong:* "Stop chasing noisy alerts. Autonomous agents validate real exploitability across your applications."
  * *Weak:* "We are a next-generation AI-powered multi-surface vulnerability platform."

### CTA & Button Rules (Podmajersky & Krug)
- Every CTA button must use an **action verb + object** (e.g., `Start Free Scan`, `Book a Demo`, `Compare Plans`).
- Never introduce novel, unintroduced CTAs in the closing conversion section.
- Limit closing CTAs strictly to the two established conversion paths (Product-Led vs. Sales-Led).

---

## 5. Review & Audit Checklist for Journey Artifacts

When auditing or reviewing user journey specifications or landing page PRs:

- [ ] **Chronological Question Test:** Does the document answer the 7 visitor questions in natural order?
- [ ] **Dual-Path Integrity:** Are the Product-Led and Enterprise paths distinct, frictionless, and mutually supportive?
- [ ] **Interactive Container Viability:** Is the operating model structured for a single-panel interactive state without scroll-hijacking?
- [ ] **Step vs. Layer Separation:** Are atomic workflow steps separated from cross-cutting enablers (like Automation / MCP)?
- [ ] **Proof-Grade Substantiation:** Is every major claim backed by a concrete moment of truth or artifact?
- [ ] **Scope Control:** Are unreleased products or experimental categories strictly filtered out?
- [ ] **Microcopy Precision:** Are button labels concise action verbs without redundant words or vague slogans?
