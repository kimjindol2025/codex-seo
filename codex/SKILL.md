---
name: codex-seo
description: "Run a lightweight, evidence-first SEO audit from Codex, with optional deeper checks for technical SEO, schema, content, GEO, local SEO, e-commerce SEO, backlinks, and drift."
user-invocable: true
argument-hint: "[quick|audit|technical|content|schema|sitemap|geo|page|...] [url]"
license: MIT
metadata:
  source: AgriciDaniel/claude-seo
  adapter: codex
---

# Codex SEO workflow

Use the repository's analysis logic, but follow this Codex-specific policy:

- Default to a lightweight first pass. Do not start a 500-page crawl or paid/API
  checks unless the user asks for a full audit or enrichment.
- Treat PageSpeed, Search Console, GA4, SERP, backlink, and other external data
  providers as optional enrichments, never as prerequisites.
- Label every result as `confirmed`, `heuristic`, `environmental`, or
  `unavailable`. Heuristics require human/context review before being called a
  defect.
- Interpret findings in context. For example, a localhost URL in production is
  a confirmed deployment concern only after checking whether it is an intentional
  browser-local development hook; report both the evidence and that distinction.
- Read only the smallest relevant `skills/*/SKILL.md` and references. Use
  `agents/*.md` as checklists, not as a requirement to spawn every agent.

## Two-stage review

Every SEO request uses two explicit stages:

### 1차: 기술·페이지 진단

Run the lightweight profile first. Check crawlability, rendering, metadata,
canonical, headings, structured data, robots, sitemap, links, mixed content,
security headers, and basic accessibility signals. Report confirmed findings,
heuristics, environmental warnings, and unavailable data separately.

At the end of the first-stage answer, ask exactly:

> 1차 검수가 끝났습니다. 검색 의도·키워드·경쟁 페이지·콘텐츠 갭·전환 흐름까지 포함한 2차 SEO 전략 검수도 진행할까요?

Do not run stage 2 unless the user asks for it.

### 2차: SEO 전략 검수

When the user requests the second review, read
`codex/skills/seo-strategy/SKILL.md`. Analyze search intent, Korean keyword
fit, live SERP competition when browsing is available, snippet clickability,
conversion flow, E-E-A-T, content expansion, internal links, and connected
Search Console/GA4 data. Clearly separate measured data, sourced observations,
heuristics, and assumptions.

Claude Code's plugin manifest, `/plugin` commands, and Claude-specific hooks are
not required by Codex.

## Runtime

Run deterministic tools only through the repository-relative wrapper:

```bash
./scripts/codex-seo doctor --json
./scripts/codex-seo setup
./scripts/codex-seo quick https://example.com
./scripts/codex-seo quick https://example.com --output-dir ./audits
./scripts/codex-seo run render_page.py "https://example.com" --mode auto --json
```

The wrapper resolves its own repository root. Never depend on
`${CLAUDE_PLUGIN_ROOT}`. Setup creates the project's managed runtime and may
install Chromium; ask before running setup if dependencies are not present.

## Default workflow

Run the quick profile first:

```bash
./scripts/codex-seo quick <url>
```

It checks one page plus robots/sitemap discovery and intentionally skips
PageSpeed, GSC, GA4, SERP providers, paid backlink APIs, and full crawling. Add
`--agentic` only when AI-agent discovery is relevant.

The quick profile is stage 1 only. It must not be presented as a complete SEO
strategy review.

## Documentation and handoff

Every audit must be saved under the user-specified output root, separated by
domain:

```text
<output-dir>/<domain>/
  README.md
  phase-1/
    REPORT.md
    audit-data.json
    sources.md
  phase-2/                 # created only after a 2차 request
    REPORT.md
    strategy-data.json
    sources.md
```

Use `--output-dir` when the user names a folder. If no folder is named, use
`./audits`. The domain folder is the hostname, not a free-form project name.
`README.md` is the handoff file: another Codex must read it first, then the
phase report, JSON evidence, and sources. Do not rely on conversation text as
the only record.

After a 2차 review, update the domain `README.md` with the latest status and
write all strategy evidence under `phase-2/`; do not overwrite phase 1.

## Full workflow

For a full audit:

1. Read `skills/seo-audit/SKILL.md` and `skills/seo/SKILL.md`.
2. Run `./scripts/codex-seo doctor --json`.
3. Use the relevant bundled tools for fetching, rendering, parsing, sitemap,
   schema, and drift evidence. Add PageSpeed or other external data only when
   explicitly requested or credentials are already available.
4. Read specialist skills for the detected site type and findings.
5. Produce a Markdown report with evidence, severity, confidence label,
   dependencies, and a falsifiable success check for every recommendation.

Codex may parallelize independent analysis tasks when worker support is
available. If it is not available, run the same specialist workflows inline.

## Command mapping

| Claude Code command | Codex action |
|---|---|
| `/seo audit <url>` | Run `quick` first; ask whether to continue to stage 2 |
| `2차 SEO 검수` | Read `codex/skills/seo-strategy/SKILL.md` and run the strategy review |
| `/seo technical <url>` | Read `skills/seo-technical/SKILL.md` |
| `/seo content <url>` | Read `skills/seo-content/SKILL.md` |
| `/seo schema <url>` | Read `skills/seo-schema/SKILL.md` |
| `/seo sitemap <url>` | Read `skills/seo-sitemap/SKILL.md` |
| `/seo geo <url>` | Read `skills/seo-geo/SKILL.md` |
| `/seo page <url>` | Read `skills/seo-page/SKILL.md` |

Claude-only hooks, plugin manifests, and MCP extensions are optional. Use an
extension only when its credentials/tool connection is explicitly available.
