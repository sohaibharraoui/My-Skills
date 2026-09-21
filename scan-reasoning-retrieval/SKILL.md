---
name: scan-reasoning-retrieval
description: Programmatically extract and retrieve multi-risk agent reasoning (prompts, plans, tasks, bash commands, tool calls, and outputs) from Ostorlab GraphQL API for any scan ID or batch of scans. Always trigger this skill whenever a request mentions a scan ID or requests investigating, inspecting, retrieving, or analyzing the reasoning, steps, plans, tool calls, or execution traces of an Ostorlab scan or agentic deep scan (CyberGym or production), especially when container logs are unavailable or expired.
---

# Scan Reasoning Retrieval & Extraction

Standard operating procedure to programmatically extract turn-by-turn agent reasoning (prompts, plans, tasks, and full tool calls) from the Ostorlab GraphQL API (`agenticDeepScan`) for any scan ID or batch of scans.

---

## 1. Multi-Risk Reasoning Structure

Each Agentic Deep Scan produces structured multi-risk execution records:
1. **Reconnaissance Risk**: Initial attack surface reconnaissance and target discovery.
2. **Detection Risk**: Exploit synthesis, local vulnerability confirmation, harness compilation, and ASan crash triggering.
3. **Validation Risk**: Autonomous verification agent runs (differential validation, cross-scheme testing, invariant checking).

Both detection and validation risks store complete turn-by-turn execution traces:
- **`prompt`**: Initial agent instructions and task environment parameters.
- **`plan`**: Planner decomposition into sequential phases.
- **`tasks`**: Discrete subtasks (`ai_pentest_task`).
- **`toolCalls`**: Every executed tool call (`ai_pentest_toolcall`) containing tool `name`, input `args` (e.g. bash commands, file paths), and raw `output` (stdout, stderr, exit codes).

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Scan ID (e.g. 211279)                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ├── Detection Risk (e.g. 105361)                                                       │
│ │   ├── Prompt (Initial exploit instructions & harness location)                       │
│ │   ├── Plan (Planner decomposition into phases)                                       │
│ │   └── Analysis Tasks (Tasks 1..N)                                                    │
│ │       └── Tool Calls (Bash commands, file reads, ASan test runs)                     │
│ └── Validation Risk (e.g. 105375)                                                      │
│     ├── Prompt (Differential verification & invariant confirmation)                    │
│     ├── Plan (Bounds source review plan)                                               │
│     └── Analysis Tasks (Tasks 1..M)                                                    │
│         └── Tool Calls (Cross-scheme tests, verification server submissions)           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication & Session Requirements

The Ostorlab GraphQL resolver `resolve_agentic_deep_scan` enforces `@authorization.authorize(accepts_api=False)`. Consequently:
- Standard Organization API Keys (`X-Api-Key`) **cannot** access `agenticDeepScan`.
- An authenticated user session cookie (`sessionid`) is **mandatory**.
- A CSRF handshake against `https://api.ostorlab.co/apis/public_graphql` is performed to acquire `csrftoken`.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Programmatic Reasoning Retrieval Flow                                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   1. Handshake Phase                                                                   │
│      GET https://api.ostorlab.co/apis/public_graphql with cookie `sessionid`           │
│      └─► Extracts `csrftoken` from response headers / cookies                          │
│                                                                                        │
│   2. Query Execution Phase                                                             │
│      POST https://api.ostorlab.co/apis/graphql?org=<ORG_SLUG>                          │
│      Headers: X-CSRFToken, Referer: https://report.ostorlab.co/                       │
│      Payload: query AgenticDeepScan($scanId: Int!) { ... }                             │
│                                                                                        │
│   3. Serialization & Output Phase                                                      │
│      Filters substantive risks (with plans or tasks) and serializes to local JSON      │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Single-Scan Retrieval CLI

Use [`scripts/fetch_scan_reasoning.py`](file:///home/sohaib-harraoui/.gemini/config/skills/scan-reasoning-retrieval/scripts/fetch_scan_reasoning.py) to fetch complete reasoning for a single scan:

```bash
python3 /home/sohaib-harraoui/.gemini/config/skills/scan-reasoning-retrieval/scripts/fetch_scan_reasoning.py \
  --scan-id <SCAN_ID> \
  --output /path/to/scan_<SCAN_ID>_reasoning.json \
  --session-id "<SESSION_ID>" \
  --org "hqp"
```

### CLI Parameters:
- `--scan-id` *(required)*: Integer ID of the scan to extract.
- `--output` *(required)*: Output path for the serialized JSON.
- `--session-id` *(optional)*: Django `sessionid` cookie value (defaults to environment variable `OSTORLAB_SESSION_ID` or internal fallback).
- `--org` *(optional)*: Organisation slug (default: `hqp`).

### Output Data Schema:
```json
{
  "scan_id": 211279,
  "agentic_deep_scan_id": 105360,
  "total_risks_count": 2,
  "substantive_risks_count": 2,
  "risks": [
    {
      "id": "105361",
      "description": "Vulnerability Detection & Exploit Synthesis",
      "riskRating": "HIGH",
      "prompt": "...",
      "plan": "Phase 1: Local analysis...",
      "analysis": {
        "id": "54210",
        "tasks": [
          {
            "id": "1020",
            "description": "Examine target memory layout",
            "result": "...",
            "createdAt": "2026-09-20T10:00:00Z",
            "toolCalls": [
              {
                "id": "40201",
                "name": "run_bash_command",
                "args": {"command": "clang -fsanitize=address harness.c -o harness"},
                "output": "Compilation succeeded",
                "createdAt": "2026-09-20T10:01:00Z"
              }
            ]
          }
        ]
      }
    }
  ]
}
```

---

## 4. Batch Retrieval CLI (From CSV)

Use [`scripts/batch_fetch_reasoning.py`](file:///home/sohaib-harraoui/.gemini/config/skills/scan-reasoning-retrieval/scripts/batch_fetch_reasoning.py) when downloading reasoning for multiple scans (e.g., CyberGym validation batches):

```bash
python3 /home/sohaib-harraoui/.gemini/config/skills/scan-reasoning-retrieval/scripts/batch_fetch_reasoning.py \
  --csv /path/to/scans.csv \
  --output-dir /path/to/download_dir/ \
  --workers 6 \
  --session-id "<SESSION_ID>"
```

### Features:
- Concurrent downloads with worker thread pool.
- Automatic rate-limit handling (backoff on HTTP 429).
- Caching: skips scans that have already been retrieved and verified.

---

## 5. Downstream Integration

Once the reasoning JSON is retrieved, it can be consumed by:
- **`scan-reasoning-audit`**: Forensically inspect agent tool calls for anti-cheat verification (git history inspection, outbound network egress, server PoC exfiltration).
- **`exploit-scan-audit`**: Review vulnerability verification, ASan crash traces, and PoC correctness.
- **Incident & production investigation**: Understand exact decisions and failures in autonomous agent runs.
