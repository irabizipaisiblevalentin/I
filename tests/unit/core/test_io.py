"""
Tests for IO utilities.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from src.compiler.core.io import FileManager, normalize_path, relative_to, ensure_dir
from src.compiler.core.io.paths import find_project_root


class TestFileManager:
    """Tests for FileManager."""

    def test_read_write(self):
        with TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))
            test_file = Path("test.txt")
            fm.write(test_file, "hello world")
            assert fm.read(test_file) == "hello world"

    def test_read_caches(self):
        with TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("original")
            assert fm.read(test_file) == "original"
            test_file.write_text("modified")
            assert fm.read(test_file) == "original"

    def test_clear_cache(self):
        with TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("original")
            fm.read(test_file)
            fm.clear_cache()
            test_file.write_text("modified")
            assert fm.read(test_file) == "modified"

    def test_exists(self):
        with TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))
            test_file = Path(tmpdir) / "existing.txt"
            test_file.write_text("x")
            assert fm.exists(test_file)
            assert not fm.exists(Path(tmpdir) / "missing.txt")

    def test_resolve_relative(self):
        with TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))
            rel = Path("sub/file.txt")
            expected = Path(tmpdir) / "sub/file.txt"
            resolved = fm._resolve(rel)
            assert resolved == expected.resolve()

    def test_root_default(self):
        fm = FileManager()
        assert fm.root == Path.cwd()


class TestPaths:
    """Tests for path utilities."""

    def test_normalize_path(self):
        p = Path(".") / "foo" / ".." / "bar"
        result = normalize_path(p)
        assert result.is_absolute()
        assert result.name == "bar"

    def test_relative_to_same_base(self):
        p = Path("/a/b/c")
        base = Path("/a/b")
        result = relative_to(p, base)
        assert result == "c"

    def test_relative_to_forward_slashes(self):
        path = Path("a") / "b" / "c"
        result = relative_to(path, Path("a"))
        assert "\\" not in result
        assert result == "b/c"

    def test_ensure_dir(self):
        with TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "a" / "b" / "c"
            result = ensure_dir(new_dir)
            assert result.exists()
            assert result.is_dir()

    def test_find_project_root(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            sub = root / "sub" / "dir"
            sub.mkdir(parents=True)
            found = find_project_root(sub)
            assert found == root

    def test_find_project_root_not_found(self):
        with TemporaryDirectory() as tmpdir:
            result = find_project_root(Path(tmpdir))
            assert result is None
