#!/usr/bin/env python3
"""
Tests for validating the context-aware-workflow plugin structure (v3.0).

Validates:
- plugin.json schema and required fields
- hooks.json schema and hook definitions
- Agent and skill file structure
- Required files existence
"""

import json
import os
import re
import unittest
from pathlib import Path

# Plugin root directory
PLUGIN_ROOT = Path(__file__).parent.parent


class TestPluginStructure(unittest.TestCase):
    """Test plugin directory structure and required files."""

    def test_plugin_json_exists(self):
        """plugin.json must exist in .claude-plugin directory."""
        plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        self.assertTrue(plugin_json.exists(), "plugin.json not found")

    def test_plugin_json_valid(self):
        """plugin.json must be valid JSON with required fields."""
        plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        with open(plugin_json, "r") as f:
            data = json.load(f)

        # Required fields
        self.assertIn("name", data, "plugin.json missing 'name'")
        self.assertIn("version", data, "plugin.json missing 'version'")
        self.assertIn("description", data, "plugin.json missing 'description'")

        # Validate name format
        self.assertRegex(
            data["name"],
            r"^[a-z][a-z0-9-]*$",
            "Plugin name must be lowercase with hyphens",
        )

        # Validate version format (semver)
        self.assertRegex(
            data["version"], r"^\d+\.\d+\.\d+", "Version must follow semver format"
        )

    def test_plugin_json_allowed_fields_only(self):
        """plugin.json must only contain allowed fields."""
        plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        with open(plugin_json, "r") as f:
            data = json.load(f)

        allowed_fields = {"name", "version", "description", "mcpServers"}
        for key in data.keys():
            self.assertIn(
                key, allowed_fields, f"plugin.json has disallowed field: {key}"
            )

    def test_hooks_json_exists(self):
        """hooks.json must exist in hooks directory."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        self.assertTrue(hooks_json.exists(), "hooks.json not found")

    def test_hooks_json_valid_schema(self):
        """hooks.json must have valid Claude Code hooks schema."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        with open(hooks_json, "r") as f:
            data = json.load(f)

        # Must have 'hooks' key at root
        self.assertIn("hooks", data, "hooks.json must have 'hooks' key at root")
        self.assertIsInstance(data["hooks"], dict, "'hooks' must be an object")

        # Valid hook event names (Claude Code supported events)
        valid_events = {
            "SessionStart",
            "SessionEnd",
            "PreToolUse",
            "PostToolUse",
            "Notification",
            "Stop",
            "SubagentStop",
            "WorktreeCreate",
            "WorktreeRemove",
            "TeammateIdle",
            "TaskCompleted",
        }

        for event_name in data["hooks"].keys():
            self.assertIn(
                event_name, valid_events, f"Invalid hook event: {event_name}"
            )

            # Each event must be an array
            self.assertIsInstance(
                data["hooks"][event_name], list, f"{event_name} must be an array"
            )

            # Each item must have 'hooks' array
            for item in data["hooks"][event_name]:
                self.assertIn(
                    "hooks", item, f"{event_name} items must have 'hooks' array"
                )
                self.assertIsInstance(
                    item["hooks"], list, f"{event_name} hooks must be an array"
                )

    def test_required_directories_exist(self):
        """Required plugin directories must exist."""
        required_dirs = ["agents", "hooks", "_shared", "skills"]

        for dir_name in required_dirs:
            dir_path = PLUGIN_ROOT / dir_name
            self.assertTrue(dir_path.is_dir(), f"Directory '{dir_name}' not found")

    def test_readme_exists(self):
        """README.md must exist in plugin root."""
        readme = PLUGIN_ROOT / "README.md"
        self.assertTrue(readme.exists(), "README.md not found")


