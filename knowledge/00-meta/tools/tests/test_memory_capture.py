#!/usr/bin/env python3
"""Tests for memory_capture module."""
import sys
from pathlib import Path
from unittest.mock import patch
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
from memory_capture import cmd_capture, cmd_promote

class MockArgs:
    def __init__(self, **kwargs):
        # Default values for all possible args
        defaults = {
            'source_task': '', 'commit': '', 'outcome': '', 'task_type': '', 'modules': None,
            'body': '', 'path': '', 'file': '', 'destination': '', 'move': False
        }
        defaults.update(kwargs)
        for k, v in defaults.items(): setattr(self, k, v)

def test_cmd_capture_success():
    """Test successful memory capture."""
    args = MockArgs(title="Test Memory Success", type="factual", template=None)
    result = cmd_capture(args)
    assert result == 0

def test_cmd_capture_invalid_type():
    """Test cmd_capture with invalid memory type."""
    args = MockArgs(title="Test Memory", type="invalid_type", template=None)
    result = cmd_capture(args)
    assert result != 0

def test_cmd_capture_unicode_error():
    """Test cmd_capture with unicode errors."""
    with patch('pathlib.Path.write_text', side_effect=UnicodeEncodeError('utf-8', '', 0, 1, 'test')):
        args = MockArgs(title="Test Unicode", type="factual", template=None)
        try:
            result = cmd_capture(args)
            assert False, "Should have raised UnicodeEncodeError"
        except UnicodeEncodeError:
            assert True  # Expected behavior

def test_cmd_promote_success():
    """Test successful memory promotion."""
    with tempfile.TemporaryDirectory() as temp_dir:
        source_file = Path(temp_dir) / "source.md"
        source_file.write_text("---\ntitle: Test\ntype: factual\n---\nContent")
        args = MockArgs(path=str(source_file), type="factual", move=False)
        assert cmd_promote(args) == 0

def test_cmd_promote_file_error():
    """Test cmd_promote with missing source file."""
    args = MockArgs(path="/nonexistent/file.md", type="factual", move=False)
    assert cmd_promote(args) != 0

def test_cmd_promote_invalid_type():
    """Test cmd_promote with invalid type."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tf:
        tf.write("test content")
        tf.flush()
        args = MockArgs(path=tf.name, type="invalid", move=False)
        result = cmd_promote(args)
        assert result != 0
        os.unlink(tf.name)

if __name__ == "__main__":
    test_cmd_capture_success()
    test_cmd_capture_invalid_type()
    test_cmd_capture_unicode_error()
    test_cmd_promote_success()
    test_cmd_promote_file_error()
    test_cmd_promote_invalid_type()
    print("All memory_capture tests passed!")