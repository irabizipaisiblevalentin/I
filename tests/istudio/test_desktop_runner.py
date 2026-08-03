"""Tests for istudio.desktop.runner — ScriptRunner."""

from __future__ import annotations

import time

from src.istudio.desktop.runner import ScriptRunner


def _wait(condition, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition():
            return True
        time.sleep(0.02)
    return False


def test_run_source_captures_output():
    collected = []
    done = []
    runner = ScriptRunner(
        on_output=lambda text: collected.append(text),
        on_done=lambda ok, err: done.append((ok, err)),
    )
    try:
        runner.run_source('andika "Muraho"')
        assert _wait(lambda: bool(done))
        assert done[0][0] is True
        assert "Muraho" in collected[0]
    finally:
        runner.close()


def test_run_file_captures_output(tmp_path):
    f = tmp_path / "hello.i"
    f.write_text('andika "Hello from file"', encoding="utf-8")
    collected = []
    done = []
    runner = ScriptRunner(
        on_output=lambda text: collected.append(text),
        on_done=lambda ok, err: done.append((ok, err)),
    )
    try:
        runner.run_file(str(f))
        assert _wait(lambda: bool(done))
        assert done[0][0] is True
        assert "Hello from file" in collected[0]
    finally:
        runner.close()


def test_run_source_error_reported():
    done = []
    runner = ScriptRunner(on_done=lambda ok, err: done.append((ok, err)))
    try:
        runner.run_source("this is not valid i code ((((")
        assert _wait(lambda: bool(done))
        assert done[0][0] is False
        assert done[0][1] is not None
    finally:
        runner.close()


def test_run_missing_file_error():
    done = []
    runner = ScriptRunner(on_done=lambda ok, err: done.append((ok, err)))
    try:
        runner.run_file("/nonexistent/file.i")
        assert _wait(lambda: bool(done))
        assert done[0][0] is False
    finally:
        runner.close()


def test_stdout_restored_after_run():
    import sys

    original = sys.stdout
    runner = ScriptRunner()
    try:
        runner.run_source('andika 1')
        assert _wait(lambda: not runner.is_running)
        assert sys.stdout is original
    finally:
        runner.close()


def test_is_running_flag():
    runner = ScriptRunner()
    assert not runner.is_running
    try:
        runner.run_source('andika 1')
        assert _wait(lambda: not runner.is_running)
        assert not runner.is_running
    finally:
        runner.close()
