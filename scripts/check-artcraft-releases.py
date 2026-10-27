#!/usr/bin/env python3
"""Report stable GitHub release drift for explicitly qualified ArtCraft apps.

This read-only check reports release pins; it never edits pins, patches, builds,
dispatch configuration, or deployed files.
"""

from __future__ import annotations

import argparse
from datetime import timezone
from email.utils import parsedate_to_datetime
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_ROOT = "https://api.github.com/repos"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
MAX_RETRIES = 2
MAX_RETRY_AFTER_SECONDS = 30


def retry_delay(error: BaseException, attempt: int) -> float | None:
    if isinstance(error, urllib.error.HTTPError):
        retryable = error.code == 429 or 500 <= error.code <= 599
        if error.code == 403 and error.headers is not None:
            retryable = error.headers.get("Retry-After") is not None or error.headers.get("X-RateLimit-Remaining") == "0"
        if not retryable:
            return None
        if error.headers is not None:
            retry_after = error.headers.get("Retry-After")
            if retry_after:
                try:
                    return min(max(float(retry_after), 0.0), MAX_RETRY_AFTER_SECONDS)
                except ValueError:
                    try:
                        retry_at = parsedate_to_datetime(retry_after)
                        if retry_at.tzinfo is None:
                            retry_at = retry_at.replace(tzinfo=timezone.utc)
                        return min(max(retry_at.timestamp() - time.time(), 0.0), MAX_RETRY_AFTER_SECONDS)
                    except (TypeError, ValueError, OverflowError):
                        pass
        return float(2**attempt)
    if isinstance(error, (urllib.error.URLError, TimeoutError, OSError)):
        return float(2**attempt)
    return None


def github_json(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "artcraft-release-check/1"},
    )
    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            delay = retry_delay(exc, attempt)
            if delay is None or attempt >= MAX_RETRIES:
                raise
            if isinstance(exc, urllib.error.HTTPError):
                exc.close()
            time.sleep(delay)
    if not isinstance(payload, dict):
        raise ValueError("GitHub API returned a non-object response")
    return payload


def latest_release(repository: str, timeout: float) -> dict[str, str]:
    repo_api = f"{API_ROOT}/{repository}"
    release = github_json(f"{repo_api}/releases/latest", timeout)
    tag = release.get("tag_name")
    if not isinstance(tag, str) or not tag:
        raise ValueError("latest release has no tag_name")

    encoded_tag = urllib.parse.quote(tag, safe="")
    ref_url = f"{repo_api}/git/ref/tags/{encoded_tag}"
    ref = github_json(ref_url, timeout)
    obj = ref.get("object")
    for _ in range(6):
        if not isinstance(obj, dict):
            raise ValueError("tag reference has no object")
        sha = obj.get("sha")
        kind = obj.get("type")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("tag reference has an invalid object SHA")
        if kind == "commit":
            return {"tag": tag, "commit": sha, "url": str(release.get("html_url", ""))}
        if kind != "tag":
            raise ValueError(f"tag resolves to unsupported Git object type: {kind}")
        tag_object = github_json(f"{repo_api}/git/tags/{sha}", timeout)
        obj = tag_object.get("object")
    raise ValueError("annotated tag nesting exceeds six levels")


def compare(repository: str, base: str, head: str, timeout: float) -> dict[str, Any]:
    url = f"{API_ROOT}/{repository}/compare/{base}...{head}"
    result = github_json(url, timeout)
    status = result.get("status")
    ahead_by = result.get("ahead_by")
    behind_by = result.get("behind_by")
    if status not in {"ahead", "behind", "diverged", "identical"}:
        raise ValueError(f"GitHub compare returned an unexpected status: {status!r}")
    if not isinstance(ahead_by, int) or not isinstance(behind_by, int):
        raise ValueError("GitHub compare response has invalid ahead/behind counts")
    merge_base = result.get("merge_base_commit")
    merge_base_sha = merge_base.get("sha") if isinstance(merge_base, dict) else None
    if not isinstance(merge_base_sha, str) or not COMMIT_RE.fullmatch(merge_base_sha):
        raise ValueError("GitHub compare response has no valid merge_base_commit SHA")
    return {
        "status": status,
        "ahead_by": ahead_by,
        "behind_by": behind_by,
        "merge_base_commit": merge_base_sha,
    }


def inspect_app(app: dict[str, str], timeout: float) -> dict[str, Any]:
    repository = app["repository"]
    base = app["qualified_commit"]
    result: dict[str, Any] = {
        "app": app["app"],
        "repository": repository,
        "qualified_ref": app["qualified_ref"],
        "qualified_commit": base,
    }
    try:
        if not COMMIT_RE.fullmatch(base):
            raise ValueError("qualified_commit must be a full 40-character SHA")
        release = latest_release(repository, timeout)
        result["latest_release"] = release
        if release["commit"] == base:
            result["drift"] = {"status": "same", "ahead_by": 0, "behind_by": 0}
        else:
            result["drift"] = compare(repository, base, release["commit"], timeout)
        return result
    except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        result["status"] = "unknown"
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "integration/config/artcraft-upstream.json",
    )
    parser.add_argument("--timeout", type=float, default=12.0)
    args = parser.parse_args()

    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        apps = config["apps"]
        if config.get("schema_version") != 1 or not isinstance(apps, list):
            raise ValueError("unsupported config schema")
        required = {"app", "repository", "qualified_ref", "qualified_commit"}
        if any(not isinstance(app, dict) or not required.issubset(app) for app in apps):
            raise ValueError("each app must include app, repository, qualified_ref and qualified_commit")
        results = [inspect_app(app, args.timeout) for app in apps]
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({"schema_version": 1, "results": results}, indent=2, sort_keys=True))
    return 1 if any("status" in result for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