class TestAgentFiles(unittest.TestCase):
    """Test agent file structure and frontmatter."""

    def get_agent_files(self):
        """Get all agent markdown files."""
        agents_dir = PLUGIN_ROOT / "agents"
        return list(agents_dir.glob("*.md"))

    def test_agents_exist(self):
        """At least one agent file must exist."""
        agents = self.get_agent_files()
        self.assertGreater(len(agents), 0, "No agent files found")

    def test_agent_frontmatter(self):
        """Each agent must have valid YAML frontmatter."""
        for agent_file in self.get_agent_files():
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Must start with ---
            self.assertTrue(
                content.startswith("---"),
                f"{agent_file.name} must start with YAML frontmatter",
            )

            # Must have closing ---
            parts = content.split("---", 2)
            self.assertGreaterEqual(
                len(parts), 3, f"{agent_file.name} must have closing ---"
            )

            # Frontmatter must contain required fields
            frontmatter = parts[1]
            self.assertIn(
                "name:", frontmatter, f"{agent_file.name} missing 'name' in frontmatter"
            )
            self.assertIn(
                "description:",
                frontmatter,
                f"{agent_file.name} missing 'description' in frontmatter",
            )

    def test_agent_has_system_prompt(self):
        """Each agent must have a system prompt section."""
        for agent_file in self.get_agent_files():
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(
                "# " in content,
                f"{agent_file.name} must have markdown headings for system prompt",
            )

    def test_no_tier_variant_agents(self):
        """No model tier variant agents should exist (removed in v3.0)."""
        agents_dir = PLUGIN_ROOT / "agents"
        tier_suffixes = ["-haiku.md", "-sonnet.md", "-opus.md"]
        for suffix in tier_suffixes:
            tier_files = list(agents_dir.glob(f"*{suffix}"))
            self.assertEqual(
                len(tier_files), 0,
                f"Tier variant agents should not exist in v3.0: {[f.name for f in tier_files]}"
            )

    def test_agent_count(self):
        """v3.0 should have exactly 8 agents."""
        agents = self.get_agent_files()
        self.assertEqual(len(agents), 8, f"Expected 8 agents, found {len(agents)}: {[a.name for a in agents]}")




class TestRequiredAgents(unittest.TestCase):
    """Test that required v3.0 agents are present."""

    REQUIRED_AGENTS = [
        "planner", "builder", "reviewer", "fixer",
        "analyst", "architect", "bootstrapper", "compliance-checker",
    ]

    def test_required_agents_exist(self):
        """All 8 required agents must exist."""
        agents_dir = PLUGIN_ROOT / "agents"
        for agent_name in self.REQUIRED_AGENTS:
            agent_file = agents_dir / f"{agent_name}.md"
            self.assertTrue(agent_file.exists(), f"{agent_name}.md agent not found")

    def test_removed_agents_absent(self):
        """Agents removed in v3.0 should not exist."""
        agents_dir = PLUGIN_ROOT / "agents"
        removed = ["ideator.md", "designer.md"]
        for name in removed:
            self.assertFalse(
                (agents_dir / name).exists(),
                f"{name} should have been removed in v3.0"
            )




class TestSkillFiles(unittest.TestCase):
    """Test skill file structure and SKILL.md files."""

    def get_skill_dirs(self):
        """Get all skill directories."""
        skills_dir = PLUGIN_ROOT / "skills"
        if not skills_dir.exists():
            return []
        return [d for d in skills_dir.iterdir() if d.is_dir()]

    def test_skills_directory_exists(self):
        """skills/ directory must exist."""
        skills_dir = PLUGIN_ROOT / "skills"
        self.assertTrue(skills_dir.is_dir(), "skills/ directory not found")

    def test_skills_exist(self):
        """At least one skill must exist."""
        skills = self.get_skill_dirs()
        self.assertGreater(len(skills), 0, "No skill directories found")

    def test_skill_has_skill_md(self):
        """Each skill directory must have a SKILL.md file."""
        for skill_dir in self.get_skill_dirs():
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(
                skill_md.exists(),
                f"{skill_dir.name} missing SKILL.md",
            )

    def test_skill_frontmatter(self):
        """Each SKILL.md must have valid YAML frontmatter with name and description."""
        for skill_dir in self.get_skill_dirs():
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()

            # Must start with ---
            self.assertTrue(
                content.startswith("---"),
                f"{skill_dir.name}/SKILL.md must start with YAML frontmatter",
            )

            # Must have closing ---
            parts = content.split("---", 2)
            self.assertGreaterEqual(
                len(parts), 3, f"{skill_dir.name}/SKILL.md must have closing ---"
            )

            # Frontmatter must contain required fields
            frontmatter = parts[1]
            self.assertIn(
                "name:", frontmatter, f"{skill_dir.name}/SKILL.md missing 'name'"
            )
            self.assertIn(
                "description:",
                frontmatter,
                f"{skill_dir.name}/SKILL.md missing 'description'",
            )

    def test_skill_count(self):
        """v4.0 should have exactly 16 skills."""
        skills = self.get_skill_dirs()
        self.assertEqual(len(skills), 16, f"Expected 16 skills, found {len(skills)}: {[s.name for s in skills]}")


