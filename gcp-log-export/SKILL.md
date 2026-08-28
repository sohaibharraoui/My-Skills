---
name: gcp-log-export
description: Export Google Cloud Logging entries selected in Logs Explorer to a local JSON file with gcloud. Use when asked to pull, download, save, or retrieve GCP logs, to translate a Logs Explorer query to gcloud, or to export the complete matching result set rather than an arbitrary 1,000-entry sample.
---

# GCP Log Export

Use `scripts/export_logs.sh` for exports. Require a project, a Cloud Logging query, and an output path. Preserve the Logs Explorer filter exactly, including any timestamp predicates.

```bash
bash scripts/export_logs.sh \
  --project PROJECT_ID \
  --filter 'resource.type="cloud_run_revision" AND severity>=ERROR' \
  --freshness 30d \
  --output /absolute/path/logs.json
```

## Retrieval rules

- Authenticate first with `gcloud auth login` (or an approved service account) and verify access with `gcloud projects describe PROJECT_ID`.
- Copy the query from Logs Explorer's **Show query** view. Do not invent a weaker resource filter.
- Always set a time range: retain timestamp predicates from the Explorer query, or pass `--freshness`. Never rely on gcloud's default 1-day freshness window.
- Default to no `--limit`. For `gcloud logging read`, no limit means the CLI requests the complete matching set; `--limit=1000` is a cap, not a maximum required value.
- Add `--limit N` only when the requester explicitly wants a capped sample. State that it may omit older matching entries.
- Use `--format=json` and save the full result to the requested file. Do not paste potentially sensitive log content into chat.
- Confirm the output exists, is valid JSON, and report its path and entry count. Warn when the query can contain credentials, tokens, PII, or production payloads.

## Common filters

```text
# Cloud Run errors for a service
resource.type="cloud_run_revision"
AND resource.labels.service_name="SERVICE"
AND severity>=ERROR

# A specific log name (URL-encode slashes as %2F)
logName="projects/PROJECT_ID/logs/run.googleapis.com%2Fstdout"

# Search structured or text payloads
jsonPayload.message:"exception" OR textPayload:"exception"
```

For a log bucket/view other than the default scope, add the matching `--bucket`, `--location`, and `--view` options directly to the gcloud command after confirming the view permissions.
