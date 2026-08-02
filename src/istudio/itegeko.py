"""I STUDIO — CLI subcommands for I Studio platform."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    ISTUDIO_VERSION,
    PROJECT_TYPE_DISPLAY,
    ProjectType,
    ProfilerType,
)
from .akazi import WorkspaceManager
from .indura import EditorEngine
from .ururimi import LanguageServer
from .ugutunganya import Debugger, BreakpointType
from .gupima import Profiler
from .umufasha import AIAssistant
from .porogaramu import ExtensionManager
from .iterambere import CollaborationManager


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="istudio", description="I STUDIO IDE Platform CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {ISTUDIO_VERSION}")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    p_workspace = subparsers.add_parser("workspace", help="Workspace management")
    p_workspace.add_argument("action", choices=["init", "open", "info"])
    p_workspace.add_argument("path", nargs="?", default=".", help="Workspace path")

    p_project = subparsers.add_parser("project", help="Project management")
    p_project.add_argument("action", choices=["create", "list", "info"])
    p_project.add_argument("name", nargs="?", help="Project name")
    p_project.add_argument("--path", default=".", help="Project path")
    p_project.add_argument("--type", default="library",
                           choices=[pt.value for pt in ProjectType],
                           help="Project type. Available types:\n" + "\n".join(
                               f"  {pt.value:25s} {label}"
                               for pt, label in PROJECT_TYPE_DISPLAY.items()
                           ))

    p_lint = subparsers.add_parser("lint", help="Lint a file")
    p_lint.add_argument("file", help="File to lint")
    p_lint.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    p_format = subparsers.add_parser("format", help="Format a file")
    p_format.add_argument("file", help="File to format")

    p_debug = subparsers.add_parser("debug", help="Debugging commands")
    p_debug.add_argument("action", choices=["start", "stop", "step", "continue", "break", "break-list"])

    p_profile = subparsers.add_parser("profile", help="Profiling commands")
    p_profile.add_argument("action", choices=["start", "stop", "list", "results"])
    p_profile.add_argument("--type", default="cpu", choices=["cpu", "memory"], help="Profile type")
    p_profile.add_argument("--name", default="session", help="Session name")

    p_ai = subparsers.add_parser("ai", help="AI Assistant commands")
    p_ai.add_argument("action", choices=["chat", "complete", "conversations"])
    p_ai.add_argument("message", nargs="?", default="", help="Message for chat")
    p_ai.add_argument("--project-type", default=None,
                      choices=[pt.value for pt in ProjectType],
                      help="Set project context for AI")

    p_extension = subparsers.add_parser("extension", help="Extension management")
    p_extension.add_argument("action", choices=["install", "uninstall", "list", "enable", "disable"])
    p_extension.add_argument("id", nargs="?", help="Extension ID")
    p_extension.add_argument("--path", help="Manifest path for install")

    p_collab = subparsers.add_parser("collaboration", help="Collaboration commands")
    p_collab.add_argument("action", choices=["session-create", "session-list", "user-list", "review-create", "review-list"])
    p_collab.add_argument("id", nargs="?", help="Session or review ID")

    p_server = subparsers.add_parser("server", help="Start I Studio language server")
    p_server.add_argument("--stdio", action="store_true", help="Use stdio transport")

    p_desktop = subparsers.add_parser("desktop", help="Launch the I Studio desktop application")
    p_desktop.add_argument("path", nargs="?", default=None, help="Optional folder to open as a workspace")

    p_ide = subparsers.add_parser("ide", help="Launch the I Studio IDE (native window by default)")
    p_ide.add_argument("path", nargs="?", default=None, help="workspace/project folder to open")
    p_ide.add_argument("--host", default="127.0.0.1", help="bind host (default: 127.0.0.1)")
    p_ide.add_argument("--port", type=int, default=8790, help="bind port (default: 8790)")
    p_ide.add_argument("--no-open", action="store_true", help="do not open a browser automatically")
    p_ide.add_argument("--browser", action="store_true", help="open in the default web browser instead of a native window")
    p_ide.add_argument("--base-dir", default=None, help="directory that stores created projects")

    return parser


def cmd_workspace(args: argparse.Namespace) -> int:
    ws = WorkspaceManager()
    if args.action == "init":
        ws.load_or_create(args.path)
        print(json.dumps({"status": "ok", "path": args.path, "name": ws.config.name}))
    elif args.action == "open":
        ws = WorkspaceManager(args.path)
        print(json.dumps({"status": "ok", "path": args.path, "name": ws.config.name}))
    elif args.action == "info":
        ws = WorkspaceManager(args.path) if args.path else ws
        print(json.dumps({"name": ws.config.name, "root": ws.config.root_path,
                          "projects": ws.config.projects, "extensions": ws.config.extensions}, indent=2))
    return 0


def cmd_project(args: argparse.Namespace) -> int:
    ws = WorkspaceManager()
    pm = ws.project_manager
    if args.action == "create":
        if not args.name:
            print("Project name is required.", file=sys.stderr)
            return 1
        cfg = pm.create_project(args.name, args.path, args.type)
        type_label = PROJECT_TYPE_DISPLAY.get(cfg.project_type, cfg.type)
        print(json.dumps({
            "status": "ok",
            "name": cfg.name,
            "type": type_label,
            "path": args.path,
        }, indent=2))
        # Seed AI assistant with project context
        ai = AIAssistant()
        ai.set_project_context(cfg.project_type)
    elif args.action == "list":
        projects = pm.list_projects()
        print(json.dumps([p.name for p in projects]) if projects else "[]")
    elif args.action == "info":
        cfg = pm.get_project(args.name) if args.name else None
        if cfg:
            print(json.dumps({"name": cfg.name, "version": cfg.version, "type": cfg.type, "language": cfg.language}))
        else:
            print(json.dumps({"error": f"Project '{args.name}' not found"}))
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    ls = LanguageServer()
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        diagnostics = ls.analyze(content, args.file)
        output_format = getattr(args, "format", "text")
        if output_format == "json":
            print(json.dumps([{
                "severity": d.severity.value,
                "message": d.message,
                "line": d.range.start.line + 1,
                "column": d.range.start.column + 1,
                "code": d.code,
            } for d in diagnostics], indent=2))
        else:
            for d in diagnostics:
                print(f"{args.file}:{d.range.start.line + 1}:{d.range.start.column + 1}: {d.severity.value}: {d.message}")
        return 1 if diagnostics else 0
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1


def cmd_format(args: argparse.Namespace) -> int:
    ls = LanguageServer()
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        formatted = ls.format_document(content, args.file)
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"Formatted: {args.file}")
        return 0
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1


def cmd_debug(args: argparse.Namespace) -> int:
    dbg = Debugger()
    if args.action == "start":
        dbg.start()
        print(json.dumps({"status": "started"}))
    elif args.action == "stop":
        dbg.stop()
        print(json.dumps({"status": "stopped"}))
    elif args.action == "step":
        dbg.step_over()
        print(json.dumps({"status": "step"}))
    elif args.action == "continue":
        dbg.continue_execution()
        print(json.dumps({"status": "continued"}))
    elif args.action == "break":
        print(json.dumps({"status": "ok", "hint": "Use break <file>:<line>"}))
    elif args.action == "break-list":
        bps = dbg.get_breakpoints()
        print(json.dumps([{"file": b.file, "line": b.line, "enabled": b.enabled} for b in bps], indent=2))
    return 0


def cmd_profile(args: argparse.Namespace) -> int:
    profiler = Profiler()
    if args.action == "start":
        ptype = ProfilerType(args.type)
        sid = profiler.start_session(getattr(args, "name", "session"), ptype)
        print(json.dumps({"status": "started", "session_id": sid}))
    elif args.action == "stop":
        result = profiler.stop_session()
        if result:
            print(json.dumps({"status": "stopped", "total_time_ms": result.total_time_ms,
                              "call_count": result.call_count}))
        else:
            print(json.dumps({"error": "No active session"}))
    elif args.action == "list":
        sessions = profiler.list_sessions()
        print(json.dumps(sessions, indent=2))
    elif args.action == "results":
        result = profiler.get_results()
        if result:
            print(json.dumps({"total_time_ms": result.total_time_ms,
                              "call_count": result.call_count,
                              "details": result.details}))
        else:
            print(json.dumps({"error": "No results available"}))
    return 0


def cmd_ai(args: argparse.Namespace) -> int:
    ai = AIAssistant()

    pt = getattr(args, "project_type", None)
    if pt:
        try:
            ptype = ProjectType(pt)
            ai.set_project_context(ptype)
        except ValueError:
            pass

    if args.action == "chat":
        if args.message:
            ctx = ai.get_project_context()
            if ctx:
                context_info = ctx.split(".")[0] + "."
                response = ai.send_message(f"[{context_info}] {args.message}")
            else:
                response = ai.send_message(args.message)
            print(response)
        else:
            print("Please provide a message")
    elif args.action == "complete":
        print(json.dumps({"status": "ok", "hint": "Use editor for code completion"}))
    elif args.action == "conversations":
        convs = ai.list_conversations()
        print(json.dumps(convs, indent=2))
    return 0


def cmd_extension(args: argparse.Namespace) -> int:
    em = ExtensionManager()
    if args.action == "install":
        plugin_path = getattr(args, "path", None)
        if plugin_path:
            manifest = em.install_plugin(plugin_path)
            print(json.dumps({"status": "ok", "id": manifest.id, "name": manifest.name}))
        else:
            print("--path required for install")
    elif args.action == "uninstall":
        if args.id:
            em.uninstall_plugin(args.id)
            print(json.dumps({"status": "ok", "id": args.id}))
    elif args.action == "list":
        plugins = em.list_plugins()
        print(json.dumps(plugins, indent=2))
    elif args.action == "enable":
        if args.id and em.enable_plugin(args.id):
            print(json.dumps({"status": "ok", "id": args.id}))
    elif args.action == "disable":
        if args.id and em.disable_plugin(args.id):
            print(json.dumps({"status": "ok", "id": args.id}))
    return 0


def cmd_collaboration(args: argparse.Namespace) -> int:
    cm = CollaborationManager()
    if args.action == "session-create":
        session = cm.create_session(args.id or "default", "local")
        print(json.dumps({"status": "ok", "session_id": session["id"], "name": session["name"]}))
    elif args.action == "session-list":
        sessions = cm.list_sessions()
        print(json.dumps([{"id": s["id"], "name": s["name"], "users": len(s["users"])} for s in sessions], indent=2))
    elif args.action == "user-list":
        users = cm.list_users()
        print(json.dumps(users, indent=2))
    elif args.action == "review-create":
        review = cm.create_review(args.id or "review-1", f"Review {args.id}", "local", [])
        print(json.dumps({"status": "ok", "review_id": review["id"]}))
    elif args.action == "review-list":
        reviews = cm.get_reviews()
        print(json.dumps([{"id": r["id"], "title": r["title"], "status": r["status"]} for r in reviews], indent=2))
    return 0


def cmd_server(args: argparse.Namespace) -> int:
    ls = LanguageServer()
    if args.stdio:
        import sys
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                method = msg.get("method", "")
                params = msg.get("params", {})
                if method == "initialize":
                    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"capabilities": {}}}
                elif method == "textDocument/didOpen":
                    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": None}
                elif method == "textDocument/didChange":
                    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": None}
                elif method == "textDocument/completion":
                    content = params.get("textDocument", {}).get("text", "")
                    pos = params.get("position", {})
                    completions = ls.get_completions(content, type("pos", (), {"line": pos.get("line", 0), "column": pos.get("character", 0)})())
                    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"items": [{"label": c.label, "kind": c.kind.value, "detail": c.detail} for c in completions]}}
                elif method == "textDocument/hover":
                    content = params.get("textDocument", {}).get("text", "")
                    pos = params.get("position", {})
                    hover = ls.get_hover(content, type("pos", (), {"line": pos.get("line", 0), "column": pos.get("character", 0)})())
                    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"contents": hover.contents if hover else []}}
                elif method == "shutdown":
                    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": None}
                    print(json.dumps(response))
                    break
                else:
                    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": None}
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                continue
    return 0


def cmd_desktop(args: argparse.Namespace) -> int:
    """Launch the I Studio desktop application (tkinter)."""
    try:
        from .desktop import is_available, main as desktop_main
    except Exception as exc:  # pragma: no cover
        print(f"Could not load desktop application: {exc}", file=sys.stderr)
        return 1
    if not is_available():
        print("I Studio Desktop requires a graphical display (tkinter).", file=sys.stderr)
        return 1
    argv = [args.path] if getattr(args, "path", None) else []
    return desktop_main(argv)


def cmd_ide(args: argparse.Namespace) -> int:
    """Launch the I Studio web IDE server."""
    from .ide.main import main as ide_main

    argv: list[str] = []
    if getattr(args, "path", None):
        argv.append(args.path)
    argv += ["--host", args.host, "--port", str(args.port)]
    if getattr(args, "no_open", False):
        argv.append("--no-open")
    if getattr(args, "browser", False):
        argv.append("--browser")
    if getattr(args, "base_dir", None):
        argv += ["--base-dir", args.base_dir]
    return ide_main(argv)


def main(argv: Optional[List[str]] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    commands = {
        "workspace": cmd_workspace,
        "project": cmd_project,
        "lint": cmd_lint,
        "format": cmd_format,
        "debug": cmd_debug,
        "profile": cmd_profile,
        "ai": cmd_ai,
        "extension": cmd_extension,
        "collaboration": cmd_collaboration,
        "server": cmd_server,
        "desktop": cmd_desktop,
        "ide": cmd_ide,
    }
    return commands[args.command](args)


def register_subcommands(subparsers: Any) -> None:
    ip = subparsers.add_parser("istudio", help="I STUDIO IDE Platform commands")
    ip_se = ip.add_subparsers(dest="istudio_command")

    p_ws = ip_se.add_parser("workspace", help="Workspace management")
    p_ws.add_argument("action", choices=["init", "open", "info"])
    p_ws.add_argument("path", nargs="?", default=".")

    p_proj = ip_se.add_parser("project", help="Project management")
    p_proj.add_argument("action", choices=["create", "list", "info"])
    p_proj.add_argument("name", nargs="?")
    p_proj.add_argument("--path", default=".")
    p_proj.add_argument("--type", default="library",
                        choices=[pt.value for pt in ProjectType],
                        help="Project type")

    p_lint = ip_se.add_parser("lint", help="Lint a file")
    p_lint.add_argument("file")
    p_lint.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    p_lint.set_defaults(func=lambda a: cmd_lint(a) or 0)

    p_fmt = ip_se.add_parser("format", help="Format a file")
    p_fmt.add_argument("file")
    p_fmt.set_defaults(func=lambda a: cmd_format(a) or 0)

    p_dbg = ip_se.add_parser("debug", help="Debugging commands")
    p_dbg.add_argument("action", choices=["start", "stop", "step", "continue", "break", "break-list"])

    p_prof = ip_se.add_parser("profile", help="Profiling commands")
    p_prof.add_argument("action", choices=["start", "stop", "list", "results"])
    p_prof.add_argument("--type", default="cpu", choices=["cpu", "memory"])
    p_prof.add_argument("--name", default="session")

    p_ai = ip_se.add_parser("ai", help="AI Assistant commands")
    p_ai.add_argument("action", choices=["chat", "conversations"])
    p_ai.add_argument("message", nargs="?", default="")
    p_ai.add_argument("--project-type", default=None,
                      choices=[pt.value for pt in ProjectType],
                      help="Set project context for AI")

    p_ext = ip_se.add_parser("extension", help="Extension management")
    p_ext.add_argument("action", choices=["install", "uninstall", "list", "enable", "disable"])
    p_ext.add_argument("id", nargs="?")
    p_ext.add_argument("--path", help="Manifest path for install")

    p_collab = ip_se.add_parser("collaboration", help="Collaboration commands")
    p_collab.add_argument("action", choices=["session-create", "session-list", "user-list", "review-create", "review-list"])
    p_collab.add_argument("id", nargs="?")

    p_srv = ip_se.add_parser("server", help="Start I Studio language server")
    p_srv.add_argument("--stdio", action="store_true")

    p_desktop = ip_se.add_parser("desktop", help="Launch the I Studio desktop application")
    p_desktop.add_argument("path", nargs="?", default=None)

    p_ide = ip_se.add_parser("ide", help="Launch the I Studio IDE (native window by default)")
    p_ide.add_argument("path", nargs="?", default=None)
    p_ide.add_argument("--host", default="127.0.0.1")
    p_ide.add_argument("--port", type=int, default=8790)
    p_ide.add_argument("--no-open", action="store_true")
    p_ide.add_argument("--browser", action="store_true", help="open in the default web browser instead of a native window")
    p_ide.add_argument("--base-dir", default=None)


def genda(args: argparse.Namespace) -> int:
    istudio_cmd = getattr(args, "istudio_command", None)
    if not istudio_cmd:
        print("istudio: missing command\nRun 'isoko istudio --help' for usage.")
        return 1
    istudio_commands = {
        "workspace": cmd_workspace,
        "project": cmd_project,
        "lint": cmd_lint,
        "format": cmd_format,
        "debug": cmd_debug,
        "profile": cmd_profile,
        "ai": cmd_ai,
        "extension": cmd_extension,
        "collaboration": cmd_collaboration,
        "server": cmd_server,
        "desktop": cmd_desktop,
        "ide": cmd_ide,
    }
    handler = istudio_commands.get(istudio_cmd)
    if not handler:
        print(f"istudio: unknown command '{istudio_cmd}'")
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
