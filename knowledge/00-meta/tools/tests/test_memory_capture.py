#!/usr/bin/env python3
"""Tests for memory_capture: failure_handling coverage."""
import sys
import os
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
from memory_capture import cmd_capture, cmd_promote

class MockArgs:
    def __init__(self, **kw):
        d = dict(source_task='', commit='', outcome='', task_type='',
                 modules=None, body='', path='', move=False)
        d.update(kw)
        for k, v in d.items(): setattr(self, k, v)

def _env(tmp, extras=()):
    td = Path(tmp)
    (td / 'tpl-memory-factual.md').write_text("---\ntitle: X\n---\n")
    return [patch('memory_capture.FACTS_DIR', td),
            patch('memory_capture.EXPERIENCES_DIR', td),
            patch('memory_capture.TEMPLATES_DIR', td)] + list(extras)

def test_capture_success():
    with tempfile.TemporaryDirectory() as d:
        with ExitStack() as es:
            for p in _env(d): es.enter_context(p)
            assert cmd_capture(MockArgs(title="T", type="factual", template=None, body='x')) == 0

def test_capture_invalid_type():
    assert cmd_capture(MockArgs(title="T", type="bad", template=None, body='x')) != 0

def test_capture_unicode_error():
    ue = UnicodeEncodeError('utf-8', '', 0, 1, 'x')
    with tempfile.TemporaryDirectory() as d:
        with ExitStack() as es:
            for p in _env(d, [patch('pathlib.Path.write_text', side_effect=ue)]): es.enter_context(p)
            try:
                cmd_capture(MockArgs(title="T", type="factual", template=None, body='x'))
                assert False, "Expected UnicodeEncodeError"
            except UnicodeEncodeError: pass

def test_capture_write_oserror():
    with tempfile.TemporaryDirectory() as d:
        with ExitStack() as es:
            for p in _env(d, [patch('pathlib.Path.write_text', side_effect=OSError("disk full"))]): es.enter_context(p)
            assert cmd_capture(MockArgs(title="T", type="factual", template=None, body='x')) == 1

def test_promote_success():
    with tempfile.TemporaryDirectory() as d:
        td = Path(d); src = td / "s.md"
        src.write_text("---\ntitle: T\ntype: factual\n---\nBody")
        with patch('memory_capture.FACTS_DIR', td), patch('memory_capture.EXPERIENCES_DIR', td):
            assert cmd_promote(MockArgs(path=str(src), type="factual")) == 0

def test_promote_missing_file():
    assert cmd_promote(MockArgs(path="/no/such/file.md", type="factual")) != 0

def test_promote_read_oserror():
    with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tf:
        tf.write(b"content"); name = tf.name
    with patch('pathlib.Path.read_text', side_effect=OSError("perm denied")):
        result = cmd_promote(MockArgs(path=name, type="factual"))
    os.unlink(name); assert result != 0

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
