# Contract Criteria Validator 스킬

acceptance_criteria의 품질을 검증하고 Contract Validation 통과를 보장하는 전용 스킬입니다.

## Level 1: 기본 검증 패턴

### 주관적 기준 탐지
다음 패턴들을 탐지하여 객관적 기준으로 치환:

**금지 패턴**:
- "정확히 반영" → `grep 'target_content' file`
- "완전히 제거" → `grep -c 'removed_pattern' file = 0`
- "적절히 수정" → `diff before.txt after.txt | specific change`
- "올바르게 설정" → `config contains key=value`
- "제대로 구현" → `function exists AND tests pass`

### 검증 가능한 기준 생성
모든 acceptance_criteria는 다음 형태 중 하나여야 함:

1. **파일 존재**: `file path/to/file exists`
2. **Grep 매칭**: `grep -c 'pattern' file = N`
3. **함수/클래스 존재**: `function foo() defined in file`
4. **테스트 통과**: `pytest test_file.py::test_name PASSED`
5. **설정값 확인**: `config.yaml contains section.key=value`

## Level 2: 자동 치환 규칙

### 일반적 변환 패턴

```yaml
# Before: 주관적 기준
- description: "plugin.json의 description이 정확히 수정됨"

# After: 객관적 기준
- description: "plugin.json의 description이 codex CLI로 변경됨"
  verification: "grep 'codex CLI' plugin.json | wc -l = 1"
```

### 문서 수정 패턴
```yaml
# Before
- "README.md에서 섹션이 완전히 제거됨"

# After  
- "README.md에서 arix-dev 섹션이 제거됨"
  verification: "grep -c 'arix-dev' README.md = 0"
```

### 코드 변경 패턴
```yaml
# Before
- "중복 코드가 적절히 제거됨"

# After
- "isConfiguredProject 함수 중복이 제거됨" 
  verification: "grep -c 'function isConfiguredProject' src/ = 1"
```

## Level 3: 검증 명령어 라이브러리

### 파일 검증
- **존재**: `test -f path/to/file`
- **삭제**: `test ! -f path/to/file`
- **크기**: `wc -l file = N`
- **권한**: `test -x file`

### 내용 검증
- **포함**: `grep -q 'pattern' file`
- **개수**: `grep -c 'pattern' file = N`
- **정확 매칭**: `grep '^exact_line$' file`
- **제외**: `grep -v 'pattern' file | wc -l = N`

### 구조 검증
- **JSON 유효성**: `jq . file > /dev/null`
- **YAML 유효성**: `yaml-lint file`
- **함수 존재**: `grep 'function name(' file`
- **클래스 존재**: `grep 'class Name' file`

## Level 4: 컨텍스트별 최적화

### 설정 파일 검증
```bash
# plugin.json 필드 확인
jq '.description' plugin.json = '"codex CLI"'

# YAML 키 확인  
yq '.domain.name' config.yaml = "claudemate"
```

### 문서 검증
```bash
# 마크다운 섹션 확인
grep -c '^## Section Name' README.md = 1

# 링크 검증
grep -c '\[.*\](http.*)'  README.md = N
```

### 코드 검증
```bash
# 함수 시그니처
grep 'function name(args)' file.js

# 클래스 메서드
grep -A 5 'class Name' file.py | grep 'def method'

# 임포트 확인
grep 'import.*module' file
```

## 검증 프로세스

### 1단계: 주관적 기준 탐지
```javascript
const subjectivePatterns = [
  /정확히|완전히|적절히|올바르게|제대로/,
  /correctly|properly|accurately|completely/
];
```

### 2단계: 객관적 대안 제시
각 탐지된 패턴에 대해:
1. 구체적 변경 내용 식별
2. 검증 가능한 명령어 생성  
3. 이진 결과(true/false) 보장

### 3단계: 검증 명령어 테스트
제안된 명령어가 실제 동작하는지 확인:
```bash
# 명령어 구문 검증
bash -n verification_command

# 실행 가능성 검증
timeout 10 verification_command
```

## 안티패턴 방지

### ❌ 여전히 주관적인 경우
- "파일이 적절한 형태로 수정됨"
- "설정이 올바르게 반영됨" 
- "코드가 정확히 변경됨"

### ✅ 완전 객관적 변환
- "config.yaml에서 model: sonnet으로 설정됨"
- "grep -c 'codex-harness' . = 0 (전체 제거)"
- "함수 lineCount가 이전보다 13줄 감소함"

## 실제 사용 예시

```yaml
original_criteria:
  - "plugin.json이 정확히 수정되어 description이 반영됨"

validated_criteria:
  - description: "plugin.json의 description 필드가 codex CLI로 변경됨"
    verification: "jq -r '.description' plugin.json = 'codex CLI'"
  - description: "plugin.json에서 codex-harness 참조가 제거됨"
    verification: "grep -c 'codex-harness' plugin.json = 0"
```

이 스킬을 사용하여 모든 acceptance_criteria가 Contract Validation을 통과할 수 있도록 보장합니다.