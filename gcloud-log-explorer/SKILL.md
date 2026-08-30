---
name: gcloud-log-explorer
description: Investigate Google Cloud scan logs for a universe ID, including logs from multiple agents, and export the matching entries as JSON to the current workspace. Use when a user requests scan-log investigation, a universe-ID log pull, or a Logs Explorer query.
---

# GCloud Log Explorer

Use this skill to investigate scan runs by universe ID. The usual result is a
complete, read-only JSON export in the workspace from which the task is being
run, plus a concise summary of what was retrieved.

The user is already authenticated with `gcloud`. Do not run authentication or
project-setup commands unless they explicitly ask.

## Inputs and defaults

Required input:

- `universe_id`

Optional inputs:

- explicit start and end timestamps;
- project, log bucket, resource type, log name, agent ID, or severity filter;
- a different universe-ID field path; and
- output filename.

Unless the user provides an explicit range, query the last seven days with
`--freshness=7d`. Do not infer a narrower time range and do not default to one
agent: scan investigations can span several agents.

The default field path is `jsonPayload.universeId`. If the user identifies a
different path, use it exactly. Do not run a broad, unfiltered seven-day query
to guess the schema. If the default query returns no entries, report that and
ask for the actual field path or a representative log entry.

## Query and export workflow

1. Confirm the current workspace with `pwd`. Save the export there, never in a
   temporary directory or a parent directory.
2. Treat the universe ID as data, not shell syntax. Validate a numeric ID with
   `^[0-9]+$`; otherwise quote and escape it correctly for both the shell and
   the Logging query language.
3. Build a narrow filter using the universe-ID field. Add only filters the user
   requested. Include all agents by default.
4. Run `gcloud logging read` with `--format=json` and redirect its complete
   output to a new, timestamped file. Do not use `--limit` by default: its
   default is unlimited and a fixed limit can silently truncate a large scan.
5. Verify the command succeeded and that the resulting file is valid JSON.
   Report its absolute path, file size, entry count if available, time range,
   filter, and whether results were empty.
6. Do not print thousands of log entries in chat. Summarize the exported data
   and inspect selected entries only when the user asks.

For a normal numeric universe ID, last seven days, and the default field path:

```bash
workspace_dir="$(pwd)"
universe_id="123456"
output_file="$workspace_dir/universe-${universe_id}-logs-$(date -u +%Y%m%dT%H%M%SZ).json"

gcloud logging read \
  "jsonPayload.universeId=\"${universe_id}\"" \
  --freshness=7d \
  --order=desc \
  --format=json \
  > "$output_file"
```

`--freshness` works only with descending order and without timestamp filters.
The default export is therefore newest-first.

If the user provides an explicit range, use timestamp filters instead of
`--freshness`. ISO 8601 UTC timestamps avoid timezone ambiguity. Ascending
order is appropriate for a timeline export:

```bash
gcloud logging read \
  'jsonPayload.universeId="123456" AND timestamp >= "2026-08-21T00:00:00Z" AND timestamp <= "2026-08-28T23:59:59Z"' \
  --order=asc \
  --format=json \
  > "$output_file"
```

Pass an explicit project only when the user supplies one or the active project
is known to be incorrect:

```bash
--project="PROJECT_ID"
```

## Large exports and failures

Scans can have 20,000 or more log entries. Preserve the full export rather
than reducing it for readability. If the request fails, times out, or produces
an impractically large result, split the *same universe-ID query* into
non-overlapping explicit daily ranges and save one JSON file per range. State
clearly that the results are split and list every output path.

Never claim an export is complete when a command failed or when a user-chosen
`--limit` was reached. If a limit is requested, report the limit prominently.

Do not overwrite an existing export. Use the timestamped default name, or ask
before replacing a user-specified filename.

## Logs Explorer equivalent

Give the user this query for the Google Cloud Logs Explorer when useful:

```text
jsonPayload.universeId="UNIVERSE_ID"
```

For the default behavior, select **Last 7 days** in Logs Explorer. For an
explicit range, add:

```text
AND timestamp >= "START_TIME"
AND timestamp <= "END_TIME"
```

The same Logging query language is used by Logs Explorer and `gcloud logging
read`. Logical operators must be uppercase: `AND`, `OR`, and `NOT`.

## Safety boundaries

- Use read-only logging commands only.
- Do not change log buckets, sinks, views, retention, exclusions, or IAM.
- Do not delete logs.
- Do not silently broaden a universe-ID query.
- Avoid exposing secrets or full sensitive payloads in chat; store the raw
  export in the workspace and summarize it instead.
