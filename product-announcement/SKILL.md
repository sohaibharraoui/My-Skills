---
name: product-announcement
description: Frameworks, narrative structures, positioning models, and copywriting standards for drafting high-impact technical product announcements, launch blog posts, and GTM articles. Use when announcing new products, major features, scan profiles, or architectural capabilities.
---

# Technical Product Announcement & Launch Playbook

A standard operating procedure for designing, positioning, and drafting high-impact technical product announcements, major feature launch articles, and Go-To-Market (GTM) blog posts.

---

## ⚡ Core Philosophy: The Paradigm Shift Engine

Technical product announcements fail when they are written as **dry release notes or feature checklists**. 

Great technical product announcements do not merely list capabilities—they **reframe the problem space, expose the fundamental breakdown of the status quo, and introduce the new product as the inevitable paradigm shift**.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE 5-STAGE LAUNCH NARRATIVE ARC                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. THE VISCERAL HOOK                                                       │
│     Open with an end-to-end, multi-step scenario demonstrating the exact    │
│     problem in action (e.g. an attacker pivoting across 5 asset boundaries).│
│                                   │                                         │
│                                   ▼                                         │
│  2. THE MECHANICS OF THE STATUS QUO BREAKDOWN                               │
│     Deconstruct why existing isolated tools (SAST, DAST, Mobile AST) fail   │
│     due to architectural silos, blind spots, and lack of shared context.    │
│                                   │                                         │
│                                   ▼                                         │
│  3. THE PARADIGM SHIFT (THE CORE INNOVATION)                                │
│     Introduce the product as a fundamentally connected architecture rather  │
│     than an incremental feature improvement.                                │
│                                   │                                         │
│                                   ▼                                         │
│  4. MULTI-DIMENSIONAL PROOF DEMONSTRATIONS                                  │
│     Provide 3-4 concrete, diverse, and reproducible technical proof points  │
│     complete with schemas, code snippets, payloads, and response outputs.   │
│                                   │                                         │
│                                   ▼                                         │
│  5. THE CLEAR ON-RAMP (CALL TO ACTION)                                      │
│     Provide frictionless, immediate pathways to try, deploy, or configure  │
│     the product (e.g. CLI commands, web links, documentation references).   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 Grounding in Authoritative Product Literature (O'Reilly Frameworks)

This playbook synthesizes battle-tested methodologies from leading product marketing, positioning, and narrative literature:

1. **Value Translation & Tiering** (*Cracking the Product Marketing Code* — Iman Bayatra):
   - Translate technical mechanisms into executive and developer value.
   - Categorize launches by impact: **Tier 1** (Category Shift), **Tier 2** (Major New Capability), **Tier 3** (Enhancement).
2. **Competitive Contrast & Category Positioning** (*The New Positioning* — Jack Trout):
   - Never position in a vacuum. Define the enemy: the friction, alert fatigue, and blind spots created by legacy point solutions.
   - Contrast *Siloed Testing* vs. *Connected Graph Intelligence*.
3. **Enterprise Proof & Complexity Navigation** (*Launching Enterprise Products* — Ravi & Malhotra):
   - Address enterprise realities: heterogeneous environments, cloud boundaries, internal microservices, and compliance overhead.
4. **Narrative Tension & Resolution** (*Storytelling in Design* — Anna Dahlström & *The Leader's Guide to Storytelling* — Stephen Denning):
   - Structure the article like a compelling story: setup the environment, trigger the obstacle/vulnerability, demonstrate the failure of traditional defenses, and deliver the resolution with reproducible proof.
5. **Modern Revenue Architecture & Flywheel** (*The Go-to-Market Cheat Code* — Gray & Wagner):
   - Ensure the announcement is actionable with self-serve on-ramps, live links, and shareable technical artifacts.

---

## 🏗 The 5 Pillars of Technical Announcement Copy

### 1. The Opening "Show, Don't Tell" Scenario
Never start with abstract corporate generalizations (*"We are thrilled to announce..."*). Start in media res with an authentic technical chain of events:
* *Bad:* "Today we are launching Multi-Asset Scanning which helps companies scan mobile apps and APIs together."
* *Good:* "Imagine an autonomous security agent given access to an organization’s architecture documentation, API schemas, mobile application, backend source code, and live web services all within the same assessment. Here is what happens when that agent investigates across all five asset boundaries in a single, connected workflow..."

### 2. Deconstructing the Mechanics of Breakdown
Explain *why* existing approaches fail mechanically:
* **SAST (Static Analysis):** Drowns teams in theoretical alerts because it lacks runtime reachability, schema awareness, and execution context.
* **DAST (Dynamic Analysis):** Hits a wall when confronted with HMAC request signing, custom client headers, multi-step authentication, or unlinked endpoints.
* **Mobile App Scanners:** Inspect client binaries in isolation, blind to backend bypass parameters or cloud logic flaws.
* **Network Scanners:** Catalog listening ports without understanding application semantics or business logic.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SILOED TOOLS VS. CONNECTED REASONING                     │
├───────────────────────────────────┬─────────────────────────────────────────┤
│ SILOED TOOLS (ISOLATED BLIND SPOTS│ CONNECTED AGENTIC GRAPH (SHARED CONTEXT)│
├───────────────────────────────────┼─────────────────────────────────────────┤
│ • SAST: Code without reachability │ • Code guides dynamic test generation   │
│ • DAST: Traffic without source/doc│ • Docs & schemas reveal hidden routes   │
│ • Mobile: Binary without backend  │ • Client decompilation solves HMAC/auth │
│ • Network: Ports without semantics│ • Cross-asset pivots prove exploitability│
└───────────────────────────────────┴─────────────────────────────────────────┘
```

### 3. Diverse, Multi-Hop Proof Points
Provide at least 3 distinct scenarios covering different corners of the tech stack:
* **Scenario A (Mobile + Backend Source + Live API):** Decompiling mobile binary for request signing, finding source bypass query parameter, executing live privilege escalation.
* **Scenario B (Architecture Docs + Public Web App + Internal Network Microservice):** Identifying internal private endpoint in OpenAPI docs, finding blind SSRF in web app, pivoting through internal network to exfiltrate private database credentials.
* **Scenario C (Source Repository Secret Leak + Live Cloud Service + IAM Escalation):** Extracting leaked staging API keys from Git history, authenticating against live cloud API, demonstrating unauthorized read/write to storage buckets.
* **Scenario D (Mobile Deep Links + Web OAuth Handler + Account Takeover):** Decompiling exported Android activity handlers, discovering wildcard OAuth redirect URIs on web, chaining them to intercept OAuth tokens.

### 4. Visual Terminal & Architecture Box Diagrams
Always include clean ASCII / Unicode box art diagrams to render system interactions cleanly across terminals, markdown viewers, and documentation sites.

### 5. Technical Artifacts & Proofs of Concept (PoCs)
Include real, sanitized HTTP request/response pairs, CLI invocations, or configuration blocks. Technical readers trust verified code and exact payloads far more than marketing claims.

---

## 📝 Canonical Article Structure Blueprint

```markdown
Title: <Action-Oriented, Value-Focused Title>
Date: YYYY-MM-DD HH:MM
Author: <Author Name>
Category: Product
Tags: <Tag1>, <Tag2>, <Tag3>
Slug: <url-friendly-slug>
Summary: <1-2 sentence high-density summary of the core breakthrough and impact>
Image: static/img/<folder>/cover.png
Thumbnail: static/img/<folder>/thumbnail.png

# <Engaging Hook: The Visceral Problem in Action>
[Step-by-step walkthrough of a concrete, multi-stage scenario illustrating the exact challenge]

```http
POST /api/v2/example-endpoint HTTP/1.1
Host: api.example.com
...
```

---

## Why Traditional / Siloed Approaches Fail
[Detailed breakdown of why existing isolated point tools cannot uncover or resolve this issue]
- **Tool Type A (e.g. SAST)**: [Specific mechanical limitation]
- **Tool Type B (e.g. DAST)**: [Specific mechanical limitation]
- **Tool Type C (e.g. Mobile)**: [Specific mechanical limitation]

---

## Introducing <Product / Feature Name>: <The Paradigm Shift>
[Explain the core architectural breakthrough and how connected context changes the outcome]

[Visual Unicode Diagram comparing Old vs New]

---

## Real-World Multi-Asset Attack Chains & Investigations

### 1. <Scenario Name: e.g. Internal Microservice Pivot via Documentation & SSRF>
[Step-by-step walkthrough with code/request snippets]

### 2. <Scenario Name: e.g. Hardcoded Credential Validation & Cloud IAM Pivot>
[Step-by-step walkthrough with code/request snippets]

### 3. <Scenario Name: e.g. Mobile Deep Link & OAuth Token Interception>
[Step-by-step walkthrough with code/request snippets]

---

## Key Capabilities & Configuration
[Clear breakdown of what is supported, effort levels, model selection, and integration options]

| Scope / Asset Type | Supported Formats / Sources | Value Delivered |
| :--- | :--- | :--- |
| **Mobile Apps** | Android APK/AAB, iOS IPA, App Store URLs | Full client decompilation & auth reverse engineering |
| **Web Applications & APIs** | REST, GraphQL, OpenAPI, Web SPAs | Live fuzzing, schema validation & SSRF testing |
| **Source Repositories** | Git repositories, source archives | Contextual logic auditing & secret reachability |
| **Network Ranges** | CIDR blocks, private subnets | Lateral movement & internal service discovery |
| **Documentation** | OpenAPI/Swagger, PDFs, Markdown | Architecture mapping & hidden route discovery |

---

## Getting Started: <Immediate Next Steps>
[Clear, actionable CTA with direct links and instructions]
```

---

## ❌ Banned Anti-Patterns vs. ✅ High-Impact Replacements

| ❌ Banned Anti-Pattern | Why It Fails | ✅ High-Impact Replacement |
| :--- | :--- | :--- |
| *"We are excited to announce our game-changing new AI tool."* | Generic marketing fluff; zero technical substance. | *"Today we are introducing Multi-Asset Deep Agentic Scan, connecting mobile binaries, backend source, and live APIs into a single investigation."* |
| *"Our AI scanner is 100% accurate with no false positives."* | Unbelievable claim; triggers immediate developer skepticism. | *"By cross-referencing source code logic with live API responses, the agent validates exploitability and produces deterministic, reproducible PoCs."* |
| *Passive feature dumping without context.* | Leaves the reader guessing why they should care. | *Walk through a multi-hop attack chain showing how asset A informed the exploit in asset B.* |
| *Hiding how the tool actually works under the hood.* | Technical buyers demand architectural clarity. | *Detail the ingestion of OpenAPI schemas, decompilation routines, and request generation mechanics.* |

---

## 🎯 6-Point Pre-Publication Quality Gate

Before submitting a product announcement PR or publishing a launch article, verify:

- [ ] **1. Visceral Opening Hook:** Does the article open with a concrete, multi-step technical scenario rather than corporate cheerleading?
- [ ] **2. Mechanical Causal Breakdown:** Does the article explain *why* traditional/siloed tools fail mechanically?
- [ ] **3. Diverse Proof Scenarios:** Are there at least 3 distinct, high-fidelity technical scenarios with payloads/code snippets?
- [ ] **4. Visual Architecture Box Art:** Is there a clean ASCII/Unicode diagram illustrating the connected workflow?
- [ ] **5. Accurate Metadata & Dates:** Are `Title:`, `Date:`, `Author:`, `Tags:`, `Slug:`, and image references verified and up to date?
- [ ] **6. Frictionless On-Ramp:** Does the conclusion provide clear, direct links/commands to test the new capability immediately?
