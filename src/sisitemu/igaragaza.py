"""igaragaza — Display server: compositor, window manager, rendering, input."""

from __future__ import annotations

import math
import time
import tkinter as tk
import tkinter.font as tkfont
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─── Geometry ───────────────────────────────────────────────────────────────

@dataclass
class Point:
    x: int = 0
    y: int = 0


@dataclass
class Rect:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def left(self) -> int: return self.x
    @property
    def top(self) -> int: return self.y
    @property
    def right(self) -> int: return self.x + self.width
    @property
    def bottom(self) -> int: return self.y + self.height
    @property
    def center(self) -> Point: return Point(self.x + self.width // 2, self.y + self.height // 2)

    def contains(self, px: int, py: int) -> bool:
        return self.left <= px < self.right and self.top <= py < self.bottom

    def intersect(self, other: Rect) -> Rect:
        x = max(self.x, other.x); y = max(self.y, other.y)
        w = min(self.right, other.right) - x; h = min(self.bottom, other.bottom) - y
        if w < 0 or h < 0: return Rect()
        return Rect(x, y, w, h)

    def inflate(self, dx: int, dy: int) -> Rect:
        return Rect(self.x - dx, self.y - dy, self.width + dx * 2, self.height + dy * 2)


# ─── Color ───────────────────────────────────────────────────────────────────

class Color:
    @staticmethod
    def rgb(r: int, g: int, b: int, a: int = 255) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def rgba(r: int, g: int, b: int, a: int = 255) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def blend(hex_color: str, alpha: float) -> str:
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        return f"#{r:02x}{g:02x}{b:02x}"

    WHITE = "#FFFFFF"
    BLACK = "#000000"
    GRAY_50 = "#808080"
    GRAY_75 = "#BFBFBF"
    GRAY_85 = "#D9D9D9"
    GRAY_90 = "#E5E5E5"
    GRAY_95 = "#F2F2F2"
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    TRANSPARENT = ""


# ─── Theme (Windows 11 inspired) ────────────────────────────────────────────

class Theme:
    title_bar_active = Color.rgb(0x00, 0x78, 0xD7)
    title_bar_active_text = Color.WHITE
    title_bar_inactive = Color.GRAY_85
    title_bar_inactive_text = Color.GRAY_50
    title_bar_height = 30
    border_width = 1
    border_color = Color.rgb(0x00, 0x5A, 0x9E)
    resize_border = 4

    desktop_background = Color.rgb(0x1E, 0x90, 0xFF)
    desktop_background_bottom = Color.rgb(0x00, 0x45, 0x87)

    taskbar_background = Color.rgb(0x20, 0x20, 0x20)
    taskbar_height = 40
    taskbar_button_active = Color.rgb(0x50, 0x50, 0x50)
    taskbar_button_hover = Color.rgb(0x3A, 0x3A, 0x3A)

    button_face = Color.GRAY_95
    button_hover = Color.rgb(0xE0, 0xE0, 0xE0)
    button_pressed = Color.rgb(0xC0, 0xC0, 0xC0)
    button_border = Color.GRAY_75
    button_text = Color.BLACK

    textbox_background = Color.WHITE
    textbox_border = Color.GRAY_75
    textbox_focused_border = Color.rgb(0x00, 0x78, 0xD7)
    textbox_text = Color.BLACK

    label_text = Color.BLACK
    link_text = Color.rgb(0x00, 0x56, 0xB3)

    highlight = Color.rgb(0x00, 0x78, 0xD7)
    highlight_text = Color.WHITE

    window_background = Color.rgb(0xF0, 0xF0, 0xF0)
    panel_background = Color.WHITE

    menu_background = Color.WHITE
    menu_border = Color.GRAY_75
    menu_hover = Color.rgb(0xE0, 0xE0, 0xE0)
    menu_text = Color.BLACK
    menu_disabled_text = Color.GRAY_50

    scrollbar_face = Color.GRAY_85
    scrollbar_hover = Color.GRAY_75
    scrollbar_width = 12

    font_family = "Segoe UI"
    font_size_normal = 10
    font_size_title = 10
    font_size_icon = 8
    font_size_large = 12


# ─── Event System ───────────────────────────────────────────────────────────

class EventType(Enum):
    MOUSE_MOVE = auto()
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()
    MOUSE_CLICK = auto()
    MOUSE_DOUBLE_CLICK = auto()
    KEY_DOWN = auto()
    KEY_UP = auto()
    KEY_CHAR = auto()
    FOCUS_GAINED = auto()
    FOCUS_LOST = auto()
    WINDOW_CLOSE = auto()
    WINDOW_RESIZE = auto()
    WINDOW_MOVE = auto()
    WINDOW_MINIMIZE = auto()
    WINDOW_MAXIMIZE = auto()
    WINDOW_RESTORE = auto()
    SCROLL = auto()
    DRAG_START = auto()
    DRAG_END = auto()
    DRAG_MOVE = auto()


@dataclass
class Event:
    type: EventType
    x: int = 0
    y: int = 0
    button: int = 0
    key: str = ""
    char: str = ""
    delta: int = 0
    target: Any = None
    handled: bool = False


EventHandler = Callable[[Event], None]


# ─── Font Rendering ─────────────────────────────────────────────────────────

class FontRenderer:
    """Renders text using tkinter fonts, measuring and drawing on Canvas."""

    def __init__(self, canvas: tk.Canvas):
        self._canvas = canvas
        self._fonts: Dict[str, tk.font.Font] = {}

    def _get_font(self, family: str = Theme.font_family, size: int = Theme.font_size_normal,
                  bold: bool = False) -> tk.font.Font:
        key = f"{family}_{size}_{bold}"
        if key not in self._fonts:
            self._fonts[key] = tkfont.Font(family=family, size=size, weight="bold" if bold else "normal")
        return self._fonts[key]

    def measure(self, text: str, family: str = Theme.font_family,
                size: int = Theme.font_size_normal) -> Tuple[int, int]:
        f = self._get_font(family, size)
        return f.measure(text), f.metrics("linespace")

    def draw(self, text: str, x: int, y: int, color: str = Theme.label_text,
             family: str = Theme.font_family, size: int = Theme.font_size_normal,
             bold: bool = False, anchor: str = "nw") -> None:
        if not text:
            return
        f = self._get_font(family, size, bold)
        self._canvas.create_text(x, y, text=text, font=f, fill=color, anchor=anchor, tags="text")


# ─── Window ─────────────────────────────────────────────────────────────────

class WindowState(Enum):
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    CLOSED = "closed"


class Window:
    def __init__(self, compositor: Compositor, title: str = "",
                 x: int = 100, y: int = 100, width: int = 600, height: int = 400):
        self.compositor = compositor
        self.title = title
        self.rect = Rect(x, y, width, height)
        self.state = WindowState.NORMAL
        self.visible = True
        self.has_title_bar = True
        self.has_border = True
        self.resizable = True
        self.minimizable = True
        self.maximizable = True
        self.closable = True
        self.z_order: int = 0
        self.opacity: float = 1.0
        self.border_color: str = Theme.border_color
        self.background_color: str = Theme.window_background
        self.icon: Optional[str] = None
        self._saved_rect: Optional[Rect] = None
        self._on_close: Optional[EventHandler] = None
        self._on_resize: Optional[EventHandler] = None

    @property
    def client_rect(self) -> Rect:
        t = Theme.title_bar_height if self.has_title_bar else 0
        b = Theme.border_width if self.has_border else 0
        return Rect(self.rect.x + b, self.rect.y + t + b,
                     self.rect.width - b * 2, self.rect.height - t - b * 2)

    def close(self) -> None:
        self.state = WindowState.CLOSED
        self.visible = False
        if self._on_close:
            self._on_close(Event(EventType.WINDOW_CLOSE, target=self))

    def minimize(self) -> None:
        if self.state == WindowState.NORMAL:
            self._saved_rect = Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.state = WindowState.MINIMIZED
        self.visible = False

    def maximize(self) -> None:
        if self.state != WindowState.MAXIMIZED:
            self._saved_rect = Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
            screen = self.compositor.screen
            self.rect = Rect(0, 0, screen.width, screen.height - Theme.taskbar_height)
            self.state = WindowState.MAXIMIZED

    def restore(self) -> None:
        if self._saved_rect:
            self.rect = self._saved_rect
            self._saved_rect = None
        self.state = WindowState.NORMAL
        self.visible = True

    def move(self, dx: int, dy: int) -> None:
        self.rect.x += dx
        self.rect.y += dy

    def resize(self, width: int, height: int) -> None:
        self.rect.width = max(100, width)
        self.rect.height = max(50, height)
        if self._on_resize:
            self._on_resize(Event(EventType.WINDOW_RESIZE, target=self))

    def hit_test(self, px: int, py: int) -> str:
        if not self.visible or self.state != WindowState.NORMAL:
            return "none"
        if not self.rect.contains(px, py):
            return "none"
        r = self.rect
        b = Theme.resize_border
        if self.resizable:
            if px < r.x + b and py < r.y + b: return "resize-tl"
            if px >= r.right - b and py < r.y + b: return "resize-tr"
            if px < r.x + b and py >= r.bottom - b: return "resize-bl"
            if px >= r.right - b and py >= r.bottom - b: return "resize-br"
            if px < r.x + b: return "resize-w"
            if px >= r.right - b: return "resize-e"
            if py < r.y + b: return "resize-n"
            if py >= r.bottom - b: return "resize-s"
        if self.has_title_bar and py < r.y + Theme.title_bar_height:
            return "title"
        return "client"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "rect": (self.rect.x, self.rect.y, self.rect.width, self.rect.height),
            "state": self.state.value,
            "visible": self.visible,
        }


