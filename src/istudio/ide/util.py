"""I STUDIO IDE — internal utilities (subprocess isolation, JSON helpers)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

_SRC_DIR = str(Path(__file__).resolve().parents[3])


def src_dir() -> str:
    return _SRC_DIR


def child_cmd(task: str, *args: str) -> list[str]:
    """Build the command that runs an IDE child task (compile/run/debug/isoko).

    In dev mode the child is ``python -m istudio.ide --istudio-child <task>``;
    in a frozen (PyInstaller) build ``sys.executable`` is the app exe itself,
    so we hand it the same hidden ``--istudio-child`` flag instead of ``-c``.
    """
    if getattr(sys, "frozen", False):
        return [sys.executable, "--istudio-child", task, *args]
    return [sys.executable, "-m", "istudio.ide", "--istudio-child", task, *args]


def env_with_src(env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if env is None else env)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = _SRC_DIR + (os.pathsep + existing if existing else "")
    # Stream child output live (the VM's print() is block-buffered on a pipe
    # otherwise, so long-running programs show nothing until they exit).
    env["PYTHONUNBUFFERED"] = "1"
    return env


def spawn(task: str, *args: str, timeout: float = 30.0, cwd: str | None = None):
    """Run an IDE child task in an isolated process, returning CompletedProcess."""
    cmd = child_cmd(task, *args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        cwd=cwd,
        env=env_with_src(),
    )


def run_source_isolated(source: str, filename: str = "unnamed.i", timeout: float = 30.0) -> dict[str, Any]:
    """Compile+run I source in a child process. Returns {ok, output, error, code}."""
    import tempfile

    fd, path = tempfile.mkstemp(prefix="istudio-run-", suffix=".i")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(source)
        return run_file_isolated(path, timeout=timeout)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def run_file_isolated(file_path: str, timeout: float = 30.0) -> dict[str, Any]:
    """Compile+run an I file in a child process. Returns {ok, output, error, code}."""
    try:
        proc = spawn("run", file_path, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "", "error": "Execution timed out", "code": None}
    output = proc.stdout
    if proc.returncode == 0:
        return {"ok": True, "output": output, "error": "", "code": 0}
    # Extract the last meaningful error line (skip traceback noise where possible).
    error = proc.stderr.strip() or proc.stdout.strip()
    return {"ok": False, "output": output, "error": error, "code": proc.returncode}


def compile_file_isolated(file_path: str, timeout: float = 20.0) -> dict[str, Any]:
    """Compile-only check in a child process. Returns {"ok": bool, "error": str}."""
    try:
        proc = spawn("compile", file_path, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Compilation timed out (possible infinite parse loop)"}
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        return payload
    except (ValueError, IndexError):
        return {"ok": False, "error": (proc.stderr or proc.stdout or "unknown error")[:4000]}


def debug_compile_chunk(file_path: str, out_chunk: str, timeout: float = 20.0) -> dict[str, Any]:
    """Compile an I file in a child process and pickle the Chunk to out_chunk."""
    try:
        proc = spawn("debug_compile", file_path, out_chunk, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Compilation timed out"}
    if proc.returncode == 0:
        return {"ok": True, "error": ""}
    tail = (proc.stderr.strip() or proc.stdout.strip()).splitlines()
    return {"ok": False, "error": tail[-1][:4000] if tail else "unknown compile error"}


def json_bytes(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")


def read_json_body(data: bytes) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8") or "null")
        if isinstance(value, dict):
            return value
        return {}
    except (ValueError, UnicodeDecodeError):
        return {}


def safe_join(root: str, *parts: str) -> str | None:
    """Join parts under root, refusing path traversal. Returns None if unsafe."""
    base = os.path.normpath(os.path.abspath(root))
    target = os.path.normpath(os.path.abspath(os.path.join(root, *parts)))
    if not target.startswith(base + os.sep) and target != base:
        return None
    return target


def _rel(base: str, full: str) -> str:
    return os.path.relpath(full, base).replace(os.sep, "/")


def walk_tree(root: str) -> list[dict[str, Any]]:
    """Return a nested file tree [{name, path, type, children?}], sorted, skipping
    .git, node_modules and __pycache__. ``path`` is a POSIX-style path relative
    to ``root`` (forward slashes)."""
    return _walk_tree(root, root)


def _walk_tree(root: str, base: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    skip = {".git", "node_modules", "__pycache__", ".istudio", "dist", "build"}
    try:
        names = sorted(os.listdir(root))
    except OSError:
        return entries
    for name in names:
        if name in skip:
            continue
        full = os.path.join(root, name)
        if os.path.isdir(full):
            children = _walk_tree(full, base)
            entries.append({"name": name, "path": _rel(base, full), "type": "directory", "children": children})
        else:
            entries.append({"name": name, "path": _rel(base, full), "type": "file"})
    return entries
