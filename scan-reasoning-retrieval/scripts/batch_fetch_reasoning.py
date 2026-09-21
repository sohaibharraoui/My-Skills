#!/usr/bin/env python3
"""Batch fetch agentic deep scan reasoning JSONs for all scans in a CSV."""

import argparse
import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

def create_session(session_id: str) -> requests.Session:
    session = requests.Session()
    session.cookies.set("sessionid", session_id, domain="api.ostorlab.co")
    csrf_resp = session.get(PUBLIC_GRAPHQL_ENDPOINT, timeout=30)
    csrf_token = session.cookies.get("csrftoken") or csrf_resp.cookies.get_dict().get("csrftoken")
    session.headers.update({
        "Content-Type": "application/json",
        "Referer": "https://report.ostorlab.co/",
        "Origin": "https://report.ostorlab.co",
        "X-CSRFToken": csrf_token or "",
    })
    return session

def fetch_one(scan_id: int, out_dir: str, session: requests.Session, org: str = "hqp") -> dict:
    out_file = os.path.join(out_dir, f"scan_{scan_id}.json")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
        return {"scan_id": scan_id, "status": "cached", "path": out_file}
    
    url = f"{GRAPHQL_ENDPOINT}?org={org}"
    payload = {"query": QUERY_FULL_SCAN_REASONING, "variables": {"scanId": scan_id}}
    
    for attempt in range(3):
        try:
            resp = session.post(url, json=payload, timeout=90)
            if resp.status_code == 200:
                body = resp.json()
                if "errors" in body and body["errors"]:
                    return {"scan_id": scan_id, "status": "error", "error": body["errors"]}
                data = body.get("data", {})
                agentic_scan = data.get("agenticDeepScan")
                if not agentic_scan:
                    return {"scan_id": scan_id, "status": "not_found"}
                
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(agentic_scan, f)
                return {"scan_id": scan_id, "status": "ok", "path": out_file}
            elif resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
            else:
                time.sleep(1)
        except Exception as e:
            if attempt == 2:
                return {"scan_id": scan_id, "status": "exception", "error": str(e)}
            time.sleep(2)
    return {"scan_id": scan_id, "status": "failed"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to input CSV with latest_scan_id")
    parser.add_argument("--output-dir", required=True, help="Directory to save scan JSONs")
    parser.add_argument("--session-id", default=DEFAULT_SESSION_ID)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    with open(args.csv) as f:
        rows = list(csv.DictReader(f))

    scan_ids = []
    for r in rows:
        sid = r.get("latest_scan_id")
        if sid:
            scan_ids.append(int(sid))
    
    scan_ids = sorted(list(set(scan_ids)))
    print(f"Total unique scan IDs to fetch: {len(scan_ids)}")

    session = create_session(args.session_id)
    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_sid = {executor.submit(fetch_one, sid, args.output_dir, session): sid for sid in scan_ids}
        for future in as_completed(future_to_sid):
            res = future.result()
            results[res["scan_id"]] = res
            status = res.get("status")
            print(f"Scan {res['scan_id']}: {status}", flush=True)

    success_count = sum(1 for r in results.values() if r.get("status") in ("ok", "cached"))
    print(f"\nCompleted: {success_count}/{len(scan_ids)} scans downloaded to {args.output_dir}")

if __name__ == "__main__":
    main()
