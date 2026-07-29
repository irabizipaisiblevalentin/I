"""ibikoresho_bya_GUI — Widget toolkit: buttons, text boxes, lists, menus, etc."""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

from .igaragaza import (
    Color, Event, EventType, FontRenderer, Point, Rect, Theme, Window,
)


class DockStyle(Enum):
    NONE = auto()
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()
    FILL = auto()


class Widget:
    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 24,
                 text: str = "", visible: bool = True, enabled: bool = True):
        self.rect = Rect(x, y, width, height)
        self._text = text
        self.visible = visible
        self.enabled = enabled
        self.parent: Optional[Container] = None
        self.tag: str = ""
        self.font_family: str = Theme.font_family
        self.font_size: int = Theme.font_size_normal
        self.dock: DockStyle = DockStyle.NONE
        self.margin: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self._canvas_id: Optional[int] = None
        self._canvas_items: List[int] = []

    @property
    def text(self) -> str: return self._text
    @text.setter
    def text(self, v: str) -> None: self._text = v

    @property
    def absolute_x(self) -> int:
        return self.rect.x + (self.parent.absolute_x if self.parent else 0)

    @property
    def absolute_y(self) -> int:
        return self.rect.y + (self.parent.absolute_y if self.parent else 0)

    def contains(self, px: int, py: int) -> bool:
        ax, ay = self.absolute_x, self.absolute_y
        return ax <= px < ax + self.rect.width and ay <= py < ay + self.rect.height

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        pass

    def handle_event(self, event: Event) -> bool:
        return False

    def find_widget_at(self, px: int, py: int) -> Optional[Widget]:
        if self.contains(px, py) and self.visible:
            return self
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {"type": type(self).__name__, "text": self.text,
                "rect": (self.rect.x, self.rect.y, self.rect.width, self.rect.height)}


class Container(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 200,
                 text: str = ""):
        super().__init__(x, y, width, height, text)
        self.children: List[Widget] = []
        self.padding: Tuple[int, int, int, int] = (0, 0, 0, 0)

    def add(self, child: Widget) -> None:
        child.parent = self
        self.children.append(child)
        self._layout_docked()

    def remove(self, child: Widget) -> None:
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            self._layout_docked()

    def clear(self) -> None:
        for c in self.children:
            c.parent = None
        self.children.clear()

    def _layout_docked(self) -> None:
        docked = [c for c in self.children if c.dock != DockStyle.NONE]
        if not docked:
            return
        x, y = self.padding[0], self.padding[1]
        w = self.rect.width - self.padding[0] - self.padding[2]
        h = self.rect.height - self.padding[1] - self.padding[3]
        for c in docked:
            if c.dock == DockStyle.TOP:
                c.rect.x, c.rect.y = x, y
                c.rect.width = w
                y += c.rect.height
                h -= c.rect.height
            elif c.dock == DockStyle.BOTTOM:
                c.rect.x, c.rect.y = x, y + h - c.rect.height
                c.rect.width = w
                h -= c.rect.height
            elif c.dock == DockStyle.LEFT:
                c.rect.x, c.rect.y = x, y
                c.rect.height = h
                x += c.rect.width
                w -= c.rect.width
            elif c.dock == DockStyle.RIGHT:
                c.rect.x, c.rect.y = x + w - c.rect.width, y
                c.rect.height = h
                w -= c.rect.width
            elif c.dock == DockStyle.FILL:
                c.rect.x, c.rect.y = x, y
                c.rect.width = w
                c.rect.height = h

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ox = offset_x + self.rect.x
        oy = offset_y + self.rect.y
        for child in self.children:
            if child.visible:
                child.render(canvas, font, ox, oy)

    def find_widget_at(self, px: int, py: int) -> Optional[Widget]:
        if not self.visible or not self.contains(px, py):
            return None
        for child in reversed(self.children):
            found = child.find_widget_at(px, py)
            if found:
                return found
        return self


