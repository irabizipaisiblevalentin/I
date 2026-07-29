"""Tests for istudio.gupima — Profiler."""

from __future__ import annotations

import time

from src.istudio.gupima import Profiler, CPUSampler, MemorySampler
from src.istudio.ibikoreshingiro import ProfilerType


def test_profiler_init():
    p = Profiler()
    assert p.get_active_session() is None
    assert p.list_sessions() == []


def test_profiler_start_stop():
    p = Profiler()
    sid = p.start_session("test", ProfilerType.CPU)
    assert sid is not None
    assert p.get_active_session() == sid
    result = p.stop_session()
    assert result is not None
    assert result.type == ProfilerType.CPU
    assert result.total_time_ms >= 0


def test_profiler_multiple_sessions():
    p = Profiler()
    s1 = p.start_session("a", ProfilerType.CPU)
    p.stop_session()
    s2 = p.start_session("b", ProfilerType.MEMORY)
    p.stop_session()
    assert len(p.list_sessions()) == 2


def test_profiler_add_sample():
    p = Profiler()
    sid = p.start_session("test", ProfilerType.CPU)
    p.add_sample({"cpu": 50})
    assert len(p._sessions[sid]["samples"]) == 1
    p.stop_session()


def test_profiler_get_session():
    p = Profiler()
    sid = p.start_session("test")
    session = p.get_session(sid)
    assert session is not None
    assert session["name"] == "test"
    assert p.get_session("nonexistent") is None


def test_profiler_get_results():
    p = Profiler()
    sid = p.start_session("test", ProfilerType.MEMORY)
    p.stop_session()
    result = p.get_results(sid)
    assert result is not None
    assert result.type == ProfilerType.MEMORY


def test_profiler_get_results_none():
    p = Profiler()
    assert p.get_results() is None


def test_profiler_clear():
    p = Profiler()
    p.start_session("test")
    p.clear()
    assert p.list_sessions() == []
    assert p.get_active_session() is None


def test_profiler_stop_none():
    p = Profiler()
    assert p.stop_session() is None


def test_profiler_events():
    p = Profiler()
    events = []
    p.on("session.started", lambda d: events.append("started"))
    p.on("session.stopped", lambda d: events.append("stopped"))
    p.start_session("test")
    p.stop_session()
    assert "started" in events
    assert "stopped" in events


def test_cpu_sampler():
    p = Profiler()
    cs = CPUSampler(p)
    sample = cs.sample()
    assert "cpu_percent" in sample
    assert "cpu_count" in sample


def test_memory_sampler():
    p = Profiler()
    ms = MemorySampler(p)
    sample = ms.sample()
    assert "total_mb" in sample
    assert "percent_used" in sample


def test_profiler_session_list_format():
    p = Profiler()
    s1 = p.start_session("cpu-test", ProfilerType.CPU)
    p.stop_session()
    s2 = p.start_session("mem-test", ProfilerType.MEMORY)
    p.stop_session()
    sessions = p.list_sessions()
    for s in sessions:
        assert "id" in s
        assert "name" in s
        assert "type" in s
        assert "start_time" in s