class TestRequiredSkills(unittest.TestCase):
    """Test that required v3.0 skills are present."""

    REQUIRED_SKILLS = [
        "progress-tracker", "plan-detector",
        "quality-gate", "commit-discipline", "insight-collector",
        "pattern-learner",
        "knowledge-engine", "session-manager", "learning-loop",
        "structured-research",
        "go", "status", "review", "parallel", "explore", "manage",
    ]

    def test_required_skills_exist(self):
        """All 10 required skills must exist."""
        for skill_name in self.REQUIRED_SKILLS:
            skill = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
            self.assertTrue(skill.exists(), f"{skill_name}/SKILL.md not found")

    def test_removed_skills_absent(self):
        """Skills removed/merged in v3.0 should not exist."""
        removed = [
            "knowledge-base", "decision-logger", "review-assistant",
            "session-persister", "context-helper", "hud", "dashboard",
            "reflect", "evolve", "research", "serena-sync",
            "quick-fix", "dependency-analyzer",
        ]
        for skill_name in removed:
            skill_dir = PLUGIN_ROOT / "skills" / skill_name
            self.assertFalse(
                skill_dir.exists(),
                f"{skill_name} should have been removed/merged in v3.0"
            )


class TestRalphLoopIntegration(unittest.TestCase):
    """Test Ralph Loop continuous improvement integration."""

    def test_learnings_template_exists(self):
        """Learnings template must exist."""
        template = PLUGIN_ROOT / "_shared" / "learnings-template.md"
        self.assertTrue(template.exists(), "learnings-template.md not found")

    def test_magic_keywords_doc_exists(self):
        """Magic keywords documentation must exist."""
        doc = PLUGIN_ROOT / "_shared" / "magic-keywords.md"
        self.assertTrue(doc.exists(), "magic-keywords.md not found")


class TestComplexityHints(unittest.TestCase):
    """Test complexity-adaptive system (replaces model routing in v3.0)."""

    def test_complexity_hints_exists(self):
        """complexity-hints.md must exist (replaces model-routing.md)."""
        hints = PLUGIN_ROOT / "_shared" / "complexity-hints.md"
        self.assertTrue(hints.exists(), "complexity-hints.md not found")

    def test_model_routing_removed(self):
        """model-routing.md should not exist in v3.0."""
        routing = PLUGIN_ROOT / "_shared" / "model-routing.md"
        self.assertFalse(routing.exists(), "model-routing.md should have been removed in v3.0")

    def test_model_routing_schema_removed(self):
        """model-routing.schema.json should not exist in v3.0."""
        schema1 = PLUGIN_ROOT / "schemas" / "model-routing.schema.json"
        schema2 = PLUGIN_ROOT / "_shared" / "schemas" / "model-routing.schema.json"
        self.assertFalse(schema1.exists(), "schemas/model-routing.schema.json should be removed")
        self.assertFalse(schema2.exists(), "_shared/schemas/model-routing.schema.json should be removed")


