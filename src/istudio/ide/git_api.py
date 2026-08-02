"""I STUDIO IDE — Git integration (git CLI)."""

from __future__ import annotations

import os
import subprocess
from typing import Any


class GitError(Exception):
    pass


class GitService:
    def __init__(self, repo_root: str):
        self.root = os.path.abspath(repo_root)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                ["git", *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=self.root,
                timeout=30,
            )
        except FileNotFoundError:
            raise GitError("git executable not found") from None
        except subprocess.TimeoutExpired:
            raise GitError("git command timed out") from None

    @property
    def is_repo(self) -> bool:
        result = self._run("rev-parse", "--is-inside-work-tree")
        return result.returncode == 0

    def status(self) -> dict[str, Any]:
        if not self.is_repo:
            return {"is_repo": False, "branch": "", "changed": [], "staged": []}
        branch = self._run("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        porcelain = self._run("status", "--porcelain", "--branch").stdout.splitlines()
        changed: list[dict[str, str]] = []
        staged: list[dict[str, str]] = []
        for line in porcelain:
            if not line:
                continue
            code, _, path = line.partition(" ")
            if code.startswith("##"):
                continue
            entry = {"path": path.strip(), "code": code}
            (staged if code.startswith(("A", "M", "D", "R", "C")) else changed).append(entry)
        return {"is_repo": True, "branch": branch, "changed": changed, "staged": staged}

    def diff(self, path: str | None = None) -> str:
        if path:
            return self._run("diff", "--", path).stdout
        return self._run("diff").stdout

    def commit(self, message: str) -> dict[str, Any]:
        result = self._run("add", "-A")
        if result.returncode != 0:
            raise GitError(result.stderr.strip())
        result = self._run("commit", "-m", message)
        if result.returncode != 0:
            raise GitError(result.stderr.strip() or result.stdout.strip())
        return {"message": message, "ok": True}

    def branches(self) -> list[str]:
        result = self._run("branch", "--format=%(refname:short)")
        return [b for b in result.stdout.splitlines() if b]

    def log(self, limit: int = 20) -> list[dict[str, str]]:
        result = self._run("log", f"-{limit}", "--pretty=format:%h|%an|%s")
        entries: list[dict[str, str]] = []
        for line in result.stdout.splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3:
                entries.append({"hash": parts[0], "author": parts[1], "message": parts[2]})
        return entries

    def init(self) -> dict[str, Any]:
        result = self._run("init")
        if result.returncode != 0:
            raise GitError(result.stderr.strip())
        return {"ok": True, "output": result.stdout}
