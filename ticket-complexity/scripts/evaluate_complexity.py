#!/usr/bin/env python3
"""Evaluate suggested complexity and impact points for a ticket description or title."""

import argparse
import re

COMPLEXITY_RULES = [
    # Complexity 0
    (0, r"(translate email|translation to|typo in|remove deprecated field|dead code cleanup)", "Trivial maintenance or translation"),
    # Complexity 1
    (1, r"(^ping |^send invoice |pay reimbursements|bill payments|share a poc|add argument in|questionnaire)", "Micro-task / single config / ping (< 1h)"),
    # Complexity 2
    (2, r"(^traceback|gcp error|apicallerror|jsondecodeerror|errors\.agentrunerror|disable gcp logging|investigate google vertex|answer [a-z0-9]+|send offer to)", "Standard bug fix / single GCP error group / standard proposal (1-3h)"),
    # Complexity 3
    (3, r"(fastmcp tools|mcp tools|soc2|memory corruption executor|multi-asset context|implement tags|enrich ticket|tree sitter parser)", "Multi-component feature / parser / agentic toolset (0.5-1 day)"),
    # Complexity 5
    (5, r"(refactor scan|migrate header|linear integration|vertex ai for glm|bypass real device|add typing to re)", "Subsystem refactor / new integration / foundation model (2-4 days)"),
    # Complexity 8
    (8, r"(brand new agent|core db rewrite|autonomous pentest engine)", "Epic / new product line / major architecture rewrite (1-2 weeks)"),
]

def evaluate(title: str, description: str = "") -> tuple[int, int, str]:
    text = f"{title} {description}".lower()
    for comp, pattern, rationale in reversed(COMPLEXITY_RULES):
        if re.search(pattern, text):
            return comp, comp ** 2, rationale
    # Default to standard bug / feature (complexity 2)
    return 2, 4, "Standard engineering or triage task (Default: Complexity 2, 4 Impact Points)"

def main():
    parser = argparse.ArgumentParser(description="Evaluate ticket complexity")
    parser.add_argument("title", help="Ticket title")
    parser.add_argument("--description", "-d", default="", help="Ticket description")
    args = parser.parse_args()

    comp, points, rationale = evaluate(args.title, args.description)
    print(f"Title: {args.title}")
    print(f"Estimated Complexity: {comp}")
    print(f"Impact Points: {points} (Complexity^2 = {comp}^2)")
    print(f"Rationale: {rationale}")

if __name__ == "__main__":
    main()
