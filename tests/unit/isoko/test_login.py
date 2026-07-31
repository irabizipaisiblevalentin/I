"""Tests for ``isoko login`` — token storage security (B2)."""
from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from unittest import mock

from isoko.commands import login


class TestLoginTokenStorage(unittest.TestCase):
    """Registry tokens must be stored in a user-restricted config file."""

    def _run_login(self, home: str, token: str = "sekrit") -> int:
        args = mock.Mock()
        args.registry = "https://registry.i-lang.dev"
        args.token = token
        with mock.patch.object(os.path, "expanduser", return_value=home):
            return login.run(args)

    def test_writes_token_to_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = self._run_login(tmp)
            self.assertEqual(code, 0)
            config_path = os.path.join(tmp, ".isoko", "config.json")
            self.assertTrue(os.path.isfile(config_path), "config.json should be written")
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            stored = cfg["registries"]["https://registry.i-lang.dev"]["token"]
            self.assertEqual(stored, "sekrit")

    def test_config_permissions_restricted(self):
        if os.name == "nt":
            self.skipTest("POSIX permission bits are not enforced on Windows")
        with tempfile.TemporaryDirectory() as tmp:
            self._run_login(tmp)
            config_path = os.path.join(tmp, ".isoko", "config.json")
            file_mode = stat.S_IMODE(os.stat(config_path).st_mode)
            self.assertEqual(
                file_mode & 0o077, 0, "config.json must be owner-only (0o600)"
            )
            dir_mode = stat.S_IMODE(os.stat(os.path.dirname(config_path)).st_mode)
            self.assertEqual(
                dir_mode & 0o077, 0, ".isoko directory must be owner-only (0o700)"
            )

    def test_login_cancelled_without_token(self):
        args = mock.Mock()
        args.registry = "https://registry.i-lang.dev"
        args.token = None
        with mock.patch("builtins.input", side_effect=EOFError):
            with mock.patch.object(os.path, "expanduser", return_value=os.path.abspath(".")):
                code = login.run(args)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