class Label(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 20,
                 text: str = "", align: str = "left", bold: bool = False):
        super().__init__(x, y, width, height, text)
        self.align = align
        self.bold = bold
        self.color: str = Theme.label_text

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        anchor = {"left": "w", "center": "center", "right": "e"}.get(self.align, "w")
        tx = ax + (self.rect.width // 2 if self.align == "center" else (self.rect.width - 4 if self.align == "right" else 4))
        font.draw(self.text, tx, ay + self.rect.height // 2, color=self.color,
                   size=self.font_size, bold=self.bold, anchor=anchor)


class Button(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 80, height: int = 24,
                 text: str = "Button"):
        super().__init__(x, y, width, height, text)
        self.pressed: bool = False
        self.hovered: bool = False
        self.on_click: Optional[Callable] = None
        self.bg_color: str = Theme.button_face
        self.border_color: str = Theme.button_border
        self.text_color: str = Theme.button_text

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                self.pressed = True
                return True
        elif event.type == EventType.MOUSE_UP and event.button == 1:
            if self.pressed:
                self.pressed = False
                if self.contains(event.x, event.y) and self.on_click:
                    self.on_click()
                return True
        elif event.type == EventType.MOUSE_MOVE:
            self.hovered = self.contains(event.x, event.y)
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        bg = Theme.button_pressed if self.pressed else (Theme.button_hover if self.hovered else self.bg_color)
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=bg, outline=self.border_color, tags="w")
        if self.pressed:
            canvas.create_rectangle(ax + 1, ay + 1, ax + self.rect.width - 1, ay + self.rect.height - 1,
                                     fill=Theme.button_pressed, outline="", tags="w")
        font.draw(self.text, ax + self.rect.width // 2, ay + self.rect.height // 2,
                   color=self.text_color, size=self.font_size, anchor="center")


class TextBox(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 24,
                 text: str = ""):
        super().__init__(x, y, width, height, text)
        self.focused: bool = False
        self.cursor_pos: int = len(text)
        self.show_cursor: bool = False
        self._cursor_blink: float = 0.0
        self.on_change: Optional[Callable[[str], None]] = None
        self.on_enter: Optional[Callable[[str], None]] = None
        self.placeholder: str = ""

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN:
            if self.contains(event.x, event.y):
                self.focused = True
                self.cursor_pos = len(self.text)
                return True
            else:
                self.focused = False
        elif event.type == EventType.KEY_DOWN and self.focused:
            if event.key == "BackSpace":
                if self.cursor_pos > 0:
                    self._text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                    if self.on_change: self.on_change(self.text)
            elif event.key == "Delete":
                if self.cursor_pos < len(self.text):
                    self._text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                    if self.on_change: self.on_change(self.text)
            elif event.key == "Left":
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == "Right":
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == "Home":
                self.cursor_pos = 0
            elif event.key == "End":
                self.cursor_pos = len(self.text)
            elif event.key == "Return":
                if self.on_enter: self.on_enter(self.text)
            elif len(event.key) == 1 and event.char:
                self._text = self.text[:self.cursor_pos] + event.char + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                if self.on_change: self.on_change(self.text)
            return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        bc = Theme.textbox_focused_border if self.focused else Theme.textbox_border
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.textbox_background, outline=bc, tags="w")
        display = self.text if self.text else self.placeholder
        tc = Theme.textbox_text if self.text else Theme.button_border
        font.draw(display, ax + 4, ay + self.rect.height // 2, color=tc,
                   size=self.font_size, anchor="w")
        if self.focused:
            cx = ax + 4 + font.measure(self.text[:self.cursor_pos])[0]
            canvas.create_line(cx, ay + 3, cx, ay + self.rect.height - 3,
                                fill=Theme.textbox_text, width=1, tags="w")


