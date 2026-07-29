"""terminal — Terminal/CLI utilities for the I language.

Provides ANSI colors, formatting, progress bars, and input prompts.
"""

from __future__ import annotations

import sys
from typing import Any, Optional, TextIO


# ---------------------------------------------------------------------------
# ANSI color codes
# ---------------------------------------------------------------------------

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def colored(text: str, fg: str = "", bg: str = "", bold: bool = False,
            underline: bool = False) -> str:
    """Wrap text in ANSI color codes."""
    parts = []
    if bold:
        parts.append(Color.BOLD)
    if underline:
        parts.append(Color.UNDERLINE)
    if fg:
        parts.append(fg)
    if bg:
        parts.append(bg)
    parts.append(text)
    parts.append(Color.RESET)
    return "".join(parts)


def red(text: str) -> str:
    return colored(text, fg=Color.RED)


def green(text: str) -> str:
    return colored(text, fg=Color.GREEN)


def yellow(text: str) -> str:
    return colored(text, fg=Color.YELLOW)


def blue(text: str) -> str:
    return colored(text, fg=Color.BLUE)


def bold(text: str) -> str:
    return colored(text, bold=True)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_color(*args: Any, fg: str = "", bg: str = "",
                file: TextIO = sys.stdout, **kwargs: Any) -> None:
    """Print with color support."""
    colored_args = [colored(str(a), fg=fg, bg=bg) for a in args]
    print(*colored_args, file=file, **kwargs)


def write(text: str, file: TextIO = sys.stdout) -> None:
    file.write(text)
    file.flush()


def writeln(text: str = "", file: TextIO = sys.stdout) -> None:
    write(text + "\n", file)


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

def prompt(message: str = "", default: str = "") -> str:
    """Prompt user for input."""
    if message:
        sys.stdout.write(message + " ")
        sys.stdout.flush()
    result = sys.stdin.readline().rstrip("\n")
    return result if result else default


def confirm(message: str = "Continue?", default: bool = True) -> bool:
    """Yes/No confirmation."""
    suffix = " [Y/n] " if default else " [y/N] "
    answer = prompt(message + suffix).lower()
    if not answer:
        return default
    return answer in ("y", "yes", "yebo")


def password(message: str = "Password: ") -> str:
    """Read password (no echo)."""
    import getpass
    return getpass.getpass(message)


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

class ProgressBar:
    """Simple terminal progress bar."""

    def __init__(self, total: int, width: int = 40, label: str = "") -> None:
        self.total = total
        self.width = width
        self.label = label
        self.current = 0

    def update(self, n: int = 1) -> None:
        self.current += n
        self._render()

    def _render(self) -> None:
        pct = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * pct)
        bar = "█" * filled + "░" * (self.width - filled)
        prefix = f"{self.label} " if self.label else ""
        sys.stdout.write(f"\r{prefix}{bar} {pct:.0%} ({self.current}/{self.total})")
        sys.stdout.flush()
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def finish(self) -> None:
        self.current = self.total
        self._render()


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------

def print_table(headers: list, rows: list, file: TextIO = sys.stdout) -> None:
    """Print a formatted table."""
    if not rows:
        return
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers), file=file)
    print(fmt.format(*("-" * w for w in widths)), file=file)
    for row in rows:
        print(fmt.format(*(str(c) for c in row)), file=file)
