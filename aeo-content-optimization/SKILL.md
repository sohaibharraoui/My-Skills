---
name: aeo-content-optimization
description: Comprehensive Answer Engine Optimization (AEO / GEO) framework based on HubSpot Academy standards. Evaluates, audits, and generates content structured for direct citation and extraction by AI search engines (ChatGPT Search, Perplexity, Google AI Overviews, Claude, Gemini).
---

# Answer Engine Optimization (AEO) Content Skill

## Purpose & Overview
Answer Engine Optimization (AEO) — also referred to as Generative Engine Optimization (GEO) — is the methodology of structuring digital content so that Large Language Models (LLMs) and AI search engines can reliably parse, extract, and cite passages as direct, authoritative answers.

This skill equips the agent to:
1. **Audit existing content & drafts** against the 8 core AEO dimensions and generate an actionable gap analysis.
2. **Draft new content or rewrite existing articles** following answer-first, modular, and high-information-gain standards.
3. **Optimize heading hierarchies, FAQ modules, schema-ready definitions, and scannable data formats** for maximum AI extractability.

---

## The 8 Core AEO Dimensions & Checklists

### 1. Answer-First Structure (Passage-Level Directness)
> *AI systems extract content at the passage level. Pages leading with a clear, direct answer are significantly more likely to be cited.*

- [ ] **Immediate Direct Answer**: The page opens with a direct, comprehensive answer to the primary question within the first **40 to 60 words**.
- [ ] **Self-Contained Opening**: The opening answer can be understood completely on its own by a human or LLM without reading the rest of the page.
- [ ] **Supporting Context Placed After**: Background information, nuances, and supporting context appear *after* the direct answer, never before it.
- [ ] **Section-Level Inverted Pyramid**: Every major H2/H3 section begins with its core conclusion/key takeaway before elaborating with explanations or evidence.

---

### 2. Headers and Page Structure (Extraction Signals)
> *Descriptive, question-based headers act as extraction signals that help AI systems map queries to exact answer passages.*

- [ ] **Concise, Query-Framed Title Tag**: `<title>` clearly frames the exact question or topic and is under **60 characters**.
- [ ] **Accurate H1 Heading**: The single `<h1>` accurately reflects the page's core topic or primary question.
- [ ] **Specific & Descriptive Headers**: H2 and H3 headers are explicit and objective rather than generic (e.g., *"How long does mobile app penetration testing take?"* instead of *"Timeline"* or *"Process"*).
- [ ] **Natural Language Query Phrasing**: Headers use conversational, question-phrased queries that target audiences naturally type into AI prompts and search engines.
- [ ] **Objective Entity Headings in Comparisons (No "Best for")**: In comparison and review articles, keep vendor/product H3 headers clean and neutral (`### Vendor Name`). Never use subjective superlative labels like `### Vendor: Best for...`. Instead, place an objective, high-density bold `**Focus:**` statement directly under the heading (`**Focus:** [Objective capability and architectural focus]...`) as an extractable parse anchor.
- [ ] **Consistent Heading Hierarchy**: Clean, nested hierarchy (`H1` $\rightarrow$ `H2` $\rightarrow$ `H3`) without skipping levels.

---

### 3. Section Independence (Modularity)
> *AI search engines index and extract individual passages, not full pages. Each section must hold up as a stand-alone knowledge unit.*

- [ ] **Stand-Alone Modularity**: Every H2 section makes complete sense as an independent answer without requiring prior sections.
- [ ] **In-Place Term Definitions**: Key acronyms, terms, and core concepts are defined wherever they first appear in a section, rather than relying exclusively on an earlier introduction.
- [ ] **Zero Dependent Transitions**: Sections avoid backward-referencing filler (e.g., avoid *"As mentioned above"*, *"Building on the previous point"*, or *"In the previous section"*).
- [ ] **Landing-Ready Sections**: A user or AI engine landing directly on any sub-section immediately receives useful, complete, and contextually whole information.

---

### 4. Query Fan-Out Coverage (Sub-Query Addressing)
> *AI tools deconstruct complex prompts into multiple sub-queries. Pages addressing natural follow-up questions capture wider citation opportunities.*

- [ ] **Follow-Up Question Breadth**: The content addresses the primary intent plus the 3–5 most logical follow-up questions branching from it.
- [ ] **Dedicated, Extractable FAQ Section**: Includes a structured FAQ block where each Q&A pair is written as a concise, self-contained response.
- [ ] **Distinct FAQ Sub-Questions**: Each FAQ item tackles a distinct sub-problem or scenario rather than rephrasing previous points.
- [ ] **Header-Surfaced Sub-Questions**: Key secondary questions are promoted to explicit H2 or H3 headers to give AI parsers multiple discrete extraction anchors.

---

### 5. Definitions, Lists, and Scannable Formatting
> *Structured formats like explicit definitions, ordered/unordered lists, and comparison tables provide high-density parse tokens for LLMs.*

- [ ] **Clear Definition Sentences**: Key concepts are introduced with bolded subject definitions (e.g., `**[Concept]** is [definition]...`).
- [ ] **Bulleted & Numbered Lists**: Workflows, criteria, steps, and feature sets use list syntax instead of dense multi-line paragraphs.
- [ ] **Structured Comparison Tables**: Multi-option comparisons, tool evaluations, and pros/cons are formatted into markdown/HTML tables.
- [ ] **Context-Labeled Tables & Lists**: Tables and lists are preceded by descriptive introductory lines or subheadings so extracted data retains its semantic context.

