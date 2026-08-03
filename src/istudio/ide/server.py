"""I STUDIO IDE — HTTP server (stdlib ThreadingHTTPServer).

Serves the built frontend (``ide/dist``) plus a JSON REST API and SSE streams
for run output, terminal I/O and debugger events.
"""

from __future__ import annotations

import os
import queue
import socketserver
import sys
import threading
import traceback
from collections.abc import Callable
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from . import __version__ as ide_version
from . import util
from .debug import DebugSession
from .diag import analyze_source, completions_at, format_source, hover_at, symbols_of
from .extensions_api import ExtensionsService
from .git_api import GitService
from .isoko_api import IsokoService
from .projects import ProjectError, ProjectService
from .run import RunService
from .sse import SSEHub
from .terminal import TerminalManager


def default_static_dir() -> str:
    """Resolve the built frontend directory, including inside a frozen exe."""
    if getattr(sys, "frozen", False):  # PyInstaller
        base = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
        return os.path.join(base, "ide", "dist")
    return str(Path(__file__).resolve().parents[3] / "ide" / "dist")


_STATIC_DIR = default_static_dir()


def with_watchdog(fn: Callable[[], Any], timeout: float = 8.0) -> tuple[bool, Any]:
    """Run fn on a watchdog thread. Returns (ok, value|None). Abandons the
    thread on timeout (pathological parses can spin forever)."""
    result: dict[str, Any] = {"done": False, "value": None, "error": None}

    def runner() -> None:
        try:
            result["value"] = fn()
        except Exception as exc:  # noqa: BLE001
            result["error"] = exc
        finally:
            result["done"] = True

    thread = threading.Thread(target=runner, daemon=True, name="ide-watchdog")
    thread.start()
    thread.join(timeout)
    if not result["done"]:
        return False, None
    if result["error"] is not None:
        raise result["error"]
    return True, result["value"]


def _analyze_watchdog(content: str, filename: str) -> Any:
    try:
        ok, value = with_watchdog(lambda: analyze_source(content, filename), timeout=8.0)
    except Exception as exc:  # noqa: BLE001
        return [{
            "range": {"start": {"line": 1, "character": 0}, "end": {"line": 1, "character": 1}},
            "severity": 1,
            "message": f"Analysis failed: {exc}",
            "source": "compiler",
            "code": "INTERNAL",
        }]
    if not ok:
        return [{
            "range": {"start": {"line": 1, "character": 0}, "end": {"line": 1, "character": 1}},
            "severity": 1,
            "message": "Analysis timed out (possible infinite parse loop).",
            "source": "compiler",
            "code": "TIMEOUT",
        }]
    return value or []


class _Handler(BaseHTTPRequestHandler):
    server_version = f"IStudioIDE/{ide_version}"

    app: IdeApplication

    # ── HTTP plumbing ───────────────────────────────────────────────────

    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, data: Any) -> None:
        self._send(status, util.json_bytes(data))

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message})

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        data = self.rfile.read(length) if length else b""
        return util.read_json_body(data)

    def _sse(self, stream_id: str) -> None:
        """Stream one SSE channel to the client until disconnect."""
        q = self.app.hub.subscribe(stream_id)
        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            while True:
                try:
                    frame = q.get(timeout=15)
                    self.wfile.write(frame.encode("utf-8"))
                    self.wfile.flush()
                except (TimeoutError, queue.Empty):
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            self.app.hub.unsubscribe(stream_id, q)

    def _project_root(self) -> str | None:
        query = self.path.split("?", 1)[1] if "?" in self.path else ""
        root = None
        for part in query.split("&"):
            if part.startswith("root="):
                root = unquote(part[5:])
        if root is None:
            return None
        return os.path.normpath(os.path.abspath(root))

    # ── dispatch ────────────────────────────────────────────────────────

    def _dispatch(self, method: str, path: str) -> None:
        handler = self.app.router.get(method, path)
        if handler is None:
            self._error(404, "not found")
            return
        try:
            handler(self, path)
        except ProjectError as exc:
            self._error(400, str(exc))
        except Exception as exc:  # noqa: BLE001 — surface failures to the UI
            traceback.print_exc()
            self._error(500, f"{type(exc).__name__}: {exc}")

    def do_GET(self) -> None:
        self._dispatch("GET", self.path)

    def do_POST(self) -> None:
        self._dispatch("POST", self.path)

    def do_DELETE(self) -> None:
        self._dispatch("DELETE", self.path)

    def log_message(self, fmt: str, *args: Any) -> None:
        if self.app.verbose:
            super().log_message(fmt, *args)