class CheckBox(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 120, height: int = 20,
                 text: str = "Check", checked: bool = False):
        super().__init__(x, y, width, height, text)
        self.checked = checked
        self.on_change: Optional[Callable[[bool], None]] = None

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                self.checked = not self.checked
                if self.on_change: self.on_change(self.checked)
                return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        cb_size = 14
        cy = ay + (self.rect.height - cb_size) // 2
        canvas.create_rectangle(ax, cy, ax + cb_size, cy + cb_size,
                                 fill=Theme.textbox_background, outline=Theme.button_border, tags="w")
        if self.checked:
            canvas.create_line(ax + 3, cy + 7, ax + 6, cy + 11, fill=Theme.highlight, width=2, tags="w")
            canvas.create_line(ax + 5, cy + 11, ax + 12, cy + 3, fill=Theme.highlight, width=2, tags="w")
        font.draw(self.text, ax + cb_size + 6, ay + self.rect.height // 2,
                   color=Theme.label_text, size=self.font_size, anchor="w")


class RadioButton(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 120, height: int = 20,
                 text: str = "Option", group: str = "default", selected: bool = False):
        super().__init__(x, y, width, height, text)
        self.group = group
        self.selected = selected
        self.on_select: Optional[Callable] = None

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                self.selected = True
                if self.on_select: self.on_select()
                return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        rb_size = 14
        cx, cy = ax + rb_size // 2, ay + self.rect.height // 2
        canvas.create_oval(cx - rb_size // 2, cy - rb_size // 2, cx + rb_size // 2, cy + rb_size // 2,
                            fill=Theme.textbox_background, outline=Theme.button_border, tags="w")
        if self.selected:
            canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=Theme.highlight, outline="", tags="w")
        font.draw(self.text, ax + rb_size + 8, cy, color=Theme.label_text,
                   size=self.font_size, anchor="w")


class ListBox(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 150, height: int = 100):
        super().__init__(x, y, width, height, "")
        self.items: List[str] = []
        self.selected_index: int = -1
        self.on_select: Optional[Callable[[int, str], None]] = None
        self._item_height: int = 20

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                rel_y = event.y - self.absolute_y
                idx = rel_y // self._item_height
                if 0 <= idx < len(self.items):
                    self.selected_index = idx
                    if self.on_select:
                        self.on_select(idx, self.items[idx])
                    return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.textbox_background, outline=Theme.textbox_border, tags="w")
        for i, item in enumerate(self.items):
            iy = ay + i * self._item_height
            if i == self.selected_index:
                canvas.create_rectangle(ax + 1, iy, ax + self.rect.width - 1, iy + self._item_height,
                                         fill=Theme.highlight, outline="", tags="w")
                font.draw(item, ax + 4, iy + self._item_height // 2,
                           color=Theme.highlight_text, size=self.font_size, anchor="w")
            else:
                font.draw(item, ax + 4, iy + self._item_height // 2,
                           color=Theme.label_text, size=self.font_size, anchor="w")


class ComboBox(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 150, height: int = 24):
        super().__init__(x, y, width, height, "")
        self.items: List[str] = []
        self.selected_index: int = -1
        self._open: bool = False
        self._list_height: int = 100
        self.on_select: Optional[Callable[[int, str], None]] = None

    @property
    def selected_text(self) -> str:
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return ""

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                self._open = not self._open
                return True
            if self._open:
                dy = event.y - self.absolute_y - self.rect.height
                idx = int(dy // 20)
                if 0 <= idx < len(self.items):
                    self.selected_index = idx
                    self._open = False
                    if self.on_select: self.on_select(idx, self.items[idx])
                    return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.textbox_background, outline=Theme.textbox_border, tags="w")
        font.draw(self.selected_text, ax + 4, ay + self.rect.height // 2,
                   color=Theme.label_text, size=self.font_size, anchor="w")
        arrow_x = ax + self.rect.width - 12
        canvas.create_polygon(arrow_x, ay + 8, arrow_x + 8, ay + 8, arrow_x + 4, ay + 16,
                               fill=Theme.button_text, outline="", tags="w")
        if self._open:
            lx, ly = ax, ay + self.rect.height
            lh = min(len(self.items) * 20, self._list_height)
            canvas.create_rectangle(lx, ly, lx + self.rect.width, ly + lh,
                                     fill=Theme.textbox_background, outline=Theme.textbox_border, tags="w")
            for i, item in enumerate(self.items):
                iy = ly + i * 20
                if i == self.selected_index:
                    canvas.create_rectangle(lx + 1, iy, lx + self.rect.width - 1, iy + 20,
                                             fill=Theme.highlight, outline="", tags="w")
                    font.draw(item, lx + 4, iy + 10, color=Theme.highlight_text, size=self.font_size, anchor="w")
                else:
                    font.draw(item, lx + 4, iy + 10, color=Theme.label_text, size=self.font_size, anchor="w")


