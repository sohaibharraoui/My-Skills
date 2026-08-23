#!/usr/bin/env python3
"""Read-only heuristic scanner for installed agent skills."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
from pathlib import Path
from typing import Iterable

MAX_FILE_BYTES = 1_000_000
TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".html", ".css"}

RULES = [
    ("HIGH", "Network-to-shell", re.compile(r"(?:curl|wget)[^\n|]{0,300}\|\s*(?:ba)?sh\b", re.I)),
    ("HIGH", "Decode-and-execute", re.compile(r"(?:base64|hex)[^\n]*(?:decode|b64decode)[^\n]*(?:exec|system|spawn|eval)", re.I)),
    ("HIGH", "Credential-store access", re.compile(r"(?:~/|/home/[^\s/'\"]+/)(?:\.ssh|\.aws|\.config/gcloud)|(?:keychain|credential[_ -]?(?:store|helper))", re.I)),
    ("MEDIUM", "Prompt-injection phrase", re.compile(r"ignore\s+(?:all\s+|any\s+|the\s+)?(?:previous|prior|above)\s+instructions|do\s+not\s+(?:tell|show)\s+the\s+user", re.I)),
    ("MEDIUM", "Hidden instruction marker", re.compile(r"<!--[^>]*(?:ignore|do not|must|never|run|execute)[^>]*-->", re.I)),
    ("MEDIUM", "Suspicious upload", re.compile(r"(?:requests\.(?:post|put)|fetch\s*\(|curl\s+)[^\n]{0,300}(?:upload|files?|data|POST|PUT)", re.I)),
    ("MEDIUM", "Plain HTTP endpoint", re.compile(r"http://(?!localhost\b|127\.0\.0\.1\b)[^\s'\"`]+", re.I)),
]

HIDDEN_UNICODE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")
BASE64_TOKEN = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{240,}={0,2}(?![A-Za-z0-9+/])")


def default_roots() -> list[Path]:
    roots: list[Path] = []
    configured = os.environ.get("AGENT_SKILLS_DIRS")
    if configured:
        roots.extend(Path(raw).expanduser() for raw in configured.split(os.pathsep) if raw)
    for raw in (os.environ.get("CODEX_HOME"), os.environ.get("AGENTS_HOME"), os.environ.get("ANTIGRAVITY_HOME"), os.environ.get("CLAUDE_HOME")):
        if raw:
            roots.append(Path(raw).expanduser() / "skills")
    home = Path.home()
    roots.extend([home / ".codex" / "skills", home / ".agents" / "skills", home / ".claude" / "skills"])
    project = Path.cwd()
    roots.extend([project / ".codex" / "skills", project / ".agents" / "skills", project / ".claude" / "skills"])
    unique: list[Path] = []
    for root in roots:
        root = root.resolve()
        if root.exists() and root not in unique:
            unique.append(root)
    return unique


def skill_dirs(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        path = path.resolve()
        if (path / "SKILL.md").is_file():
            result.append(path)
            continue
        if path.is_dir():
            result.extend(child for child in path.iterdir() if child.is_dir() and (child / "SKILL.md").is_file())
    return sorted(set(result))


def evidence(line: str) -> str:
    return " ".join(line.strip().split())[:240]


def scan_file(path: Path) -> list[dict]:
    try:
        if path.stat().st_size > MAX_FILE_BYTES or path.suffix.lower() not in TEXT_SUFFIXES:
            return []
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    findings: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        for severity, title, pattern in RULES:
            if pattern.search(line):
                findings.append({"severity": severity, "title": title, "file": str(path), "line": number, "evidence": evidence(line)})
        if HIDDEN_UNICODE.search(line):
            findings.append({"severity": "HIGH", "title": "Hidden Unicode instruction marker", "file": str(path), "line": number, "evidence": "Line contains zero-width or bidirectional Unicode."})
        for token in BASE64_TOKEN.findall(line):
            try:
                base64.b64decode(token, validate=True)
            except Exception:
                continue
            findings.append({"severity": "MEDIUM", "title": "Large decodable Base64 payload", "file": str(path), "line": number, "evidence": f"Decodable payload of {len(token)} characters."})
    return findings


def scan_skill(skill: Path) -> dict:
    if (skill / "scripts" / "security_scan.py").resolve() == Path(__file__).resolve():
        return {"skill": skill.name, "path": str(skill), "verdict": "PASS", "findings": [], "self_scan_excluded": True}
    findings: list[dict] = []
    for path in skill.rglob("*"):
        if path.is_file():
            findings.extend(scan_file(path))
    highest = "PASS"
    if any(f["severity"] == "HIGH" for f in findings):
        highest = "RISK"
    elif findings:
        highest = "REVIEW"
    return {"skill": skill.name, "path": str(skill), "verdict": highest, "findings": findings, "self_scan_excluded": False}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only heuristic scan of agent skills")
    parser.add_argument("--path", action="append", help="Skill directory or skills root; repeatable")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit structured JSON")
    args = parser.parse_args()

    paths = [Path(p).expanduser() for p in args.path] if args.path else default_roots()
    skills = skill_dirs(paths)
    reports = [scan_skill(skill) for skill in skills]
    summary = {
        "scanned": len(reports),
        "risk": sum(r["verdict"] == "RISK" for r in reports),
        "review": sum(r["verdict"] == "REVIEW" for r in reports),
        "pass": sum(r["verdict"] == "PASS" for r in reports),
    }
    output = {"summary": summary, "skills": reports}
    if args.as_json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0
    print(f"Scanned: {summary['scanned']} | RISK: {summary['risk']} | REVIEW: {summary['review']} | PASS: {summary['pass']}")
    for report in reports:
        if report["verdict"] == "PASS":
            continue
        print(f"\n[{report['verdict']}] {report['skill']}")
        for finding in report["findings"]:
            print(f"- {finding['severity']} {finding['title']} — {finding['file']}:{finding['line']}")
            print(f"  {finding['evidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
