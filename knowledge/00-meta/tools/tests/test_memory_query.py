#!/usr/bin/env python3
"""Tests for memory_query module."""
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
from memory_query import cmd_query, cmd_status, cmd_retrieve

class MockArgs:
    def __init__(self, **kwargs):
        defaults = {'keywords': [], 'type': None, 'confidence': None,
                   'task_type': 'explore', 'exclude_duplicates': False,
                   'min_confidence': 0.0, 'keyword': 'test', 'module': None}
        defaults.update(kwargs)
        for k, v in defaults.items(): setattr(self, k, v)

def test_cmd_query():
    """Test memory query command."""
    args = MockArgs(keywords=['test'])
    assert cmd_query(args) == 0

def test_cmd_status():
    """Test memory status command."""
    assert cmd_status(MockArgs()) == 0

def test_cmd_query_with_filters():
    """Test query with type and confidence filters."""
    args = MockArgs(keywords=['test'], type='factual', confidence='high')
    assert cmd_query(args) == 0

def test_cmd_retrieve_with_exclusions():
    """Test retrieve with invalid task_type."""
    args = MockArgs(task_type='invalid_task', exclude_duplicates=True)
    assert cmd_retrieve(args) != 0

def test_cmd_retrieve():
    """Test retrieve without budget file."""
    assert cmd_retrieve(MockArgs(task_type='explore')) != 0

def test_cmd_retrieve_missing_budget():
    """Test retrieve with missing budget file."""
    with patch('pathlib.Path.exists', return_value=False):
        assert cmd_retrieve(MockArgs(task_type='nonexistent')) != 0

def test_cmd_query_file_access_error():
    """Test query with file access errors."""
    with patch('pathlib.Path.iterdir', side_effect=OSError("Permission denied")):
        assert cmd_query(MockArgs(keywords=['test'])) == 0

if __name__ == "__main__":
    test_cmd_query()
    test_cmd_status()
    test_cmd_query_with_filters()
    test_cmd_retrieve_with_exclusions()
    test_cmd_retrieve()
    test_cmd_retrieve_missing_budget()
    test_cmd_query_file_access_error()
    print("All memory_query tests passed!")