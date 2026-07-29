"""I STUDIO test configuration."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


@pytest.fixture
def temp_file(temp_dir: str) -> Generator[str, None, None]:
    path = Path(temp_dir) / "test.i"
    path.write_text("", encoding="utf-8")
    yield str(path)
