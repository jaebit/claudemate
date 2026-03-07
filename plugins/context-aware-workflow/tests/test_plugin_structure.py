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
        required_dirs = ["agents", "hooks", "commands", "_shared", "skills"]

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


class TestCommandFiles(unittest.TestCase):
    """Test command file structure and frontmatter."""

    def get_command_files(self):
        """Get all command .md files."""
        commands_dir = PLUGIN_ROOT / "commands"
        return list(commands_dir.glob("*.md"))

    def test_commands_exist(self):
        """At least one command file must exist."""
        commands = self.get_command_files()
        self.assertGreater(len(commands), 0, "No command files found")

    def test_command_frontmatter(self):
        """Each command must have valid YAML frontmatter with description."""
        for cmd_file in self.get_command_files():
            with open(cmd_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Must start with ---
            self.assertTrue(
                content.startswith("---"),
                f"{cmd_file.name} must start with YAML frontmatter",
            )

            # Must have closing ---
            parts = content.split("---", 2)
            self.assertGreaterEqual(
                len(parts), 3, f"{cmd_file.name} must have closing ---"
            )

            # Frontmatter must contain description
            frontmatter = parts[1]
            self.assertIn(
                "description:",
                frontmatter,
                f"{cmd_file.name} missing 'description' in frontmatter",
            )


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


class TestRequiredCommands(unittest.TestCase):
    """Test that required v3.0 commands are present."""

    ACTIVE_COMMANDS = ["go", "status", "review", "parallel", "explore", "manage"]

    def test_active_commands_exist(self):
        """All 6 active v3.0 commands must exist."""
        for cmd_name in self.ACTIVE_COMMANDS:
            cmd = PLUGIN_ROOT / "commands" / f"{cmd_name}.md"
            self.assertTrue(cmd.exists(), f"commands/{cmd_name}.md not found")

    def test_deprecated_commands_removed(self):
        """Deprecated v2 commands should be fully removed in v3.1."""
        removed = [
            "auto", "pipeline", "loop", "start", "next",
            "analytics", "qaloop", "ultraqa", "check", "fix",
            "swarm", "team", "brainstorm", "design", "research",
            "context", "sync", "merge", "worktree", "tidy",
            "init", "evolve", "reflect",
        ]
        for cmd_name in removed:
            cmd = PLUGIN_ROOT / "commands" / f"{cmd_name}.md"
            self.assertFalse(cmd.exists(), f"Deprecated {cmd_name}.md should be removed in v3.1")

    def test_command_count(self):
        """v3.1 should have exactly 6 commands."""
        commands_dir = PLUGIN_ROOT / "commands"
        cmds = list(commands_dir.glob("*.md"))
        self.assertEqual(len(cmds), 6, f"Expected 6 commands, found {len(cmds)}: {[c.name for c in cmds]}")


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
        """v3.0 should have exactly 11 skills."""
        skills = self.get_skill_dirs()
        self.assertEqual(len(skills), 11, f"Expected 11 skills, found {len(skills)}: {[s.name for s in skills]}")


class TestRequiredSkills(unittest.TestCase):
    """Test that required v3.0 skills are present."""

    REQUIRED_SKILLS = [
        "context-manager", "progress-tracker", "plan-detector",
        "quality-gate", "commit-discipline", "insight-collector",
        "pattern-learner", "plugin-authoring",
        "knowledge-engine", "session-manager", "learning-loop",
    ]

    def test_required_skills_exist(self):
        """All 11 required skills must exist."""
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


if __name__ == "__main__":
    unittest.main()
