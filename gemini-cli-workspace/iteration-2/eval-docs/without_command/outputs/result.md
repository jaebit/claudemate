# Gemini Search Command Documentation

This document provides a comprehensive overview of the `search.md` command file located in the Gemini CLI plugin directory.

## 1. Overview and Purpose
The `search.md` file defines the **Gemini Search** command, which leverages Google Search Grounding to provide real-time web search capabilities within the Gemini CLI. Its primary purpose is to allow users to fetch up-to-date information from the internet, analyze it using the Large Language Model (LLM), and receive a cited response with source URLs.

## 2. Structure Description
The file follows a structured Markdown format with a YAML frontmatter section, organized as follows:

- **Frontmatter (Metadata):**
  - `description`: A brief summary of the command's function (Web search using Google Search Grounding).
  - `argument-hint`: Indicates that the command expects a `<query>` as an argument.
  - `allowed-tools`: Specifies that this command is permitted to use the `Bash` tool to execute system commands.
- **Heading (# Gemini Search):** The formal name of the command.
- **Instructions:** A three-step guide for the CLI agent on how to process the user's query. It highlights the use of the `gemini -p` flag to trigger a specific search prompt.
- **Output Format:** Defines the expected structure of the result, ensuring consistency (Summary, Key Information, and Source URLs).
- **Usage Examples:** Provides clear syntax examples for common search scenarios.
- **Notes:** Contains technical constraints, behavior details, and integration suggestions.

## 3. Configuration and Parameters
The command utilizes the following parameters and configurations:

- **Primary Argument:** `<user_query>` — The natural language question or keywords provided by the user.
- **Execution Tool:** `Bash` — Required to run the `gemini` CLI binary.
- **Prompt Template:** The command uses a predefined prompt string:
  ```text
  "Perform a web search for the following question and answer based on the search results.
  Always include source URLs.
  Question: <user_query>"
  ```

## 4. Usage Examples
Users can invoke this command through the Gemini CLI interface using the following syntax:

- **General Search:**
  ```bash
  /gemini:search jQuery 4 release date 2026
  ```
- **Feature Research:**
  ```bash
  /gemini:search latest React 19 features
  ```
- **Documentation Lookup:**
  ```bash
  /gemini:search Claude Code plugins documentation
  ```

## 5. Important Notes and Caveats
- **Automatic Grounding:** Gemini automatically enables "Search Grounding" when it detects a web search request in the prompt; no manual toggle is required within the command.
- **API Limits:** There is a daily limit of **1,500 queries** on the free tier. Users should monitor usage for high-volume tasks.
- **LLM Synthesis:** This command is not a "raw" search; it combines real-time data with LLM analysis to provide a coherent answer rather than just a list of links.
- **Workflow Integration:** For exhaustive investigations, it is recommended to use this in conjunction with a `/research` command if available.