class ProgressBar(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 20,
                 value: float = 0.0, maximum: float = 100.0):
        super().__init__(x, y, width, height, "")
        self.value = value
        self.maximum = maximum
        self.show_text: bool = True

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.textbox_background, outline=Theme.textbox_border, tags="w")
        pct = max(0, min(1, self.value / self.maximum if self.maximum else 0))
        fw = max(2, int((self.rect.width - 2) * pct))
        canvas.create_rectangle(ax + 1, ay + 1, ax + 1 + fw, ay + self.rect.height - 1,
                                 fill=Theme.highlight, outline="", tags="w")
        if self.show_text:
            text = f"{int(pct * 100)}%"
            font.draw(text, ax + self.rect.width // 2, ay + self.rect.height // 2,
                       color=Theme.label_text, size=self.font_size, anchor="center")


class Slider(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 20,
                 value: float = 50.0, min_value: float = 0.0, max_value: float = 100.0):
        super().__init__(x, y, width, height, "")
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self._dragging: bool = False
        self.on_change: Optional[Callable[[float], None]] = None

    def _value_from_x(self, px: int) -> float:
        ax = self.absolute_x
        t = (px - ax - 6) / (self.rect.width - 12)
        t = max(0, min(1, t))
        return self.min_value + t * (self.max_value - self.min_value)

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                self._dragging = True
                self.value = self._value_from_x(event.x)
                if self.on_change: self.on_change(self.value)
                return True
        elif event.type == EventType.MOUSE_UP and event.button == 1:
            self._dragging = False
        elif event.type == EventType.MOUSE_MOVE and self._dragging:
            self.value = self._value_from_x(event.x)
            if self.on_change: self.on_change(self.value)
            return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        cy = ay + self.rect.height // 2
        canvas.create_rectangle(ax + 4, cy - 2, ax + self.rect.width - 4, cy + 2,
                                 fill=Theme.button_border, outline="", tags="w")
        t = (self.value - self.min_value) / (self.max_value - self.min_value) if self.max_value > self.min_value else 0
        hx = ax + 6 + int((self.rect.width - 12) * t)
        hr = 6
        canvas.create_oval(hx - hr, cy - hr, hx + hr, cy + hr,
                            fill=Theme.button_face, outline=Theme.button_border, tags="w")
        canvas.create_oval(hx - hr + 1, cy - hr + 1, hx + hr - 1, cy + hr - 1,
                            fill=Theme.button_face, outline="", tags="w")


class Panel(Container):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 200,
                 text: str = "", border: bool = False):
        super().__init__(x, y, width, height, text)
        self.border = border
        self.bg_color: str = Theme.panel_background

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=self.bg_color, outline=Theme.button_border if self.border else "",
                                 tags="w")
        super().render(canvas, font, ax, ay)


class GroupBox(Container):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 200,
                 text: str = "Group"):
        super().__init__(x, y, width, height, text)
        self.padding = (0, 16, 0, 0)

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay + 8, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.panel_background, outline=Theme.button_border, tags="w")
        bg = Theme.panel_background
        tw = font.measure(self.text)[0] + 10
        canvas.create_rectangle(ax + 6, ay, ax + 6 + tw, ay + 16,
                                 fill=bg, outline="", tags="w")
        font.draw(self.text, ax + 11, ay + 8, color=Theme.label_text,
                   size=self.font_size, bold=True, anchor="w")
        super().render(canvas, font, ax, ay)


