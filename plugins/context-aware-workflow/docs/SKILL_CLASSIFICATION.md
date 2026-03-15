# Skill Classification

스킬을 두 가지 유형으로 분류하여 검증 전략과 유지보수 우선순위를 결정한다.

## 분류 기준

| 유형 | 목적 | 모델 업그레이드 영향 | 핵심 검증 |
|------|------|---------------------|----------|
| **Encoded Preference** | 나만의 워크플로우와 톤앤매너 강제 | 없음 | eval 테스트 |
| **Capability** | AI가 원래 못하는 영역 보강 | 매우 취약 (불필요한 족쇄가 됨) | A/B 테스트 |

---

## Encoded Preference (4개)

모델이 아무리 똑똑해져도 사용자가 원하는 방식을 알 수 없다. 모델 업그레이드와 무관하게 유지된다.

| 스킬 | 근거 |
|------|------|
| **commit-discipline** | Kent Beck의 Tidy First 규칙 강제. structural/behavioral 커밋 분리는 사용자 고유 방법론 |
| **plan-detector** | Plan Mode 완료 → CAW 워크플로우 전환이라는 특정 handoff 규칙 |
| **plugin-authoring** | 에이전트/스킬 파일의 frontmatter 형식, 네이밍 컨벤션, 티어 구조 |
| **quality-gate** | 어떤 체크를 required/warning으로 분류하고, coverage 80%, Tidy First 강제 등 사용자 정의 품질 기준 |

## Capability (7개)

AI의 구조적 한계를 보완한다. 모델이 해당 한계를 극복하면 불필요한 족쇄가 된다.

| 스킬 | 보완하는 한계 | 불필요해지는 시점 |
|------|-------------|-----------------|
| **context-manager** | 컨텍스트 윈도우 크기 제한 | 무한/충분한 컨텍스트 |
| **session-manager** | 세션간 상태 소실 | 네이티브 세션 영속성 |
| **progress-tracker** | 다단계 작업 상태 추적 불가 | 네이티브 상태 관리 |
| **insight-collector** | 세션간 학습/패턴 기억 불가 | 네이티브 크로스-세션 학습 |
| **learning-loop** | 지속적 학습, 인스팅트 진화 불가 | 네이티브 자기 개선 |
| **pattern-learner** | 코드베이스 패턴 체계적 분석/기억 불가 | 네이티브 코드 이해력 향상 |
| **knowledge-engine** | 프로젝트 지식/결정 영속 저장 불가 | 네이티브 장기 기억 |

---

## A/B 테스트 결과: knowledge-engine

> 테스트 일자: 2026-03-15 | 결과 상세: `skills/knowledge-engine-workspace/iteration-1/`

### 실험 설계

3개 테스트 (ADR 기록, 지식 분류, 리뷰 체크리스트) × 2 조건 (with/without skill) = 6 runs.
15개 assertion으로 정량 채점. 사용자 정성 평가 병행.

### 결과

| 지표 | with_skill | without_skill | 차이 |
|------|-----------|---------------|------|
| Assertion 통과율 | 15/15 (100%) | 12/15 (80%) | +20% |
| 평균 토큰 | 27,129 | 25,953 | +4.5% |
| 평균 소요시간 | 82초 | 63초 | +29.9% |
| 사용자 정성 평가 | great | great | 동일 |

### 실패 패턴

without_skill이 실패한 3개 assertion은 **모두 인프라 계층**:

| Assertion | 유형 | 설명 |
|-----------|------|------|
| A5 | 디렉토리 구조 | ADR 인덱스 파일 미생성 |
| B4 | 인덱스 파일 | 지식 항목 index.json 미생성 |
| B5 | 태그 시스템 | 교차 검색용 태그 미부여 |

**콘텐츠 계층은 차이 없음**: 모델이 자발적으로 Michael Nygard ADR 형식 채택, 5개 카테고리 정확 분류, 37개 항목 체크리스트 생성 (스킬 버전보다 11개 더 많음).

### 판정

```
콘텐츠 생성 능력: 스킬 불필요 (모델이 네이티브로 동등 품질 생산)
검색 인프라 가치: 프로젝트 규모 의존적
  - 소규모: 29.9% 시간 오버헤드 > 인프라 가치 → 불필요
  - 대규모/장기: .caw/ 지식 축적 시 검색성이 핵심 → 유지
```

Capability 분류 확정. 모델 업그레이드로 인프라 관리까지 네이티브화되면 완전히 불필요해질 첫 번째 후보.

---

## 경계선 케이스

**knowledge-engine**: A/B 테스트로 확인. 콘텐츠 품질은 스킬 없이도 동등하나, 검색 인프라(index, 태그, 디렉토리 규약)에서 차이 발생. Capability 확정.

## 비율

```
Encoded Preference : Capability = 4 : 7
```
