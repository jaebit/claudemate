---
description: Ask Gemini a question using headless mode
argument-hint: "<question>"
allowed-tools: ["Bash"]
---

# Gemini Ask

Execute general queries using Google Gemini CLI in headless mode.

## Instructions

1. Get the user's question from the arguments
2. Check if the question relates to the current project by looking for code/project-related keywords
3. Run Gemini CLI:

For general questions:
```bash
gemini -p "<user_question>"
```

For project-related questions (when the question references files, code, or architecture), include project context:
```bash
gemini -p "Context: I am working in a project at $(pwd). Here is relevant context:
$(git log --oneline -5 2>/dev/null)

Question: <user_question>

Provide a practical, actionable answer."
```

4. Display the result to the user

## Usage Examples

```
/gemini:ask What is machine learning?
/gemini:ask Explain the difference between REST and GraphQL
/gemini:ask How does garbage collection work in Python?
```

## Notes

- For code review, use `/gemini:review`
- For commit message generation, use `/gemini:commit`
- For documentation generation, use `/gemini:docs`
