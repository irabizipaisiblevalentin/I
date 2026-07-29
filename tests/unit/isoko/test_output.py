"""Tests for isoko output module."""

import io
import sys

import pytest
from isoko import output


@pytest.fixture(autouse=True)
def no_color():
    """Disable color for all tests."""
    output.set_color(False)
    yield
    output.set_color(True)


class TestOutputFunctions:
    def test_success(self, capsys):
        output.success("done")
        captured = capsys.readouterr()
        assert "done" in captured.err

    def test_error(self, capsys):
        output.error("problem")
        captured = capsys.readouterr()
        assert "problem" in captured.err

    def test_warning(self, capsys):
        output.warning("heads up")
        captured = capsys.readouterr()
        assert "heads up" in captured.err

    def test_info(self, capsys):
        output.info("note")
        captured = capsys.readouterr()
        assert "note" in captured.err

    def test_dim(self, capsys):
        output.dim("subtle")
        captured = capsys.readouterr()
        assert "subtle" in captured.err

    def test_bold(self, capsys):
        output.bold("strong")
        captured = capsys.readouterr()
        assert "strong" in captured.err

    def test_header(self, capsys):
        output.header("Section")
        captured = capsys.readouterr()
        assert "Section" in captured.err

    def test_label_value(self, capsys):
        output.label_value("Key", "Value")
        captured = capsys.readouterr()
        assert "Key" in captured.err
        assert "Value" in captured.err

    def test_downloading(self, capsys):
        output.downloading("pkg", "1.0.0")
        captured = capsys.readouterr()
        assert "pkg" in captured.err
        assert "1.0.0" in captured.err

    def test_installing(self, capsys):
        output.installing("pkg", "1.0.0")
        captured = capsys.readouterr()
        assert "pkg" in captured.err


class TestSpinner:
    def test_start_stop(self, capsys):
        spinner = output.Spinner("loading")
        spinner.start()
        spinner.stop("done")
        captured = capsys.readouterr()
        assert "done" in captured.err

    def test_context_manager(self, capsys):
        with output.Spinner("working") as spinner:
            pass
        captured = capsys.readouterr()
        assert "working" in captured.err or "✓" in captured.err

    def test_update(self, capsys):
        spinner = output.Spinner("initial")
        spinner.start()
        spinner.update("updated")
        spinner.stop()
        captured = capsys.readouterr()
        assert "updated" in captured.err

    def test_fail(self, capsys):
        spinner = output.Spinner("working")
        spinner.start()
        spinner.fail("failed")
        captured = capsys.readouterr()
        assert "failed" in captured.err


class TestProgressBar:
    def test_basic(self, capsys):
        bar = output.ProgressBar(10, "test")
        bar.update(5)
        bar.finish()
        captured = capsys.readouterr()
        assert "test" in captured.err

    def test_zero_total(self, capsys):
        bar = output.ProgressBar(0)
        bar.finish()
        captured = capsys.readouterr()
        assert captured.err  # no crash


class TestPrintTable:
    def test_basic(self, capsys):
        output.print_table(["Name", "Version"], [["a", "1.0"], ["b", "2.0"]])
        captured = capsys.readouterr()
        assert "Name" in captured.err
        assert "a" in captured.err

    def test_empty(self, capsys):
        output.print_table(["Col"], [])
        captured = capsys.readouterr()
        assert captured.err == ""


class TestPrintJson:
    def test_basic(self, capsys):
        output.print_json({"key": "value"})
        captured = capsys.readouterr()
        assert '"key"' in captured.out
        assert '"value"' in captured.out


class TestOutputClass:
    def test_json_mode(self, capsys):
        out = output.Output(json_mode=True)
        out.success("done")
        out.error("fail")
        out.warning("warn")
        out.info("note")
        out.flush_json()
        captured = capsys.readouterr()
        assert '"level"' in captured.out

    def test_quiet_mode(self, capsys):
        out = output.Output(quiet=True)
        out.success("done")
        out.error("fail")
        out.warning("warn")
        out.info("note")
        captured = capsys.readouterr()
        # quiet suppresses success, warning, info
        assert "done" not in captured.err
        assert "fail" in captured.err
        assert "warn" not in captured.err
        assert "note" not in captured.err

    def test_verbose_mode(self, capsys):
        out = output.Output(verbose=True)
        out.dim("subtle")
        captured = capsys.readouterr()
        assert "subtle" in captured.err

    def test_color_set(self):
        output.set_color(True)
        output.set_color(False)
        # No crash
