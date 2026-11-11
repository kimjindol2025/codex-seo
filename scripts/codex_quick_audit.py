#!/usr/bin/env python3
"""Codex's lightweight, first-pass SEO audit.

This deliberately avoids PageSpeed, Search Console, GA4, SERP providers, and
full-site crawling. Those are opt-in enrichments, not prerequisites for a useful
first diagnosis.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent


def run(script: str, args: list[str]) -> dict[str, object]:
    command = [sys.executable, str(ROOT / "scripts" / script), *args]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    output = result.stdout.strip()
    try:
        payload: object = json.loads(output) if output else {"error": result.stderr.strip()}
    except json.JSONDecodeError:
        payload = {"raw_output": output, "stderr": result.stderr.strip()}
    return {"exit_code": result.returncode, "result": payload}


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex lightweight SEO audit")
    parser.add_argument("url", help="Public URL to inspect")
    parser.add_argument("--agentic", action="store_true", help="Also inspect AI-agent discovery surfaces")
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        parser.error("url must be an absolute http:// or https:// URL")
    url = args.url.rstrip("/") + "/"

    checks: dict[str, object] = {
        "profile": "codex-quick",
        "url": url,
        "policy": {
            "external_apis": "not_requested",
            "full_crawl": False,
            "performance": "not_requested",
            "heuristics_require_review": True,
        },
        "next_step": "1차 검수가 끝났습니다. 검색 의도·키워드·경쟁 페이지·콘텐츠 갭·전환 흐름까지 포함한 2차 SEO 전략 검수도 진행할까요?",
        "checks": {
            "page": run("page_checks.py", ["--url", url, "--json"]),
            "sitemap": run("sitemap_discovery.py", [url, "--expand", "--json"]),
        },
    }
    if args.agentic:
        checks["checks"]["agentic"] = run("agentic_check.py", [url, "--json"])  # type: ignore[index]
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