class Router:
    def __init__(self) -> None:
        self._routes: dict[str, list] = {}

    def route(self, method: str, prefix: str) -> Callable:
        def register(fn: Callable) -> Callable:
            self._routes.setdefault(method, []).append((prefix, fn))
            return fn

        return register

    def get(self, method: str, path: str) -> Callable | None:
        clean = path.split("?", 1)[0]
        best: Callable | None = None
        best_len = -1
        for prefix, fn in self._routes.get(method, []):
            if clean == prefix or clean.startswith(prefix + "/") or (prefix != "/" and clean.startswith(prefix)):
                if len(prefix) > best_len:
                    best, best_len = fn, len(prefix)
        return best


class IdeApplication:
    def __init__(self, base_dir: str, static_dir: str = _STATIC_DIR, verbose: bool = False):
        self.base_dir = os.path.abspath(base_dir)
        self.static_dir = static_dir
        self.verbose = verbose
        self.projects = ProjectService(base_dir)
        self.hub = SSEHub()
        self.runner = RunService(self.hub)
        self.terminals = TerminalManager(self.hub)
        self.debug_sessions: dict[str, DebugSession] = {}
        self._debug_lock = threading.Lock()
        self.router = Router()
        self._register_routes()

    def _resolve_file(self, root: str, file_path: str) -> str:
        """Resolve a (possibly relative) file path under a project root."""
        if not file_path:
            raise ProjectError("missing file")
        if root:
            resolved = util.safe_join(root, file_path)
            if resolved is None:
                raise ProjectError("file escapes project root")
            return resolved
        return os.path.normpath(os.path.abspath(file_path))

    # ── routes ──────────────────────────────────────────────────────────

    def _register_routes(self) -> None:
        r = self.router

        # health / meta
        @r.route("GET", "/api/health")
        def health(h: _Handler, path: str) -> None:
            h._json(200, {"ok": True, "version": ide_version, "python": sys.version.split()[0]})

        @r.route("GET", "/api/templates")
        def templates(h: _Handler, path: str) -> None:
            from . import templates as tpl

            h._json(200, [
                {"key": key, "name": meta["name"], "description": meta["description"],
                 "category": meta["category"]}
                for key, meta in sorted(tpl.TEMPLATES.items())
            ])

        # projects
        @r.route("GET", "/api/projects")
        def projects(h: _Handler, path: str) -> None:
            h._json(200, {"projects": self.projects.list_projects(), "base_dir": self.base_dir})

        @r.route("GET", "/api/projects/recent")
        def recent(h: _Handler, path: str) -> None:
            h._json(200, {"recent": self.projects.recent()})

        @r.route("GET", "/api/projects/current")
        def current(h: _Handler, path: str) -> None:
            h._json(200, self.projects.current())

        @r.route("POST", "/api/projects/create")
        def create(h: _Handler, path: str) -> None:
            body = h._body()
            result = self.projects.create(
                str(body.get("name", "")), str(body.get("template", "console")),
                str(body["path"]) if body.get("path") else None,
            )
            h._json(200, result)

        @r.route("POST", "/api/projects/import")
        def create_from_upload(h: _Handler, path: str) -> None:
            body = h._body()
            source = body.get("source")
            if isinstance(source, str) and source:
                h._json(200, self.projects.create_from_folder(str(body.get("name", "")), source))
                return
            files = body.get("files")
            if not isinstance(files, dict):
                h._error(400, "files must be an object of path -> content, or provide a source folder")
                return
            result = self.projects.create_from_upload(
                str(body.get("name", "")),
                {str(k): str(v) for k, v in files.items()},
            )
            h._json(200, result)

        @r.route("POST", "/api/projects/open")
        def open_project(h: _Handler, path: str) -> None:
            body = h._body()
            h._json(200, self.projects.open_project(str(body.get("path", ""))))

        @r.route("GET", "/api/project/tree")
        def tree(h: _Handler, path: str) -> None:
            root = h._project_root()
            if root is None:
                h._error(400, "missing root")
                return
            h._json(200, {"root": root, "tree": self.projects.file_tree(root)})

        @r.route("GET", "/api/project/file")
        def read_file(h: _Handler, path: str) -> None:
            query = path.split("?", 1)[1] if "?" in path else ""
            root = file_rel = None
            for part in query.split("&"):
                if part.startswith("root="):
                    root = unquote(part[5:])
                elif part.startswith("path="):
                    file_rel = unquote(part[5:])
            if root is None or file_rel is None:
                h._error(400, "missing root/path")
                return
            h._json(200, {"path": file_rel, "content": self.projects.read_file(root, file_rel)})

        @r.route("POST", "/api/project/file")
        def write_file(h: _Handler, path: str) -> None:
            body = h._body()
            root = str(body.get("root", ""))
            rel = str(body.get("path", ""))
            self.projects.write_file(root, rel, str(body.get("content", "")))
            h._json(200, {"ok": True})

        @r.route("POST", "/api/project/delete")
        def delete_path(h: _Handler, path: str) -> None:
            body = h._body()
            self.projects.delete_path(str(body.get("root", "")), str(body.get("path", "")))
            h._json(200, {"ok": True})

        @r.route("POST", "/api/project/import")
        def import_files(h: _Handler, path: str) -> None:
            body = h._body()
            root = str(body.get("root", ""))
            source = body.get("source")
            if isinstance(source, str) and source:
                written = self.projects.replace_from_folder(root, source)
                h._json(200, {"ok": True, "count": len(written), "files": written})
                return
            files = body.get("files")
            if not isinstance(files, dict):
                h._error(400, "files must be an object of path -> content, or provide a source folder")
                return
            written = self.projects.replace_with(
                root, {str(k): str(v) for k, v in files.items()}
            )
            h._json(200, {"ok": True, "count": len(written), "files": written})

        @r.route("POST", "/api/project/rename")
        def rename_path(h: _Handler, path: str) -> None:
            body = h._body()
            self.projects.rename_path(str(body.get("root", "")), str(body.get("path", "")), str(body.get("newName", "")))
            h._json(200, {"ok": True})

        # language service
        @r.route("POST", "/api/diagnostics")
        def diagnostics(h: _Handler, path: str) -> None:
            body = h._body()
            content = str(body.get("content", ""))
            filename = str(body.get("filename", "unnamed.i"))
            h._json(200, {"diagnostics": _analyze_watchdog(content, filename)})

        @r.route("POST", "/api/completion")
        def completion(h: _Handler, path: str) -> None:
            body = h._body()
            content = str(body.get("content", ""))
            line = int(body.get("line", 1))
            column = int(body.get("column", 0))
            ok, value = with_watchdog(lambda: completions_at(content, line, column), timeout=5.0)
            h._json(200, {"completions": value if ok else []})

        @r.route("POST", "/api/hover")
        def hover(h: _Handler, path: str) -> None:
            body = h._body()
            content = str(body.get("content", ""))
            line = int(body.get("line", 1))
            column = int(body.get("column", 0))
            ok, value = with_watchdog(lambda: hover_at(content, line, column), timeout=5.0)
            h._json(200, {"hover": value if ok else None})

        @r.route("POST", "/api/symbols")
        def symbols(h: _Handler, path: str) -> None:
            body = h._body()
            ok, value = with_watchdog(lambda: symbols_of(str(body.get("content", "")), str(body.get("filename", "unnamed.i"))), timeout=5.0)
            h._json(200, {"symbols": value if ok else []})

        @r.route("POST", "/api/format")
        def format_doc(h: _Handler, path: str) -> None:
            body = h._body()
            h._json(200, {"formatted": format_source(str(body.get("content", "")))})

        # run
        @r.route("POST", "/api/run")
        def run(h: _Handler, path: str) -> None:
            body = h._body()
            root = str(body.get("root", "")) or None
            if body.get("source") is not None:
                job_id = self.runner.start_source(str(body["source"]), root)
            elif body.get("file"):
                file_path = self._resolve_file(root, str(body["file"]))
                job_id = self.runner.start_file(file_path, root)
            else:
                h._error(400, "provide source or file")
                return
            h._json(200, {"job_id": job_id})

        @r.route("POST", "/api/run/cancel")
        def run_cancel(h: _Handler, path: str) -> None:
            body = h._body()
            h._json(200, {"cancelled": self.runner.cancel(str(body.get("job_id", "")))})

        @r.route("GET", "/sse/run")
        def sse_run(h: _Handler, path: str) -> None:
            job_id = path.split("/", 3)[-1].split("?", 1)[0]
            h._sse(f"run:{job_id}")

        # debug
        @r.route("POST", "/api/debug/start")
        def debug_start(h: _Handler, path: str) -> None:
            body = h._body()
            root = str(body.get("root", ""))
            file_path = self._resolve_file(root, str(body.get("file", "")))
            if not body.get("file"):
                h._error(400, "missing file")
                return
            session = DebugSession(self.hub, file_path, root or None)
            with self._debug_lock:
                self.debug_sessions[session.session_id] = session
            session.start()
            h._json(200, {"session_id": session.session_id})

        @r.route("POST", "/api/debug/stop")
        def debug_stop(h: _Handler, path: str) -> None:
            body = h._body()
            session = self.debug_sessions.get(str(body.get("session_id", "")))
            if session:
                session.stop()
            h._json(200, {"ok": True})

        @r.route("POST", "/api/debug/command")
        def debug_command(h: _Handler, path: str) -> None:
            body = h._body()
            session = self.debug_sessions.get(str(body.get("session_id", "")))
            if not session:
                h._error(404, "session not found")
                return
            command = str(body.get("command", ""))
            if command == "continue":
                session.continue_run()
            elif command == "step":
                session.step()
            elif command == "stop":
                session.stop()
            elif command == "breakpoints":
                session.set_breakpoints([int(ln) for ln in body.get("lines", [])])
            else:
                h._error(400, f"unknown command: {command}")
                return
            h._json(200, {"ok": True})

        @r.route("GET", "/sse/debug")
        def sse_debug(h: _Handler, path: str) -> None:
            session_id = path.split("/", 3)[-1].split("?", 1)[0]
            h._sse(f"debug:{session_id}")

        # terminal
        @r.route("POST", "/api/terminal")
        def term_create(h: _Handler, path: str) -> None:
            body = h._body()
            root = str(body.get("root", ""))
            session = self.terminals.create(root or os.path.expanduser("~"), body.get("shell") or None)
            h._json(200, {"term_id": session.term_id})

        @r.route("POST", "/api/terminal/input")
        def term_input(h: _Handler, path: str) -> None:
            body = h._body()
            session = self.terminals.get(str(body.get("term_id", "")))
            if not session:
                h._error(404, "terminal not found")
                return
            session.write(str(body.get("data", "")))
            h._json(200, {"ok": True})

        @r.route("DELETE", "/api/terminal")
        def term_close(h: _Handler, path: str) -> None:
            term_id = path.split("/", 3)[-1].split("?", 1)[0]
            self.terminals.close(term_id)
            h._json(200, {"ok": True})

        @r.route("GET", "/sse/terminal")
        def sse_terminal(h: _Handler, path: str) -> None:
            term_id = path.split("/", 3)[-1].split("?", 1)[0]
            h._sse(f"term:{term_id}")

        # isoko
        @r.route("GET", "/api/packages/search")
        def pkg_search(h: _Handler, path: str) -> None:
            query = path.split("?", 1)[1] if "?" in path else ""
            q = ""
            for part in query.split("&"):
                if part.startswith("q="):
                    q = unquote(part[2:])
            service = IsokoService(self.base_dir)
            h._json(200, service.search(q))

        @r.route("POST", "/api/project/install")
        def pkg_install(h: _Handler, path: str) -> None:
            body = h._body()
            service = IsokoService(str(body.get("root", "")))
            h._json(200, service.install(str(body.get("name", "")), str(body.get("version", "")) or None))

        @r.route("POST", "/api/project/uninstall")
        def pkg_uninstall(h: _Handler, path: str) -> None:
            body = h._body()
            service = IsokoService(str(body.get("root", "")))
            h._json(200, service.uninstall(str(body.get("name", ""))))

        @r.route("GET", "/api/project/packages")
        def pkg_installed(h: _Handler, path: str) -> None:
            root = h._project_root()
            if root is None:
                h._error(400, "missing root")
                return
            service = IsokoService(root)
            h._json(200, {"packages": service.installed()})

        # git
        @r.route("GET", "/api/project/git/status")
        def git_status(h: _Handler, path: str) -> None:
            root = h._project_root()
            if root is None:
                h._error(400, "missing root")
                return
            h._json(200, GitService(root).status())

        @r.route("GET", "/api/project/git/log")
        def git_log(h: _Handler, path: str) -> None:
            root = h._project_root()
            if root is None:
                h._error(400, "missing root")
                return
            h._json(200, {"log": GitService(root).log()})

        @r.route("POST", "/api/project/git/commit")
        def git_commit(h: _Handler, path: str) -> None:
            body = h._body()
            service = GitService(str(body.get("root", "")))
            h._json(200, service.commit(str(body.get("message", ""))))

        @r.route("POST", "/api/project/git/init")
        def git_init(h: _Handler, path: str) -> None:
            body = h._body()
            h._json(200, GitService(str(body.get("root", ""))).init())

        # extensions
        @r.route("GET", "/api/extensions")
        def extensions_list(h: _Handler, path: str) -> None:
            h._json(200, {"extensions": ExtensionsService().list_installed()})

        @r.route("GET", "/api/extensions/browse")
        def extensions_browse(h: _Handler, path: str) -> None:
            query = ""
            raw = path.split("?", 1)[1] if "?" in path else ""
            for part in raw.split("&"):
                if part.startswith("q="):
                    query = unquote(part[2:])
            h._json(200, {"extensions": ExtensionsService().browse(query)})

        @r.route("POST", "/api/extensions/install")
        def extensions_install(h: _Handler, path: str) -> None:
            body = h._body()
            result = ExtensionsService().install(
                str(body.get("name", "")), str(body.get("version", "")))
            if result is None:
                h._error(404, "extension not found in registry")
                return
            h._json(200, result)

        @r.route("POST", "/api/extensions/uninstall")
        def extensions_uninstall(h: _Handler, path: str) -> None:
            body = h._body()
            ok = ExtensionsService().uninstall(str(body.get("name", "")))
            h._json(200, {"ok": ok})

        # static frontend
        @r.route("GET", "/assets")
        def assets(h: _Handler, path: str) -> None:
            self._serve_static(h, path)

        @r.route("GET", "/docs")
        def docs(h: _Handler, path: str) -> None:
            self._serve_static(h, path)

        @r.route("GET", "/")
        def index(h: _Handler, path: str) -> None:
            self._serve_static(h, path)

        @r.route("GET", "/favicon.ico")
        def favicon(h: _Handler, path: str) -> None:
            self._serve_static(h, path)

        @r.route("GET", "/logo.png")
        def logo(h: _Handler, path: str) -> None:
            self._serve_static(h, path)

    def _serve_static(self, h: _Handler, path: str) -> None:
        clean = path.split("?", 1)[0]
        rel = clean if clean != "/" else "/index.html"
        target = os.path.normpath(os.path.join(self.static_dir, rel.lstrip("/")))
        if not target.startswith(os.path.normpath(self.static_dir) + os.sep) and rel.lstrip("/"):
            h._error(403, "forbidden")
            return
        if not os.path.isfile(target):
            if not os.path.isdir(self.static_dir):
                h._send(200, b"<!doctype html><meta charset=utf-8><title>I Studio IDE</title>"
                              b"<h1>I Studio IDE</h1><p>Frontend not built. Run <code>npm run build</code> in <code>ide/</code>.</p>")
                return
            h._error(404, "not found")
            return
        content_type = "text/html"
        if target.endswith(".js"):
            content_type = "text/javascript"
        elif target.endswith(".css"):
            content_type = "text/css"
        elif target.endswith(".svg"):
            content_type = "image/svg+xml"
        elif target.endswith(".png"):
            content_type = "image/png"
        elif target.endswith(".ico"):
            content_type = "image/x-icon"
        elif target.endswith(".woff2"):
            content_type = "font/woff2"
        elif target.endswith(".json"):
            content_type = "application/json"
        with open(target, "rb") as f:
            h._send(200, f.read(), content_type)

    # ── lifecycle ───────────────────────────────────────────────────────

    def close(self) -> None:
        self.terminals.close_all()
        with self._debug_lock:
            sessions = list(self.debug_sessions.values())
            self.debug_sessions.clear()
        for session in sessions:
            session.stop()


class _FastHTTPServer(ThreadingHTTPServer):
    """ThreadingHTTPServer whose bind skips the blocking reverse-DNS lookup.

    ``HTTPServer.server_bind`` calls ``socket.getfqdn(host)`` on every startup,
    which on macOS can stall for seconds inside the system resolver and race
    with garbage collection running in background daemon threads. We bind
    normally and set ``server_name`` directly instead.
    """

    daemon_threads = True

    def server_bind(self) -> None:
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = host
        self.server_port = port


def make_server(host: str, port: int, app: IdeApplication) -> _FastHTTPServer:
    server = _FastHTTPServer((host, port), _Handler)
    _Handler.app = app
    return server
