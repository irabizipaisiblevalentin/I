"""Tests for istudio.ide.run and istudio.ide.debug — SSE streaming services."""

from __future__ import annotations

import json
import os
import time

from src.istudio.ide.debug import DebugSession
from src.istudio.ide.run import RunService
from src.istudio.ide.sse import SSEHub, sse_frame


def _wait(condition, timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.02)
    return False


def _drain_until(q, marker: str, timeout: float = 20.0) -> list[str]:
    frames = []
    joined = ""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            frame = q.get(timeout=0.25)
        except Exception:  # noqa: BLE001
            if marker in joined:
                return frames
            continue
        frames.append(frame)
        joined += frame
        if marker in joined:
            return frames
    return frames


def test_sse_frame_format() -> None:
    frame = sse_frame("done", {"ok": True}).decode("utf-8")
    assert frame.startswith("event: done\n")
    assert "\n\n" in frame
    payload = json.loads(frame.split("data: ", 1)[1])
    assert payload == {"ok": True}


def test_sse_hub_publish_subscribe() -> None:
    hub = SSEHub()
    q = hub.subscribe("x:1")
    hub.publish("x:1", "msg", {"a": 1})
    frame = q.get(timeout=1)
    assert "msg" in frame
    hub.unsubscribe("x:1", q)
    hub.publish("x:1", "msg", {"a": 2})
    assert q.empty()


def test_run_service_streams_output(temp_dir: str) -> None:
    hub = SSEHub()
    service = RunService(hub)
    job = service.start_source('andika "ping"\nandika "pong"\n')
    frames = _drain_until(hub.subscribe(f"run:{job}"), "event: done", timeout=20)
    joined = "\n".join(frames)
    assert "ping" in joined and "pong" in joined
    assert "event: done" in joined
    assert '"ok": true' in joined


def test_run_service_reports_compile_error(temp_dir: str) -> None:
    hub = SSEHub()
    service = RunService(hub)
    job = service.start_source("shyira x = 1\ny\n")
    frames = _drain_until(hub.subscribe(f"run:{job}"), "event: done", timeout=20)
    joined = "\n".join(frames)
    assert "event: done" in joined
    assert '"ok": false' in joined


def test_run_cancel_unknown_job() -> None:
    service = RunService(SSEHub())
    assert service.cancel("nope") is False


def test_debug_session_lifecycle(temp_dir: str) -> None:
    path = os.path.join(temp_dir, "prog.i")
    with open(path, "w", encoding="utf-8") as f:
        f.write("shyira x = 1\nshyira y = 2\nandika x + y\n")

    hub = SSEHub()
    session = DebugSession(hub, path)
    q = hub.subscribe(session._stream)
    session.set_breakpoints([3])
    session.start()

    frames = []
    ended = False
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            frame = q.get(timeout=0.25)
        except Exception:  # noqa: BLE001
            if ended:
                break
            continue
        frames.append(frame)
        event = frame.split("event: ", 1)[1].split("\n")[0] if "event: " in frame else ""
        if event == "stopped":
            session.continue_run()
        elif event == "ended":
            ended = True
            break

    joined = "\n".join(frames)
    assert ended, "debug session should end after continue"
    assert "event: started" in joined
    assert "event: breakpoints" in joined
    assert "event: stopped" in joined
    assert '"ok": true' in joined
    session.stop()


def test_debug_steps_to_next_line(temp_dir: str) -> None:
    path = os.path.join(temp_dir, "step.i")
    with open(path, "w", encoding="utf-8") as f:
        f.write("shyira a = 1\nandika a\nandika 9\n")

    hub = SSEHub()
    session = DebugSession(hub, path)
    q = hub.subscribe(session._stream)
    session.set_breakpoints([2])
    session.start()

    deadline = time.monotonic() + 20
    stopped_lines = []
    ended = False
    while time.monotonic() < deadline:
        try:
            frame = q.get(timeout=0.25)
        except Exception:  # noqa: BLE001
            if ended:
                break
            continue
        event = frame.split("event: ", 1)[1].split("\n")[0] if "event: " in frame else ""
        if event == "stopped":
            data = json.loads(frame.split("data: ", 1)[1])
            stopped_lines.append(data["line"])
            if len(stopped_lines) < 2:
                session.step()
            else:
                session.continue_run()
        elif event == "ended":
            ended = True
            break

    assert stopped_lines, "expected at least one stop"
    assert len(stopped_lines) >= 2, "step should stop on a later line"
    assert ended
    session.stop()
