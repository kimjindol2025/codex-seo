# Codex SEO project instructions

This repository is a Codex-native SEO auditing toolkit. Read `codex/SKILL.md`
before starting an audit; it defines the two-stage workflow and report contract.

## Entry points

```bash
./scripts/codex-seo quick https://example.com
./scripts/codex-seo setup
./scripts/codex-seo doctor --json
./scripts/codex-seo portability
```

Use `quick` for the deterministic first pass. Codex then interprets the
findings and writes a domain-scoped report under `audits/<domain>/` unless the
user supplies another `--output-dir`.

## Audit workflow

1. Phase 1: fetch the page, inspect technical SEO, metadata, headings, links,
   images, structured data, robots, sitemap, and crawlability.
2. Ask whether the user wants Phase 2.
3. Phase 2: apply `codex/skills/seo-strategy/SKILL.md` for search intent,
   Korean keyword fit, SERP competition, snippets, conversion, E-E-A-T,
   content expansion, internal links, and GSC/GA4 evidence.
4. Save evidence and the human-readable report. Never present a heuristic as a
   Google ranking fact.

## Report contract

Every domain report must contain `README.md`, `phase-1/REPORT.md`,
`phase-1/audit-data.json`, and `phase-1/sources.md`. Phase 2 belongs in
`phase-2/` with the same evidence-first structure. Keep credentials and raw
private analytics out of the repository.

## Implementation rules

- Prefer `./scripts/codex-seo run <script.py>`.
- Use bundled URL-safe fetch/render tools for user-supplied URLs.
- Keep external APIs optional and label unavailable data rather than inventing it.
- Preserve user changes and use `apply_patch` for edits.
- Run `git diff --check`, Python compilation, and portability checks before committing.

## Layout

- `codex/`: Codex workflow and strategy skill.
- `skills/`: reusable SEO skills and reference material.
- `agents/`: specialist checklists used during a full audit.
- `scripts/`: deterministic analyzers and the managed Python runtime.
- `schema/`, `data/`: validation schemas and static data.
- `audits/`: ignored, domain-scoped output generated during local work.
