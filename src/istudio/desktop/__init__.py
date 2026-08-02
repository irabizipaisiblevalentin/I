"""I STUDIO — Desktop application (tkinter).

The desktop package layers a graphical IDE on top of the I Studio engine.
Pure-logic modules (theme, highlight, runner, controller) are headless and
fully testable; the widget modules (editor, sidebar, panel, app) require a
display (tkinter).
"""

from __future__ import annotations

from ..ibikoreshingiro import EditorTheme
from .controller import DesktopController
from .highlight import tokenize_line
from .runner import ScriptRunner
from .theme import get_palette, theme_names

DESKTOP_VERSION = "1.0.0"

__all__ = [
    "DESKTOP_VERSION",
    "DesktopController",
    "EditorTheme",
    "ScriptRunner",
    "get_palette",
    "theme_names",
    "tokenize_line",
]


def is_available() -> bool:
    """Return True if a tkinter display is available (GUI can launch)."""
    try:
        import tkinter

        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:  # pragma: no cover
        return False


def main(argv=None) -> int:
    from .app import main as _main

    return _main(argv)
