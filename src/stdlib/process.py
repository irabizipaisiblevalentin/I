"""process — Process management for the I language.

Provides subprocess execution, process control, and inter-process communication.
"""

from __future__ import annotations

import subprocess
import os
from typing import Any, Dict, List, Optional, Tuple, Union


class ProcessResult:
    """Result of a completed process."""

    __slots__ = ("stdout", "stderr", "returncode", "args")

    def __init__(self, stdout: str, stderr: str, returncode: int, args: List[str]) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.args = args

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def __repr__(self) -> str:
        return f"ProcessResult(returncode={self.returncode})"


def run(command: Union[str, List[str]], cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None, timeout: Optional[float] = None,
        shell: bool = False) -> ProcessResult:
    """Run a command and return result."""
    args = command if isinstance(command, list) else command.split()
    result = subprocess.run(
        args, capture_output=True, text=True, cwd=cwd,
        env=env, timeout=timeout, shell=shell,
    )
    return ProcessResult(result.stdout, result.stderr, result.returncode, args)


def run_checked(command: Union[str, List[str]], **kwargs: Any) -> ProcessResult:
    """Run command, raise on non-zero exit."""
    result = run(command, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {result.stderr}")
    return result


def run_capture(command: Union[str, List[str]], **kwargs: Any) -> str:
    """Run command, return stdout as string."""
    result = run(command, **kwargs)
    return result.stdout


def popen(command: Union[str, List[str]], cwd: Optional[str] = None):
    """Open a subprocess for streaming I/O."""
    args = command if isinstance(command, list) else command.split()
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE, cwd=cwd, text=True)


def exec_command(command: str) -> Tuple[int, str, str]:
    """Execute shell command, return (returncode, stdout, stderr)."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def which(name: str) -> Optional[str]:
    """Find executable in PATH."""
    return subprocess.os.path.abspath(subprocess.os.path.expanduser(name))


def list_processes() -> List[str]:
    """List running processes (basic)."""
    result = run(["tasklist" if os.name == "nt" else "ps", "aux"])
    return result.stdout.splitlines() if result.ok else []
