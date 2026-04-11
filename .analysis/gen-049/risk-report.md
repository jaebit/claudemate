# Claudemate Plugin Ecosystem Risk Analysis Report

**Generation**: gen-049  
**Sprint**: 2  
**Analysis Date**: 2026-04-11  
**Scope**: 7 plugins dependency analysis and risk assessment

## 1. 공유 리소스 맵 (_shared 분석)

### 공유 리소스 보유 플러그인 (3/7)

| Plugin | _shared 리소스 수 | 주요 카테고리 |
|--------|------------------|---------------|
| **crew** | 23개 파일 + 3개 디렉토리 | 에이전트 오케스트레이션, 병렬 실행, Serena 통합 템플릿 |
| **autopilot** | 1개 파일 | 페이즈 아티팩트 정의 |
| **arch-guard** | 2개 파일 | 프로젝트 감지, 설정 로드 스크립트 |

### _shared 미보유 플러그인 (4/7)
- codex-cli, gemini-cli, multi-model-debate, worktree

### 공유 리소스 의존성 패턴
- **crew**: 가장 광범위한 공유 리소스 (전사 에이전트 프로토콜, 템플릿, 스키마)
- **autopilot**: crew 플러그인에 의존적 (phase-artifacts.md만 보유)
- **arch-guard**: 독립적 유틸리티 스크립트 (detect-project.mjs, load-config.mjs)

## 2. 리스크 목록

### [P0] 즉시 해결 필요

#### R001: plugin.json 전면 누락 위험
- **영향도**: Critical
- **범위**: 전체 7개 플러그인
- **증상**: marketplace 연동 불가, 자동 디스커버리 실패
- **결과**: 플러그인 시스템 전면 마비 가능성

#### R002: 테스트 커버리지 편중
- **영향도**: Critical  
- **범위**: crew 외 6개 플러그인
- **증상**: tests/ 디렉토리 없음 (crew만 보유)
- **결과**: 품질 보증 불가, 회귀 오류 감지 실패

### [P1] 단기 개선 권고

#### R003: 공유 리소스 표준화 부재
- **영향도**: Important
- **범위**: _shared/ 보유 3개 플러그인
- **증상**: 파일 구조, 명명 규칙 불일치
- **결과**: 재사용성 저하, 유지보수 복잡도 증가

#### R004: hooks 구현 수준 격차
- **영향도**: Important
- **범위**: hooks 보유 5개 플러그인
- **증상**: crew (복잡), 나머지 (단순) 이원화
- **결과**: 행동 일관성 부족, 디버깅 복잡성

### [P2] 장기 검토

#### R005: 스킬 중심 아키텍처 의존성
- **영향도**: Minor
- **범위**: 5개 플러그인 (skills-driven 패턴)
- **증상**: commands 대신 skills 위주 설계
- **결과**: 복잡성 증가, 학습 곡선 상승

#### R006: 프로그래밍 언어 혼재
- **영향도**: Minor
- **범위**: hooks 스크립트
- **증상**: Python (crew, insight-collector) vs Node.js (나머지)
- **결과**: 런타임 의존성 복잡화

## 3. 의존성 그래프 요약

### 직접 의존성
```
autopilot → crew (prerequisite)
crew → insight-collector (skill 내장)
arch-guard → [독립적]
나머지 4개 → [독립적]
```

### 공유 리소스 의존성
- **crew._shared**: 23개 파일 → 다른 플러그인에서 참조 가능성
- **autopilot._shared**: phase-artifacts.md → crew와 협력 시 사용
- **arch-guard._shared**: 유틸리티 스크립트 → 재사용 잠재력

### hooks 이벤트 충돌 가능성
- **SessionStart**: 4개 플러그인 (crew, gemini-cli, autopilot, arch-guard)
- **PreToolUse**: 2개 플러그인 (crew, arch-guard) → Edit/Write 매처 중복
- **Stop**: 2개 플러그인 (crew, arch-guard)

## 4. 개선 우선순위 로드맵

### Phase 1: P0 리스크 해결 (즉시 착수)

1. **plugin.json 전면 보충**
   - 각 플러그인별 필수 필드 (name, version, description, mcpServers) 생성
   - marketplace.json 동기화
   - 스키마 검증 통과 확인

2. **테스트 인프라 구축**
   - crew 외 6개 플러그인에 tests/ 디렉토리 생성
   - 기본 smoke test 스위트 구현
   - CI/CD 파이프라인 통합

### Phase 2: P1 리스크 개선 (1-2주 내)

1. **공유 리소스 표준화**
   - _shared/ 구조 가이드라인 정립
   - 파일 명명 규칙 통일
   - 크로스 레퍼런스 문서화

2. **hooks 거버넌스**
   - 이벤트 매처 충돌 해결 프로토콜
   - hooks.json 스키마 표준화
   - 실행 순서 및 타임아웃 정책

### Phase 3: P2 리스크 검토 (장기)

1. **아키텍처 일관성**
   - skills vs commands 패턴 가이드라인
   - 복잡도에 따른 플러그인 설계 원칙

2. **런타임 통일성**
   - hooks 스크립트 언어 표준화 검토
   - 공통 유틸리티 라이브러리 개발

## 결론

marketplace 연동을 위한 plugin.json 누락이 가장 심각한 위험 요소이며, 즉시 해결이 필요합니다. 테스트 커버리지 부족 또한 품질 보증 관점에서 critical risk입니다. 공유 리소스와 hooks 구조의 표준화를 통해 생태계의 일관성과 유지보수성을 향상시킬 수 있습니다.