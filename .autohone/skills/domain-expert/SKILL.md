---
name: domain-expert
description: 도메인 지식이 필요한 태스크에서 knowledge-base 검색, 규칙 준수 확인, 골든 예제 참조를 수행합니다.
version: 1.5.0
---

# Domain Expert Skill

## Metadata
- **Name**: domain-expert
- **Trigger**: 도메인 지식이 필요한 모든 태스크
- **Priority**: HIGH
- **Model**: default

## Description

도메인 특화 지식을 제공하는 스킬입니다. 프로젝트의 `domain/knowledge-base/`에서 
관련 문서를 검색하고, `domain/rules/`의 불변 규칙을 적용합니다.

## Level 1: Quick Reference (항상 로드)

이 프로젝트의 도메인 지식은 다음 위치에 있습니다:
- `domain/knowledge-base/AGENTS.md` — 도메인 지식 목차 (~100줄)
- `domain/rules/` — 불변 규칙 (위반 불가)
- `domain/evaluator/criteria.yaml` — 평가 기준

## Level 2: Full Instructions (태스크 매칭 시 로드)

### 도메인 지식 활용 절차

1. **규칙 확인**: `domain/rules/` 내 모든 `.yaml` 파일을 먼저 읽고, 불변 제약을 파악
2. **지식 검색**: `domain/knowledge-base/`에서 태스크 관련 문서 탐색
3. **골든 예제 참조**: `data/golden-examples/`에서 유사 태스크의 성공 사례 검색
4. **규칙 적용**: 생성물이 모든 규칙을 준수하는지 검증

### 문서 작성 완결성 체크리스트

문서 태스크 수행 시 제출 전 반드시 확인:

1. **트리 다이어그램 정합성**: 프로젝트 트리 작성 시 실제 파일시스템과 대조하여 누락 파일이 없는지 확인. **반드시 숨김 디렉토리를 포함**하여 탐색할 것 — `fd -H -t f` 또는 `eza -a --tree` 사용 (`ls -R` 단독 사용 금지: `.claude-plugin/` 등 dot-prefix 디렉토리 누락 위험)
2. **플레이스홀더 표시**: 미완성/템플릿 상태인 파일은 "(placeholder)" 또는 "(template)"로 명시
3. **알려진 이슈 주석**: 오타, 의도적 명명, 미완성 부분 등은 주석으로 이유를 기록 (예: `referrences/` 디렉토리명)
4. **데이터 교환 포맷**: 에이전트/컴포넌트 간 데이터 교환이 있으면 YAML 스키마 또는 구조 설명 포함
5. **커스터마이징 가이드**: 도메인 추가, 설정 변경 등 확장 절차가 필요하면 포함 여부 판단
6. **Critical Claim 교차 검증**: "0% 준수율", "전면 누락", "모든 X가 Y" 등 극단적 주장(0%/100%)을 기술하기 전에 반드시 파일 직접 확인으로 교차 검증할 것. 검증 명령 예시: `fd -H -t f "plugin.json"` — 발견 시 주장을 즉시 수정
7. **Single-pass 문서 작성**: 분석 보고서·매트릭스 등 구조화 문서는 반드시 **Write 도구 1회**로 완성된 내용을 한 번에 작성. 중간에 Edit/append로 내용을 덧붙이는 방식 금지 — 중복 행·섹션 발생 원인 (ref-20260411T181500: gen-050 structure_quality 0.65). 작성 후 `wc -l` 검증 시 예상 줄 수와 크게 다르면 중복 여부 확인

### 문서 생성 패턴

분석 보고서를 생성할 때는 다음 순서를 따른다:

1. **Draft-then-Write**: 먼저 전체 내용을 컨텍스트 안에서 완성한 뒤 Write 도구로 한 번에 저장
2. **구조 검증 (의무)**: 저장 후 level-2 헤딩 수를 반드시 확인
   ```bash
   # ⚠ 반드시 '^## [^#]' 패턴 사용 — '^##'는 ### 서브섹션도 매칭하여 오탐 발생
   # (ref-20260411T185000: gen-051 AC5 FAIL 원인)
   grep -c '^## [^#]' <output_file>
   # Sprint Contract AC와 동일 패턴으로 검증 — 범위 밖이면 ### 제거 후 재작성
   ```
3. **중복 탐지 (의무 — 건너뛰기 금지)**: Write 직후 핵심 항목의 중복 여부를 반드시 확인
   ```bash
   # 분석 대상(플러그인·파일·항목) 중 첫 번째와 마지막 항목으로 검증
   grep -c '<first_item>' <output_file>   # 1 초과면 중복
   grep -c '<last_item>' <output_file>    # 1 초과면 중복
   # 중복 발견 시 Write 도구로 전체 재작성 (Edit 금지)
   ```

### 지식 기반 구조

```
domain/knowledge-base/
├── AGENTS.md          # 전체 목차 (이것만 읽으면 됨)
├── architecture/      # 시스템 아키텍처 문서
├── api-specs/         # API 명세
├── coding-standards/  # 코딩 표준
└── business-rules/    # 비즈니스 규칙
```

### 코드 구현 품질 가이드 (implementation task_type용, ref-20260411T205500)

코드를 생성하는 태스크에서 `conciseness` 및 `structure_quality` 점수를 유지하기 위한 규칙:

1. **300줄 상한 규칙**: 단일 Python/JS 파일이 300줄을 초과할 것으로 예상되면, Sprint 설계 시점에 모듈 분리를 계획할 것.
   - CLI 도구: 서브커맨드별 모듈 + 공통 유틸리티 모듈로 분리
   - 예: `memory_cli.py`(611줄) → `memory_cli.py`(메인) + `memory_capture.py` + `memory_query.py`
   - (ref: gen-055 conciseness 0.65 — 단일 파일 CLI 병목)

2. **Syntax 검증 의무**: Write/Edit 후 Python 파일은 `python3 -c "import ast; ast.parse(open('<file>').read())"` 실행
3. **테스트 동반 권고**: 주요 함수(argparse 서브커맨드 핸들러 등)에 최소 1개 테스트 작성 권고

> **배경**: gen-054(scaffold, 0.88)와 gen-055(tool-impl, 0.73)의 15포인트 차이는 파일 크기/모듈화 차이가 주된 원인. scaffold 태스크는 자연히 높은 structure_quality를 얻지만, tool 구현은 의식적 모듈화가 필요하다.

### 규칙 적용 우선순위

1. 안전 규칙 (security rules) — 최우선
2. 불변 비즈니스 규칙 (invariant business rules)
3. 코딩 표준 (coding standards)
4. 스타일 가이드 (style guide)

## Level 3: Resources (필요 시 로드)

### 도메인 지식 업데이트 프로세스

도메인 지식이 부족하다고 판단되면:
1. `data/reflections/`에 지식 부족 기록 생성
2. 관련 문서 요청을 `domain/knowledge-base/gaps.md`에 추가
3. 다음 개선 루프에서 Meta Agent가 처리

### MCP 도구 연동

도메인 MCP 서버(`servers/harness-mcp-server.py`)의 다음 도구를 활용:
- `search_knowledge` — 지식 기반 검색
- `check_rules` — 규칙 위반 검사
- `get_golden_example` — 골든 예제 조회
