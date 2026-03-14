---
description: Generate release notes from git commits using Gemini
argument-hint: "<from-tag>"
allowed-tools: ["Bash"]
---

# Gemini Release

Generate release notes from git commits using Google Gemini CLI.

## Instructions

1. Get the tag from arguments
2. Determine the commit range:

If a tag is provided as argument:
```bash
git log --oneline <tag>..HEAD | gemini -p "Generate professional release notes from these commits. Group changes by category (Features, Bug Fixes, Improvements, Breaking Changes). Use markdown format with bullet points. Include a brief summary at the top. If commits follow conventional commit format, use the type prefixes to categorize accurately."
```

If no tag specified, try to find the most recent tag:
```bash
git describe --tags --abbrev=0 2>/dev/null
```

If a tag was found, use commits since that tag (same command as above with the discovered tag).

If no tags exist at all, use the full commit history (not just last 20) to generate comprehensive release notes:
```bash
git log --oneline | gemini -p "Generate professional release notes from these commits. Group changes by version milestones where version patterns are visible in commit messages. For each version group, categorize by: Features, Bug Fixes, Improvements, Breaking Changes. Use markdown format with bullet points. Include a brief summary at the top."
```

3. Display the release notes to the user

## Usage Examples

```
/gemini:release v1.0.0
/gemini:release v2.3.1
/gemini:release
```

## Notes

- Provide a git tag as the starting point for the release notes
- If no tag is specified, uses the most recent tag or full commit history
- This command requires a git repository with commit history