class TestHooksConfiguration(unittest.TestCase):
    """Test hooks configuration details."""

    def setUp(self):
        """Load hooks.json."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        with open(hooks_json, "r") as f:
            self.hooks_data = json.load(f)

    def test_required_hooks_exist(self):
        """Required hooks must be configured."""
        self.assertIn("PreToolUse", self.hooks_data["hooks"])
        self.assertIn("PostToolUse", self.hooks_data["hooks"])

    def test_hook_types_valid(self):
        """All hooks must have valid type field."""
        valid_types = {"prompt", "command"}

        for event_name, event_hooks in self.hooks_data["hooks"].items():
            for hook_group in event_hooks:
                for hook in hook_group["hooks"]:
                    self.assertIn("type", hook, f"{event_name} hook missing 'type'")
                    self.assertIn(
                        hook["type"],
                        valid_types,
                        f"{event_name} has invalid hook type: {hook['type']}",
                    )

    def test_hooks_have_matchers_where_needed(self):
        """PostToolUse hooks should have matchers for tool filtering."""
        post_hooks = self.hooks_data["hooks"].get("PostToolUse", [])
        for hook_group in post_hooks:
            self.assertIn(
                "matcher",
                hook_group,
                "PostToolUse hooks should have matcher for tool filtering",
            )


class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility patterns."""

    def setUp(self):
        """Load hooks.json."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        with open(hooks_json, "r") as f:
            self.hooks_data = json.load(f)
            self.hooks_content = hooks_json.read_text()

    def test_no_single_quote_echo_in_hooks(self):
        """Hooks should not use echo with single quotes (Windows incompatible)."""
        self.assertNotIn(
            "echo '",
            self.hooks_content,
            "Single quote echo found - use 'type: prompt' instead for Windows compatibility"
        )

    def test_pretooluse_uses_claude_plugin_root_pattern(self):
        """PreToolUse hooks using paths should use ${CLAUDE_PLUGIN_ROOT} pattern."""
        pre_tool_hooks = self.hooks_data["hooks"].get("PreToolUse", [])
        for hook_group in pre_tool_hooks:
            for hook in hook_group.get("hooks", []):
                if hook.get("type") == "command":
                    cmd = hook.get("command", "")
                    if "CLAUDE_PLUGIN_ROOT" in cmd:
                        self.assertIn(
                            "${CLAUDE_PLUGIN_ROOT}",
                            cmd,
                            "Plugin paths should use ${CLAUDE_PLUGIN_ROOT} (with curly braces)"
                        )

    def test_no_bare_shell_variable_in_path(self):
        """Hook commands should use ${VAR} pattern, not $VAR without braces."""
        for event_name, event_hooks in self.hooks_data["hooks"].items():
            for hook_group in event_hooks:
                for hook in hook_group.get("hooks", []):
                    if hook.get("type") == "command":
                        cmd = hook.get("command", "")
                        bare_var_match = re.search(r'\$CLAUDE_PLUGIN_ROOT(?!\})', cmd)
                        if bare_var_match and "${CLAUDE_PLUGIN_ROOT}" not in cmd:
                            self.fail(
                                f"{event_name} hook uses bare $CLAUDE_PLUGIN_ROOT - "
                                "use ${{CLAUDE_PLUGIN_ROOT}} for Claude Code substitution"
                            )


class TestSkillFrontmatterFields(unittest.TestCase):
    """Test that SKILL.md frontmatter only uses recognized fields."""

    RECOGNIZED_FIELDS = {"name", "description", "allowed-tools", "context", "disable-model-invocation", "user-invocable", "agent", "argument-hint"}

    def get_skill_frontmatters(self):
        """Parse frontmatter from all SKILL.md files."""
        skills_dir = PLUGIN_ROOT / "skills"
        results = []
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                fields = set()
                for line in frontmatter.splitlines():
                    if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
                        key = line.split(":", 1)[0].strip()
                        if key:
                            fields.add(key)
                results.append((skill_dir.name, fields, frontmatter))
        return results

    def test_no_non_standard_frontmatter_fields(self):
        """SKILL.md frontmatter should only use recognized fields."""
        for skill_name, fields, _ in self.get_skill_frontmatters():
            non_standard = fields - self.RECOGNIZED_FIELDS
            self.assertEqual(
                non_standard, set(),
                f"{skill_name}/SKILL.md has non-standard frontmatter fields: {non_standard}"
            )

    def test_forked_context_uses_correct_syntax(self):
        """Skills should use 'context: fork', not 'forked-context: true'."""
        for skill_name, fields, frontmatter in self.get_skill_frontmatters():
            self.assertNotIn(
                "forked-context",
                fields,
                f"{skill_name}/SKILL.md uses 'forked-context' instead of 'context: fork'"
            )
            self.assertNotIn(
                "forked-context-returns",
                fields,
                f"{skill_name}/SKILL.md has 'forked-context-returns' in frontmatter (move to body)"
            )


class TestSkillStaleReferences(unittest.TestCase):
    """Test that SKILL.md files don't reference removed commands or skills."""

    REMOVED_COMMANDS = [
        "/crew:start", "/crew:next", "/crew:design", "/crew:tidy",
        "/crew:evolve", "/crew:reflect", "/crew:init",
    ]
    REMOVED_SKILLS = [
        "review-assistant", "context-helper", "session-persister",
        "knowledge-base", "decision-logger", "hud", "dashboard",
    ]

    def get_skill_contents(self):
        """Read all SKILL.md file contents."""
        skills_dir = PLUGIN_ROOT / "skills"
        results = []
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")
                results.append((skill_dir.name, content))
        return results

    def test_no_removed_command_references(self):
        """SKILL.md files should not reference removed commands."""
        for skill_name, content in self.get_skill_contents():
            for cmd in self.REMOVED_COMMANDS:
                # Match exact command (e.g., /crew:start but not /crew:status)
                pattern = re.escape(cmd) + r'(?:\s|`|$|"|\))'
                match = re.search(pattern, content)
                self.assertIsNone(
                    match,
                    f"{skill_name}/SKILL.md references removed command '{cmd}'"
                )

    def test_no_removed_skill_references(self):
        """SKILL.md files should not reference removed/merged skills by name."""
        for skill_name, content in self.get_skill_contents():
            for removed in self.REMOVED_SKILLS:
                # Skip if the reference is about the removal itself
                # Look for references like "review-assistant" as a skill name
                pattern = r'(?:skill|from|by)\b.*?\b' + re.escape(removed)
                match = re.search(pattern, content, re.IGNORECASE)
                self.assertIsNone(
                    match,
                    f"{skill_name}/SKILL.md references removed skill '{removed}'"
                )


if __name__ == "__main__":
    unittest.main()
