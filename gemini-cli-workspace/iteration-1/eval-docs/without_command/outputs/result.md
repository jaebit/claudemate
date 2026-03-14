# Gemini Search Command Documentation

This documentation provides a comprehensive guide for the `gemini:search` command, a Claude Code plugin that integrates Google Search Grounding via the Gemini CLI.

## Overview
The `gemini:search` command allows users to perform real-time web searches directly from their development environment. By leveraging Google Search Grounding, it provides up-to-date information, factual answers, and verified source URLs, making it ideal for researching libraries, documentation, or technical news that may have emerged after the model's training cutoff.

## Usage Instructions
To use the search command, invoke it using the plugin prefix followed by your search query.

**Syntax:**
```bash
/gemini:search <query>
```

**Steps to use:**
1. Type `/gemini:search` in the Claude Code terminal.
2. Follow the command with the specific question or topic you want to search for.
3. Press Enter. The command will execute the search and return a grounded response.

## Parameter Descriptions

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `<query>` | String | **Required.** The search terms, question, or topic you want Gemini to investigate on the web. |

## How It Works Internally
The command acts as a wrapper for the Gemini CLI. When executed, it performs the following sequence:

1. **Argument Capture:** It retrieves the `<user_query>` provided by the user.
2. **CLI Invocation:** It executes a bash command that calls the `gemini` executable with a specific system prompt.
3. **Prompt Engineering:** The prompt is structured to force Gemini to:
    - Activate Search Grounding.
    - Synthesize an answer based *only* on the search results.
    - Explicitly list source URLs.
4. **Result Processing:** The output from the Gemini CLI is streamed or returned back to the Claude Code interface for the user to read.

**Internal Command Template:**
```bash
gemini -p "Perform a web search for the following question and answer based on the search results.
Always include source URLs.

Question: <user_query>"
```

## Examples and Expected Outputs

### Example 1: Checking for new releases
**Command:**
```bash
/gemini:search jQuery 4 release date 2026
```
**Expected Output:**
- **Summary:** Information regarding the current status of jQuery 4.0 as of early 2026.
- **Key Info:** Mention of the transition to ES modules, removal of deprecated APIs, and the official release or beta status.
- **Sources:** Links to `blog.jquery.com` or GitHub release pages.

### Example 2: Exploring features
**Command:**
```bash
/gemini:search latest React 19 features
```
**Expected Output:**
- **Summary:** A bulleted list of React 19 highlights (e.g., React Compiler, Actions, Document Metadata).
- **Key Info:** Brief explanation of how the new features improve performance or DX.
- **Sources:** Links to `react.dev` or official React blog posts.

## Limitations
- **Rate Limits:** The command is subject to the Gemini API free tier limit of **1,500 queries per day**.
- **Dependency:** Requires the `gemini` CLI to be installed and authenticated in the local environment's shell path.
- **Connectivity:** Requires an active internet connection to perform the grounding.
- **Scope:** While powerful for information retrieval, it is designed for discrete queries. For multi-step investigations, a dedicated research tool is recommended.

## Related Commands
- **/gemini:ask**: Used for general LLM queries where real-time web data is not strictly required.
- **/gemini:research**: (Recommended for complex tasks) Handles deeper, multi-query investigations.
- **/gemini:docs**: Specifically optimized for searching and summarizing project-related documentation.
