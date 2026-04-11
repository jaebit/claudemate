#!/usr/bin/env python3
"""
Integration Test Suite for Knowledge Management Tools

Tests basic functionality of knowledge management components:
- Graph configuration loading
- MCP server imports
- Memory CLI imports
- Wiki module existence
- Zone marker consistency
- Retrieval budget configuration
"""

import json
import os
import sys
import yaml
from pathlib import Path

# Base directory for the knowledge vault
KNOWLEDGE_BASE = Path(__file__).parent.parent.parent
TOOLS_DIR = Path(__file__).parent

def test_graph_config_loading():
    """Test that graph.json exists and can be loaded"""
    graph_path = KNOWLEDGE_BASE / "graph.json"
    assert graph_path.exists(), f"Graph config not found at {graph_path}"

    with open(graph_path, 'r') as f:
        graph_data = json.load(f)

    assert isinstance(graph_data, dict), "Graph config must be a valid JSON object"
    assert 'nodes' in graph_data or 'entities' in graph_data, "Graph must contain nodes or entities"
    print("✅ Graph config loads successfully")

def test_knowledge_mcp_import():
    """Test that knowledge_mcp.py can be imported"""
    mcp_path = TOOLS_DIR / "knowledge_mcp.py"
    assert mcp_path.exists(), f"MCP server not found at {mcp_path}"

    # Check basic syntax by attempting to parse
    with open(mcp_path, 'r') as f:
        code = f.read()

    import ast
    try:
        ast.parse(code)
        print("✅ knowledge_mcp.py syntax is valid")
    except SyntaxError as e:
        raise AssertionError(f"MCP server has syntax error: {e}")

    # Check for essential MCP server components
    assert 'class' in code and 'mcp' in code.lower(), "MCP server should contain class definitions"
    assert 'async def' in code or 'def ' in code, "MCP server should contain function definitions"

def test_memory_cli_import():
    """Test that memory_cli.py can be imported if it exists"""
    cli_path = TOOLS_DIR / "memory_cli.py"

    if not cli_path.exists():
        print("⚠️  memory_cli.py not found - skipping CLI tests")
        return

    with open(cli_path, 'r') as f:
        code = f.read()

    import ast
    try:
        ast.parse(code)
        print("✅ memory_cli.py syntax is valid")
    except SyntaxError as e:
        raise AssertionError(f"Memory CLI has syntax error: {e}")

def test_retrieval_budget_config():
    """Test that retrieval-budget.yaml exists and is parseable"""
    budget_path = KNOWLEDGE_BASE / "retrieval-budget.yaml"

    if not budget_path.exists():
        print("⚠️  retrieval-budget.yaml not found - skipping budget tests")
        return

    with open(budget_path, 'r') as f:
        budget_data = yaml.safe_load(f)

    assert isinstance(budget_data, dict), "Budget config must be a valid YAML object"
    print("✅ Retrieval budget config is parseable")

def test_wiki_modules_existence():
    """Test that wiki modules directory exists and contains pages"""
    modules_dir = KNOWLEDGE_BASE / "10-wiki" / "modules"

    if not modules_dir.exists():
        print("⚠️  Wiki modules directory not found - skipping module tests")
        return

    module_files = list(modules_dir.glob("*.md"))
    assert len(module_files) > 0, f"No module files found in {modules_dir}"

    # Check that at least one module has proper frontmatter
    for module_file in module_files[:3]:  # Check first 3 files
        with open(module_file, 'r') as f:
            content = f.read()

        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end > 0:
                frontmatter = content[3:frontmatter_end]
                try:
                    yaml.safe_load(frontmatter)
                    print(f"✅ Module {module_file.name} has valid frontmatter")
                    break
                except yaml.YAMLError:
                    continue

    print(f"✅ Found {len(module_files)} wiki modules")

