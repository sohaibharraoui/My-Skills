---
name: janitor-security
description: "Portable, read-only heuristic security scan of installed agent skills for prompt-injection phrases, hidden Unicode instructions, credential access, network-to-shell behavior, and payload smuggling. Use when checking skills before trusting or publishing them."
allowed-tools: Read, Bash(bash:*)
license: MIT
metadata:
  version: "1.6.0"
  author: "Krzysztof Hendzel <krzysztoff.hendzel@gmail.com>"
  compatibility: "Requires Python 3 and Bash; reads local skill files only; no network access."
  argument-hint: "[--path <dir>] [--json]"
  tags: "skills, security, prompt-injection, audit, maintenance"
---

# Security Scan

Heuristic scan of skill content for prompt-injection and malicious patterns.

## Overview

A skill is text your agent trusts: its SKILL.md is read as instructions and its scripts run on your machine. Public research (Snyk's ToxicSkills, 2026) found prompt injection in roughly a third of tested community skills. This scan flags the known bad shapes across every installed skill, in every scope (user, project, codex, plugin):

- **Injection phrases** — "ignore all previous instructions", "do not tell the user"
- **Hidden instructions** — imperative text in HTML comments (invisible when rendered), zero-width/bidi unicode between plain characters
- **Payload smuggling** — large decodable base64 blobs in markdown
- **Dangerous scripts** — network piped into a shell (`curl … | bash`), decode-and-execute, credential-store access (`~/.ssh`, `~/.aws`, keychain), URL shorteners, plain-HTTP calls, uploads of variable data

Findings are heuristics, not proof: a RISK verdict means "read this before trusting it". Legit tools trip these rules too (e.g. an installer that pipes curl into bash) — the point is that YOU see it and decide.

## Prerequisites

- Python 3. Bash is optional; `scripts/security.sh` is a convenience entrypoint
  for Unix-like hosts.
- No plugin installation, authentication, or network access is required.

## Instructions

### Step 1: Run the scan

```bash
scripts/security.sh                         # Unix-like hosts
scripts/security.sh --json                  # machine-readable report
scripts/security.sh --path ~/some/skill-dir # scan one skill or skills root
```

On hosts without Bash, run the portable implementation directly:

```bash
python3 scripts/security_scan.py
python3 scripts/security_scan.py --path path/to/skills --json
```

The scanner detects common Codex, Agents, Antigravity, and Claude roots when
they exist. It also checks project-local `.codex/skills`, `.agents/skills`, and
`.claude/skills` directories. Use `--path` for any host-specific location or
set `AGENT_SKILLS_DIRS` to a path-separated list of skill roots. The scan is
read-only and does not delete, modify, install, or publish anything.

### Step 2: Present verdicts honestly

Per-skill verdict: **RISK** (any HIGH finding), **REVIEW** (any MEDIUM), **PASS**. For each flagged skill show the finding titles, the file, and the evidence snippet. Do NOT call a finding "malware" — describe what the pattern does and let the user judge intent (e.g. "media-use pipes a HeyGen installer from the network into bash — a common install pattern, but verify the URL before trusting it").

### Step 3: Recommend next steps

- RISK on a skill the user doesn't recognize or need → `/janitor-swipe` or delete it outright
- RISK on a known/trusted tool → read the flagged file once, then move on
- Before installing something new → `/janitor-discover <url>` runs this same scan pre-install

## Output

Summary line (`Scanned: N | RISK: x | REVIEW: y | PASS: z`) followed by flagged skills, each with severity-tagged findings, the file, and an evidence snippet. `--json` emits the full structured report.

## Error Handling

1. **Error**: `security.sh: No such file or directory`
   **Solution**: The plugin is installed under a different root — locate it with `ls ~/.claude/skills` or check the plugin cache.

2. **Error**: Everything shows PASS but the user expected a finding
   **Solution**: The scan covers markdown and script files up to 1MB, 200 files per skill; binaries and huge files are skipped. Check the specific file manually.

3. **Error**: A trusted skill shows RISK
   **Solution**: Expected for tools that legitimately use flagged patterns (installers, credential helpers). Read the evidence line — if it matches the tool's documented purpose, note it and move on. Verdicts are advisory; nothing is deleted.

## Examples

### Example 1: Full audit

**Input**: "Are my skills safe? Check for prompt injection."

**Output**: Run the scan, lead with the summary ("178 scanned, 2 RISK, 0 REVIEW"), then explain each flagged skill in plain language with its evidence, and close with a recommendation per skill.

### Example 2: One suspicious folder

**Input**: "Scan ~/Downloads/cool-skill before I install it."

**Output**: Run with `--path ~/Downloads/cool-skill` and present the verdict; suggest `/janitor-discover` for the overlap check too.

## Resources

- Bundled scanner: `scripts/security.sh`
- Python implementation: `scripts/security_scan.py`
- Use `--path` to scan a downloaded candidate before installing it.
