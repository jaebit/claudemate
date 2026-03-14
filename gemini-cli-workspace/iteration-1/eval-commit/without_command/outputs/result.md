# Commit Message Generation (Without Command)

## Method
Used `gemini -p` (non-interactive/headless mode) with `git diff --cached` piped as stdin.

## Command
```bash
git diff --cached | gemini -p "다음 staged diff에 대한 커밋 메시지를 생성해줘. conventional commit 형식으로, 영어로 작성해줘. 커밋 메시지만 출력해줘, 다른 설명은 필요없어."
```

## Generated Commit Message
```
feat: add user authentication module with password hashing and login functionality
```

## Staged Changes Summary
- New file: `test_fixture.py` — a user authentication module with `hash_password()`, `verify_password()`, and `login()` functions.

## Notes
- Gemini CLI was invoked without any custom command/skill configuration.
- The `-p` flag runs gemini in non-interactive (headless) mode, which returns output directly to stdout.
- The diff was piped via stdin, and the prompt was passed as the `-p` argument.
- No commit was made; only the message was generated.