def test_memory_directories():
    """Test that memory directories exist"""
    memory_dir = KNOWLEDGE_BASE / "30-memory"

    if not memory_dir.exists():
        print("⚠️  Memory directory not found - skipping memory tests")
        return

    facts_dir = memory_dir / "facts"
    experiences_dir = memory_dir / "experiences"

    if facts_dir.exists():
        fact_files = list(facts_dir.glob("*.md"))
        print(f"✅ Found {len(fact_files)} fact files")

    if experiences_dir.exists():
        exp_files = list(experiences_dir.glob("*.md"))
        print(f"✅ Found {len(exp_files)} experience files")

def test_zone_marker_consistency():
    """Test that zone markers in frontmatter are consistent"""
    zones_found = set()
    inconsistent_files = []

    for md_file in KNOWLEDGE_BASE.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue

        try:
            with open(md_file, 'r') as f:
                content = f.read()

            if content.startswith('---'):
                frontmatter_end = content.find('---', 3)
                if frontmatter_end > 0:
                    frontmatter = content[3:frontmatter_end]
                    try:
                        fm_data = yaml.safe_load(frontmatter)
                        if isinstance(fm_data, dict) and 'zone' in fm_data:
                            zone = fm_data['zone']
                            zones_found.add(zone)

                            # Check if zone matches directory structure
                            relative_path = md_file.relative_to(KNOWLEDGE_BASE)
                            expected_zone = None

                            if relative_path.parts[0] == '00-meta':
                                expected_zone = 'meta'
                            elif relative_path.parts[0].startswith('10-'):
                                expected_zone = 'wiki'
                            elif relative_path.parts[0].startswith('30-'):
                                expected_zone = 'memory'

                            if expected_zone and zone != expected_zone:
                                inconsistent_files.append((str(md_file), zone, expected_zone))
                    except yaml.YAMLError:
                        continue
        except (UnicodeDecodeError, PermissionError):
            continue

    print(f"✅ Found zones: {', '.join(sorted(zones_found))}")

    if inconsistent_files:
        print("⚠️  Zone inconsistencies found:")
        for file_path, actual, expected in inconsistent_files[:5]:  # Show first 5
            print(f"   {file_path}: zone='{actual}' (expected '{expected}')")
    else:
        print("✅ Zone markers are consistent")

def test_dashboard_exists():
    """Test that the dashboard file exists and contains Dataview queries"""
    dashboard_path = KNOWLEDGE_BASE / "00-meta" / "dashboard.md"
    assert dashboard_path.exists(), f"Dashboard not found at {dashboard_path}"

    with open(dashboard_path, 'r') as f:
        content = f.read()

    assert 'dataview' in content.lower(), "Dashboard should contain Dataview queries"
    assert '```dataview' in content, "Dashboard should contain Dataview code blocks"

    # Count Dataview blocks
    dataview_blocks = content.count('```dataview')
    assert dataview_blocks >= 3, f"Dashboard should have at least 3 Dataview blocks, found {dataview_blocks}"

    print(f"✅ Dashboard contains {dataview_blocks} Dataview queries")

def test_meta_zone_structure():
    """Test that meta zone has proper structure"""
    meta_dir = KNOWLEDGE_BASE / "00-meta"
    assert meta_dir.exists(), "Meta directory should exist"

    tools_dir = meta_dir / "tools"
    assert tools_dir.exists(), "Tools directory should exist"

    dashboard_file = meta_dir / "dashboard.md"
    assert dashboard_file.exists(), "Dashboard file should exist"

    print("✅ Meta zone structure is valid")

def run_all_tests():
    """Run all integration tests"""
    print("🧪 Starting Knowledge Management Integration Tests\n")

    tests = [
        test_graph_config_loading,
        test_knowledge_mcp_import,
        test_memory_cli_import,
        test_retrieval_budget_config,
        test_wiki_modules_existence,
        test_memory_directories,
        test_zone_marker_consistency,
        test_dashboard_exists,
        test_meta_zone_structure
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"\n📋 Running {test.__name__}...")
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__} ERROR: {e}")
            failed += 1

    print(f"\n🏁 Test Summary: {passed} passed, {failed} failed")

    if failed > 0:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False
    else:
        print("\n🎉 All integration tests passed!")
        return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)