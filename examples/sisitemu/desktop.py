"""SISITEMU Desktop — A beautiful Windows-like operating system demonstration."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from sisitemu.igaragaza import Compositor, Color, Theme
from sisitemu.ikigoroba import Desktop

compositor: Compositor
desktop: Desktop


def main():
    global compositor, desktop

    compositor = Compositor(width=1280, height=720,
                            title="SISITEMU OS — Windows-like Desktop")
    desktop = Desktop(compositor)

    compositor.set_background_handler(
        click_handler=lambda x, y, btn: desktop.handle_click(x, y, btn),
        dblclick_handler=lambda x, y: desktop.handle_double_click(x, y),
        renderer=lambda canvas, font: desktop.render(canvas, font),
    )

    explorer = compositor.create_window("File Explorer", 50, 30, 700, 500)
    desktop.taskbar._setup_explorer(explorer)

    notepad = compositor.create_window("Untitled - Notepad", 120, 60, 600, 450)
    desktop.taskbar._open_notepad()

    compositor.run()


if __name__ == "__main__":
    main()
