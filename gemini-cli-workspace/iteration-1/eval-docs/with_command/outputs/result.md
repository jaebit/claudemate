Loaded cached credentials.
I will start by locating the `search.md` file within the `plugins/gemini-cli/commands/` directory and then generate the requested documentation based on its contents and the surrounding project structure.

I will read the content of `plugins/gemini-cli/commands/search.md` to ensure I have the most accurate and up-to-date information before generating the documentation.

I will search for "gemini search" throughout the codebase to see if there is any other related code or logic that should be included in the documentation.

I will read `plugins/gemini-cli/.claude-plugin/plugin.json` to see if there's any additional information about the plugin and its commands.

I will read `plugins/gemini-cli/commands/ask.md` to see if there's a pattern in how commands are defined and if it provides any more context.

I'll read `plugins/gemini-cli/README.md` to see if it provides any further context for the `search` command and its related documentation.

Based on the `search.md` command definition, here is the comprehensive documentation for the **Gemini Search** command.

# Gemini Search Command Documentation

## 1. Overview and Purpose
The **Gemini Search** command (`/gemini:search`) integrates Google Search Grounding into the Gemini CLI environment. Its primary purpose is to allow users to perform real-time web searches directly from their command-line interface, leveraging Gemini's ability to synthesize information from multiple web sources while providing citations.

This command is particularly useful when:
*   Searching for up-to-date information (e.g., library release dates, recent tech news).
*   Researching documentation that may not be present in the local codebase.
*   Getting a quick summary of a complex topic with source verification.

## 2. Command Description
The command is implemented as a plugin-driven CLI action that invokes the `gemini` executable with specific grounding parameters.

### Input Parameters
*   **`<query>`** (String, Required): The search query or question you want to ask the web.
    *   *Type:* Positional argument.
    *   *Example:* `"jQuery 4 release date 2026"`

### Output Format
The command returns a formatted markdown response containing:
*   **Search Results Summary:** A synthesized answer based on the retrieved web content.
*   **Key Information:** Bulleted points highlighting the most critical facts.
*   **Source URLs List:** A list of verified links used to generate the answer for further verification.

## 3. Usage Examples

### Basic Web Search
```bash
/gemini:search latest React 19 features
```

### Specific Date or Version Queries
```bash
/gemini:search jQuery 4 release date 2026
```

### Tool or Documentation Search
```bash
/gemini:search Claude Code plugins documentation
```

## 4. Important Notes and Caveats

### API Quotas and Limits
*   **Free Tier Limit:** The Google Search Grounding feature is subject to a limit of **1,500 queries per day** on the free tier.
*   **Rate Limiting:** Frequent back-to-back searches may trigger rate limits depending on your Gemini API configuration.

### Best Practices
*   **Automatic Grounding:** Gemini automatically activates Search Grounding when it detects a query that requires real-time web access.
*   **Complex Research:** For deep-dive investigations requiring multi-step analysis across multiple files and web results, consider combining this command with a dedicated `/research` workflow if available.
*   **Verification:** While Search Grounding significantly reduces hallucinations, users should always verify critical information via the provided **Source URLs**.

### Requirements
*   **Gemini CLI:** Must be installed and authenticated (`gemini auth login`).
*   **Connectivity:** Requires an active internet connection to reach Google Search services.
