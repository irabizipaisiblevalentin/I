# I STUDIO — User Guide

I STUDIO is the official IDE platform for the I programming language. Version 1.0
ships the full CLI and language-server toolchain: workspace and project
management, language intelligence (lint/format), a debugger, profiler, AI
assistant, extension manager, collaboration, an LSP server over stdio, and a
desktop GUI application.

## Installation

I STUDIO ships with the I toolchain:

```bash
pip install i-lang
```

Three entry points are provided:

```bash
istudio --version            # standalone CLI command
istudio-desktop              # desktop GUI application (tkinter)
isoko istudio ...            # through the isoko bridge
```

## Web IDE

The web IDE is a browser-based development environment served by a local backend:

```bash
istudio-ide                  # or: isoko istudio ide
istudio-ide --port 8790      # custom port (default 8790)
istudio-ide --no-open        # do not auto-open the browser
istudio-ide ./my-project     # open a folder as a workspace
```

It provides a React/TypeScript/Monaco frontend with edit, run, debug,
breakpoints, a built-in terminal, project templates, a Git panel, and Isoko
package management. The backend is a stdlib-only Python HTTP server
(`src/istudio/ide/`) that isolates compilation and execution in subprocesses
with hard timeouts, so a misbehaving program never blocks the IDE.

## Desktop Application (Windows)

For Windows, I STUDIO ships as a native desktop app (pywebview/WebView2):

```bash
istudio-ide --app             # native window instead of the browser
```

A standalone installer is built from `packaging/windows/`:

```powershell
.\packaging\windows\build_windows.ps1   # builds the .exe + setup.exe
```

This produces `release/IStudioIDE-Setup-<version>.exe` (PyInstaller onedir app
bundling the backend and the built frontend, wrapped by Inno Setup). The
installer installs per-user, adds Start Menu/desktop shortcuts, registers the
`istudio-ide://` URL protocol, and adds an **Open with I Studio** entry to the
File Explorer right-click menu for any folder (plus a background-menu entry).

Opening a workspace works like other desktop IDEs:

- **File Explorer**: right-click a folder → *Open with I Studio* (or run
  `istudio-ide --app C:\path\to\folder`).
- **In the app**: the **Open Folder…** button on the Welcome screen shows a
  native folder picker; the last workspace is restored on launch.
- **Drag & drop**: drop files from Explorer onto the window to import them into
  the active project.

## Getting Started

Launch the graphical IDE:

```bash
istudio desktop               # open with a blank workspace
istudio desktop ./my-project  # open a folder as a workspace
istudio-desktop               # equivalent shortcut
```

The desktop app (`istudio.desktop`, built on tkinter with no extra dependencies)
provides:

- **Editor** — tabbed code editing with line numbers, syntax highlighting
  (Kinyarwanda + English keywords), bracket matching, current-line highlight,
  gutter breakpoints, and engine-backed undo/redo (Ctrl+Z / Ctrl+Y).
- **Language intelligence** — live diagnostics with squiggles and a Problems
  panel, autocomplete (Ctrl+Space), hover documentation (Ctrl+mouse),
  go-to-definition (F12), document formatting (Shift+Alt+F), and a Symbols
  outline (Ctrl+Shift+O).
- **Run** — F5 runs the active file through the real I compiler/VM with output
  captured in the Run panel.
- **Workspace** — Open Folder (Ctrl+K O), file explorer and outline sidebar.
- **Themes** — Dark, Light, Solarized, and Monokai (View menu).
- Shortcuts: Ctrl+N/O/S/Shift+S/W for files, Ctrl+Q to quit, F9 to toggle a
  breakpoint on the current line.

> The engine modules (`desktop/controller.py`, `desktop/runner.py`,
> `desktop/highlight.py`, `desktop/theme.py`) are headless and fully testable;
> only the widgets (`desktop/editor.py`, `desktop/sidebar.py`,
> `desktop/panel.py`, `desktop/app.py`) need a display.

## Getting Started

```bash
# Initialize a workspace
istudio workspace init ./my-project

# Create a project
istudio project create my-app --path ./my-project --type library

# Inspect the workspace
istudio workspace info ./my-project
```

## Editor

The I STUDIO editor engine (`istudio.indura.EditorEngine`) supports:
- Multi-tab file editing with undo/redo
- Syntax-aware operations
- Find and replace across files
- File type detection by extension

## Language Intelligence

```bash
# Lint a file (exits 1 on diagnostics)
istudio lint main.i

# JSON diagnostics (for tooling integration)
istudio lint main.i --format json

# Format a file in place
istudio format main.i
```

## Debugging

```bash
istudio debug start
istudio debug break-list
istudio debug step
istudio debug continue
istudio debug stop
```

## Profiling

```bash
istudio profile start --type cpu --name session
istudio profile stop
istudio profile list
istudio profile results
```

## AI Assistant

```bash
istudio ai chat "How do I create a class in I?"
istudio ai conversations
istudio ai chat --project-type library "Generate a starter template"
```

## Extensions

```bash
istudio extension install --path ./my-plugin/plugin.json
istudio extension list
istudio extension enable my-plugin
istudio extension disable my-plugin
istudio extension uninstall my-plugin
```

## Collaboration

```bash
istudio collaboration session-create my-session
istudio collaboration session-list
istudio collaboration user-list
istudio collaboration review-create PR-42
istudio collaboration review-list
```

## Language Server Protocol

```bash
istudio server --stdio
```

The LSP server supports stdio transport and handles:
- `initialize` / `shutdown`
- `textDocument/didOpen` / `didChange`
- `textDocument/completion`
- `textDocument/hover`

Any LSP-capable editor (VS Code, Neovim, Emacs, ...) can connect by launching
`istudio server --stdio` as the language server for `.i` files.
