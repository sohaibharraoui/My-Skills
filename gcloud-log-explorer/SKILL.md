---
name: gcloud-log-explorer
description: Investigate and export Google Cloud logs (Ostorlab scan universes, agent keys, scan IDs, or general GCP resources) directly into a persistent JSON file in the workspace. Always saves complete logs to disk, provides clickable file references, and produces structured inspection summaries. Use when investigating scan runs, troubleshooting GCP services, pulling un-truncated logs, or querying Cloud Logging.
---

# GCloud Log Explorer & Exporter

Investigate, query, and export Google Cloud Platform (GCP) logs with guaranteed file persistence.

> [!IMPORTANT]
> **Mandatory File Export Contract**:
> - **Always save logs to a file**: Never dump thousands of raw log entries to stdout or the terminal buffer. Every query **MUST redirect its full output to a JSON file** in `./logs/` within the current workspace.
> - **Always provide a clickable file reference**: The assistant must always present the absolute path as a clickable Markdown link: `[<filename>](file:///absolute/path/to/logs/<filename>)`.
> - **Provide high-density inspection summaries**: Include total entry count, time range, severity breakdown, agent breakdown, and highlight critical errors with timestamps so the user can inspect specific records immediately.

The user is already authenticated with `gcloud`. Do not run authentication or project-setup commands unless explicitly requested.

---

## 🏛 Supported Query Types

### 1. Ostorlab Scan Universes & Agents (Primary)
Google Cloud Logging for scan universes uses these label keys:
- **Universe ID**: `labels.universe` (e.g. `labels.universe="421612"`)
- **Agent Key**: `labels.agent_key` (e.g. `labels.agent_key:"agent/ostorlab/nuclei"`)

#### Automatic Scan ID to Universe ID Resolution
When provided a **Scan ID** from the Reporting Engine (e.g. `204478`):
1. Query the Reporting Engine GraphQL API:
   ```graphql
   query GetUniverseId($scanId: Int!) {
     scan(scanId: $scanId) {
       id
       universeIds
     }
   }
   ```
2. Extract the `universeIds` list (e.g. `[421612]`).
3. Use the resolved `universe_id` in `labels.universe="<UNIVERSE_ID>"`.

### 2. General GCP Resource & Service Queries (Consolidated GCP Exporter)
You can query and export logs for any GCP service (Cloud Run, GKE, Cloud SQL, Composer):
- Cloud Run: `resource.type="cloud_run_revision" AND resource.labels.service_name="<service>"`
- GKE Pod: `resource.type="k8s_container" AND resource.labels.pod_name:"<prefix>"`
- Cloud SQL: `resource.type="cloudsql_database"`
- High Severity Errors: `severity>=ERROR`

---

## 🚀 Execution & Export Workflow

### Step 1: Ensure Log Directory & Output Path
Always place exported logs inside a `./logs` subfolder in the workspace:
```bash
workspace_dir="$(pwd)"
mkdir -p "$workspace_dir/logs"
```

Output naming convention:
- Scan Universe: `logs/universe-<universe_id>-logs-<timestamp>.json`
- Specific Agent: `logs/universe-<universe_id>-<agent_slug>-logs-<timestamp>.json`
- General GCP: `logs/gcp-<service>-logs-<timestamp>.json`

### Step 2: Execute `gcloud logging read` with Output Redirection
Always use `--format=json` and redirect directly to the output file. Never cap with `--limit` unless explicitly asked by the user.

#### Option A: Entire Universe (All Agents, Last 7 Days)
```bash
universe_id="421612"
output_file="$workspace_dir/logs/universe-${universe_id}-logs-$(date -u +%Y%m%dT%H%M%SZ).json"

gcloud logging read \
  "labels.universe=\"${universe_id}\"" \
  --freshness=7d \
  --order=desc \
  --format=json \
  > "$output_file"
```

#### Option B: Specific Agent in Universe
```bash
universe_id="421612"
agent_key="agent/ostorlab/nuclei"
agent_slug=$(echo "$agent_key" | tr '/' '_')
output_file="$workspace_dir/logs/universe-${universe_id}-${agent_slug}-logs-$(date -u +%Y%m%dT%H%M%SZ).json"

gcloud logging read \
  "labels.universe=\"${universe_id}\" AND labels.agent_key:\"${agent_key}\"" \
  --freshness=7d \
  --order=desc \
  --format=json \
  > "$output_file"
```

#### Option C: Chronological Explicit Timestamp Range
```bash
output_file="$workspace_dir/logs/universe-${universe_id}-logs-$(date -u +%Y%m%dT%H%M%SZ).json"

gcloud logging read \
  'labels.universe="421612" AND timestamp >= "2026-08-21T00:00:00Z" AND timestamp <= "2026-08-28T23:59:59Z"' \
  --order=asc \
  --format=json \
  > "$output_file"
```

#### Option D: Generic GCP Resource Filter
```bash
output_file="$workspace_dir/logs/gcp-errors-$(date -u +%Y%m%dT%H%M%SZ).json"

gcloud logging read \
  'resource.type="k8s_container" AND severity>=ERROR' \
  --freshness=3d \
  --format=json \
  > "$output_file"
```

---

## 🔍 Log Inspection & Reference Tool

A lightweight, zero-dependency Python inspection utility is bundled with this skill at `scripts/inspect_logs.py`. Use it to analyze and reference the file without overflowing token limits:

### 1. Executive Summary & Counts
```bash
python3 /home/sohaib-harraoui/.gemini/config/skills/gcloud-log-explorer/scripts/inspect_logs.py "$output_file" --summary
```
Prints:
- Total entry count
- Timestamp range
- Breakdown by severity (`INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- Breakdown by scanning agent / pod name
- Top 5 error messages with entry indices

### 2. Slicing & Searching within the Exported File
```bash
# Filter errors from a specific agent
python3 <skill_dir>/scripts/inspect_logs.py "$output_file" --agent "nuclei" --severity ERROR

# Grep for substrings inside messages (e.g. exception, timeout, OOM)
python3 <skill_dir>/scripts/inspect_logs.py "$output_file" --grep "Connection refused"

# View full JSON payload of a specific entry index
python3 <skill_dir>/scripts/inspect_logs.py "$output_file" --entry 42
```

---

## 📋 Standard Response Structure

When reporting log query results to the user, always follow this structure:

1. **File Artifact Link**:
   - Provide the clickable link: `📄 Exported Log: [universe-421612-logs-20260908T123000Z.json](file:///absolute/path/to/logs/universe-421612-logs-20260908T123000Z.json)`
   - File size on disk (e.g. `14.2 MB`)
2. **Query Metadata**:
   - Universe ID / Scan ID / Filter used
   - Time window covered
   - Total records retrieved
3. **Breakdowns**:
   - Severity distribution table
   - Agent / component breakdown table
4. **Key Findings & Errors**:
   - Specific failure points, uncaught exceptions, or timeout errors with timestamps and references to their entry indexes in the file.
5. **Logs Explorer UI Query**:
   - Include the exact filter query ready to paste into the GCP Cloud Logging Console.

---

## 🛡️ Operational Safety Boundaries

- Strictly read-only operations (`gcloud logging read`).
- Never delete logs, alter retention policies, modify log sinks, or change IAM bindings.
- Always store exports inside the project/workspace directory (`./logs/`), never in `/tmp` or root paths.
- Redact obvious API keys, authorization bearer tokens, or database credentials before printing snippets in chat.
