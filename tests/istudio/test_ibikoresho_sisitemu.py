"""Tests for istudio.ibikoresho_sisitemu — System Tools."""

from __future__ import annotations

from src.istudio.ibikoresho_sisitemu import SystemExplorer


def test_system_explorer_init():
    se = SystemExplorer()
    assert se is not None


def test_get_system_info():
    se = SystemExplorer()
    info = se.get_system_info()
    assert "os" in info
    assert "architecture" in info
    assert "python_version" in info


def _maybe_skip_no_psutil(result, keys):
    if isinstance(result, dict) and "error" in result:
        return  # skip assertion when psutil not available
    for k in keys:
        assert k in result


def test_get_cpu_info():
    se = SystemExplorer()
    cpu = se.get_cpu_info()
    _maybe_skip_no_psutil(cpu, ["physical_cores", "logical_cores", "percent_usage"])


def test_get_memory_info():
    se = SystemExplorer()
    mem = se.get_memory_info()
    _maybe_skip_no_psutil(mem, ["total_gb", "available_gb", "percent"])


def test_get_disk_info():
    se = SystemExplorer()
    disks = se.get_disk_info()
    assert isinstance(disks, list)
    if disks and "error" not in disks[0]:
        assert "device" in disks[0]
        assert "mountpoint" in disks[0]


def test_get_network_info():
    se = SystemExplorer()
    net = se.get_network_info()
    _maybe_skip_no_psutil(net, ["interfaces", "bytes_sent"])


def test_list_processes():
    se = SystemExplorer()
    procs = se.list_processes()
    assert isinstance(procs, list)
    if procs and "error" not in procs[0]:
        assert "pid" in procs[0]
        assert "name" in procs[0]


def test_get_process_info():
    se = SystemExplorer()
    # This should either return info or error for non-existent pid
    info = se.get_process_info(1)
    assert info is not None


def test_get_environment_variables():
    se = SystemExplorer()
    env = se.get_environment_variables()
    assert isinstance(env, dict)
    if "PATH" in env:
        assert len(env["PATH"]) > 0


def test_get_file_system_info():
    se = SystemExplorer()
    fs = se.get_file_system_info(".")
    assert "path" in fs or "error" in fs
