---
description: Generate documentation for code using Gemini
argument-hint: "<file>"
allowed-tools: ["Bash"]
---

# Gemini Docs

Generate comprehensive documentation for code using Google Gemini CLI.

## Instructions

1. Get the file path from arguments
2. If no file specified, inform the user and exit
3. Detect file type from extension to tailor the documentation prompt
4. Run Gemini CLI to generate documentation:

For Python files (.py), use the Read tool (preferred) to read the file, then pipe content to gemini:
```bash
python3 -c 'import sys; sys.stdout.buffer.write(open(sys.argv[1], "rb").read())' "<file>" | gemini -p "Generate comprehensive documentation for this Python code. Include: 1) Module overview and purpose, 2) Each class with its methods, parameters, return types, and behavior, 3) Each standalone function with parameters, return values, and edge cases, 4) Usage examples with expected output, 5) Dependencies and important notes. Use markdown format with proper code blocks."
```

For JavaScript/TypeScript files (.js, .ts, .tsx), use the Read tool (preferred) to read the file, then pipe content to gemini:
```bash
python3 -c 'import sys; sys.stdout.buffer.write(open(sys.argv[1], "rb").read())' "<file>" | gemini -p "Generate comprehensive documentation for this JavaScript/TypeScript code. Include: 1) Module overview and exports, 2) Each function/component with props/parameters, return values, and types, 3) Usage examples, 4) Dependencies and important notes. Use markdown format with proper code blocks."
```

For config/markdown/other files, use the Read tool (preferred) to read the file, then pipe content to gemini:
```bash
python3 -c 'import sys; sys.stdout.buffer.write(open(sys.argv[1], "rb").read())' "<file>" | gemini -p "Generate comprehensive documentation for this file. Include: 1) Overview and purpose, 2) Structure description with each section explained, 3) Configuration options or parameters if applicable, 4) Usage examples, 5) Important notes or caveats. Use markdown format."
```

5. Display the generated documentation to the user

## Usage Examples

```
/gemini:docs src/utils.py
/gemini:docs api/routes.js
/gemini:docs lib/auth.ts
```

## Notes

- Provide a valid file path as argument
- The output is in markdown format for easy integration

### If gemini fails

- Surface the error message to the user — do not silently continue or skip documentation generation.
- If the error is auth-related (401/403 or "not authenticated"), suggest running `gemini auth login` or setting the `GEMINI_API_KEY` environment variable.
