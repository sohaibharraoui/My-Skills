---
name: gcp-json-log-converter
description: Convert Google Cloud Logging JSON exports into readable chronological plain-text logs. Use when a user provides a GCP log export as a JSON array or JSONL/NDJSON file and asks to make it human-readable, console-like, easier to inspect, or similar to normal application logs.
---

# GCP JSON Log Converter

Convert GCP JSON log exports with the bundled deterministic script.

## Workflow

1. Identify the input `.json`, `.jsonl`, or `.ndjson` file.
2. Choose an output path. Default to `<input_stem>_readable.log` beside the input.
3. Run:

```bash
python3 ~/.codex/skills/gcp-json-log-converter/scripts/convert_gcp_logs.py INPUT
```

4. Inspect the beginning, one multiline entry, and the end of the output.
5. Report the output path and any malformed entries that were skipped.

## Output Format

The default format is:

```text
[03:03:56] INFO     Created risk with ID: 23242    storage.py:577
[03:03:57] WARNING  Multiline message starts here    worker.py:91
                    continuation line
```

The script:

- Accepts a JSON array or JSONL/NDJSON.
- Sorts entries by `timestamp`.
- Reads `textPayload`, `jsonPayload`, or `protoPayload`.
- Preserves multiline messages.
- Includes severity and `sourceLocation`.
- Omits the GCP service prefix by default.
- Omits successful OpenRouter chat-completion HTTP diagnostics by default.
- Never invents missing tool output or payload content.

## Options

```bash
# Set an explicit output path
python3 ~/.codex/skills/gcp-json-log-converter/scripts/convert_gcp_logs.py INPUT -o OUTPUT

# Add a service prefix similar to Docker/agent console streams
python3 ~/.codex/skills/gcp-json-log-converter/scripts/convert_gcp_logs.py INPUT --service-prefix

# Include the calendar date as well as the time
python3 ~/.codex/skills/gcp-json-log-converter/scripts/convert_gcp_logs.py INPUT --include-date

# Keep successful OpenRouter chat-completion HTTP diagnostics
python3 ~/.codex/skills/gcp-json-log-converter/scripts/convert_gcp_logs.py INPUT --keep-openrouter-success
```

Use `--service-prefix` only when the user explicitly wants lines such as
`service_name: [time] severity message`.

## Validation

After conversion, verify:

```bash
wc -l -c OUTPUT
sed -n '1,20p' OUTPUT
tail -20 OUTPUT
```

Also search for a known event from the input to confirm it survived conversion.
