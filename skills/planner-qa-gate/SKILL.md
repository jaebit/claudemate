# Planner QA Gate 스킬

계획 수립 완료 후 자동 품질 검증을 수행하여 Contract Validation 실패를 사전 방지하는 스킬입니다.

## Level 1: 사전 품질 검증

### 핵심 검증 항목
1. **주관적 기준 탐지**: acceptance_criteria의 모호한 표현 식별
2. **검증 가능성 확인**: 각 기준이 명령어로 검증 가능한지 점검  
3. **의존성 유효성**: 스프린트 간 의존관계 논리적 일관성
4. **범위 적정성**: 각 스프린트가 30분 내 완료 가능한지 평가

### 자동 검증 프로세스
```
Plan Generated
      ↓
 QA Gate Check
      ↓
[PASS] → Execute
      ↓
[FAIL] → Auto-Fix → Re-validate
```

## Level 2: 주관적 기준 자동 탐지

### 탐지 패턴 (정규표현식)
```javascript
const subjectiveIndicators = [
  // 한국어 패턴
  /(정확히|완전히|적절히|올바르게|제대로|충분히)/,
  
  // 영어 패턴  
  /(correctly|properly|accurately|completely|adequately|appropriately)/,
  
  // 모호한 동작어
  /(반영|수정|변경|처리|구현|설정).*됨$/,
  
  // 정도 부사
  /(잘|좋게|효과적으로|성공적으로)/
];
```

### 자동 수정 제안
탐지된 주관적 기준을 즉시 객관적 대안으로 치환:

```yaml
# 원본 (주관적)
- "plugin.json이 정확히 수정됨"

# 자동 수정 제안 (객관적)  
- "plugin.json의 description 필드가 'codex CLI'로 설정됨"
  verification: "jq -r '.description' plugin.json = 'codex CLI'"
```

## Level 3: 검증 가능성 점수

### 점수 기준 (0-100점)
- **100점**: grep/jq/test 명령어 포함
- **80점**: 구체적 파일/함수명 언급
- **60점**: 명확한 변경 대상 지정
- **40점**: 일반적 설명이지만 측정 가능
- **20점**: 모호하지만 추론 가능
- **0점**: 완전히 주관적

### 통과 기준
- 모든 acceptance_criteria가 80점 이상
- 평균 점수 90점 이상
- 0점 기준 존재 시 즉시 실패

## Level 4: 의존성 검증

### 의존성 그래프 분석
```yaml
# 유효한 의존성
sprint-1: []
sprint-2: [sprint-1]  
sprint-3: [sprint-2]

# 무효한 의존성 (순환 참조)
sprint-1: [sprint-3]
sprint-2: [sprint-1]
sprint-3: [sprint-2]
```

### 논리적 일관성 검증
1. **순환 의존성**: DAG(Directed Acyclic Graph) 검증
2. **누락 의존성**: 파일 변경이 겹치는 스프린트 간 의존성 확인
3. **과도한 의존성**: 불필요한 순차 실행 제거

## Level 5: 범위 적정성 평가

### 스프린트 크기 추정
```javascript
const estimateComplexity = (sprint) => {
  const factors = {
    fileCount: sprint.files.length * 2,      // 파일 수 × 2분
    newFiles: sprint.newFiles.length * 5,    // 새 파일 × 5분  
    deletions: sprint.deletions.length * 3,  // 삭제 × 3분
    integration: sprint.hasIntegration ? 10 : 0  // 통합 작업 +10분
  };
  return Object.values(factors).reduce((a, b) => a + b, 0);
};
```

### 분할 제안
30분 초과 예상 스프린트는 자동 분할 제안:
```yaml
# 원본 (과도한 범위)
sprint-1:
  goal: "전체 플러그인 config 수정"
  files: [plugin.json, README.md, SKILL.md, meta.yaml]

# 분할 제안
sprint-1a:
  goal: "plugin.json 수정"  
  files: [plugin.json]
sprint-1b:
  goal: "문서 업데이트"
  files: [README.md, SKILL.md]
```

## 검증 실행 플로우

### 1단계: 기본 구조 검증
```javascript
const validateStructure = (plan) => {
  return {
    hasSprints: plan.sprints.length > 0,
    hasAcceptanceCriteria: plan.sprints.every(s => s.acceptance_criteria),
    hasValidIds: plan.sprints.every(s => s.id.match(/^sprint-\d+$/))
  };
};
```

### 2단계: 품질 점수 산출
```javascript
const calculateQualityScore = (criteria) => {
  const scores = criteria.map(c => assessObjectivity(c));
  return {
    average: scores.reduce((a, b) => a + b) / scores.length,
    minimum: Math.min(...scores),
    failing: scores.filter(s => s < 80).length
  };
};
```

### 3단계: 자동 수정 적용
통과하지 못한 기준에 대해:
1. 주관적 문구 식별
2. 컨텍스트 기반 객관적 대안 생성
3. verification 명령어 추가
4. 재검증 수행

## 실제 사용 시나리오

### 입력: 원본 계획
```yaml
acceptance_criteria:
  - "plugin.json이 적절히 수정됨"
  - "README 파일이 정확히 업데이트됨"
```

### QA Gate 처리 결과
```yaml
quality_issues:
  - criterion: "plugin.json이 적절히 수정됨"
    score: 20
    issue: "주관적 기준 '적절히'"
    suggestion: "plugin.json의 description이 'codex CLI'로 변경됨"
    
validation_passed: false
auto_fix_applied: true

improved_criteria:
  - description: "plugin.json의 description이 'codex CLI'로 변경됨"  
    verification: "jq -r '.description' plugin.json = 'codex CLI'"
  - description: "README.md에서 codex-harness 참조가 제거됨"
    verification: "grep -c 'codex-harness' README.md = 0"
```

## 통과/실패 기준

### 자동 통과 조건
- 모든 acceptance_criteria 품질 점수 ≥ 80
- 의존성 그래프가 DAG
- 모든 스프린트 예상 시간 ≤ 30분

### 수정 후 재검증 
- 자동 수정 적용 후 즉시 재검증
- 3회 수정 후에도 통과하지 못하면 인간 에스컬레이션

이 스킬을 통해 계획 품질을 사전에 보장하여 Contract Validation 실패를 방지할 수 있습니다.