#!/usr/bin/env python3
"""Convert Google Cloud Logging JSON exports to readable plain-text logs."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


OPENROUTER_SUCCESS_MARKER = (
    'HTTP Request: POST https://openrouter.ai/api/v1/chat/completions '
    '"HTTP/1.1 200 OK"'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a GCP JSON array or JSONL export to a readable log."
    )
    parser.add_argument("input", type=Path, help="Input .json, .jsonl, or .ndjson file")
    parser.add_argument("-o", "--output", type=Path, help="Output log path")
    parser.add_argument(
        "--service-prefix",
        action="store_true",
        help="Prefix lines with the GCP service_name label",
    )
    parser.add_argument(
        "--include-date",
        action="store_true",
        help="Render YYYY-MM-DD HH:MM:SS instead of HH:MM:SS",
    )
    parser.add_argument(
        "--keep-openrouter-success",
        action="store_true",
        help="Keep successful OpenRouter chat-completion HTTP diagnostics",
    )
    return parser.parse_args()


def load_entries(path: Path) -> tuple[list[dict[str, Any]], int]:
    text = path.read_text(encoding="utf-8-sig")
    malformed = 0

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        entries: list[dict[str, Any]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                malformed += 1
                print(
                    f"warning: skipped malformed JSONL line {line_number}: {exc}",
                    file=sys.stderr,
                )
                continue
            if isinstance(value, dict):
                entries.append(value)
            else:
                malformed += 1
        return entries, malformed

    if isinstance(parsed, list):
        entries = [entry for entry in parsed if isinstance(entry, dict)]
        malformed = len(parsed) - len(entries)
        return entries, malformed
    if isinstance(parsed, dict):
        return [parsed], 0

    raise ValueError("Input JSON must contain an object, an array of objects, or JSONL")


def timestamp_text(value: Any, include_date: bool) -> str:
    if not isinstance(value, str) or not value:
        return "NO_TIMESTAMP"

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M:%S" if include_date else "%H:%M:%S")
    except ValueError:
        if "T" in value:
            date, time = value.split("T", 1)
            clock = time[:8]
            return f"{date} {clock}" if include_date else clock
        return value


def payload_text(entry: dict[str, Any]) -> str:
    text_payload = entry.get("textPayload")
    if isinstance(text_payload, str):
        return text_payload

    for key in ("jsonPayload", "protoPayload"):
        payload = entry.get(key)
        if payload is not None:
            return json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return ""


def source_text(entry: dict[str, Any]) -> str:
    source = entry.get("sourceLocation")
    if not isinstance(source, dict):
        return ""

    file_value = source.get("file")
    line_value = source.get("line")
    if not file_value:
        return ""

    filename = Path(str(file_value)).name
    return f"{filename}:{line_value}" if line_value else filename


def service_name(entry: dict[str, Any]) -> str:
    labels = entry.get("labels")
    if isinstance(labels, dict) and labels.get("service_name"):
        return str(labels["service_name"])

    resource = entry.get("resource")
    if isinstance(resource, dict):
        resource_labels = resource.get("labels")
        if isinstance(resource_labels, dict):
            for key in ("service_name", "service", "container_name"):
                if resource_labels.get(key):
                    return str(resource_labels[key])
    return "gcp"


def is_noisy_openrouter_success(entry: dict[str, Any]) -> bool:
    return OPENROUTER_SUCCESS_MARKER in payload_text(entry)


def render_entry(
    entry: dict[str, Any], include_date: bool, include_service: bool
) -> list[str]:
    timestamp = timestamp_text(entry.get("timestamp"), include_date)
    severity = str(entry.get("severity") or "INFO").upper()
    message_lines = payload_text(entry).splitlines() or [""]
    source = source_text(entry)
    prefix = f"{service_name(entry)}: " if include_service else ""

    first = f"{prefix}[{timestamp}] {severity:<8} {message_lines[0]}"
    if source:
        first += f"    {source}"

    continuation_width = len(prefix) + len(timestamp) + 12
    continuation = " " * continuation_width
    return [first, *(continuation + line for line in message_lines[1:])]


def main() -> int:
    args = parse_args()
    output = args.output or args.input.with_name(f"{args.input.stem}_readable.log")

    try:
        entries, malformed = load_entries(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    entries.sort(key=lambda entry: str(entry.get("timestamp") or ""))
    lines: list[str] = []
    omitted = 0
    for entry in entries:
        if not args.keep_openrouter_success and is_noisy_openrouter_success(entry):
            omitted += 1
            continue
        lines.extend(render_entry(entry, args.include_date, args.service_prefix))

    output.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"Wrote {len(entries) - omitted} entries to {output}")
    if omitted:
        print(f"Omitted {omitted} noisy OpenRouter 200 OK entries")
    if malformed:
        print(f"Skipped {malformed} malformed or non-object entries", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
