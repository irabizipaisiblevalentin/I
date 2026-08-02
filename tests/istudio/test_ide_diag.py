"""Tests for istudio.ide.diag — diagnostics, completion, hover, symbols, format."""

from __future__ import annotations

import subprocess
import sys

from src.istudio.ide import diag, util

CLEAN = "shyira x = 1\nandika x\n"


def test_analyze_clean() -> None:
    assert diag.analyze_source(CLEAN) == []


def test_analyze_semantic_error() -> None:
    results = diag.analyze_source("shyira x = y\n")
    assert results
    assert results[0]["severity"] == 1
    assert results[0]["source"] == "compiler"
    assert "range" in results[0]


def test_analyze_lexer_error() -> None:
    results = diag.analyze_source('andika "unterminated\n')
    assert results
    assert any(d["code"].startswith("LEX") for d in results)


def test_analyze_infinite_loop_guarded() -> None:
    """Pathological input that hangs the parser must not hang the test (8s watchdog)."""
    import time

    start = time.monotonic()
    results = diag.analyze_source("shyira " * 5000)
    elapsed = time.monotonic() - start
    assert elapsed < 12, "analysis must not hang"
    assert isinstance(results, list)


def test_completions_prefix_filter() -> None:
    items = diag.completions_at("shy\n", 1, 3)
    labels = [i["label"] for i in items]
    assert "shyira" in labels
    assert all(i["kind"] in (14, 12, 6) for i in items)


def test_completions_identifiers() -> None:
    items = diag.completions_at("shyira kabone = 1\nkab\n", 2, 3)
    assert any(i["label"] == "kabone" for i in items)


def test_hover_builtin() -> None:
    result = diag.hover_at("andika 1\n", 1, 1)
    assert result is not None
    assert "andika" in result["contents"][0]["value"]


def test_hover_unknown_returns_none() -> None:
    assert diag.hover_at("andika\n", 1, 20) is None


def test_symbols_function_decl() -> None:
    symbols = diag.symbols_of("umurimo main() -> int\n    subira 0\niherezo\n")
    names = {s["name"] for s in symbols}
    assert "main" in names


def test_format_source_indents_blocks() -> None:
    formatted = diag.format_source("umurimo f()\nandika 1\niherezo\n")
    assert "    andika 1" in formatted
    assert formatted.endswith("\n")


def test_util_run_source_isolated_ok() -> None:
    result = util.run_source_isolated("andika 21 + 21\n")
    assert result["ok"] is True
    assert "42" in result["output"]


def test_util_run_source_isolated_compile_error() -> None:
    result = util.run_source_isolated("shyira x = 1\ny\n")
    assert result["ok"] is False
    assert result["error"]


def test_util_compile_file_isolated_timeout_handling() -> None:
    import os
    import tempfile

    fd, path = tempfile.mkstemp(prefix="istudio-cmp-", suffix=".i")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("andika 1\n")
        result = util.compile_file_isolated(path, timeout=5)
        assert result["ok"] is True
    finally:
        os.unlink(path)


def test_spawn_sandbox_pythonpath() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys;sys.path.insert(0,sys.argv[1]);import compiler;print(compiler.__name__)",
            util.src_dir(),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.stdout.strip() == "compiler"
