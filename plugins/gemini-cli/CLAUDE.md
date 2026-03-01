# Module Context

**Module:** Gemini CLI
**Version:** 1.0.0
**Role:** Google Gemini CLI integration for code review, commits, and documentation.

## Prerequisites

- Gemini CLI installed (`brew install google-gemini/tap/gemini-cli`)
- Authenticated via `gemini auth login`

---

# Operational Commands

```bash
# External CLI setup
brew install google-gemini/tap/gemini-cli
gemini auth login
gemini --version

# Plugin commands (in Claude Code)
/gemini:ask <question>       # Ask Gemini a question
/gemini:review [file]        # Code review (staged changes or file)
/gemini:commit               # Generate commit message
/gemini:docs <file>          # Generate documentation
/gemini:release [tag]        # Generate release notes
/gemini:search <query>       # Web search with Search Grounding
```

---

# Constraints

- **DO** verify Gemini CLI is installed before running commands.
- **DO** ensure `git add` is run before `/gemini:commit`.
- **DO** use `-p` flag for non-interactive prompt execution.
- **DON'T** assume Gemini CLI is available without checking.
- **DON'T** run `/gemini:commit` without staged changes.
- **DON'T** expose API keys or tokens in command output.
- **DON'T** use interactive Gemini CLI modes (always use `-p` flag).