---

### 6. Credibility and Information Gain Signals
> *AI models prioritize unique, high-entropy information from authoritative and verifiable sources.*

- [ ] **Original Information Gain**: Contains proprietary data, original benchmarks, firsthand practitioner experience, a unique case study, or proprietary analysis not found elsewhere.
- [ ] **Named Author & Byline**: Content is explicitly attributed to a named author with an identifiable byline.
- [ ] **Verifiable Author Credentials**: Author bio includes relevant professional credentials, industry experience, title, and linked professional profiles.
- [ ] **Direct Source Attribution**: External claims, statistics, and industry benchmarks are cited and hyperlinked to original primary sources.
- [ ] **Demonstrated Domain Depth**: Content demonstrates deep subject-matter authority and nuanced domain insights over generic regurgitation.

---

### 7. Freshness and Maintenance Signals
> *Answer engines favor accurate, up-to-date content. Explicit freshness signals establish trust and recency scoring.*

- [ ] **Visible Publish Date**: Clear timestamp showing the original publication date.
- [ ] **Visible "Last Updated" Date**: Prominently displayed modified/updated timestamp reflecting recent reviews.
- [ ] **Current Benchmarks & Statistics**: All statistics, tooling versions, regulatory citations, and data points reflect the current year.
- [ ] **Current Screenshots & Tool References**: UI captures and workflow descriptions match the latest active software releases.
- [ ] **Scheduled Review Cadence**: Content is tagged for regular maintenance cycles (at least quarterly for high-priority pages).

---

### 8. Audience Alignment and Product Connection
> *AI engines personalize answers to user context. Content tailored to a defined audience and connected to real solutions surfaces more frequently in recommendation prompts.*

- [ ] **Explicit Target Audience Framing**: Content directly speaks to a defined role, industry, or company stage (e.g., *"For DevSecOps engineers managing mobile CI/CD pipelines"*).
- [ ] **Contextual Vocabulary & Scenarios**: Examples, terminology, and edge cases reflect the realistic operating environment of that audience.
- [ ] **Direct Meta Description**: Meta description concisely summarizes the core answer in plain, specific language (under 160 characters).
- [ ] **Contextual, Non-Salesy Product Connection**: Includes at least one natural, value-additive mention or example connecting the problem to a relevant product/solution.
- [ ] **Descriptive Image Alt Text**: All diagrams, architectural figures, and images feature semantic, informative alt text describing the visual data.

---

## Operating Modes

### Mode 1: AEO Content Audit & Gap Analysis
When analyzing an existing article, draft, or URL:
1. Evaluate each of the 8 dimensions against the criteria.
2. Assign a score out of 100 based on standard checklist criteria.
3. Highlight missing extraction anchors (e.g., missing direct 40–60 word answer, vague headers, dependent transitions).
4. Provide immediate, drop-in replacement snippets for weak sections.

#### Audit Output Template
```markdown
# AEO Content Audit Report: [Page Title / URL]

## Overall AEO Score: [X / 100]

### Dimension Breakdown
| Dimension | Status | Score (/12.5) | Key Findings & Deficiencies |
| :--- | :---: | :---: | :--- |
| 1. Answer-First Structure | PASS / FAIL / WARN | X | [Notes] |
| 2. Headers & Page Structure | PASS / FAIL / WARN | X | [Notes] |
| 3. Section Independence | PASS / FAIL / WARN | X | [Notes] |
| 4. Query Fan-Out Coverage | PASS / FAIL / WARN | X | [Notes] |
| 5. Definitions & Scannable Formatting | PASS / FAIL / WARN | X | [Notes] |
| 6. Credibility & Information Gain | PASS / FAIL / WARN | X | [Notes] |
| 7. Freshness & Maintenance | PASS / FAIL / WARN | X | [Notes] |
| 8. Audience & Solution Connection | PASS / FAIL / WARN | X | [Notes] |

### Top 3 High-Impact Fixes
1. **[Direct Answer Optimization]**: [Exact proposed 40-60 word opening block]
2. **[Objective Focus Anchor Insertion]**: [Provide clean `### Entity` heading + objective `**Focus:**` statement rather than "Best for..."]
3. **[Modular FAQ / Table Insertion]**: [Extractable snippet]
```

---

### Mode 2: AEO-First Content Creation & Optimization
When generating or rewriting content:
1. **Draft the H1 & Title**: Formulate as high-intent questions.
2. **Draft the Direct Answer Block**: 40–60 word self-contained summary in the first paragraph.
3. **Structure H2/H3s with Query Phrasing**: Cover primary topic and fan-out queries. In comparison articles, keep vendor/product H3 headers clean (`### Vendor Name`) and immediately follow with an objective bold `**Focus:**` sentence (avoiding subjective "Best for..." phrases).
4. **Enforce Section Independence**: Define terms locally, eliminate inter-section transition dependencies.
5. **Add High-Density Elements**: Markdown tables, bulleted steps, and bolded definitions.
6. **Integrate Trust & Context Elements**: Primary citations, author attribution placeholder, freshness dates, audience callout, and semantic alt tags.
