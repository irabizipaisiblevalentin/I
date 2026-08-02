"""I STUDIO IDE — command-line entry point.

Starts the local IDE server and (optionally) opens the browser or, with
``--app``, shows a native desktop window via pywebview (WebView2).
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import webbrowser
from pathlib import Path

from istudio.ide import __version__
from istudio.ide.server import IdeApplication, make_server


def default_base_dir() -> str:
    return os.path.join(os.environ.get("ISTUDIO_HOME", str(Path.home() / ".istudio")), "projects")


def dispatch_child(argv: list[str]) -> int:
    """Run an IDE child task. Invoked with ``--istudio-child <task> ...`` by the
    same entry point that the parent spawned (``python -m istudio.ide`` in dev,
    the frozen exe in a packaged build)."""
    if not argv:
        print("istudio: --istudio-child requires a task", file=sys.stderr)
        return 2
    task, args = argv[0], argv[1:]
    if task == "compile":
        import json as _json

        from compiler.compiler import Compiler

        try:
            Compiler().compile_file(args[0])
            print(_json.dumps({"ok": True}))
        except BaseException as exc:  # noqa: BLE001
            print(_json.dumps({"ok": False, "error": str(exc)[:4000]}))
        return 0
    if task == "run":
        from compiler.compiler import Compiler, CompilerError
        from vm.virtual_machine import RuntimeError as VMRuntimeError

        try:
            Compiler().run_file(args[0])
        except CompilerError as exc:
            print(f"Compile error (umukosororo):\n{exc}", flush=True)
            return 1
        except VMRuntimeError as exc:
            print(f"Runtime error (ikosa): {exc}", flush=True)
            return 1
        except RecursionError:
            print("Runtime error (ikosa): infinite recursion detected", flush=True)
            return 1
        except Exception as exc:  # noqa: BLE001 — surface a clean message, never a raw traceback
            print(f"Runtime error (ikosa): {type(exc).__name__}: {exc}", flush=True)
            return 1
        return 0
    if task == "debug_compile":
        import pickle

        from compiler.compiler import Compiler

        chunk = Compiler().compile_file(args[0])
        with open(args[1], "wb") as f:
            pickle.dump(chunk, f)
        return 0
    if task == "isoko":
        from isoko.cli import main as isoko_main

        return int(isoko_main(args) or 0)
    print(f"istudio: unknown child task: {task}", file=sys.stderr)
    return 2


def _start_server(app: IdeApplication, host: str, port: int):
    try:
        return make_server(host, port, app)
    except OSError:
        return make_server(host, 0, app)


def _run_desktop(app: IdeApplication, host: str, port: int) -> int:
    server = _start_server(app, host, port)
    url = f"http://{host}:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        import webview  # type: ignore
    except ImportError:
        print("pywebview is not installed; falling back to the default browser.", flush=True)
        webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            app.close()
            server.server_close()
        return 0

    class JsApi:
        """Bridged into the frontend as ``window.pywebview.api`` in desktop mode."""

        def open_folder(self) -> str:
            """Show a native folder picker and open the chosen folder as a project."""
            import webview as _wv  # noqa: PLC0415

            dialog = _wv.FileDialog.FOLDER if hasattr(_wv, "FileDialog") else _wv.FOLDER_DIALOG
            result = _wv.windows[0].create_file_dialog(dialog)
            if not result:
                return ""
            path = str(result[0])
            try:
                app.projects.open_project(path)
                return path
            except Exception as exc:  # noqa: BLE001
                return f"error: {exc}"

        def pick_folder(self) -> str:
            """Show a native folder picker and return the chosen folder path."""
            import webview as _wv  # noqa: PLC0415

            dialog = _wv.FileDialog.FOLDER if hasattr(_wv, "FileDialog") else _wv.FOLDER_DIALOG
            result = _wv.windows[0].create_file_dialog(dialog)
            if not result:
                return ""
            return str(result[0])

        def open_path(self, path: str) -> str:
            """Open an arbitrary folder as a project (used by the Explorer context menu)."""
            if not path or not os.path.isdir(path):
                return f"error: not a folder: {path}"
            try:
                app.projects.open_project(path)
                return path
            except Exception as exc:  # noqa: BLE001
                return f"error: {exc}"

    webview.create_window(
        "I Studio IDE",
        url,
        width=1280,
        height=820,
        min_size=(800, 600),
        background_color="#1e1e1e",
        js_api=JsApi(),
    )
    webview.start()
    server.shutdown()
    app.close()
    server.server_close()
    return 0


def _ensure_streams() -> None:
    """PyInstaller windowed (``console=False``) apps leave ``sys.stdin``,
    ``sys.stdout`` and ``sys.stderr`` as ``None``; any ``print()`` then raises
    ``RuntimeError: lost sys.stdout`` and an uncaught traceback leaves the
    process hanging on a hidden error dialog. Give each a real sink so the app
    and its child run/compile processes can never crash on stdio."""
    devnull = os.devnull
    if sys.stdin is None:
        sys.stdin = open(devnull, "r", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = open(devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(devnull, "w", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    if getattr(sys, "frozen", False):
        _ensure_streams()
    if args_list and args_list[0] == "--istudio-child":
        return dispatch_child(args_list[1:])
    parser = argparse.ArgumentParser(
        prog="istudio-ide",
        description="Launch the I Studio IDE (local web IDE for the I Programming Language).",
    )
    parser.add_argument("path", nargs="?", default=None, help="workspace/project folder to open")
    parser.add_argument("--host", default="127.0.0.1", help="bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8790, help="bind port (default: 8790)")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser automatically")
    parser.add_argument("--base-dir", default=None, help="directory that stores created projects")
    parser.add_argument("--app", action="store_true", help="run as a native desktop window (pywebview) [default]")
    parser.add_argument("--browser", action="store_true", help="open in the default web browser instead of a native window")
    parser.add_argument("--version", action="version", version=f"I Studio IDE {__version__}")
    args = parser.parse_args(argv)

    base_dir = args.base_dir or default_base_dir()
    app = IdeApplication(base_dir=base_dir)
    if args.path:
        path = os.path.abspath(os.path.expanduser(args.path))
        try:
            app.projects.open_project(path)
        except Exception as exc:  # noqa: BLE001 — still serve; user can open from the UI
            print(f"note: could not open {path}: {exc}", flush=True)

    if args.app or not args.browser:
        return _run_desktop(app, args.host, args.port)

    server = _start_server(app, args.host, args.port)
    url = f"http://{args.host}:{server.server_address[1]}"
    print(f"I Studio IDE serving at {url}", flush=True)
    if not args.no_open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app.close()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