class MenuItem:
    def __init__(self, text: str = "", command: Optional[Callable] = None,
                 enabled: bool = True, checked: bool = False, separator: bool = False):
        self.text = text
        self.command = command
        self.enabled = enabled
        self.checked = checked
        self.separator = separator
        self.children: List[MenuItem] = []

    def add(self, item: MenuItem) -> None:
        self.children.append(item)


class Menu:
    def __init__(self, text: str = ""):
        self.text = text
        self.items: List[MenuItem] = []

    def add(self, item: MenuItem) -> None:
        self.items.append(item)

    def add_separator(self) -> None:
        self.items.append(MenuItem(separator=True))


class MenuBar(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 600, height: int = 24):
        super().__init__(x, y, width, height, "")
        self.menus: List[Menu] = []
        self._open_menu_index: int = -1
        self._item_height: int = 22

    def add(self, menu: Menu) -> None:
        self.menus.append(menu)

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                rel_x = event.x - self.absolute_x
                x = 0
                for i, m in enumerate(self.menus):
                    mw = len(m.text) * 9 + 16
                    if x <= rel_x < x + mw:
                        self._open_menu_index = i if self._open_menu_index != i else -1
                        return True
                    x += mw
            else:
                self._open_menu_index = -1
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.menu_background, outline=Theme.button_border, tags="w")
        x = ax
        for i, menu in enumerate(self.menus):
            mw = len(menu.text) * 9 + 16
            if i == self._open_menu_index:
                canvas.create_rectangle(x, ay, x + mw, ay + self.rect.height,
                                         fill=Theme.menu_hover, outline="", tags="w")
            font.draw(menu.text, x + 8, ay + self.rect.height // 2,
                       color=Theme.menu_text, size=self.font_size, anchor="w")
            x += mw

        if self._open_menu_index >= 0 and self._open_menu_index < len(self.menus):
            menu = self.menus[self._open_menu_index]
            mx = ax
            for i in range(self._open_menu_index):
                mx += len(self.menus[i].text) * 9 + 16
            my = ay + self.rect.height
            mw = max(120, max((len(it.text) * 9 + 32) for it in menu.items if not it.separator) if menu.items else 120)
            mh = len([it for it in menu.items if not it.separator]) * self._item_height + \
                  len([it for it in menu.items if it.separator]) * 6
            canvas.create_rectangle(mx, my, mx + mw, my + mh,
                                     fill=Theme.menu_background, outline=Theme.menu_border, tags="w")
            iy = my + 4
            for item in menu.items:
                if item.separator:
                    canvas.create_line(mx + 8, iy, mx + mw - 8, iy, fill=Theme.button_border, tags="w")
                    iy += 6
                    continue
                if item == getattr(self, '_hovered_item', None) and item.enabled:
                    canvas.create_rectangle(mx + 2, iy, mx + mw - 2, iy + self._item_height,
                                             fill=Theme.menu_hover, outline="", tags="w")
                tc = Theme.menu_text if item.enabled else Theme.menu_disabled_text
                font.draw(item.text, mx + 8, iy + self._item_height // 2, color=tc,
                           size=self.font_size, anchor="w")
                iy += self._item_height


class ScrollView(Container):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 200):
        super().__init__(x, y, width, height, "")
        self.scroll_x: int = 0
        self.scroll_y: int = 0
        self.content_width: int = width
        self.content_height: int = height

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.panel_background, outline=Theme.textbox_border, tags="w")
        canvas.create_rectangle(ax + 1, ay + 1, ax + self.rect.width - Theme.scrollbar_width,
                                 ay + self.rect.height - Theme.scrollbar_width,
                                 fill=Theme.panel_background, outline="", tags="w")
        super().render(canvas, font, ax - self.scroll_x, ay - self.scroll_y)
        if self.content_height > self.rect.height:
            sh = self.rect.height * self.rect.height // self.content_height
            sy = ay + self.scroll_y * (self.rect.height - sh) // (self.content_height - self.rect.height) if self.content_height > self.rect.height else ay
            sx = ax + self.rect.width - Theme.scrollbar_width
            canvas.create_rectangle(sx, ay, sx + Theme.scrollbar_width, ay + self.rect.height,
                                     fill=Theme.scrollbar_face, outline="", tags="w")
            canvas.create_rectangle(sx, sy, sx + Theme.scrollbar_width, sy + sh,
                                     fill=Theme.scrollbar_hover, outline=Theme.button_border, tags="w")


