"""output — Terminal output utilities for isoko.

Provides colored output, progress indicators, and diagnostics.
"""

from __future__ import annotations

import os
import sys
import time
from typing import IO, Optional, TextIO


# ---------------------------------------------------------------------------
# Color support detection
# ---------------------------------------------------------------------------

def _supports_color(stream: IO = sys.stderr) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


_use_color = _supports_color()


def set_color(enabled: bool) -> None:
    global _use_color
    _use_color = enabled


# ---------------------------------------------------------------------------
# ANSI color codes
# ---------------------------------------------------------------------------

class _Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def _fmt(text: str, *codes: str, stream: IO = sys.stderr) -> str:
    if not _use_color or not codes:
        return text
    return "".join(codes) + text + _Style.RESET


# ---------------------------------------------------------------------------
# High-level output functions
# ---------------------------------------------------------------------------

def _get_stream(stream: Optional[TextIO] = None) -> TextIO:
    return stream or sys.stderr


def success(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  {msg}", _Style.GREEN, _Style.BOLD), file=_get_stream(stream))


def error(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  error: {msg}", _Style.RED, _Style.BOLD), file=_get_stream(stream))


def warning(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  warning: {msg}", _Style.YELLOW), file=_get_stream(stream))


def info(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  {msg}", _Style.CYAN), file=_get_stream(stream))


def dim(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(msg, _Style.DIM), file=_get_stream(stream))


def bold(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(msg, _Style.BOLD), file=_get_stream(stream))


def header(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"\n{msg}", _Style.BOLD, _Style.UNDERLINE), file=_get_stream(stream))


def label_value(label: str, value: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  {label}: ", _Style.BOLD) + value, file=_get_stream(stream))


def status(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  [{msg}]", _Style.CYAN), file=_get_stream(stream))


def found(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"    found {msg}", _Style.GREEN), file=_get_stream(stream))


def skipped(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"    skipped {msg}", _Style.DIM), file=_get_stream(stream))


def downloading(name: str, version: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  Downloading {name}@{version}", _Style.CYAN), file=_get_stream(stream))


def installing(name: str, version: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  Installing {name}@{version}", _Style.GREEN), file=_get_stream(stream))


def compiling(msg: str, stream: Optional[TextIO] = None) -> None:
    print(_fmt(f"  Compiling {msg}", _Style.BLUE), file=_get_stream(stream))


# ---------------------------------------------------------------------------
# Progress indicator
# ---------------------------------------------------------------------------

class Spinner:
    """Simple terminal spinner."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "", stream: Optional[TextIO] = None) -> None:
        self._message = message
        self._stream = stream
        self._frame = 0
        self._active = False
        self._start_time = 0.0

    @property
    def _out(self) -> TextIO:
        return _get_stream(self._stream)

    def start(self) -> None:
        self._active = True
        self._start_time = time.time()
        self._tick()

    def update(self, message: str) -> None:
        self._message = message
        if self._active:
            self._tick()

    def stop(self, final_msg: Optional[str] = None) -> None:
        if not self._active:
            return
        self._active = False
        elapsed = time.time() - self._start_time
        msg = final_msg if final_msg else self._message
        line = f"\r{_fmt(f'  ✓ {msg} ', _Style.GREEN, _Style.BOLD)}"
        line += _fmt(f"({elapsed:.1f}s)", _Style.DIM)
        print(line, file=self._out)
        self._out.flush()

    def fail(self, msg: str) -> None:
        self._active = False
        print(f"\r{_fmt(f'  ✗ {msg}', _Style.RED, _Style.BOLD)}", file=self._out)
        self._out.flush()

    def _tick(self) -> None:
        frame = self.FRAMES[self._frame % len(self.FRAMES)]
        self._frame += 1
        line = f"\r{_fmt(f'  {frame} {self._message}', _Style.CYAN)}"
        print(line, end="", file=self._out)
        self._out.flush()

    def __enter__(self) -> Spinner:
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        if self._active:
            self.stop()


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------

class ProgressBar:
    """Terminal progress bar."""

    def __init__(self, total: int, message: str = "",
                 stream: Optional[TextIO] = None) -> None:
        self._total = total
        self._current = 0
        self._message = message
        self._stream = stream
        self._start_time = time.time()

    @property
    def _out(self) -> TextIO:
        return _get_stream(self._stream)

    def update(self, n: int = 1) -> None:
        self._current += n
        self._render()

    def _render(self) -> None:
        pct = self._current / self._total if self._total > 0 else 0
        filled = int(40 * pct)
        bar = "█" * filled + "░" * (40 - filled)
        elapsed = time.time() - self._start_time
        line = f"\r{_fmt(f'  {bar}', _Style.CYAN)} {pct*100:.0f}%"
        if self._message:
            line += f" {self._message}"
        if elapsed > 0.1:
            rate = self._current / elapsed
            line += _fmt(f" ({rate:.1f}/s)", _Style.DIM)
        print(line, end="", file=self._out)
        self._out.flush()

    def finish(self) -> None:
        elapsed = time.time() - self._start_time
        bar = "█" * 40
        line = f"\r{_fmt(f'  {bar}', _Style.GREEN)} 100%"
        if elapsed > 0.1:
            line += _fmt(f" ({elapsed:.1f}s)", _Style.DIM)
        print(line, file=self._out)
        self._out.flush()


# ---------------------------------------------------------------------------
# Table output
# ---------------------------------------------------------------------------

def print_table(headers: list[str], rows: list[list[str]],
                stream: Optional[TextIO] = None) -> None:
    out = _get_stream(stream)
    if not rows:
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    header_line = "  ".join(
        _fmt(h.ljust(widths[i]), _Style.BOLD) for i, h in enumerate(headers)
    )
    print(header_line, file=out)

    sep = "  ".join("─" * w for w in widths)
    print(_fmt(f"  {sep}", _Style.DIM), file=out)

    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            w = widths[i] if i < len(widths) else len(cell)
            cells.append(cell.ljust(w))
        print("  ".join(cells), file=out)


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def print_json(data: object, stream: Optional[TextIO] = None) -> None:
    import json
    out = _get_stream(stream) if stream is not None else sys.stdout
    print(json.dumps(data, indent=2, ensure_ascii=False), file=out)


# ---------------------------------------------------------------------------
# Machine-readable output
# ---------------------------------------------------------------------------

class Output:
    """Unified output handler supporting human and machine-readable formats."""

    def __init__(self, json_mode: bool = False, quiet: bool = False,
                 verbose: bool = False) -> None:
        self.json_mode = json_mode
        self.quiet = quiet
        self.verbose = verbose
        self._json_data: list[dict] = []

    def success(self, msg: str) -> None:
        if self.json_mode:
            self._json_data.append({"level": "success", "message": msg})
        elif not self.quiet:
            success(msg)

    def error(self, msg: str) -> None:
        if self.json_mode:
            self._json_data.append({"level": "error", "message": msg})
        else:
            error(msg)

    def warning(self, msg: str) -> None:
        if self.json_mode:
            self._json_data.append({"level": "warning", "message": msg})
        elif not self.quiet:
            warning(msg)

    def info(self, msg: str) -> None:
        if self.json_mode:
            self._json_data.append({"level": "info", "message": msg})
        elif not self.quiet:
            info(msg)

    def dim(self, msg: str) -> None:
        if not self.json_mode and self.verbose and not self.quiet:
            dim(msg)

    def flush_json(self) -> None:
        if self.json_mode and self._json_data:
            print_json(self._json_data)
            self._json_data.clear()
