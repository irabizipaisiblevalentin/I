"""Tests for isoko commands/__init__.py — verify all command modules are importable."""

import pytest

from isoko.commands import (
    new, init, build, run, test, bench,
    check, fmt, lint, doc, publish,
    install, uninstall, update, upgrade,
    search, info, login, logout, cache,
    doctor, clean, verify, audit, vendor,
    graph, tree, workspace, self_update,
)


class TestCommandImports:
    def test_all_commands_have_add_subparser(self):
        commands = [
            new, init, build, run, test, bench,
            check, fmt, lint, doc, publish,
            install, uninstall, update, upgrade,
            search, info, login, logout, cache,
            doctor, clean, verify, audit, vendor,
            graph, tree, workspace, self_update,
        ]
        for cmd in commands:
            assert hasattr(cmd, "add_subparser"), f"{cmd.__name__} missing add_subparser"
            assert callable(cmd.add_subparser)

    def test_all_commands_have_run(self):
        commands = [
            new, init, build, run, test, bench,
            check, fmt, lint, doc, publish,
            install, uninstall, update, upgrade,
            search, info, login, logout, cache,
            doctor, clean, verify, audit, vendor,
            graph, tree, workspace, self_update,
        ]
        for cmd in commands:
            assert hasattr(cmd, "run"), f"{cmd.__name__} missing run"
            assert callable(cmd.run)
