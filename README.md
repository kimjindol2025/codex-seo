# Codex SEO

웹사이트를 Codex로 조사하고, SEO 문제와 검색 전략을 문서로 남기는 도구입니다.

이 저장소는 [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)의
검사 로직을 기반으로 하되, 사용 방식과 결과물은 Codex 작업 흐름에 맞게
구성했습니다.

## 핵심 방식

SEO 검수는 두 단계로 진행합니다.

### 1차: 기술·페이지 검수

- 공개 페이지 HTML·헤더·렌더링 확인
- title·description·H1·canonical 점검
- Schema·Open Graph·이미지 점검
- robots.txt·sitemap.xml 확인
- 내부 링크·혼합 콘텐츠·기본 보안 헤더 확인
- 확인된 오류, 휴리스틱, 환경 경고, 미확인 데이터를 구분

### 2차: SEO 전략 검수

1차 검수 후 요청이 있을 때 진행합니다.

- 검색 의도와 한국어 키워드군
- 경쟁 페이지와 콘텐츠 갭
- 검색 결과 제목·설명 개선
- 가입·사용 전환 흐름
- E-E-A-T와 신뢰 요소
- 콘텐츠 확장 주제와 내부 링크
- Search Console·GA4 실제 데이터

## 시작하기

요구 사항: Python 3.11~3.14, Git

```bash
git clone https://github.com/kimjindol2025/codex-seo.git
cd codex-seo
./scripts/codex-seo setup
```

설치 상태 확인:

```bash
./scripts/codex-seo doctor --json
```

## 1차 검수

기본 검수는 무겁지 않은 프로필로 실행합니다. PageSpeed, Search Console,
GA4, 유료 키워드·백링크 API, 전체 사이트 크롤링은 자동으로 실행하지 않습니다.

```bash
./scripts/codex-seo quick https://example.com \
  --output-dir /home/kim/seo-audits
```

AI 에이전트 접근성까지 확인하려면:

```bash
./scripts/codex-seo quick https://example.com \
  --agentic \
  --output-dir /home/kim/seo-audits
```

## 문서화 결과

`--output-dir` 아래에 도메인별 인수인계 폴더가 만들어집니다.

```text
seo-audits/
└── example.com/
    ├── README.md
    ├── phase-1/
    │   ├── REPORT.md
    │   ├── audit-data.json
    │   └── sources.md
    └── phase-2/
        ├── REPORT.md
        ├── strategy-data.json
        └── sources.md
```

다른 Codex가 이어서 작업할 때는 해당 도메인의 `README.md`를 먼저 읽고,
그 다음 단계별 보고서·JSON·근거 문서를 읽습니다. 대화 내용만을 유일한
기록으로 사용하지 않습니다.

## 명령어

```bash
./scripts/codex-seo doctor --json
./scripts/codex-seo portability
./scripts/codex-seo quick <url> [--agentic] [--output-dir <folder>]
./scripts/codex-seo run <script.py> [args...]
```

개별 검사 예시:

```bash
./scripts/codex-seo run page_checks.py \
  --url https://example.com --json

./scripts/codex-seo run render_page.py \
  https://example.com --mode auto --json
```

## Codex 진입점

- [`AGENTS.md`](AGENTS.md): 프로젝트 작업 규칙
- [`codex/SKILL.md`](codex/SKILL.md): 1차·2차 SEO 작업 흐름
- [`codex/skills/seo-strategy/SKILL.md`](codex/skills/seo-strategy/SKILL.md): 2차 전략 검수
- [`scripts/codex-seo`](scripts/codex-seo): Codex용 실행 래퍼

## 데이터와 한계

- URL만으로는 공개 페이지와 공개 리소스만 확인할 수 있습니다.
- 로그인 후 화면·비공개 API는 별도 권한과 브라우저 세션이 필요합니다.
- 검색량·CTR·순위·전환율은 Search Console, GA4 또는 키워드 데이터 연결 전에는
  실제 값으로 제시하지 않습니다.
- SEO 휴리스틱은 검색엔진의 절대 규칙이 아니므로 맥락 검토가 필요합니다.
- 외부 사이트는 소유자의 허가 범위 안에서 조사하고, 코드를 그대로 복제하지
  않고 관찰된 구조와 근거를 바탕으로 독자적으로 구현해야 합니다.

## 라이선스

MIT License. 원본 분석 로직과 저작권 고지는 저장소의 [`LICENSE`](LICENSE)를
따릅니다.
