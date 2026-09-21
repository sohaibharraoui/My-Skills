#!/usr/bin/env python3
"""Forensic audit parser for agent reasoning JSON files.

Extracts all executed commands, tool calls, and outputs to facilitate
rigorous semantic anti-cheat audits without regex false positives.
"""

import json
import os
import sys

def audit_scan_file(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scan_id = data.get("scan_id") or data.get("id")
    risks = data.get("risks", [])

    all_tool_calls = []
    bash_commands = []
    git_commands = []
    network_calls = []
    server_poc_queries = []

    for r in risks:
        analysis = r.get("analysis") or {}
        tasks = analysis.get("tasks") or []
        for t in tasks:
            tool_calls = t.get("toolCalls") or []
            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("args") or {}
                output = tc.get("output") or ""
                all_tool_calls.append({"tool": name, "args": args, "output": output})

                # Check bash command
                cmd = ""
                if isinstance(args, dict):
                    cmd = args.get("command") or args.get("cmd") or ""
                elif isinstance(args, str):
                    cmd = args

                if cmd:
                    bash_commands.append({"cmd": cmd, "output": output[:300]})
                    
                    # Semantically check git
                    if "git " in cmd or cmd.startswith("git"):
                        git_commands.append({"cmd": cmd, "output": output[:300]})
                    
                    # Semantically check network egress
                    if any(net_tool in cmd for net_tool in ["curl", "wget", "nc ", "python3 -c", "import requests"]):
                        if any(domain in cmd for domain in ["github.com", "gitlab.com", "http://", "https://"]):
                            network_calls.append({"cmd": cmd, "output": output[:300]})

                    # Semantically check server poc
                    if any(p in cmd for p in ["server-poc", "query-poc", "server_poc"]):
                        server_poc_queries.append({"cmd": cmd, "output": output[:300]})

    return {
        "scan_id": scan_id,
        "total_risks": len(risks),
        "total_tool_calls": len(all_tool_calls),
        "total_bash_commands": len(bash_commands),
        "git_commands": git_commands,
        "network_calls": network_calls,
        "server_poc_queries": server_poc_queries
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        res = audit_scan_file(sys.argv[1])
        print(json.dumps(res, indent=2))
