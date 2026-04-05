# Task Planner 스킬

사용자 요청을 구조화된 태스크 계획으로 변환하는 스킬입니다.

## Level 1: 태스크 계획 기본 구조

### 계획 요소
1. **목표 명확화**: 사용자 요청의 핵심 의도 파악
2. **스프린트 분할**: 논리적 단위로 작업 분할 (최대 5개)
3. **수용 기준**: 객관적이고 검증 가능한 완료 조건
4. **의존성 식별**: 스프린트 간 선후관계

### acceptance_criteria 품질 기준 (Contract Validation 통과)

**❌ 금지 사항 - 주관적 문구**:
- "정확히 반영", "완전히 제거", "적절히 수정"
- "올바르게 설정", "제대로 구현", "효과적으로 처리"

**✅ 필수 사항 - 객관적 기준**:
- 파일 존재 검증: `file X exists`
- Grep 패턴 검증: `grep -c 'pattern' file = N`
- 함수/클래스 존재: `function foo() defined in file`
- 설정값 확인: `config.yaml contains key=value`

### 올바른 acceptance_criteria 예시

```yaml
# ❌ 잘못된 예시
- description: "README.md에서 codex-harness 참조가 정확히 제거됨"

# ✅ 올바른 예시  
- description: "README.md에서 codex-harness 참조가 제거됨"
  verification: "grep -c 'codex-harness' README.md = 0"
```

## Level 2: 스프린트 설계 패턴

### 스프린트 분할 원칙
1. **단일 책임**: 각 스프린트는 하나의 명확한 목표
2. **독립성**: 가능한 한 다른 스프린트와 독립적 실행
3. **검증 가능**: 각 스프린트 완료 후 결과 검증 가능
4. **적정 크기**: 30분 내 완료 가능한 범위

### 의존성 관리
- **선형 의존성**: Sprint-1 → Sprint-2 → Sprint-3
- **병렬 가능**: 독립적 작업은 별도 스프린트로 분리
- **검증점**: 의존성 있는 스프린트 간 중간 검증

## Level 3: 계획 품질 검증

### 자체 검증 체크리스트
1. **모든 acceptance_criteria가 grep/파일존재 형태인가?**
2. **주관적 문구('정확히', '완전히') 사용하지 않았는가?**
3. **각 스프린트가 30분 내 완료 가능한가?**
4. **의존성이 명시적으로 표현되었는가?**

### Contract Validation 대비
- 계획 완성 후 acceptance_criteria 재검토 필수
- 주관적 기준 발견 시 즉시 객관적 대안으로 교체
- verification 필드에 구체적 명령어 제시

## Level 4: 고급 계획 기법

### 비기능 요구사항 체크리스트
- **성능**: 응답시간, 처리량 기준 명시
- **보안**: 인증, 권한, 입력 검증 요구사항
- **에러 처리**: 예외 상황 처리 방안
- **확장성**: 향후 변경사항 대응 고려

### 계획 최적화
- 중복 작업 제거
- 병렬 처리 가능한 작업 식별
- 리스크 높은 작업 우선 배치
- 피드백 루프 최소화

## 안티패턴

### ❌ 피해야 할 패턴
1. **모호한 완료 조건**: "적절히 구현"
2. **과도한 스프린트 분할**: 10분 작업을 별도 스프린트로
3. **숨겨진 의존성**: 명시되지 않은 스프린트 간 의존관계
4. **검증 불가능한 기준**: 주관적 판단 필요한 조건

### ✅ 권장 패턴
1. **구체적 완료 조건**: grep 명령어로 검증 가능
2. **적정 단위 분할**: 30분-1시간 단위 작업
3. **명시적 의존성**: 스프린트 간 관계 명확히 표시
4. **이진 검증**: true/false로 판단 가능한 기준

## 예시: 좋은 계획

```yaml
sprints:
  - id: "sprint-1" 
    goal: "plugin.json 수정"
    acceptance_criteria:
      - description: "description 필드가 codex CLI로 변경됨"
        verification: "grep 'codex CLI' plugin.json | wc -l = 1"
      - description: "codex-harness 참조가 제거됨"  
        verification: "grep -c 'codex-harness' plugin.json = 0"
```

이 스킬은 Contract Validation의 품질 기준을 만족하는 계획 수립을 보장합니다.