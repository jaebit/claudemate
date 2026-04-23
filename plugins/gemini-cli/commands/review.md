---
description: Run code review using Gemini CLI
argument-hint: "[file or focus area]"
allowed-tools: ["Bash"]
---

# Gemini Review

Run code review using Google Gemini CLI in headless mode.

## Instructions

1. Check if arguments specify files or focus area
2. Run Gemini CLI review with the appropriate command:

If no arguments provided (review staged changes):
```bash
git diff --cached | gemini -p "Review this code diff for bugs, security vulnerabilities, and code quality issues. For each issue found: 1) State the severity (Critical/High/Medium/Low), 2) Reference the specific line number, 3) Explain the issue and its impact, 4) Provide a concrete fix recommendation. Focus especially on: SQL injection, XSS, insecure hashing, hardcoded secrets, race conditions, and error handling gaps."
```

If no staged changes, review unstaged changes:
```bash
git diff | gemini -p "Review this code diff for bugs, security vulnerabilities, and code quality issues. For each issue found: 1) State the severity (Critical/High/Medium/Low), 2) Reference the specific line number, 3) Explain the issue and its impact, 4) Provide a concrete fix recommendation. Focus especially on: SQL injection, XSS, insecure hashing, hardcoded secrets, race conditions, and error handling gaps."
```

If specific file provided, use the Read tool (preferred) to read the file content, then pipe it to gemini:
```bash
python3 -c "print(open('<file>').read())" | gemini -p "Review this code for bugs, security vulnerabilities, and code quality issues. For each issue found: 1) State the severity (Critical/High/Medium/Low), 2) Reference the specific line number, 3) Explain the issue and its impact, 4) Provide a concrete fix recommendation. Focus especially on: SQL injection, XSS, insecure hashing, hardcoded secrets, race conditions, and error handling gaps."
```

3. Display the review results to the user

## Usage Examples

```
/gemini:review
/gemini:review src/auth.py
/gemini:review api/routes.js
```

## Notes

- This command works best when run inside a git repository
- If no file is specified, it reviews git staged changes (or unstaged if none staged)

### If gemini fails

- Surface the error message to the user — do not silently continue or skip the review.
- If the error is auth-related (401/403 or "not authenticated"), suggest running `gemini auth login` or setting the `GEMINI_API_KEY` environment variable.
