#!/usr/bin/env python3
"""Programmatic Agentic Deep Scan reasoning retriever for Ostorlab scans.

Fetches complete multi-risk reasoning (detection + validation risks),
including prompts, plans, tasks, and full tool calls (arguments and outputs).
"""

import argparse
import json
import os
import sys
from typing import Any
import requests

DEFAULT_SESSION_ID = "h0ab9jo75vpygzs926xyyja9rgrlthct"
BASE_URL = "https://api.ostorlab.co"
GRAPHQL_ENDPOINT = f"{BASE_URL}/apis/graphql"
PUBLIC_GRAPHQL_ENDPOINT = f"{BASE_URL}/apis/public_graphql"

QUERY_FULL_SCAN_REASONING = """
query AgenticDeepScan($scanId: Int!) {
  agenticDeepScan(scanId: $scanId) {
    id
    risks {
      id
      description
      riskRating
      prompt
      plan
      analysis {
        id
        tasks {
          id
          description
          result
          createdAt
          toolCalls {
            id
            name
            args
            output
            createdAt
          }
        }
      }
    }
  }
}
"""


def create_authenticated_session(session_id: str, org: str = "hqp") -> requests.Session:
    """Create an authenticated requests session with CSRF cookie handshake."""
    session = requests.Session()
    session.cookies.set("sessionid", session_id, domain="api.ostorlab.co")

    # Perform handshake to acquire csrftoken
    csrf_resp = session.get(PUBLIC_GRAPHQL_ENDPOINT, timeout=30)
    csrf_token = session.cookies.get("csrftoken")

    if not csrf_token:
        cookies_dict = csrf_resp.cookies.get_dict()
        csrf_token = cookies_dict.get("csrftoken")

    session.headers.update({
        "Content-Type": "application/json",
        "Referer": "https://report.ostorlab.co/",
        "Origin": "https://report.ostorlab.co",
        "X-CSRFToken": csrf_token or "",
    })
    return session


def fetch_scan_reasoning(session: requests.Session, scan_id: int, org: str = "hqp") -> dict[str, Any]:
    """Fetch full reasoning for all risks associated with a given scan ID."""
    url = f"{GRAPHQL_ENDPOINT}?org={org}"
    payload = {
        "query": QUERY_FULL_SCAN_REASONING,
        "variables": {"scanId": scan_id},
    }
    resp = session.post(url, json=payload, timeout=90)
    resp.raise_for_status()
    body = resp.json()

    if "errors" in body and body["errors"]:
        raise RuntimeError(f"GraphQL error for scan {scan_id}: {body['errors']}")

    data = body.get("data", {})
    agentic_scan = data.get("agenticDeepScan")
    if not agentic_scan:
        raise ValueError(f"No agenticDeepScan found for scan {scan_id}")

    all_risks = agentic_scan.get("risks", [])

    # Filter substantive risks with execution history
    substantive_risks = []
    for risk in all_risks:
        tasks = []
        if risk.get("analysis") and risk["analysis"].get("tasks"):
            tasks = risk["analysis"]["tasks"]
        has_plan = bool(risk.get("plan"))
        if tasks or has_plan:
            substantive_risks.append(risk)

    return {
        "scan_id": scan_id,
        "agentic_deep_scan_id": agentic_scan.get("id"),
        "total_risks_count": len(all_risks),
        "substantive_risks_count": len(substantive_risks),
        "risks": substantive_risks if substantive_risks else all_risks,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch full scan reasoning from Ostorlab GraphQL.")
    parser.add_argument("--scan-id", type=int, required=True, help="Scan ID to fetch reasoning for.")
    parser.add_argument("--output", type=str, required=True, help="Path to write output JSON.")
    parser.add_argument("--session-id", type=str, default=os.getenv("OSTORLAB_SESSION_ID", DEFAULT_SESSION_ID), help="Django sessionid cookie.")
    parser.add_argument("--org", type=str, default="hqp", help="Organisation slug.")

    args = parser.parse_args()

    session = create_authenticated_session(args.session_id, org=args.org)
    print(f"Fetching reasoning for scan {args.scan_id} (org: {args.org})...", flush=True)

    result = fetch_scan_reasoning(session, args.scan_id, org=args.org)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    total_tasks = sum(len(r.get("analysis", {}).get("tasks", [])) for r in result["risks"])
    total_tools = sum(
        sum(len(t.get("toolCalls", [])) for t in r.get("analysis", {}).get("tasks", []))
        for r in result["risks"]
    )
    print(f"Successfully retrieved scan {args.scan_id}: {len(result['risks'])} risks, {total_tasks} tasks, {total_tools} tool calls -> {args.output}")


if __name__ == "__main__":
    main()