class StatusBar(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 600, height: int = 22,
                 text: str = ""):
        super().__init__(x, y, width, height, text)
        self.parts: List[str] = []

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.button_face, outline=Theme.button_border, tags="w")
        if self.text:
            font.draw(self.text, ax + 6, ay + self.rect.height // 2,
                       color=Theme.label_text, size=self.font_size, anchor="w")
        x = ax + self.rect.width - 6
        for part in reversed(self.parts):
            pw = font.measure(part)[0] + 12
            x -= pw
            canvas.create_line(x, ay, x, ay + self.rect.height, fill=Theme.button_border, tags="w")
            font.draw(part, x + 6, ay + self.rect.height // 2, color=Theme.label_text,
                       size=self.font_size, anchor="w")


class ToolTip(Widget):
    def __init__(self, text: str = ""):
        super().__init__(0, 0, 0, 0, text)
        self.target: Optional[Widget] = None
        self.delay_ms: int = 500
        self._timer_id: Optional[str] = None
        self._showing: bool = False
        self.bg_color: str = Theme.rgb(0xFF, 0xFF, 0xE0)
        self.border_color: str = Theme.GRAY_75

    def show(self, x: int, y: int) -> None:
        self.rect.x = x + 10
        self.rect.y = y + 10
        self._showing = True

    def hide(self) -> None:
        self._showing = False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self._showing or not self.text:
            return
        tw, th = font.measure(self.text)
        pw, ph = tw + 12, th + 8
        ax, ay = self.rect.x, self.rect.y
        canvas.create_rectangle(ax, ay, ax + pw, ay + ph,
                                 fill=self.bg_color, outline=self.border_color, tags="w")
        font.draw(self.text, ax + 6, ay + ph // 2, color=Theme.label_text, anchor="w")


class TabControl(Container):
    def __init__(self, x: int = 0, y: int = 0, width: int = 400, height: int = 300):
        super().__init__(x, y, width, height, "")
        self.tabs: List[Tuple[str, Container]] = []
        self.selected_index: int = 0
        self._tab_height: int = 24

    def add_tab(self, title: str, panel: Optional[Container] = None) -> Container:
        p = panel or Container(0, self._tab_height, self.rect.width, self.rect.height - self._tab_height)
        self.tabs.append((title, p))
        self.add(p)
        p.visible = (len(self.tabs) - 1 == self.selected_index)
        return p

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                rel_x = event.x - self.absolute_x
                x = 0
                for i, (title, _) in enumerate(self.tabs):
                    tw = len(title) * 9 + 20
                    if x <= rel_x < x + tw and rel_y < self._tab_height:
                        self.selected_index = i
                        for j, (_, p) in enumerate(self.tabs):
                            p.visible = (j == i)
                        return True
                    x += tw
        rel_y = event.y - self.absolute_y
        if rel_y >= self._tab_height:
            return super().handle_event(event)
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        x = ax
        for i, (title, _) in enumerate(self.tabs):
            tw = len(title) * 9 + 20
            selected = i == self.selected_index
            bg = Theme.panel_background if selected else Theme.button_face
            canvas.create_rectangle(x, ay, x + tw, ay + self._tab_height,
                                     fill=bg, outline=Theme.button_border, tags="w")
            if selected:
                canvas.create_line(x, ay + self._tab_height, x + tw, ay + self._tab_height,
                                    fill=bg, width=2, tags="w")
            font.draw(title, x + tw // 2, ay + self._tab_height // 2,
                       color=Theme.label_text, size=self.font_size, bold=selected, anchor="center")
            x += tw
        canvas.create_rectangle(ax, ay + self._tab_height, ax + self.rect.width,
                                 ay + self.rect.height, fill=Theme.panel_background,
                                 outline=Theme.button_border, tags="w")
        super().render(canvas, font, ax, ay)


class TreeView(Widget):
    class Node:
        def __init__(self, text: str = "", children: Optional[List[Node]] = None):
            self.text = text
            self.children = children or []
            self.expanded: bool = False
            self.data: Any = None

    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 200):
        super().__init__(x, y, width, height, "")
        self.root = TreeView.Node("")
        self.on_select: Optional[Callable[[Node], None]] = None
        self.selected_node: Optional[TreeView.Node] = None

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                rel_y = event.y - self.absolute_y
                self.selected_node = self._node_at(rel_y)
                if self.selected_node and self.on_select:
                    self.on_select(self.selected_node)
                return True
        return False

    def _node_at(self, rel_y: int, node: Optional[Node] = None, depth: int = 0) -> Optional[Node]:
        node = node or self.root
        y = 0
        for child in node.children:
            if y <= rel_y < y + 20:
                return child
            y += 20
            if child.expanded:
                result = self._node_at(rel_y - y, child, depth + 1)
                if result:
                    return result
                y += self._count_visible(child) * 20 - 20
        return None

    def _count_visible(self, node: Node) -> int:
        count = 0
        for child in node.children:
            count += 1
            if child.expanded:
                count += self._count_visible(child)
        return count

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.textbox_background, outline=Theme.textbox_border, tags="w")
        self._render_nodes(canvas, font, self.root, ax + 4, ay + 2, 0)


    def _render_nodes(self, canvas: tk.Canvas, font: FontRenderer, node: Node,
                      x: int, y: int, depth: int) -> int:
        cy = y
        for child in node.children:
            indent = depth * 16
            cx = x + indent
            if child.children:
                sym = "▼" if child.expanded else "▶"
                font.draw(sym, cx, cy + 10, color=Theme.label_text, size=8, anchor="center")
            selected = child is self.selected_node
            if selected:
                canvas.create_rectangle(cx + 14, cy, x + self.rect.width - 8, cy + 20,
                                         fill=Theme.highlight, outline="", tags="w")
            font.draw(child.text, cx + 20, cy + 10, color=Theme.highlight_text if selected else Theme.label_text,
                       size=self.font_size, anchor="w")
            cy += 20
            if child.expanded:
                cy = self._render_nodes(canvas, font, child, x, cy, depth + 1)
        return cy


