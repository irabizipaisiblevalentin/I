"""Tests for isoko templates module."""

import os
import tempfile

import pytest
from isoko.templates import (
    Template, list_templates, get_template, render_template,
)


class TestTemplate:
    def test_render(self):
        t = Template("test", "A test template")
        t.files = {
            "readme.md": "# {{project_name}}\nHello!",
            "src/main.i": "// {{project_name}} entry",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            files = t.render("my-project", tmpdir)
            assert len(files) == 2

            readme = os.path.join(tmpdir, "readme.md")
            assert os.path.exists(readme)
            with open(readme) as f:
                content = f.read()
            assert "my-project" in content

            main = os.path.join(tmpdir, "src", "main.i")
            assert os.path.exists(main)
            with open(main) as f:
                content = f.read()
            assert "my-project" in content

    def test_render_creates_dirs(self):
        t = Template("test", "")
        t.files = {"a/b/c/file.txt": "content"}

        with tempfile.TemporaryDirectory() as tmpdir:
            files = t.render("proj", tmpdir)
            assert len(files) == 1
            assert os.path.exists(os.path.join(tmpdir, "a", "b", "c", "file.txt"))


class TestListTemplates:
    def test_list(self):
        templates = list_templates()
        assert len(templates) >= 5
        names = [t["name"] for t in templates]
        assert "console" in names
        assert "library" in names
        assert "web-api" in names

    def test_each_has_fields(self):
        templates = list_templates()
        for t in templates:
            assert "name" in t
            assert "description" in t


class TestGetTemplate:
    def test_get_existing(self):
        tpl = get_template("console")
        assert tpl is not None
        assert tpl.name == "console"
        assert len(tpl.files) > 0

    def test_get_nonexistent(self):
        tpl = get_template("nonexistent-template")
        assert tpl is None

    def test_library(self):
        tpl = get_template("library")
        assert tpl is not None

    def test_web_api(self):
        tpl = get_template("web-api")
        assert tpl is not None

    def test_ai(self):
        tpl = get_template("ai")
        assert tpl is not None

    def test_game(self):
        tpl = get_template("game")
        assert tpl is not None

    def test_desktop(self):
        tpl = get_template("desktop")
        assert tpl is not None

    def test_mobile(self):
        tpl = get_template("mobile")
        assert tpl is not None

    def test_website(self):
        tpl = get_template("website")
        assert tpl is not None

    def test_cloud(self):
        tpl = get_template("cloud")
        assert tpl is not None

    def test_embedded(self):
        tpl = get_template("embedded")
        assert tpl is not None

    def test_os(self):
        tpl = get_template("os")
        assert tpl is not None

    def test_framework(self):
        tpl = get_template("framework")
        assert tpl is not None


class TestRenderTemplate:
    def test_render_console(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = os.path.join(tmpdir, "my-project")
            files = render_template("console", "my-project", project_dir)
            assert len(files) > 0
            assert os.path.exists(project_dir)

    def test_render_invalid(self):
        with pytest.raises(ValueError):
            render_template("nonexistent", "test", "/tmp/test")

    def test_render_library(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = os.path.join(tmpdir, "my-lib")
            files = render_template("library", "my-lib", project_dir)
            assert len(files) > 0
