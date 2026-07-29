"""ikigoroba — Desktop shell: taskbar, start menu, desktop icons, system tray."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .igaragaza import (
    Color, Compositor, Event, EventType, FontRenderer, Point, Rect,
    Theme, Window, WindowState,
)
from .ibikoresho_bya_GUI import (
    Button, Container, Label, Menu, MenuBar, MenuItem, Panel, Widget,
)


# ─── Desktop Icon ────────────────────────────────────────────────────────────

@dataclass
class DesktopIcon:
    name: str = ""
    icon: str = "📄"
    x: int = 0
    y: int = 0
    width: int = 80
    height: int = 80
    selected: bool = False
    on_double_click: Optional[Callable] = None
    description: str = ""

    def contains(self, px: int, py: int) -> bool:
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height


# ─── System Tray ─────────────────────────────────────────────────────────────

@dataclass
class TrayIcon:
    icon: str = ""
    tooltip: str = ""
    on_click: Optional[Callable] = None


class SystemTray:
    def __init__(self):
        self.icons: List[TrayIcon] = []
        self._clock: str = ""

    def add(self, icon: TrayIcon) -> None:
        self.icons.append(icon)

    def update_clock(self) -> None:
        import time
        self._clock = time.strftime("%H:%M")

    def render(self, canvas: tk.Canvas, font: FontRenderer, x: int, y: int,
               width: int, height: int) -> int:
        self.update_clock()
        rx = x + width
        cw = font.measure(self._clock)[0] + 16
        rx -= cw
        font.draw(self._clock, rx + cw // 2, y + height // 2,
                   color=Color.WHITE, size=Theme.font_size_normal, anchor="center")
        rx -= 8
        for icon in reversed(self.icons):
            rx -= 24
            font.draw(icon.icon, rx + 12, y + height // 2, color=Color.WHITE,
                       size=Theme.font_size_large, anchor="center")
        return rx


# ─── Taskbar ─────────────────────────────────────────────────────────────────

class Taskbar:
    def __init__(self, compositor: Compositor):
        self.compositor = compositor
        self.height = Theme.taskbar_height
        self.background = Theme.taskbar_background
        self._start_open: bool = False
        self._hovered_button: Optional[Window] = None
        self.system_tray = SystemTray()
        self._start_items: List[Dict[str, Any]] = [
            {"text": "File Explorer", "icon": "📁", "action": "explorer"},
            {"text": "Notepad", "icon": "📝", "action": "notepad"},
            {"text": "Terminal", "icon": "💻", "action": "terminal"},
            {"text": "Settings", "icon": "⚙", "action": "settings"},
            {"text": "Calculator", "icon": "🔢", "action": "calculator"},
        ]

    @property
    def rect(self) -> Rect:
        return Rect(0, self.compositor.screen_height - self.height,
                     self.compositor.screen_width, self.height)

    def handle_click(self, x: int, y: int) -> Optional[str]:
        tr = self.rect
        if not tr.contains(x, y):
            self._start_open = False
            return None

        if x < 50:
            self._start_open = not self._start_open
            return "start"

        running = [w for w in self.compositor.windows if w.visible and w.state == WindowState.NORMAL]
        bx = 50
        for win in running:
            tw = len(win.title) * 7 + 24
            bw = min(180, max(80, tw))
            if bx <= x < bx + bw:
                if self.compositor.focused_window == win:
                    win.minimize()
                else:
                    if win.state == WindowState.MINIMIZED:
                        win.restore()
                    self.compositor.focus_window(win)
                return "taskbar-button"
            bx += bw

        return "tray"

    def handle_start_click(self, action: str) -> None:
        self._start_open = False
        if action == "explorer":
            self._open_explorer()
        elif action == "notepad":
            self._open_notepad()
        elif action == "terminal":
            self._open_terminal()
        elif action == "settings":
            self._open_settings()
        elif action == "calculator":
            self._open_calculator()

    def _open_explorer(self) -> None:
        w = self.compositor.create_window("File Explorer", 50, 50, 700, 500)
        self._setup_explorer(w)

    def _setup_explorer(self, win: Window) -> None:
        p = Panel(0, 0, win.client_rect.width, win.client_rect.height)
        p.bg_color = Color.WHITE
        addr = Label(4, 4, 200, 20, "C:\\Users\\IUser\\Documents", bold=True)
        p.add(addr)
        folders = Label(4, 30, 680, 20, "📁  Projects    📁  Downloads    📁  Pictures    📁  Music", bold=False)
        folders.color = Color.BLUE
        p.add(folders)
        files = Label(4, 55, 680, 380,
                       "📄  report.txt          3 KB\n📄  notes.md            1 KB\n📄  presentation.pptx   2 MB\n📄  budget.xlsx         45 KB\n📄  photo.jpg           3 MB\n📄  code.py             8 KB",
                       bold=False)
        p.add(files)
        win.background_color = Color.WHITE
        win._on_resize = lambda e: setattr(p, 'rect', Rect(0, 0, win.client_rect.width, win.client_rect.height))

    def _open_notepad(self) -> None:
        w = self.compositor.create_window("Untitled - Notepad", 100, 100, 600, 400)
        p = Panel(0, 0, w.client_rect.width, w.client_rect.height)
        p.bg_color = Color.WHITE
        text_area = Label(4, 4, 580, 360,
                          "Welcome to SISITEMU Notepad\n\n"
                          "This is a beautiful Windows-like operating system\n"
                          "built entirely with the I Language.\n\n"
                          "You can type, save, and edit documents.\n"
                          "The compositor handles window management,\n"
                          "the taskbar shows running applications,\n"
                          "and the start menu launches programs.",
                          bold=False)
        p.add(text_area)
        w.background_color = Color.WHITE

    def _open_terminal(self) -> None:
        w = self.compositor.create_window("Terminal", 150, 150, 650, 400)
        p = Panel(0, 0, w.client_rect.width, w.client_rect.height)
        p.bg_color = Color.rgb(0x1E, 0x1E, 0x1E)
        text = Label(4, 4, 630, 360,
                     "SISITEMU OS v1.0 - I Language Terminal\n"
                     "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                     "C:\\Users\\IUser> _\n\n"
                     "Available commands:\n"
                     "  dir    - List directory contents\n"
                     "  type   - Display file contents\n"
                     "  cls    - Clear screen\n"
                     "  echo   - Display a message",
                     bold=False)
        text.color = Color.rgb(0x00, 0xFF, 0x00)
        p.add(text)
        w.background_color = Color.rgb(0x1E, 0x1E, 0x1E)

    def _open_settings(self) -> None:
        w = self.compositor.create_window("Settings", 200, 100, 500, 450)
        p = Panel(0, 0, w.client_rect.width, w.client_rect.height)
        p.bg_color = Color.WHITE
        items = [
            Label(4, 4, 480, 24, "⚙  System Settings", bold=True),
            Label(4, 32, 480, 20, "Display      1920 × 1080   💡 100%"),
            Label(4, 56, 480, 20, "Sound        Speakers     🔊 75%"),
            Label(4, 80, 480, 20, "Network      Wi-Fi Connected  📶"),
            Label(4, 104, 480, 20, "Bluetooth    On              🛜"),
            Label(4, 128, 480, 20, "Theme        Light           🎨"),
            Label(4, 152, 480, 20, "About        SISITEMU v1.0  ℹ️"),
        ]
        for item in items:
            p.add(item)
        w.background_color = Color.WHITE

    def _open_calculator(self) -> None:
        w = self.compositor.create_window("Calculator", 300, 200, 250, 300)
        p = Panel(0, 0, w.client_rect.width, w.client_rect.height)
        p.bg_color = Color.rgb(0xF0, 0xF0, 0xF0)
        display = Label(4, 4, 234, 30, "42", bold=True)
        display.font_size = Theme.font_size_large
        p.add(display)
        buttons_rows = [
            "7  8  9  ÷",
            "4  5  6  ×",
            "1  2  3  −",
            "0  .  =  +",
        ]
        by = 40
        for row in buttons_rows:
            bx = 4
            for ch in row.split("  "):
                btn_text = ch.strip()
                if btn_text:
                    b = Button(bx, by, 50, 24, btn_text)
                    p.add(b)
                bx += 56
            by += 28
        w.background_color = Color.rgb(0xF0, 0xF0, 0xF0)

    def render(self, canvas: tk.Canvas, font: FontRenderer) -> None:
        tr = self.rect
        canvas.create_rectangle(tr.x, tr.y, tr.right, tr.bottom,
                                 fill=self.background, outline="", tags="desktop")

        canvas.create_rectangle(tr.x + 2, tr.y + 4, tr.x + 46, tr.bottom - 4,
                                 fill=Color.rgb(0x30, 0x30, 0x30) if self._start_open else Color.rgb(0x28, 0x28, 0x28),
                                 outline="", tags="desktop")
        font.draw("⊞", tr.x + 24, tr.y + tr.height // 2, color=Color.WHITE,
                   size=Theme.font_size_large, anchor="center")

        running = [w for w in self.compositor.windows
                   if w.visible and w.state == WindowState.NORMAL]
        bx = 50
        for win in running:
            focused = win == self.compositor.focused_window
            hovered = win == self._hovered_button
            bw = min(180, max(100, font.measure(win.title)[0] + 24))
            bg = Theme.taskbar_button_active if focused else (Theme.taskbar_button_hover if hovered else Color.rgb(0x28, 0x28, 0x28))
            canvas.create_rectangle(bx, tr.y + 4, bx + bw, tr.bottom - 4,
                                     fill=bg, outline="", tags="desktop")
            if focused:
                canvas.create_rectangle(bx, tr.y + 4, bx + bw, tr.y + 6,
                                         fill=Theme.highlight, outline="", tags="desktop")
            font.draw(win.title, bx + bw // 2, tr.y + tr.height // 2,
                       color=Color.WHITE, size=Theme.font_size_normal, anchor="center")
            bx += bw + 2

        self.system_tray.render(canvas, font, bx, tr.y, tr.right - bx, tr.height)

        if self._start_open:
            self._render_start_menu(canvas, font, tr)

    def _render_start_menu(self, canvas: tk.Canvas, font: FontRenderer, tr: Rect) -> None:
        sm_w, sm_h = 300, 400
        sm_x = 2
        sm_y = tr.y - sm_h - 4
        canvas.create_rectangle(sm_x, sm_y, sm_x + sm_w, sm_y + sm_h,
                                 fill=Color.rgb(0x28, 0x28, 0x28),
                                 outline=Color.rgb(0x40, 0x40, 0x40), tags="desktop")
        font.draw("SISITEMU", sm_x + sm_w // 2, sm_y + 20, color=Color.WHITE,
                   size=Theme.font_size_large, bold=True, anchor="center")
        canvas.create_line(sm_x + 12, sm_y + 32, sm_x + sm_w - 12, sm_y + 32,
                            fill=Color.rgb(0x40, 0x40, 0x40), tags="desktop")

        iy = sm_y + 44
        for item in self._start_items:
            canvas.create_rectangle(sm_x + 4, iy, sm_x + sm_w - 4, iy + 36,
                                     fill=Color.rgb(0x34, 0x34, 0x34) if False else Color.TRANSPARENT,
                                     outline="", tags="desktop")
            font.draw(f"{item['icon']}  {item['text']}", sm_x + 16, iy + 18,
                       color=Color.WHITE, size=Theme.font_size_normal, anchor="w")
            iy += 40

        canvas.create_line(sm_x + 12, sm_y + sm_h - 48, sm_x + sm_w - 12, sm_y + sm_h - 48,
                            fill=Color.rgb(0x40, 0x40, 0x40), tags="desktop")
        font.draw("⏻  Power    ⚙  Settings    📁  Files",
                   sm_x + sm_w // 2, sm_y + sm_h - 24,
                   color=Color.GRAY_75, size=Theme.font_size_normal, anchor="center")


# ─── Desktop ─────────────────────────────────────────────────────────────────

class Desktop:
    """The desktop environment — manages the background, icons, taskbar, and start menu."""

    def __init__(self, compositor: Compositor):
        self.compositor = compositor
        self.taskbar = Taskbar(compositor)
        self.icons: List[DesktopIcon] = []
        self._selected_icon: Optional[DesktopIcon] = None
        self._init_icons()

        compositor.on_frame(self._on_frame)

    def _init_icons(self) -> None:
        self.icons = [
            DesktopIcon("File Explorer", "📁", 20, 20, on_double_click=lambda: self.taskbar._open_explorer(), description="Browse files"),
            DesktopIcon("Notepad", "📝", 20, 110, on_double_click=lambda: self.taskbar._open_notepad(), description="Text editor"),
            DesktopIcon("Terminal", "💻", 20, 200, on_double_click=lambda: self.taskbar._open_terminal(), description="Command line"),
            DesktopIcon("Settings", "⚙", 20, 290, on_double_click=lambda: self.taskbar._open_settings(), description="System settings"),
            DesktopIcon("Calculator", "🔢", 110, 20, on_double_click=lambda: self.taskbar._open_calculator(), description="Calculator"),
            DesktopIcon("Recycle Bin", "🗑️", 110, 110, description="Deleted items"),
        ]

    def _on_frame(self) -> None:
        pass

    def handle_click(self, x: int, y: int, button: int = 1) -> bool:
        if self.taskbar.rect.contains(x, y):
            result = self.taskbar.handle_click(x, y)
            if result == "start":
                pass
            return True

        for icon in self.icons:
            if icon.contains(x, y):
                self._selected_icon = icon
                icon.selected = True
                return True
            else:
                icon.selected = False

        self._selected_icon = None
        return False

    def handle_double_click(self, x: int, y: int) -> bool:
        for icon in self.icons:
            if icon.contains(x, y) and icon.on_double_click:
                icon.on_double_click()
                return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer) -> None:
        for icon in self.icons:
            bg = Color.rgb(0x00, 0x78, 0xD7, 0x40) if icon.selected else Color.TRANSPARENT
            if icon.selected:
                canvas.create_rectangle(icon.x - 4, icon.y - 4,
                                         icon.x + icon.width + 4, icon.y + icon.height + 4,
                                         fill=Color.rgb(0x00, 0x78, 0xD7),
                                         stipple="gray25", outline="", tags="desktop")
                canvas.create_rectangle(icon.x - 4, icon.y - 4,
                                         icon.x + icon.width + 4, icon.y + icon.height + 4,
                                         fill=Color.rgb(0x00, 0x5A, 0x9E, 0x60),
                                         outline=Color.rgb(0x00, 0x78, 0xD7), tags="desktop")
            font.draw(icon.icon, icon.x + icon.width // 2, icon.y + 24,
                       color=Color.WHITE, size=24, anchor="center")
            font.draw(icon.name, icon.x + icon.width // 2, icon.y + 58,
                       color=Color.WHITE, size=Theme.font_size_icon, anchor="center")
        self.taskbar.render(canvas, font)

    def handle_key(self, event: Event) -> bool:
        if event.key == "Return" and self._selected_icon and self._selected_icon.on_double_click:
            self._selected_icon.on_double_click()
            return True
        return False
