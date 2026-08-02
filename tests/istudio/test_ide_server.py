"""Tests for istudio.ide.server — HTTP integration over a live in-process server."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import threading
import urllib.request
from urllib import error as urllib_error

import pytest

from src.istudio.ide.server import IdeApplication, make_server


@pytest.fixture
def base_url(temp_dir: str):
    app = IdeApplication(os.path.join(temp_dir, "workspace"), static_dir=os.path.join(temp_dir, "static"))
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield f"http://{host}:{port}"
    app.close()
    server.shutdown()
    server.server_close()


def _request(url: str, method: str = "GET", body=None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except ValueError:
                return resp.status, raw
    except urllib_error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _sse_read(url: str, until: str = "event: done", timeout: float = 20.0) -> str:
    """Read an SSE stream with a raw socket (EventSource-like), returning all
    frames received before the marker appears. urllib/http.client is avoided:
    its buffered reads misbehave on slow streaming responses."""
    from urllib.parse import urlsplit

    parts = urlsplit(url)
    host, port = parts.hostname, parts.port
    sock = socket.create_connection((host, port), timeout=10)
    sock.settimeout(timeout)
    try:
        sock.sendall(
            (
                f"GET {parts.path} HTTP/1.1\r\n"
                f"Host: {host}:{port}\r\n"
                "Accept: text/event-stream\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii")
        )
        data = b""
        while until.encode() not in data:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        return data.decode("utf-8", "replace")
    finally:
        sock.close()


def test_health(base_url: str) -> None:
    status, body = _request(f"{base_url}/api/health")
    assert status == 200
    assert body["ok"] is True


def test_templates_list(base_url: str) -> None:
    status, body = _request(f"{base_url}/api/templates")
    assert status == 200
    assert len(body) >= 10
    assert all(t["key"] for t in body)


def test_project_create_read_write(base_url: str) -> None:
    status, created = _request(f"{base_url}/api/projects/create", "POST", {"name": "demo", "template": "console"})
    assert status == 200
    root = created["path"]
    assert os.path.isfile(os.path.join(root, "src", "main.i"))

    status, read = _request(f"{base_url}/api/project/file?root={root}&path=src/main.i")
    assert status == 200
    assert "andika" in read["content"]

    status, _ = _request(f"{base_url}/api/project/file", "POST", {"root": root, "path": "src/main.i", "content": "shyira x = 1\nandika x\n"})
    assert status == 200
    assert _request(f"{base_url}/api/project/file?root={root}&path=src/main.i")[1]["content"] == "shyira x = 1\nandika x\n"


def test_diagnostics_endpoint(base_url: str) -> None:
    status, body = _request(f"{base_url}/api/diagnostics", "POST", {"content": "shyira x = 1\nandika x\n"})
    assert status == 200
    assert body["diagnostics"] == []

    status, body = _request(f"{base_url}/api/diagnostics", "POST", {"content": "shyira x = unknown_symbol_xyz\n"})
    assert status == 200
    assert body["diagnostics"]


def test_completion_hover_symbols_format(base_url: str) -> None:
    _, comp = _request(f"{base_url}/api/completion", "POST", {"content": "shy\n", "line": 1, "column": 3})
    assert any(c["label"] == "shyira" for c in comp["completions"])

    _, hover = _request(f"{base_url}/api/hover", "POST", {"content": "andika 1\n", "line": 1, "column": 1})
    assert hover["hover"] is not None

    _, syms = _request(f"{base_url}/api/symbols", "POST", {"content": "umurimo main() -> int\nsubira 0\niherezo\n"})
    assert any(s["name"] == "main" for s in syms["symbols"])

    _, fmt = _request(f"{base_url}/api/format", "POST", {"content": "umurimo f()\nandika 1\niherezo\n"})
    assert "    andika 1" in fmt["formatted"]


def test_run_endpoint_streams_events(base_url: str) -> None:
    status, body = _request(f"{base_url}/api/run", "POST", {"source": 'andika "streamed"\n'})
    assert status == 200
    job_id = body["job_id"]

    text = _sse_read(f"{base_url}/sse/run/{job_id}", until="event: done")
    assert "streamed" in text
    assert "event: done" in text
    assert '"ok": true' in text


def test_traversal_blocked_over_http(base_url: str) -> None:
    status, body = _request(f"{base_url}/api/projects/create", "POST", {"name": "sec", "template": "console"})
    root = body["path"]
    status, body = _request(f"{base_url}/api/project/file?root={root}&path=../../outside.txt")
    assert status == 400
    assert "escapes" in body["error"]


def test_static_index_served(base_url: str) -> None:
    status, body = _request(f"{base_url}/")
    assert status == 200
    assert "I Studio IDE" in body


def test_static_assets_served(base_url: str, temp_dir: str) -> None:
    static = os.path.join(temp_dir, "static")
    os.makedirs(os.path.join(static, "assets"), exist_ok=True)
    with open(os.path.join(static, "index.html"), "w", encoding="utf-8") as f:
        f.write("<html><head><title>I Studio IDE</title></head></html>")
    with open(os.path.join(static, "assets", "bundle.js"), "w", encoding="utf-8") as f:
        f.write("console.log('hi');")

    status, body = _request(f"{base_url}/")
    assert status == 200
    assert "I Studio IDE" in body

    status, body = _request(f"{base_url}/assets/bundle.js")
    assert status == 200
    assert body == "console.log('hi');"


def test_git_init_commit(base_url: str) -> None:
    _, created = _request(f"{base_url}/api/projects/create", "POST", {"name": "gitproj", "template": "console"})
    root = created["path"]

    status, body = _request(f"{base_url}/api/project/git/status?root={root}")
    assert status == 200
    assert body["is_repo"] is False

    status, body = _request(f"{base_url}/api/project/git/init", "POST", {"root": root})
    assert status == 200 and body["ok"] is True

    status, body = _request(f"{base_url}/api/project/git/status?root={root}")
    assert status == 200 and body["is_repo"] is True

    for cfg in (["config", "user.email", "ide@test.local"], ["config", "user.name", "IDE Test"]):
        assert subprocess.run(["git", "-C", root, *cfg], capture_output=True).returncode == 0

    status, body = _request(f"{base_url}/api/project/git/commit", "POST", {"root": root, "message": "initial"})
    assert status == 200 and body["ok"] is True

    status, body = _request(f"{base_url}/api/project/git/log?root={root}")
    assert status == 200
    assert body["log"] and body["log"][0]["message"] == "initial"


def test_debug_over_http(base_url: str) -> None:
    _, created = _request(f"{base_url}/api/projects/create", "POST", {"name": "dbg", "template": "console"})
    root = created["path"]
    main = os.path.join(root, "src", "main.i")
    with open(main, "w", encoding="utf-8") as f:
        f.write("shyira x = 1\nshyira y = 2\nandika x + y\n")

    status, body = _request(f"{base_url}/api/debug/start", "POST", {"root": root, "file": main})
    assert status == 200
    session_id = body["session_id"]

    text = _sse_read(f"{base_url}/sse/debug/{session_id}", until="event: ended")
    assert "event: started" in text
    assert '"ok": true' in text
