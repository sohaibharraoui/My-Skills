#!/usr/bin/env python3
"""GCP Log Inspector CLI

Quickly summarize, filter, inspect, and extract entries from exported GCP JSON log files
without blowing up context budgets.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from typing import Any


def parse_entry_message(entry: dict[str, Any]) -> str:
    """Extract human-readable log message from an entry."""
    if "textPayload" in entry:
        return entry["textPayload"]
    if "jsonPayload" in entry:
        jp = entry["jsonPayload"]
        if isinstance(jp, dict):
            for key in ("message", "msg", "log", "error", "event"):
                if key in jp and isinstance(jp[key], str):
                    return jp[key]
            return json.dumps(jp)
        return str(jp)
    if "protoPayload" in entry:
        pp = entry["protoPayload"]
        if isinstance(pp, dict) and "status" in pp:
            return f"ProtoPayload status: {pp['status']}"
        return str(pp)
    return ""


def summarize_logs(entries: list[dict[str, Any]], file_path: str) -> None:
    """Print an executive summary of the log file."""
    total = len(entries)
    if total == 0:
        print(f"Log file '{file_path}' contains 0 entries.")
        return

    severities = collections.Counter()
    agents = collections.Counter()
    first_time = entries[0].get("timestamp", "unknown")
    last_time = entries[-1].get("timestamp", "unknown")

    error_samples: list[tuple[int, str, str, str]] = []

    for idx, entry in enumerate(entries):
        sev = entry.get("severity", "DEFAULT").upper()
        severities[sev] += 1

        labels = entry.get("labels", {})
        agent = labels.get("agent_key") or entry.get("resource", {}).get("labels", {}).get("pod_name") or "unknown"
        agents[agent] += 1

        if sev in ("ERROR", "CRITICAL", "EMERGENCY", "ALERT") and len(error_samples) < 5:
            msg = parse_entry_message(entry).strip().replace("\n", " ")[:120]
            error_samples.append((idx, entry.get("timestamp", ""), agent, msg))

    print(f"📊 Summary for: {file_path}")
    print(f"  • Total Entries: {total}")
    print(f"  • Time Range:    {first_time} -> {last_time}")
    print("\n  • Severities:")
    for sev, count in severities.most_common():
        print(f"    - {sev:<10}: {count} ({count/total*100:.1f}%)")

    print("\n  • Top Agents / Components:")
    for agent, count in agents.most_common(8):
        print(f"    - {agent:<40}: {count}")

    if error_samples:
        print(f"\n  • Sample Errors ({len(error_samples)} shown):")
        for idx, ts, agent, msg in error_samples:
            print(f"    [{idx}] {ts} [{agent}] {msg}")


def filter_entries(
    entries: list[dict[str, Any]],
    severity: str | None = None,
    agent: str | None = None,
    grep: str | None = None,
    limit: int = 50,
    tail: bool = False,
) -> None:
    """Filter and print matching entries."""
    matched: list[tuple[int, dict[str, Any]]] = []

    for idx, entry in enumerate(entries):
        if severity and entry.get("severity", "DEFAULT").upper() != severity.upper():
            continue

        labels = entry.get("labels", {})
        entry_agent = labels.get("agent_key") or entry.get("resource", {}).get("labels", {}).get("pod_name") or ""
        if agent and agent.lower() not in entry_agent.lower():
            continue

        msg = parse_entry_message(entry)
        if grep and grep.lower() not in msg.lower():
            continue

        matched.append((idx, entry))

    print(f"Found {len(matched)} matching entries.")

    display_subset = matched[-limit:] if tail else matched[:limit]
    for idx, entry in display_subset:
        ts = entry.get("timestamp", "")
        sev = entry.get("severity", "DEFAULT")
        labels = entry.get("labels", {})
        ag = labels.get("agent_key") or entry.get("resource", {}).get("labels", {}).get("pod_name") or ""
        msg = parse_entry_message(entry).strip()
        print(f"\n--- Entry #{idx} | {ts} | {sev} | {ag} ---")
        print(msg)


def show_single_entry(entries: list[dict[str, Any]], index: int) -> None:
    """Show the full JSON representation of a single entry."""
    if 0 <= index < len(entries):
        print(json.dumps(entries[index], indent=2))
    else:
        print(f"Error: Index {index} out of range (0..{len(entries)-1})", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect exported GCP JSON logs")
    parser.add_argument("file", help="Path to exported JSON log file")
    parser.add_argument("--summary", action="store_true", help="Print summary statistics")
    parser.add_argument("--severity", help="Filter by severity (e.g. ERROR, WARNING, INFO)")
    parser.add_argument("--agent", help="Filter by agent_key or pod name substring")
    parser.add_argument("--grep", help="Search substring inside log messages")
    parser.add_argument("--entry", type=int, help="Show full JSON for a specific entry index")
    parser.add_argument("--limit", type=int, default=50, help="Max entries to display (default: 50)")
    parser.add_argument("--tail", action="store_true", help="Display latest matching entries instead of first")

    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except Exception as e:
        print(f"Error loading {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(entries, list):
        print(f"Error: Expected JSON list of entries, got {type(entries).__name__}", file=sys.stderr)
        sys.exit(1)

    if args.entry is not None:
        show_single_entry(entries, args.entry)
    elif args.summary or (not args.severity and not args.agent and not args.grep):
        summarize_logs(entries, args.file)
    else:
        filter_entries(
            entries,
            severity=args.severity,
            agent=args.agent,
            grep=args.grep,
            limit=args.limit,
            tail=args.tail,
        )


if __name__ == "__main__":
    main()
