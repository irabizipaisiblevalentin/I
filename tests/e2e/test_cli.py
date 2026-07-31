"""End-to-end tests for the ``i`` command-line interface.

Spins up the real CLI as a subprocess and checks exit codes, stdout
output, and bytecode artifacts for the shipped example programs.
"""
from __future__ import annotations

import os
import pickle
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXAMPLES = os.path.join(REPO_ROOT, "examples")

EXPECTED_OUTPUTS = {
    "hello.i": ["Muraho, Isi!"],
    "variables.i": ["Jean", "25", "Rwanda", "3.14159"],
    "functions.i": ["8", "30"],
    "conditionals.i": ["X ni kure", "X si binini", "X ni gitoya"],
    "loops.i": ["0", "1", "2", "3", "4", "0", "1", "2", "3", "4", "1", "2", "3", "4", "5"],
    "fibonacci.i": ["0", "1", "1", "2", "3", "5", "8", "13", "21", "34"],
}

ALL_EXAMPLES = sorted(EXPECTED_OUTPUTS)


def run_cli(*args: str, cwd: str = REPO_ROOT) -> subprocess.CompletedProcess:
    """Run the compiler CLI in a subprocess and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "compiler.compiler", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestExamplePrograms(unittest.TestCase):
    """Each shipped example must run and produce its expected output."""

    def test_all_examples_run(self):
        for name in ALL_EXAMPLES:
            with self.subTest(example=name):
                proc = run_cli(os.path.join(EXAMPLES, name), "-r")
                self.assertEqual(
                    proc.returncode,
                    0,
                    msg=f"{name} failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
                )
                lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
                self.assertEqual(lines, EXPECTED_OUTPUTS[name])


class TestCliCompileErrors(unittest.TestCase):
    """Compile errors must exit cleanly with a message, not a traceback."""

    def test_lexical_error_clean_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.i")
            with open(path, "w", encoding="utf-8") as f:
                f.write('shyira x = "unterminated\n')
            proc = run_cli(path, "-r")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Lexical errors", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_parse_error_clean_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.i")
            with open(path, "w", encoding="utf-8") as f:
                f.write("shyira x =\n")
            proc = run_cli(path, "-r")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Parse errors", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


class TestCliBytecodeOutput(unittest.TestCase):
    """Compiling with -o must produce a loadable bytecode artifact."""

    def test_compile_to_bytecode_file(self):
        for name in ("hello.i", "fibonacci.i"):
            with self.subTest(example=name):
                with tempfile.TemporaryDirectory() as tmp:
                    out = os.path.join(tmp, "out.bin")
                    proc = run_cli(os.path.join(EXAMPLES, name), "-o", out)
                    self.assertEqual(proc.returncode, 0, msg=proc.stderr)
                    self.assertTrue(os.path.isfile(out), "bytecode file should exist")
                    with open(out, "rb") as f:
                        chunk = pickle.load(f)
                    self.assertEqual(chunk.name, os.path.splitext(name)[0])

    def test_missing_file_clean_exit(self):
        proc = run_cli(os.path.join(EXAMPLES, "does_not_exist.i"), "-r")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("File not found", proc.stderr)


class TestCliVersion(unittest.TestCase):
    """--version must report the v1.0.0 release."""

    def test_version_flag(self):
        proc = run_cli("--version")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("v1.0.0", proc.stdout)


if __name__ == "__main__":
    unittest.main()
