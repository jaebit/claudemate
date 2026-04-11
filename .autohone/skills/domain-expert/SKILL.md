---
name: domain-expert
description: 도메인 지식이 필요한 태스크에서 knowledge-base 검색, 규칙 준수 확인, 골든 예제 참조를 수행합니다.
version: 1.2.0
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

### 지식 기반 구조

```
domain/knowledge-base/
├── AGENTS.md          # 전체 목차 (이것만 읽으면 됨)
├── architecture/      # 시스템 아키텍처 문서
├── api-specs/         # API 명세
├── coding-standards/  # 코딩 표준
└── business-rules/    # 비즈니스 규칙
```

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
