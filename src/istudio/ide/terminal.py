"""I STUDIO IDE — built-in terminal.

Spawns a shell per session and bridges I/O over SSE. On Windows we prefer
``winpty`` (ships with Git for Windows) so shells get a real PTY; otherwise we
fall back to plain pipes.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
from typing import Any

from .sse import SSEHub


def _find_winpty() -> str | None:
    exe = shutil.which("winpty")
    if exe:
        return exe
    for candidate in (
        r"C:\Program Files\Git\usr\bin\winpty.exe",
        r"C:\Program Files (x86)\Git\usr\bin\winpty.exe",
    ):
        if os.path.isfile(candidate):
            return candidate
    return None


def _default_shell() -> str:
    if os.name == "nt":
        shell = os.environ.get("COMSPEC") or "cmd.exe"
    else:
        shell = os.environ.get("SHELL") or "/bin/bash"
    return shell


class TerminalSession:
    def __init__(self, hub: SSEHub, term_id: str, shell: str | None, cwd: str):
        self.hub = hub
        self.term_id = term_id
        self.stream = f"term:{term_id}"
        self.shell = shell or _default_shell()
        self.cwd = cwd
        self._proc: subprocess.Popen | None = None
        self._winpty = _find_winpty()

    @property
    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def start(self) -> None:
        if not os.path.isdir(self.cwd):
            self.cwd = os.path.expanduser("~")
        command: Any
        if os.name == "nt" and self._winpty:
            command = [self._winpty, self.shell]
        else:
            command = self.shell
        self._proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self.cwd,
            bufsize=1,
        )
        threading.Thread(target=self._pump, daemon=True, name=f"term-{self.term_id}").start()
        self.hub.publish(self.stream, "ready", {"id": self.term_id, "shell": self.shell, "winpty": bool(self._winpty)})

    def write(self, data: str) -> None:
        if not self.is_alive or self._proc.stdin is None:
            return
        try:
            self._proc.stdin.write(data)
            self._proc.stdin.flush()
        except (OSError, ValueError):
            pass

    def resize(self, cols: int, rows: int) -> None:
        if not self.is_alive:
            return

    def close(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except OSError:
                pass

    def _pump(self) -> None:
        assert self._proc is not None
        assert self._proc.stdout is not None
        try:
            while True:
                chunk = self._proc.stdout.read(4096)
                if not chunk:
                    break
                self.hub.publish(self.stream, "output", {"data": chunk})
        except Exception:  # noqa: BLE001
            pass
        finally:
            self.hub.publish(self.stream, "exit", {})


class TerminalManager:
    def __init__(self, hub: SSEHub):
        self.hub = hub
        self._sessions: dict[str, TerminalSession] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def create(self, cwd: str, shell: str | None = None) -> TerminalSession:
        with self._lock:
            self._counter += 1
            term_id = f"term-{self._counter}"
            session = TerminalSession(self.hub, term_id, shell, cwd)
            self._sessions[term_id] = session
        session.start()
        return session

    def get(self, term_id: str) -> TerminalSession | None:
        with self._lock:
            return self._sessions.get(term_id)

    def close(self, term_id: str) -> bool:
        with self._lock:
            session = self._sessions.pop(term_id, None)
        if session is None:
            return False
        session.close()
        self.hub.close_stream(session.stream)
        return True

    def close_all(self) -> None:
        with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        for session in sessions:
            session.close()
            self.hub.close_stream(session.stream)
