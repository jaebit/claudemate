#!/usr/bin/env python3
"""Tests for memory_utils module."""
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from memory_utils import slugify, parse_simple_yaml_frontmatter, render_template, now_iso, rebuild_frontmatter

def test_slugify():
    """Test slug generation."""
    assert slugify("Hello World") == "hello-world"
    assert slugify("Test-File_123") == "test-file-123"
    assert slugify("Special!@#$%Characters") == "special-characters"
    assert slugify("  Extra   Spaces  ") == "extra-spaces"
    assert slugify("") == ""

def test_parse_simple_yaml_frontmatter():
    """Test YAML frontmatter parsing."""
    content = "---\ntitle: Test\ntype: note\n---\nBody content here"
    meta, body = parse_simple_yaml_frontmatter(content)
    assert meta["title"] == "Test" and meta["type"] == "note"
    assert body == "Body content here"

    meta, body = parse_simple_yaml_frontmatter("Just body content")
    assert meta == {} and body == "Just body content"

    meta, body = parse_simple_yaml_frontmatter("---\n---\nBody content")
    assert meta == {} and body == "Body content"

def test_render_template():
    """Test template variable replacement."""
    variables = {"name": "World", "date": "2026-04-12"}
    result = render_template("Hello {{name}}, today is {{date}}", variables)
    assert result == "Hello World, today is 2026-04-12"
    assert render_template("Hello {{missing}}", {}) == "Hello {{missing}}"

def test_now_iso():
    """Test ISO timestamp generation."""
    result = now_iso()
    parsed = datetime.fromisoformat(result.replace('Z', '+00:00'))
    assert isinstance(parsed, datetime)

def test_rebuild_frontmatter():
    """Test frontmatter reconstruction."""
    meta = {"title": "Test", "type": "note"}
    result = rebuild_frontmatter(meta, "Content here")
    assert result.startswith("---\n") and "title: Test" in result
    assert result.endswith("\n---\nContent here")
    assert rebuild_frontmatter({}, "Content here") == "---\n---\nContent here"

if __name__ == "__main__":
    test_slugify()
    test_parse_simple_yaml_frontmatter()
    test_render_template()
    test_now_iso()
    test_rebuild_frontmatter()
    print("All tests passed!")