#!/usr/bin/env python3
"""Scheduled PR review automation: candidate locator, deduplicator, and diff fetcher.

Identifies open pull requests requiring review across a GitHub organization or specific
repositories, deduplicating against previously reviewed commit SHAs using a local state cache.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence, TypedDict

logger = logging.getLogger("scheduled_pr_review")

DEFAULT_ORG = "Ostorlab"
DEFAULT_CACHE_PATH = "~/.gemini/antigravity/pr_review_cache.json"
DEFAULT_LIMIT = 10
DEFAULT_IGNORE_AUTHORS = [
    "dependabot",
    "dependabot[bot]",
    "renovate",
    "renovate[bot]",
    "app/dependabot",
    "app/renovate",
]


class PRCacheEntry(TypedDict):
    head_sha: str
    last_reviewed_at: str
    title: str
    author: str


@dataclass(frozen=True)
class PullRequest:
    owner: str
    repo: str
    number: int
    title: str
    author: str
    is_draft: bool
    url: str
    head_sha: str

    @property
    def key(self) -> str:
        return f"{self.owner}/{self.repo}#{self.number}"

    @property
    def repo_slug(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass(frozen=True)
class CandidatePR:
    pr: PullRequest
    reason: str
    previous_sha: Optional[str] = None


def _run_gh(args: Sequence[str]) -> str:
    """Execute a GitHub CLI command and return stdout.

    Raises:
        RuntimeError: If 'gh' is not found.
        subprocess.CalledProcessError: If command fails with non-zero exit code.
    """
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI binary 'gh' not found in PATH.")

    cmd = ["gh", *args]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(
            "Command '%s' failed with exit code %d: %s",
            " ".join(cmd),
            e.returncode,
            e.stderr.strip(),
        )
        raise
    except FileNotFoundError as e:
        logger.error("GitHub CLI binary 'gh' not found: %s", e)
        raise


def fetch_pr_diff(owner: str, repo: str, number: int) -> str:
    """Fetch unified diff for a pull request using gh pr diff."""
    repo_slug = f"{owner}/{repo}"
    try:
        return _run_gh(["pr", "diff", str(number), "--repo", repo_slug])
    except subprocess.CalledProcessError:
        return ""
    except RuntimeError:
        return ""


def fetch_review_comments(owner: str, repo: str, number: int) -> List[Dict[str, Any]]:
    """Fetch existing PR review comments via GitHub REST API."""
    endpoint = f"repos/{owner}/{repo}/pulls/{number}/comments"
    try:
        raw_output = _run_gh(["api", endpoint])
        parsed = json.loads(raw_output)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        return []
    except subprocess.CalledProcessError:
        return []
    except json.JSONDecodeError:
        return []
    except RuntimeError:
        return []


def fetch_head_sha(owner: str, repo: str, number: int) -> str:
    """Fetch the latest head commit SHA for a pull request."""
    repo_slug = f"{owner}/{repo}"
    try:
        raw_output = _run_gh([
            "pr", "view", str(number),
            "--repo", repo_slug,
            "--json", "headRefOid",
            "-q", ".headRefOid",
        ])
        return raw_output.strip()
    except subprocess.CalledProcessError:
        return ""
    except RuntimeError:
        return ""


def post_pr_comment(owner: str, repo: str, number: int, body: str) -> bool:
    """Post a general comment on the pull request."""
    repo_slug = f"{owner}/{repo}"
    try:
        _run_gh(["pr", "comment", str(number), "--repo", repo_slug, "--body", body])
        return True
    except subprocess.CalledProcessError:
        return False
    except RuntimeError:
        return False


def post_pr_review(
    owner: str,
    repo: str,
    number: int,
    body: str,
    event: str = "COMMENT",
) -> bool:
    """Submit a GitHub Pull Request review with findings.

    Args:
        owner: Repository owner.
        repo: Repository name.
        number: Pull request number.
        body: Review body markdown content.
        event: Review decision ('COMMENT', 'APPROVE', 'REQUEST_CHANGES').
    """
    repo_slug = f"{owner}/{repo}"
    event_upper = event.upper()
    flag = "--comment"
    if event_upper == "APPROVE":
        flag = "--approve"
    elif event_upper in ("REQUEST_CHANGES", "REQUEST-CHANGES"):
        flag = "--request-changes"

    try:
        _run_gh(["pr", "review", str(number), "--repo", repo_slug, flag, "--body", body])
        return True
    except (subprocess.CalledProcessError, RuntimeError) as e:
        logger.error("Failed to post PR review to %s#%d: %s", repo_slug, number, e)
        return False


def parse_pr_key(key: str, default_org: str = DEFAULT_ORG) -> tuple[str, str, int]:
    """Parse a PR key (e.g. 'Ostorlab/repo#123' or 'repo#123') into owner, repo, number."""
    if "#" not in key:
        raise ValueError(f"Invalid PR key '{key}'. Expected format: 'owner/repo#number' or 'repo#number'.")
    repo_part, number_str = key.split("#", 1)
    number = int(number_str)
    if "/" in repo_part:
        owner, repo = repo_part.split("/", 1)
    else:
        owner, repo = default_org, repo_part
    return owner, repo, number


def summarize_diff(diff_text: str) -> Dict[str, int]:
    """Calculate additions, deletions, and changed files count from unified diff."""
    additions = 0
    deletions = 0
    files_changed = 0
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            files_changed += 1
        elif line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
    return {
        "files_changed": files_changed,
        "additions": additions,
        "deletions": deletions,
    }


def load_pr_cache(cache_path: str) -> Dict[str, PRCacheEntry]:
    """Load PR review cache from JSON file."""
    expanded_path = Path(os.path.expanduser(cache_path))
    if not expanded_path.is_file():
        return {}
    try:
        with expanded_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                cache: Dict[str, PRCacheEntry] = {}
                for k, v in data.items():
                    if isinstance(k, str) and isinstance(v, dict):
                        head_sha = str(v.get("head_sha") or "")
                        last_reviewed_at = str(v.get("last_reviewed_at") or "")
                        title = str(v.get("title") or "")
                        author = str(v.get("author") or "")
                        cache[k] = {
                            "head_sha": head_sha,
                            "last_reviewed_at": last_reviewed_at,
                            "title": title,
                            "author": author,
                        }
                return cache
    except json.JSONDecodeError as e:
        logger.warning("Cache file %s corrupted, starting fresh: %s", expanded_path, e)
    except OSError as e:
        logger.warning("Failed to read cache file %s: %s", expanded_path, e)
    return {}


def save_pr_cache(cache_path: str, cache: Dict[str, PRCacheEntry]) -> None:
    """Save PR review cache to JSON file."""
    expanded_path = Path(os.path.expanduser(cache_path))
    try:
        expanded_path.parent.mkdir(parents=True, exist_ok=True)
        with expanded_path.open("w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except OSError as e:
        logger.error("Failed to write cache file %s: %s", expanded_path, e)


def format_pr_summary(
    candidate: CandidatePR,
    comments_count: int,
    diff_summary: Optional[Dict[str, int]] = None,
) -> str:
    """Format candidate PR review summary using clean ASCII/Unicode box art."""
    pr = candidate.pr
    diff_line = ""
    if diff_summary is not None:
        diff_info = (
            f"{diff_summary['files_changed']} files, "
            f"+{diff_summary['additions']} / -{diff_summary['deletions']} lines"
        )
        diff_line = f"│ Diff:     {diff_info:<66}│\n"

    short_sha = pr.head_sha[:8] if pr.head_sha else "unknown"
    border = "─" * 78
    return (
        f"┌{border}┐\n"
        f"│ Candidate PR: {pr.key:<63}│\n"
        f"├{border}┤\n"
        f"│ Title:    {pr.title[:64]:<66}│\n"
        f"│ Author:   {pr.author[:64]:<66}│\n"
        f"│ Head SHA: {short_sha:<66}│\n"
        f"│ Reason:   {candidate.reason[:64]:<66}│\n"
        f"│ URL:      {pr.url[:64]:<66}│\n"
        f"│ Comments: {f'{comments_count} existing review comments':<66}│\n"
        f"{diff_line}"
        f"└{border}┘"
    )


def _normalize_string_list(items: Optional[Sequence[str]]) -> List[str]:
    """Split comma-separated or space-separated items into clean string list."""
    if not items:
        return []
    result: List[str] = []
    for item in items:
        for part in item.split(","):
            cleaned = part.strip()
            if cleaned:
                result.append(cleaned)
    return result


def _normalize_repos(repos_input: Optional[Sequence[str]], default_org: str) -> List[str]:
    """Normalize repository slugs into full owner/repo strings."""
    raw_repos = _normalize_string_list(repos_input)
    result: List[str] = []
    for repo in raw_repos:
        if "/" in repo:
            result.append(repo)
        else:
            result.append(f"{default_org}/{repo}")
    return result


def _fetch_prs_for_repos(repos: Sequence[str], limit: int) -> List[PullRequest]:
    """Fetch open pull requests across specific repositories using gh pr list."""
    prs: List[PullRequest] = []
    for repo_slug in repos:
        if "/" in repo_slug:
            owner, repo_name = repo_slug.split("/", 1)
        else:
            owner, repo_name = DEFAULT_ORG, repo_slug

        try:
            raw_output = _run_gh([
                "pr", "list",
                "--repo", repo_slug,
                "--state", "open",
                "--limit", str(limit),
                "--json", "number,title,author,isDraft,headRefOid,url",
            ])
            data = json.loads(raw_output)
            if not isinstance(data, list):
                continue
            for item in data:
                if not isinstance(item, dict):
                    continue
                number = int(item.get("number") or 0)
                title = str(item.get("title") or "")
                is_draft = bool(item.get("isDraft"))
                head_sha = str(item.get("headRefOid") or "")
                url = str(item.get("url") or "")
                author_dict = item.get("author")
                author_login = ""
                if isinstance(author_dict, dict):
                    author_login = str(author_dict.get("login") or "")

                prs.append(
                    PullRequest(
                        owner=owner,
                        repo=repo_name,
                        number=number,
                        title=title,
                        author=author_login,
                        is_draft=is_draft,
                        url=url,
                        head_sha=head_sha,
                    )
                )
        except subprocess.CalledProcessError as e:
            logger.warning("Failed to fetch PRs for %s: %s", repo_slug, e)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON for %s: %s", repo_slug, e)
        except RuntimeError as e:
            logger.error("Error executing gh for %s: %s", repo_slug, e)

    return prs


def _fetch_prs_for_org(org: str, limit: int) -> List[PullRequest]:
    """Fetch open pull requests across an entire organization using gh search prs."""
    prs: List[PullRequest] = []
    search_limit = max(limit * 4, 40)
    try:
        raw_output = _run_gh([
            "search", "prs",
            "--owner", org,
            "--state", "open",
            "--limit", str(search_limit),
            "--json", "number,title,repository,author,isDraft,url",
        ])
        data = json.loads(raw_output)
        if not isinstance(data, list):
            return []
        for item in data:
            if not isinstance(item, dict):
                continue
            number = int(item.get("number") or 0)
            title = str(item.get("title") or "")
            is_draft = bool(item.get("isDraft"))
            url = str(item.get("url") or "")

            repo_dict = item.get("repository")
            repo_name = ""
            owner = org
            if isinstance(repo_dict, dict):
                name_with_owner = str(repo_dict.get("nameWithOwner") or "")
                if "/" in name_with_owner:
                    owner, repo_name = name_with_owner.split("/", 1)
                else:
                    repo_name = str(repo_dict.get("name") or "")

            author_dict = item.get("author")
            author_login = ""
            if isinstance(author_dict, dict):
                author_login = str(author_dict.get("login") or "")

            prs.append(
                PullRequest(
                    owner=owner,
                    repo=repo_name,
                    number=number,
                    title=title,
                    author=author_login,
                    is_draft=is_draft,
                    url=url,
                    head_sha="",
                )
            )
    except subprocess.CalledProcessError as e:
        logger.error("Failed to search PRs for org %s: %s", org, e)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse search JSON for org %s: %s", org, e)
    except RuntimeError as e:
        logger.error("Error executing gh for org %s: %s", org, e)

    return prs


def find_candidate_prs(
    prs: Sequence[PullRequest],
    cache: Dict[str, PRCacheEntry],
    ignore_drafts: bool,
    ignore_authors: Sequence[str],
    limit: int,
) -> List[CandidatePR]:
    """Filter open pull requests and evaluate deduplication state against cache."""
    candidates: List[CandidatePR] = []
    ignored_authors_set = {a.lower() for a in ignore_authors}

    for pr in prs:
        if len(candidates) >= limit:
            break

        # 1. Draft check
        if ignore_drafts and pr.is_draft:
            logger.debug("Skipping draft PR: %s", pr.key)
            continue

        # 2. Ignored authors check
        if pr.author.lower() in ignored_authors_set:
            logger.debug("Skipping bot/ignored author PR: %s (%s)", pr.key, pr.author)
            continue

        # 3. Resolve head commit SHA if not present
        head_sha = pr.head_sha
        if not head_sha:
            head_sha = fetch_head_sha(pr.owner, pr.repo, pr.number)
            if not head_sha:
                logger.warning("Could not determine head SHA for %s, skipping", pr.key)
                continue

        current_pr = PullRequest(
            owner=pr.owner,
            repo=pr.repo,
            number=pr.number,
            title=pr.title,
            author=pr.author,
            is_draft=pr.is_draft,
            url=pr.url,
            head_sha=head_sha,
        )

        # 4. Check cache for deduplication
        cached_entry = cache.get(current_pr.key)
        if cached_entry is not None:
            cached_sha = cached_entry.get("head_sha")
            if cached_sha == head_sha:
                logger.debug("Skipping already reviewed PR at %s: %s", head_sha[:8], current_pr.key)
                continue
            candidates.append(
                CandidatePR(
                    pr=current_pr,
                    reason=f"New commits pushed (previous SHA: {cached_sha[:8]}, current: {head_sha[:8]})",
                    previous_sha=cached_sha,
                )
            )
        else:
            candidates.append(
                CandidatePR(
                    pr=current_pr,
                    reason="New open pull request needing initial review",
                    previous_sha=None,
                )
            )

    return candidates


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Find candidate open pull requests needing review across an org or repos.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--org",
        default=DEFAULT_ORG,
        help="Organization name to search pull requests for.",
    )
    parser.add_argument(
        "--repos",
        nargs="*",
        help="Optional specific repositories to target (comma or space separated).",
    )
    parser.add_argument(
        "--cache-path",
        default=DEFAULT_CACHE_PATH,
        help="Path to the JSON review cache state file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't update state cache or post comments; just display candidate open PRs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Max number of candidate open PRs to process per run.",
    )
    parser.add_argument(
        "--ignore-drafts",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip draft PRs.",
    )
    parser.add_argument(
        "--ignore-authors",
        nargs="*",
        default=DEFAULT_IGNORE_AUTHORS,
        help="List of authors or bots whose PRs should be skipped.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output candidate PRs formatted as a JSON array.",
    )
    parser.add_argument(
        "--auto-cache",
        action="store_true",
        help="Automatically mark candidates as reviewed during scan (default: False, review must complete first).",
    )
    parser.add_argument(
        "--fetch-context",
        metavar="PR_KEY",
        help="Fetch unified diff, existing comments, and head SHA for a PR key in JSON format.",
    )
    parser.add_argument(
        "--post-review",
        metavar="PR_KEY",
        help="Submit a formal PR review on GitHub (e.g. Ostorlab/repo#123).",
    )
    parser.add_argument(
        "--review-event",
        choices=["COMMENT", "APPROVE", "REQUEST_CHANGES"],
        default="COMMENT",
        help="Review action event when using --post-review.",
    )
    parser.add_argument(
        "--review-body",
        help="Markdown text content for the review submission.",
    )
    parser.add_argument(
        "--review-body-file",
        help="Path to file containing markdown review text.",
    )
    parser.add_argument(
        "--mark-reviewed",
        nargs=2,
        metavar=("PR_KEY", "HEAD_SHA"),
        help="Explicitly record a PR key and head commit SHA into the review state cache.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging output.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main CLI entrypoint."""
    args = parse_args(argv)
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    cache = load_pr_cache(args.cache_path)

    if args.mark_reviewed:
        key, sha = args.mark_reviewed[0], args.mark_reviewed[1]
        now_iso = datetime.now(timezone.utc).isoformat()
        cache[key] = {
            "head_sha": sha,
            "last_reviewed_at": now_iso,
            "title": "",
            "author": "",
        }
        save_pr_cache(args.cache_path, cache)
        print(f"✓ Explicitly recorded {key} (SHA: {sha}) as reviewed in {os.path.expanduser(args.cache_path)}")
        return 0

    if args.fetch_context:
        owner, repo, number = parse_pr_key(args.fetch_context, args.org)
        diff_text = fetch_pr_diff(owner, repo, number)
        comments = fetch_review_comments(owner, repo, number)
        head_sha = fetch_head_sha(owner, repo, number)
        print(json.dumps({
            "key": f"{owner}/{repo}#{number}",
            "owner": owner,
            "repo": repo,
            "number": number,
            "head_sha": head_sha,
            "comments_count": len(comments),
            "comments": comments,
            "diff": diff_text,
        }, indent=2))
        return 0

    if args.post_review:
        owner, repo, number = parse_pr_key(args.post_review, args.org)
        body = args.review_body or ""
        if args.review_body_file:
            try:
                body = Path(args.review_body_file).read_text(encoding="utf-8")
            except OSError as e:
                logger.error("Failed to read --review-body-file: %s", e)
                return 1

        if not body.strip():
            logger.error("No review body content provided for --post-review.")
            return 1

        success = post_pr_review(owner, repo, number, body, event=args.review_event)
        if success:
            head_sha = fetch_head_sha(owner, repo, number)
            key = f"{owner}/{repo}#{number}"
            now_iso = datetime.now(timezone.utc).isoformat()
            cache[key] = {
                "head_sha": head_sha,
                "last_reviewed_at": now_iso,
                "title": "",
                "author": "",
            }
            save_pr_cache(args.cache_path, cache)
            print(f"✓ Successfully submitted review ({args.review_event}) to {key} and updated state cache.")
            return 0
        else:
            logger.error("Failed to submit review to %s/%s#%d.", owner, repo, number)
            return 1

    clean_repos = _normalize_repos(args.repos, args.org)
    clean_ignore_authors = _normalize_string_list(args.ignore_authors)

    if clean_repos:
        logger.info("Fetching open PRs for %d specific repos...", len(clean_repos))
        raw_prs = _fetch_prs_for_repos(clean_repos, args.limit)
    else:
        logger.info("Searching open PRs across organization '%s'...", args.org)
        raw_prs = _fetch_prs_for_org(args.org, args.limit)

    candidates = find_candidate_prs(
        prs=raw_prs,
        cache=cache,
        ignore_drafts=args.ignore_drafts,
        ignore_authors=clean_ignore_authors,
        limit=args.limit,
    )

    if args.output_json:
        json_output = [
            {
                "key": c.pr.key,
                "owner": c.pr.owner,
                "repo": c.pr.repo,
                "number": c.pr.number,
                "title": c.pr.title,
                "author": c.pr.author,
                "url": c.pr.url,
                "head_sha": c.pr.head_sha,
                "is_draft": c.pr.is_draft,
                "reason": c.reason,
                "previous_sha": c.previous_sha,
            }
            for c in candidates
        ]
        print(json.dumps(json_output, indent=2))
        return 0

    mode_label = "DRY RUN - CANDIDATES ONLY" if args.dry_run else "DISCOVERY RUN"
    print(f"\n=== Scheduled PR Review: {mode_label} ===")
    print(f"Organization:  {args.org}")
    print(f"Cache File:    {os.path.expanduser(args.cache_path)}")
    print(f"Open PRs seen: {len(raw_prs)}")
    print(f"Candidates:    {len(candidates)} needing review (limit: {args.limit})\n")

    if not candidates:
        print("✓ All open PRs are up to date and have been previously reviewed.")
        return 0

    for candidate in candidates:
        pr = candidate.pr
        comments = fetch_review_comments(pr.owner, pr.repo, pr.number)
        diff_text = fetch_pr_diff(pr.owner, pr.repo, pr.number)
        diff_summary = summarize_diff(diff_text)
        print(format_pr_summary(candidate, len(comments), diff_summary))

    if args.auto_cache and not args.dry_run:
        now_iso = datetime.now(timezone.utc).isoformat()
        for candidate in candidates:
            pr = candidate.pr
            cache[pr.key] = {
                "head_sha": pr.head_sha,
                "last_reviewed_at": now_iso,
                "title": pr.title,
                "author": pr.author,
            }
        save_pr_cache(args.cache_path, cache)
        print(f"\n✓ Updated state cache at {os.path.expanduser(args.cache_path)} with {len(candidates)} reviewed PRs.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
