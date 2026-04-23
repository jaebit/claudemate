---
description: Generate commit message from staged changes using Gemini
argument-hint: ""
allowed-tools: ["Bash"]
---

# Gemini Commit

Generate a commit message from staged changes using Google Gemini CLI.

## Instructions

1. Check for staged changes using `git diff --cached`
2. If no staged changes, inform the user and exit
3. Get the list of changed files to detect scope:
```bash
git diff --cached --name-only
```
4. Run Gemini CLI to generate commit message:

```bash
git diff --cached | gemini -p "Write a concise commit message for these changes. Rules:
1. Use conventional commit format: type(scope): description
2. Types: feat, fix, docs, style, refactor, test, chore
3. Infer scope from the changed file paths (e.g., auth, api, ui, config)
4. Keep the first line under 72 characters - this is mandatory
5. Add bullet points for details only if there are multiple distinct changes
6. Output ONLY the commit message, no explanations"
```

5. Display the suggested commit message to the user

## Usage Examples

```
/gemini:commit
```

## Notes

- Stage your changes with `git add` before running this command
- Review the suggested message before committing

### If gemini fails

- Surface the error message to the user — do not silently continue or skip commit message generation.
- If the error is auth-related (401/403 or "not authenticated"), suggest running `gemini auth login` or setting the `GEMINI_API_KEY` environment variable.