# ─── Cursors ─────────────────────────────────────────────────────────────────

class CursorShape(Enum):
    DEFAULT = "arrow"
    HAND = "hand2"
    TEXT = "xterm"
    MOVE = "fleur"
    RESIZE_N = "top_side"
    RESIZE_S = "bottom_side"
    RESIZE_E = "right_side"
    RESIZE_W = "left_side"
    RESIZE_NE = "top_right_corner"
    RESIZE_NW = "top_left_corner"
    RESIZE_SE = "bottom_right_corner"
    RESIZE_SW = "bottom_left_corner"
    WAIT = "watch"
    CROSSHAIR = "crosshair"


# ─── Compositor ──────────────────────────────────────────────────────────────

class Compositor:
    """The display server. Manages the screen, windows, compositing, and input."""

    def __init__(self, width: int = 1280, height: int = 720, title: str = "SISITEMU Desktop"):
        self.screen_width = width
        self.screen_height = height
        self.windows: List[Window] = []
        self.focused_window: Optional[Window] = None
        self.cursor_shape: CursorShape = CursorShape.DEFAULT
        self.running = False
        self._window_counter = 0
        self._drag_window: Optional[Window] = None
        self._drag_type: str = ""
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._drag_start_rect: Optional[Rect] = None
        self._double_click_time = 0.0
        self._last_click_time = 0.0
        self._last_click_x = 0
        self._last_click_y = 0

        self._tk = tk.Tk()
        self._tk.title(title)
        self._tk.geometry(f"{width}x{height}+50+50")
        self.screen_height = height - 0
        self._canvas = tk.Canvas(self._tk, width=width, height=height, highlightthickness=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self.font = FontRenderer(self._canvas)

        self._bind_events()
        self._on_frame_callbacks: List[Callable] = []
        self._background_click_handler: Optional[Callable] = None
        self._background_dblclick_handler: Optional[Callable] = None
        self._background_renderer: Optional[Callable] = None

    def set_background_handler(self, click_handler: Optional[Callable] = None,
                                dblclick_handler: Optional[Callable] = None,
                                renderer: Optional[Callable] = None) -> None:
        self._background_click_handler = click_handler
        self._background_dblclick_handler = dblclick_handler
        self._background_renderer = renderer

    def on_frame(self, callback: Callable) -> None:
        self._on_frame_callbacks.append(callback)

    def _bind_events(self) -> None:
        c = self._canvas
        c.bind("<Motion>", self._on_mouse_move)
        c.bind("<ButtonPress-1>", lambda e: self._on_mouse_down(e, 1))
        c.bind("<ButtonRelease-1>", lambda e: self._on_mouse_up(e, 1))
        c.bind("<ButtonPress-3>", lambda e: self._on_mouse_down(e, 3))
        c.bind("<ButtonRelease-3>", lambda e: self._on_mouse_up(e, 3))
        c.bind("<Double-Button-1>", lambda e: self._on_double_click(e))
        c.bind("<B1-Motion>", self._on_drag_move)
        c.bind("<Key>", self._on_key)
        c.bind("<Configure>", self._on_configure)
        c.focus_set()

    @property
    def screen(self) -> Rect:
        return Rect(0, 0, self.screen_width, self.screen_height)

    def create_window(self, title: str = "", x: int = 100, y: int = 100,
                      width: int = 600, height: int = 400) -> Window:
        self._window_counter += 1
        offset = self._window_counter * 20
        win = Window(self, title or f"Window {self._window_counter}",
                      x + offset % 200, y + offset % 200, width, height)
        win.z_order = len(self.windows)
        self.windows.append(win)
        self.focus_window(win)
        return win

    def focus_window(self, window: Window) -> None:
        if window and window.state != WindowState.NORMAL:
            return
        if self.focused_window and self.focused_window != window:
            old = self.focused_window
            self._dispatch(old, Event(EventType.FOCUS_LOST, target=old))
        self.focused_window = window
        if window:
            self.windows.remove(window)
            window.z_order = len(self.windows)
            self.windows.append(window)
            self._dispatch(window, Event(EventType.FOCUS_GAINED, target=window))

    def close_window(self, window: Window) -> None:
        window.close()
        if window in self.windows:
            self.windows.remove(window)
        if self.focused_window == window:
            self.focused_window = self.windows[-1] if self.windows else None

    def _dispatch(self, window: Optional[Window], event: Event) -> None:
        if window:
            event.target = window
            if window._on_close and event.type == EventType.WINDOW_CLOSE:
                window._on_close(event)
            if window._on_resize and event.type == EventType.WINDOW_RESIZE:
                window._on_resize(event)

    def _get_window_at(self, px: int, py: int) -> Tuple[Optional[Window], str]:
        for win in reversed(self.windows):
            if not win.visible or win.state != WindowState.NORMAL:
                continue
            ht = win.hit_test(px, py)
            if ht != "none":
                return win, ht
        return None, "none"

    def _update_cursor(self, hit_test: str) -> None:
        mapping = {
            "title": CursorShape.DEFAULT, "client": CursorShape.DEFAULT,
            "resize-n": CursorShape.RESIZE_N, "resize-s": CursorShape.RESIZE_S,
            "resize-e": CursorShape.RESIZE_E, "resize-w": CursorShape.RESIZE_W,
            "resize-ne": CursorShape.RESIZE_NE, "resize-nw": CursorShape.RESIZE_NW,
            "resize-se": CursorShape.RESIZE_SE, "resize-sw": CursorShape.RESIZE_SW,
            "resize-tl": CursorShape.RESIZE_NW, "resize-tr": CursorShape.RESIZE_NE,
            "resize-bl": CursorShape.RESIZE_SW, "resize-br": CursorShape.RESIZE_SE,
        }
        shape = mapping.get(hit_test, CursorShape.DEFAULT)
        if shape != self.cursor_shape:
            self.cursor_shape = shape
            self._canvas.config(cursor=shape.value)

    def _on_mouse_move(self, e: tk.Event) -> None:
        win, ht = self._get_window_at(e.x, e.y)
        self._update_cursor(ht)

    def _on_mouse_down(self, e: tk.Event, button: int) -> None:
        win, ht = self._get_window_at(e.x, e.y)
        if not win:
            self.focused_window = None
            if self._background_click_handler:
                self._background_click_handler(e.x, e.y, button)
            return

        self.focus_window(win)

        if ht == "title":
            self._drag_window = win
            self._drag_type = "move"
            self._drag_start_x = e.x
            self._drag_start_y = e.y
            self._drag_start_rect = Rect(win.rect.x, win.rect.y, win.rect.width, win.rect.height)
        elif ht.startswith("resize"):
            self._drag_window = win
            self._drag_type = ht
            self._drag_start_x = e.x
            self._drag_start_y = e.y
            self._drag_start_rect = Rect(win.rect.x, win.rect.y, win.rect.width, win.rect.height)
        elif ht == "client":
            pass

    def _on_mouse_up(self, e: tk.Event, button: int) -> None:
        now = time.time()
        if self._drag_window and self._drag_type == "move":
            if abs(e.x - self._drag_start_x) < 3 and abs(e.y - self._drag_start_y) < 3:
                if now - self._last_click_time < 0.3 and abs(e.x - self._last_click_x) < 5:
                    win = self._drag_window
                    if win.state == WindowState.MAXIMIZED:
                        win.restore()
                    else:
                        win.maximize()
                self._last_click_time = now
                self._last_click_x = e.x
                self._last_click_y = e.y
        self._drag_window = None
        self._drag_type = ""

    def _on_drag_move(self, e: tk.Event) -> None:
        if not self._drag_window or not self._drag_start_rect:
            return
        win = self._drag_window
        dx = e.x - self._drag_start_x
        dy = e.y - self._drag_start_y
        sr = self._drag_start_rect

        if self._drag_type == "move":
            win.rect.x = sr.x + dx
            win.rect.y = sr.y + dy
        elif self._drag_type == "resize-e":
            win.resize(sr.width + dx, sr.height)
        elif self._drag_type == "resize-s":
            win.resize(sr.width, sr.height + dy)
        elif self._drag_type == "resize-se" or self._drag_type == "resize-br":
            win.resize(sr.width + dx, sr.height + dy)
        elif self._drag_type == "resize-sw" or self._drag_type == "resize-bl":
            win.resize(sr.width - dx, sr.height + dy)
            win.rect.x = sr.x + dx
        elif self._drag_type == "resize-ne" or self._drag_type == "resize-tr":
            win.resize(sr.width + dx, sr.height - dy)
            win.rect.y = sr.y + dy
        elif self._drag_type == "resize-nw" or self._drag_type == "resize-tl":
            win.resize(sr.width - dx, sr.height - dy)
            win.rect.x = sr.x + dx
            win.rect.y = sr.y + dy
        elif self._drag_type == "resize-n":
            win.resize(sr.width, sr.height - dy)
            win.rect.y = sr.y + dy
        elif self._drag_type == "resize-w":
            win.resize(sr.width - dx, sr.height)
            win.rect.x = sr.x + dx

    def _on_double_click(self, e: tk.Event) -> None:
        win, ht = self._get_window_at(e.x, e.y)
        if win and ht == "title":
            if win.state == WindowState.MAXIMIZED:
                win.restore()
            else:
                win.maximize()
        elif not win and self._background_dblclick_handler:
            self._background_dblclick_handler(e.x, e.y)

    def _on_key(self, e: tk.Event) -> None:
        if self.focused_window:
            ev = Event(EventType.KEY_DOWN, key=e.keysym, char=e.char if e.char else "")
            self._dispatch(self.focused_window, ev)

    def _on_configure(self, e: tk.Event) -> None:
        self.screen_width = e.width
        self.screen_height = e.height

    def render(self) -> None:
        self._canvas.delete("all")
        self._draw_background()
        if self._background_renderer:
            self._background_renderer(self._canvas, self.font)
        for win in self.windows:
            if win.visible and win.state != WindowState.MINIMIZED:
                self._draw_window(win)
        for cb in self._on_frame_callbacks:
            cb()

    def _draw_background(self) -> None:
        w, h = self.screen_width, self.screen_height
        steps = 20
        for i in range(steps):
            t = i / steps
            r = int(0x1E + (0x00 - 0x1E) * t)
            g = int(0x90 + (0x45 - 0x90) * t)
            b = int(0xFF + (0x87 - 0xFF) * t)
            y0 = int(h * i / steps)
            y1 = int(h * (i + 1) / steps)
            color = Color.rgb(r, g, b)
            self._canvas.create_rectangle(0, y0, w, y1, fill=color, outline="", tags="bg")

    def _draw_window(self, win: Window) -> None:
        r = win.rect
        if win.has_border:
            self._canvas.create_rectangle(r.x - 1, r.y - 1, r.right + 1, r.bottom + 1,
                                            fill=win.border_color, outline="", tags="w")
        bg = win.background_color
        self._canvas.create_rectangle(r.x, r.y, r.right, r.bottom, fill=bg, outline="", tags="w")

        if win.has_title_bar:
            ty = r.y
            is_active = win == self.focused_window
            tb_color = Theme.title_bar_active if is_active else Theme.title_bar_inactive
            tt_color = Theme.title_bar_active_text if is_active else Theme.title_bar_inactive_text
            tb_height = Theme.title_bar_height

            self._canvas.create_rectangle(r.x, ty, r.right, ty + tb_height,
                                            fill=tb_color, outline="", tags="w")

            self._canvas.create_line(r.x, ty + tb_height, r.right, ty + tb_height,
                                       fill=Theme.border_color, tags="w")

            if win.title:
                self.font.draw(win.title, r.x + 8, ty + tb_height // 2, color=tt_color,
                                size=Theme.font_size_title, anchor="w")

            bx = r.right - 5
            bs = 12
            by = ty + (tb_height - bs) // 2

            if win.minimizable:
                bx -= bs + 2
                self._canvas.create_rectangle(bx, by + bs // 2 - 1, bx + bs, by + bs // 2 + 1,
                                                fill=tt_color, outline="", tags="w")
            if win.maximizable:
                bx -= bs + 2
                self._canvas.create_rectangle(bx + 2, by + 2, bx + bs - 2, by + bs - 2,
                                                outline=tt_color, tags="w")
            if win.closable:
                bx -= bs + 2
                self._canvas.create_line(bx + 3, by + 3, bx + bs - 3, by + bs - 3,
                                           fill=tt_color, width=2, tags="w")
                self._canvas.create_line(bx + bs - 3, by + 3, bx + 3, by + bs - 3,
                                           fill=tt_color, width=2, tags="w")

    def start(self) -> None:
        self.running = True
        self._loop()

    def _loop(self) -> None:
        if not self.running:
            return
        self.render()
        self._tk.update_idletasks()
        self._tk.update()
        self._tk.after(16, self._loop)

    def stop(self) -> None:
        self.running = False
        self._tk.quit()

    def run(self) -> None:
        try:
            self.start()
            self._tk.mainloop()
        except KeyboardInterrupt:
            self.stop()
