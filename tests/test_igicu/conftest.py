"""Pytest configuration for IGICU tests — uses temporary directories."""

from __future__ import annotations

import os
import tempfile
from typing import Generator

import pytest


@pytest.fixture(autouse=True)
def _temp_home(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Use a temporary ~/.igicu directory to avoid state leaking between tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        igicu_dir = os.path.join(tmpdir, ".igicu")
        os.makedirs(igicu_dir, exist_ok=True)
        old_home = os.environ.get("HOME")
        old_userprofile = os.environ.get("USERPROFILE")
        monkeypatch.setenv("HOME", tmpdir)
        monkeypatch.setenv("USERPROFILE", tmpdir)
        yield
        if old_home:
            monkeypatch.setenv("HOME", old_home)
        else:
            monkeypatch.delenv("HOME", raising=False)
        if old_userprofile:
            monkeypatch.setenv("USERPROFILE", old_userprofile)
        else:
            monkeypatch.delenv("USERPROFILE", raising=False)