class VScrollBar(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 12, height: int = 200):
        super().__init__(x, y, width, height, "")
        self.value: float = 0.0
        self.maximum: float = 100.0
        self._dragging: bool = False

    def handle_event(self, event: Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == EventType.MOUSE_DOWN and event.button == 1:
            if self.contains(event.x, event.y):
                self._dragging = True
                return True
        elif event.type == EventType.MOUSE_UP:
            self._dragging = False
        elif event.type == EventType.MOUSE_MOVE and self._dragging:
            rel_y = event.y - self.absolute_y
            self.value = max(0, min(self.maximum, rel_y / self.rect.height * self.maximum))
            return True
        return False

    def render(self, canvas: tk.Canvas, font: FontRenderer, offset_x: int = 0, offset_y: int = 0) -> None:
        if not self.visible:
            return
        ax, ay = offset_x + self.rect.x, offset_y + self.rect.y
        canvas.create_rectangle(ax, ay, ax + self.rect.width, ay + self.rect.height,
                                 fill=Theme.scrollbar_face, outline="", tags="w")
        thumb_h = max(20, self.rect.height * 0.3)
        t = self.value / self.maximum if self.maximum > 0 else 0
        ty = ay + t * (self.rect.height - thumb_h)
        canvas.create_rectangle(ax, ty, ax + self.rect.width, ty + thumb_h,
                                 fill=Theme.scrollbar_hover, outline=Theme.button_border, tags="w")
