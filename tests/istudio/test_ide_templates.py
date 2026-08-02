"""Tests for istudio.ide.templates — every template must compile."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import pytest

from src.istudio.ide import templates as tpl


@pytest.mark.parametrize("key", sorted(tpl.TEMPLATES))
def test_template_metadata(key: str) -> None:
    meta = tpl.get_template(key)
    assert meta["name"]
    assert meta["description"]
    assert meta["category"]
    assert "main.i" in meta["files"] or any(name.endswith(".i") for name in meta["files"])
    assert "ilang.toml" in meta["files"]


@pytest.mark.parametrize("key", sorted(tpl.TEMPLATES))
def test_template_compiles(key: str) -> None:
    src = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "src")
    for rel, content in tpl.template_files(key).items():
        if not rel.endswith(".i"):
            continue
        fd, path = tempfile.mkstemp(prefix=f"tpl-{key}-", suffix=".i")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys;sys.path.insert(0,sys.argv[1]);"
                    "from compiler.compiler import Compiler;Compiler().compile_file(sys.argv[2])",
                    src,
                    path,
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )
            assert result.returncode == 0, f"{key}/{rel} failed to compile:\n{result.stderr}"
        finally:
            os.unlink(path)


@pytest.mark.parametrize("key", sorted(tpl.TEMPLATES))
def test_template_runs(key: str) -> None:
    """Templates must not only compile but run to completion."""
    src = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "src")
    for rel, content in tpl.template_files(key).items():
        if not rel.endswith(".i"):
            continue
        fd, path = tempfile.mkstemp(prefix=f"tpl-{key}-", suffix=".i")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys;sys.path.insert(0,sys.argv[1]);"
                    "from compiler.compiler import Compiler;Compiler().run_file(sys.argv[2])",
                    src,
                    path,
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )
            assert result.returncode == 0, f"{key}/{rel} failed to run:\n{result.stderr}"
            assert result.stdout.strip(), f"{key}/{rel} produced no output"
        finally:
            os.unlink(path)
