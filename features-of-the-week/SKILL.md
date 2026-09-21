---
name: features-of-the-week
description: >-
  Curates and formats the cultural and closing features of The Breach Brief:
  Tool of the Week (🛠️), Event of the Week (📅), Book of the Week (📚), The Meme (😅), and One Question Before You Leave (❓).
---

# The Breach Brief: Features of the Week Skill

This skill formats the community, cultural, and thought-provoking sections of each issue.

## 1. 🛠️ Tool of the Week
* **Focus**: Pragmatic, open-source utilities or command-line tools that solve concrete engineering pain points.
* **Format**: Tool Name & Repository Link, Core Capabilities, and a local Quickstart CLI snippet.

## 2. 📅 Event of the Week
* **Focus**: High-signal, practitioner-first technical gatherings (e.g. GrrCON, AppSec Village at DEF CON, Ekoparty, Hackfest, OWASP Global).
* **Format**: Event Name, Date & Location, and a 2-paragraph overview emphasizing hands-on labs and low-ego technical culture.

## 3. 📚 Book of the Week
* **Focus**: Foundational computer security literature or definitive engineering books (*The Tangled Web*, *Cult of the Dead Cow*, *Android Hacker's Handbook*, *Practical Reverse Engineering*).
* **Format**: Book Title & Author, followed by a 2-paragraph narrative detailing how the historical or architectural lessons apply directly to modern defense.

## 4. 😅 The Meme
* **Focus**: Developer vs. Security tension, AI hallucinations, permission debt, or unexpected production incidents.
* **Format**: Structured dialogue mapped to classic relatable templates or short scenario captions.

## 5. ❓ One Question Before You Leave
* **Focus**: A single piercing, non-trivial question that challenges the reader's team defaults and lingers after they close the email.

## Output Schema
```markdown
### 🛠️ Tool of the Week
**[Tool Name]** - [Brief Tagline]
[Description and capabilities]
```bash
# Quickstart
pip install [tool]
```

---

### 📅 Event of the Week
**[Event Name]** — [Dates | Location]
[2-paragraph overview]

---

### 📚 Book of the Week
**[Book Title]** by [Author]
[2-paragraph review and defensive application]

---

### 😅 The Meme
[Meme Caption / Dialogue]

---

### ❓ One Question Before You Leave
[Single thought-provoking question]
```
