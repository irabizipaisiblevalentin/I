"""I STUDIO IDE — run service.

Executes I source/files in an isolated child process and streams stdout/stderr
over SSE to the Run panel. Cancel terminates the child process.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from . import util
from .sse import SSEHub


class RunService:
    def __init__(self, hub: SSEHub):
        self.hub = hub
        self._jobs: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"job-{self._counter}"

    def start_file(self, file_path: str, project_dir: str | None = None) -> str:
        job_id = self._next_id()
        stream = f"run:{job_id}"
        env = util.env_with_src()
        cwd = project_dir or str(Path(file_path).resolve().parent)
        if not os.path.isdir(cwd):
            cwd = str(Path(tempfile.gettempdir()))

        proc = subprocess.Popen(
            util.child_cmd("run", file_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        job = {"proc": proc, "stream": stream, "started": time.time()}
        with self._lock:
            self._jobs[job_id] = job

        threading.Thread(target=self._watch, args=(job_id,), daemon=True, name=f"run-{job_id}").start()
        return job_id

    def start_source(self, source: str, project_dir: str | None = None) -> str:
        fd, path = tempfile.mkstemp(prefix="istudio-run-", suffix=".i")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(source)
        job_id = self.start_file(path, project_dir)
        with self._lock:
            self._jobs[job_id]["temp"] = path
        return job_id

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            return False
        proc = job["proc"]
        if proc.poll() is None:
            try:
                proc.terminate()
            except OSError:
                pass
        return True

    def _watch(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            return
        proc = job["proc"]
        stream = job["stream"]
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                self.hub.publish(stream, "output", {"line": line})
            code = proc.wait()
        except Exception as exc:  # noqa: BLE001
            code = -1
            self.hub.publish(stream, "output", {"line": f"[runner error] {exc}\n"})
        finally:
            temp = job.get("temp")
            if temp:
                try:
                    os.unlink(temp)
                except OSError:
                    pass
            with self._lock:
                self._jobs.pop(job_id, None)
        self.hub.publish(stream, "done", {"ok": code == 0, "code": code})
