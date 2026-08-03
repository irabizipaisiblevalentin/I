"""I STUDIO Desktop — script runner (headless-testable).

Runs I source files through the real compiler/VM in a child process so that a
crashing script can never take down the IDE, output is captured from pipes, and
``stop()`` is a real process termination. Callbacks are invoked from a worker
thread, so GUI consumers must marshal them back to the UI thread (e.g. with
``after``).
"""

from __future__ import annotations

import os
import select
import subprocess
import sys
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path

_SRC_DIR = str(Path(__file__).resolve().parents[3])

_LAUNCHER = (
    "import sys\n"
    "from compiler.compiler import Compiler\n"
    "Compiler().run_file(sys.argv[1])\n"
)


class ScriptRunner:
    def __init__(
        self,
        on_output: Callable[[str], None] | None = None,
        on_done: Callable[[bool, str | None], None] | None = None,
        timeout: float | None = None,
    ):
        self._on_output = on_output
        self._on_done = on_done
        self._timeout = timeout
        self._process: subprocess.Popen | None = None
        self._thread: threading.Thread | None = None
        self._cancel_r: int | None = None
        self._cancel_w: int | None = None

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def run_file(self, file_path: str) -> threading.Thread:
        return self._start(file_path, None)

    def run_source(self, source: str, name: str = "unnamed.i") -> threading.Thread:
        fd, tmp = tempfile.mkstemp(prefix="istudio-", suffix=".i")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(source)
        return self._start(tmp, tmp)

    def stop(self) -> None:
        if self._process is not None and self._process.poll() is None:
            try:
                self._process.terminate()
            except OSError:
                pass

    def close(self) -> None:
        """Terminate the child, close its pipes, and reap the worker thread.

        Guarantees no ``istudio-runner`` daemon thread survives past this call:
        a write to the cancel pipe deterministically wakes a drain blocked in
        ``select`` (closing the fd does not reliably wake ``select`` on macOS).
        """
        if self._cancel_w is not None:
            try:
                os.write(self._cancel_w, b"\x00")
            except OSError:
                pass
        proc = self._process
        if proc is not None:
            if proc.poll() is None:
                try:
                    proc.terminate()
                except OSError:
                    pass
            try:
                if proc.stdout is not None:
                    proc.stdout.close()
            except OSError:
                pass
            try:
                if proc.stderr is not None:
                    proc.stderr.close()
            except OSError:
                pass
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2.0)
            self._thread = None
        for name in ("_cancel_r", "_cancel_w"):
            fd = getattr(self, name)
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
                setattr(self, name, None)

    def _start(self, target: str, cleanup: str | None) -> threading.Thread:
        if self._cancel_r is not None:
            try:
                os.close(self._cancel_r)
            except OSError:
                pass
        if self._cancel_w is not None:
            try:
                os.close(self._cancel_w)
            except OSError:
                pass
        self._cancel_r, self._cancel_w = os.pipe()

        env = os.environ.copy()
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = _SRC_DIR + (os.pathsep + existing if existing else "")

        parent = Path(target).resolve().parent
        cwd = str(parent) if parent.is_dir() else str(Path(tempfile.gettempdir()))

        self._process = subprocess.Popen(
            [sys.executable, "-c", _LAUNCHER, target],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        thread = threading.Thread(
            target=self._watch,
            args=(cleanup,),
            daemon=True,
            name="istudio-runner",
        )
        thread.start()
        self._thread = thread
        return thread

    def _watch(self, cleanup: str | None) -> None:
        proc = self._process
        try:
            assert proc is not None
            assert proc.stdout is not None
            if os.name == "nt":
                code = self._drain_blocking(proc)
            else:
                code = self._drain_select(proc, self._cancel_r)
        finally:
            if cleanup:
                try:
                    os.unlink(cleanup)
                except OSError:
                    pass

        ok = code == 0
        error = None if ok else f"process exited with code {code}"
        if self._on_done is not None:
            self._on_done(ok, error)

    def _drain_blocking(self, proc: subprocess.Popen) -> int:
        assert proc.stdout is not None
        elapsed = 0.0
        for line in proc.stdout:
            if self._timeout is not None:
                elapsed += 0.05
                if elapsed > self._timeout and proc.poll() is None:
                    proc.terminate()
            if self._on_output is not None:
                self._on_output(line)
        return proc.wait()

    def _drain_select(
        self, proc: subprocess.Popen, cancel_fd: int | None
    ) -> int:
        assert proc.stdout is not None
        fd = proc.stdout.fileno()
        fds = [fd] if cancel_fd is None else [fd, cancel_fd]
        pending = ""
        elapsed = 0.0
        while True:
            rlist, _, _ = select.select(fds, [], [], 0.05)
            if cancel_fd is not None and cancel_fd in rlist:
                break
            if fd in rlist:
                try:
                    chunk = os.read(fd, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                pending += chunk.decode("utf-8", "replace")
                while "\n" in pending:
                    line, pending = pending.split("\n", 1)
                    if self._timeout is not None:
                        elapsed += 0.05
                        if elapsed > self._timeout and proc.poll() is None:
                            proc.terminate()
                    if self._on_output is not None:
                        self._on_output(line + "\n")
            else:
                if self._timeout is not None:
                    elapsed += 0.05
                    if elapsed > self._timeout and proc.poll() is None:
                        proc.terminate()
                if proc.poll() is not None:
                    break
        if pending and self._on_output is not None:
            self._on_output(pending)
        return proc.wait()
