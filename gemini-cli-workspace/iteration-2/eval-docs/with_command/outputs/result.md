# Gemini Search Command Documentation

## 1. Overview and Purpose
The **Gemini Search** command is a plugin utility designed for the Gemini CLI to perform real-time web searches using **Google Search Grounding**. Its primary purpose is to provide users with up-to-date information by bridging the gap between the LLM's training data cutoff and current web content. It synthesizes search results into a concise summary with verified source citations.

## 2. Structure Description
The file follows a structured metadata-heavy Markdown format used by Gemini CLI plugins:

*   **Frontmatter (YAML-like):**
    *   `description`: A brief summary of what the command does.
    *   `argument-hint`: A placeholder showing the expected input format (e.g., `<query>`).
    *   `allowed-tools`: Specifies that this command requires permission to use the `Bash` tool to execute the CLI.
*   **Instructions Section:** Defines the internal logic. It instructs the agent to wrap the user's query into a specific prompt that explicitly requests web searching and source URLs.
*   **Output Format Section:** Establishes a consistent response structure consisting of a summary, key findings, and a list of references.
*   **Usage Examples Section:** Provides concrete templates for how users can invoke the command.
*   **Notes Section:** Contains technical constraints, such as API limits and best-use scenarios.

## 3. Configuration & Parameters
This command relies on the following parameters:

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `user_query` | String (Required) | The natural language question or topic to search for. |
| `gemini -p` | Command Flag | Executes the search via the Gemini CLI's prompt interface. |

**Internal Configuration:**
- **Search Grounding:** Automatically triggered when the prompt explicitly asks for a web search.
- **Tools:** Requires `Bash` execution rights within the environment.

## 4. Usage Examples
Users can trigger the search functionality using the following syntax:

*   **Technology Updates:**
    ```bash
    /gemini:search jQuery 4 release date 2026
    ```
*   **Feature Discovery:**
    ```bash
    /gemini:search latest React 19 features
    ```
*   **Technical Documentation:**
    ```bash
    /gemini:search Claude Code plugins documentation
    ```

## 5. Important Notes & Caveats
*   **Rate Limits:** The command is subject to a free tier limit of **1,500 queries per day**.
*   **Real-time Dependency:** This command is most effective for information that changes frequently (e.g., software releases, news, API changes).
*   **Tool Execution:** Because it uses `Bash` to call the `gemini` executable, the environment must have the Gemini CLI properly installed and authenticated.
*   **Research Depth:** While excellent for quick queries, complex multi-step research may be better handled by combining this with a dedicated `/research` agent if available.
