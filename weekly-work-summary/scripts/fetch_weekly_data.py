#!/usr/bin/env python3
"""
Reusable script to fetch, aggregate, and analyze weekly engineering activity
across GitHub PRs and Ostorlab FastMCP tickets.
"""

import argparse
import datetime
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def run_cmd(cmd: list[str]) -> str:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Command error: {' '.join(cmd)}\n{res.stderr}", file=sys.stderr)
        return ""
    return res.stdout


def fetch_github_prs_by_day(org: str, start_date: str, end_date: str) -> list[dict]:
    """
    Fetch PRs day-by-day using gh CLI to bypass the 200-result query limit.
    """
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    delta = datetime.timedelta(days=1)

    all_prs = {}
    current = start

    while current <= end:
        date_str = current.isoformat()
        print(f"Fetching PRs for {date_str}...", file=sys.stderr)
        cmd = [
            "gh", "search", "prs",
            f"owner:{org}",
            f"created:{date_str}",
            "--limit", "1000",
            "--json", "number,title,state,url,createdAt,closedAt,repository,author,labels"
        ]
        out = run_cmd(cmd)
        if out:
            try:
                prs = json.loads(out)
                for pr in prs:
                    pr_id = f"{pr.get('repository', {}).get('name')}-{pr.get('number')}"
                    all_prs[pr_id] = pr
            except json.JSONDecodeError as e:
                print(f"JSON error on {date_str}: {e}", file=sys.stderr)
        current += delta

    return list(all_prs.values())


def parse_mcp_stream_output(content: str) -> list[dict]:
    decoder = json.JSONDecoder()
    items = []
    pos = 0
    while pos < len(content):
        while pos < len(content) and content[pos].isspace():
            pos += 1
        if pos >= len(content):
            break
        try:
            obj, end_pos = decoder.raw_decode(content, pos)
            if isinstance(obj, list):
                items.extend(obj)
            elif isinstance(obj, dict):
                if "tickets" in obj:
                    items.extend(obj["tickets"])
                elif "ticket_streams" in obj:
                    items.extend(obj["ticket_streams"])
                else:
                    items.append(obj)
            pos = end_pos
        except Exception:
            break
    return items


def main():
    parser = argparse.ArgumentParser(description="Fetch and aggregate weekly engineering data.")
    parser.add_argument("--org", default="Ostorlab", help="GitHub Organization name")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default="./output", help="Directory to save aggregated data")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Sourcing GitHub PRs for {args.org} ({args.start_date} to {args.end_date}) ===")
    prs = fetch_github_prs_by_day(args.org, args.start_date, args.end_date)
    print(f"Total PRs fetched: {len(prs)}")

    prs_file = out_dir / "prs_dataset.json"
    with open(prs_file, "w") as f:
        json.dump(prs, f, indent=2)
    print(f"Saved PRs to {prs_file}")

    # Compute PR stats
    states = Counter(p.get("state", "UNKNOWN").upper() for p in prs)
    repos = Counter(
        p.get("repository", {}).get("name") if isinstance(p.get("repository"), dict) else str(p.get("repository"))
        for p in prs
    )
    authors = Counter(
        p.get("author", {}).get("login") if isinstance(p.get("author"), dict) else str(p.get("author"))
        for p in prs
    )

    summary = {
        "timeframe": {"start": args.start_date, "end": args.end_date},
        "total_prs": len(prs),
        "states": dict(states),
        "top_repositories": dict(repos.most_common(20)),
        "top_authors": dict(authors.most_common(15))
    }

    summary_file = out_dir / "weekly_metrics.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved metrics summary to {summary_file}")
    print("\nSummary Metrics:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
