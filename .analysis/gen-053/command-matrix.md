# Gemini CLI Plugin Command Matrix

## Command Role Matrix

| Command | Purpose | Trigger Condition | Gemini CLI Usage | Key Features |
|---------|---------|-------------------|------------------|--------------|
| **ask** | General Q&A | Any question from user | `gemini -p "<question>"` | Context-aware prompting for project-related questions |
| **commit** | Git commit message generation | User runs `/gemini:commit` | `git diff --cached \| gemini -p "..."` | Conventional commit format, scope inference |
| **docs** | Code documentation generation | User provides file path | `cat <file> \| gemini -p "..."` | Language-aware prompts (Python, JS/TS, config) |
| **release** | Release notes generation | User provides git tag | `git log --oneline <tag>..HEAD \| gemini -p "..."` | Commit categorization, version milestone grouping |
| **review** | Code review and security audit | User requests code review | `git diff \| gemini -p "..."` | Severity-based issue reporting, security focus |
| **search** | Web search with grounding | User needs real-time information | `gemini -p "Perform web search..."` | Search Grounding integration, source attribution |

**Common Pattern**: All commands use `gemini -p` (non-interactive mode) with carefully crafted prompts. Context injection varies by command type:
- **ask**: Project context via `git log` and `pwd` for project-related questions
- **commit/review**: Git diff piping for change analysis  
- **docs**: File content streaming with language-specific documentation templates
- **release**: Git log ranges with commit categorization instructions
- **search**: Web search activation through prompt engineering

## Hook Architecture

**Hook Configuration** (`hooks.json`):
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command", 
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/session-init.mjs\""
          }
        ]
      }
    ]
  }
}
```

**Session Initialization Logic** (`session-init.mjs`):
- **Purpose**: Validate Gemini CLI installation and authentication at session start
- **Execution**: Node.js script that checks `gemini --version` with 5-second timeout
- **Success Path**: Returns `{"result": "continue"}` if Gemini CLI is accessible
- **Failure Path**: Returns warning message with installation instructions
  - Install command: `brew install google-gemini/tap/gemini-cli`
  - Authentication: `gemini auth login` 
  - User notification: "gemini:* commands will not work until installed"

**Hook Strategy**: Proactive dependency checking prevents runtime failures. The hook provides clear remediation steps rather than letting commands fail silently.

## Integration Points

**File Type Detection**: The docs command adapts prompts based on file extensions (.py, .js, .ts, .tsx, others)

**Git Integration**: Four commands (commit, release, review, ask) leverage git state:
- **commit**: Requires staged changes (`git diff --cached`)
- **review**: Falls back from staged to unstaged changes if needed
- **release**: Tag-based commit range calculation with fallback to full history
- **ask**: Project context injection for code-related queries

**Error Handling**: Commands validate preconditions (file existence, git repository, staged changes) before invoking Gemini CLI

**Plugin Ecosystem**: Follows standard claudemate plugin structure with `.claude-plugin/plugin.json`, `CLAUDE.md` constraints, and markdown-based command definitions