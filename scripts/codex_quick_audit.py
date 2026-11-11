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
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent


def write_artifacts(checks: dict[str, object], output_root: Path, domain: str) -> Path:
    """Write a durable handoff that another Codex can continue from."""
    audit_dir = output_root / domain
    phase_dir = audit_dir / "phase-1"
    phase_dir.mkdir(parents=True, exist_ok=True)
    page = checks["checks"]["page"]["result"]  # type: ignore[index]
    sitemap = checks["checks"]["sitemap"]["result"]  # type: ignore[index]
    page_facts = page.get("facts", {}) if isinstance(page, dict) else {}
    findings = page.get("findings", []) if isinstance(page, dict) else []
    totals = sitemap.get("expanded", {}).get("totals", {}) if isinstance(sitemap, dict) else {}
    generated = datetime.now(timezone.utc).isoformat()
    checks["artifacts"] = {
        "generated_at": generated,
        "directory": str(audit_dir),
        "handoff": str(audit_dir / "README.md"),
        "report": str(phase_dir / "REPORT.md"),
        "data": str(phase_dir / "audit-data.json"),
        "sources": str(phase_dir / "sources.md"),
    }
    (phase_dir / "audit-data.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    finding_lines = []
    for finding in findings if isinstance(findings, list) else []:
        if isinstance(finding, dict):
            finding_lines.append(
                f"- **{finding.get('severity', 'Info')}** `{finding.get('id', 'unknown')}`: "
                f"{finding.get('message', '')} — {finding.get('evidence', '')}"
            )
    report = f"""# {domain} 1차 SEO 검수

- 대상: {checks['url']}
- 생성 시각(UTC): {generated}
- 프로필: Codex quick (기술·페이지 진단)

## 요약

- HTTP 상태: {page.get('status_code', '미확인') if isinstance(page, dict) else '미확인'}
- Title: {page_facts.get('title', '없음')}
- 본문 단어 수: {page_facts.get('word_count', '미확인')}
- Sitemap URL 수: {totals.get('total_urls', '미확인')}
- 외부 API: 사용하지 않음

## 발견사항

{chr(10).join(finding_lines) or '- 자동 발견사항 없음'}

## 다음 단계

1차 검수는 기술·페이지 진단만 포함합니다. 검색 의도, 키워드, 경쟁 페이지,
콘텐츠 갭, 전환 흐름은 사용자가 요청할 때 2차 검수로 진행합니다.

## 다음 Codex를 위한 읽기 순서

1. 이 파일
2. `audit-data.json`
3. `sources.md`
4. 저장소의 `codex/SKILL.md`
"""
    (phase_dir / "REPORT.md").write_text(report, encoding="utf-8")
    sources = f"""# {domain} 검수 근거

- 분석 대상: {checks['url']}
- robots.txt: {sitemap.get('robots_url', '미확인') if isinstance(sitemap, dict) else '미확인'}
- sitemap 선언·검사 결과는 `audit-data.json`의 `checks.sitemap`에 저장됨
- 페이지 검사 원본은 `audit-data.json`의 `checks.page`에 저장됨
- 생성 시각(UTC): {generated}
"""
    (phase_dir / "sources.md").write_text(sources, encoding="utf-8")
    handoff = f"""# {domain} SEO 감사 작업공간

대상: {checks['url']}

현재 상태: **1차 기술·페이지 검수 완료**

## 파일

- [1차 보고서](phase-1/REPORT.md)
- [구조화 감사 데이터](phase-1/audit-data.json)
- [검수 근거](phase-1/sources.md)

## 이어서 작업할 때

먼저 `phase-1/REPORT.md`와 `phase-1/audit-data.json`을 읽으세요. 2차 요청이
있으면 `codex/skills/seo-strategy/SKILL.md`를 읽고 `phase-2/` 아래에
`REPORT.md`, `strategy-data.json`, `sources.md`를 추가하세요. 실제 검색량·
CTR·유입 데이터가 없으면 추정으로 표시하고 사실처럼 쓰지 않습니다.
"""
    (audit_dir / "README.md").write_text(handoff, encoding="utf-8")
    return audit_dir


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
    parser.add_argument(
        "--output-dir",
        default="audits",
        help="Root folder for durable domain reports (default: ./audits)",
    )
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
    audit_dir = write_artifacts(checks, Path(args.output_dir), parsed.hostname or parsed.netloc)
    checks["artifacts"] = {**checks["artifacts"], "directory": str(audit_dir)}  # type: ignore[index]
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
