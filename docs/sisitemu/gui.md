# GUI & Desktop Shell — `igaragaza`, `ibikoresho_bya_GUI`, `ikigoroba`

Build a complete Windows-like graphical operating system with SISITEMU's
display server, widget toolkit, and desktop shell.

## Architecture

```
igaragaza (Display Server / Compositor)
├── Compositor     — tkinter-backed compositor, input dispatch, rendering loop
├── Window         — top-level windows with title bar, border, resize, min/max/close
├── Theme          — Windows 11 inspired colors and metrics
├── FontRenderer   — text measurement and rendering via tkinter fonts
├── Color / Rect / Point — geometry and color utilities
└── Event system   — mouse move/down/up/click, keyboard, focus, window events

ibikoresho_bya_GUI (Widget Toolkit)
├── Widget / Container — base classes
├── Label, Button, TextBox, CheckBox, RadioButton
├── ListBox, ComboBox, ProgressBar, Slider
├── Panel, GroupBox, ScrollView, StatusBar
├── MenuBar, Menu, MenuItem
├── TabControl, TreeView, VScrollBar
└── ToolTip

ikigoroba (Desktop Shell)
├── Desktop        — background, icons, event dispatch
├── Taskbar        — start button, running apps, system tray
├── Start Menu     — app launcher with icons
├── SystemTray     — clock, notification icons
└── DesktopIcon    — clickable desktop icons
```

## Quick Start

```python
from sisitemu.igaragaza import Compositor, Theme, Window
from sisitemu.ikigoroba import Desktop

compositor = Compositor(width=1280, height=720,
                        title="SISITEMU OS")
desktop = Desktop(compositor)

compositor.set_background_handler(
    click_handler=lambda x, y, btn: desktop.handle_click(x, y, btn),
    dblclick_handler=lambda x, y: desktop.handle_double_click(x, y),
    renderer=lambda canvas, font: desktop.render(canvas, font),
)

win = compositor.create_window("My App", 100, 100, 600, 400)
win.background_color = Theme.panel_background

compositor.run()
```

## Creating Windows

```python
from sisitemu.igaragaza import Compositor, Theme, Color

compositor = Compositor(1280, 720)
win = compositor.create_window("My Window", x=50, y=50, width=600, height=400)
compositor.run()
```

## Widgets

```python
from sisitemu.igaragaza import Compositor
from sisitemu.ibikoresho_bya_GUI import Button, Label, TextBox, CheckBox, Panel

compositor = Compositor(800, 600)
win = compositor.create_window("Widget Demo", 50, 50, 500, 400)
p = Panel(0, 0, win.client_rect.width, win.client_rect.height)

label = Label(10, 10, 200, 20, "Hello SISITEMU!", bold=True)
button = Button(10, 40, 100, 24, "Click Me")
textbox = TextBox(10, 75, 200, 24, "Type here...")
checkbox = CheckBox(10, 110, 150, 20, "Enable Feature")

p.add(label); p.add(button); p.add(textbox); p.add(checkbox)
compositor.run()
```

## Desktop Shell

The `Desktop` class automatically provides:
- Gradient blue background
- Desktop icons (File Explorer, Notepad, Terminal, Settings, Calculator)
- Taskbar with start button and running application buttons
- Start menu with application launcher
- System tray with clock

Built-in applications auto-open on double-click:
- **File Explorer** — browse files
- **Notepad** — text editor
- **Terminal** — command line
- **Settings** — system settings
- **Calculator** — simple calculator
