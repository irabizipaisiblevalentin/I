"""Tests for isoko resolver module."""

import pytest
from isoko.resolver import Resolver, PackageNode, ConflictError
from isoko.semver import Version


class MockManifest:
    def __init__(self, deps=None, dev_deps=None, build_deps=None, optional_deps=None):
        self.dependencies = deps or {}
        self.dev_dependencies = dev_deps or {}
        self.build_dependencies = build_deps or {}
        self.optional_dependencies = optional_deps or {}


class MockRegistry:
    def __init__(self, packages=None):
        self._packages = packages or {}

    def get_versions(self, name):
        return self._packages.get(name, [])

    def get_package(self, name, version):
        ver_str = str(version)
        if name in self._packages:
            for v in self._packages[name]:
                if str(v) == ver_str:
                    return {"dependencies": {}}
        return None


class TestPackageNode:
    def test_basic(self):
        node = PackageNode("test", Version(1, 0, 0))
        assert node.name == "test"
        assert node.version == Version(1, 0, 0)
        assert node.deps == {}

    def test_repr(self):
        node = PackageNode("test", Version(1, 2, 3))
        assert "test" in repr(node)
        assert "1.2.3" in repr(node)


class TestResolver:
    def test_resolve_empty(self):
        manifest = MockManifest()
        resolver = Resolver()
        result = resolver.resolve(manifest)
        assert len(result) == 0

    def test_resolve_single_dep(self):
        registry = MockRegistry({
            "foo": [Version(1, 0, 0), Version(1, 1, 0)],
        })
        manifest = MockManifest(deps={"foo": "^1.0.0"})
        resolver = Resolver(registry)
        result = resolver.resolve(manifest)
        assert "foo" in result
        assert result["foo"].version == Version(1, 1, 0)

    def test_resolve_multiple_deps(self):
        registry = MockRegistry({
            "a": [Version(1, 0, 0)],
            "b": [Version(2, 0, 0)],
        })
        manifest = MockManifest(deps={"a": "^1.0.0", "b": "^2.0.0"})
        resolver = Resolver(registry)
        result = resolver.resolve(manifest)
        assert len(result) == 2
        assert "a" in result
        assert "b" in result

    def test_resolve_dev_deps(self):
        registry = MockRegistry({
            "test-pkg": [Version(1, 0, 0)],
        })
        manifest = MockManifest(dev_deps={"test-pkg": "^1.0.0"})
        resolver = Resolver(registry)
        result = resolver.resolve(manifest)
        assert "test-pkg" in result
        assert result["test-pkg"].is_dev

    def test_resolve_optional_missing(self):
        registry = MockRegistry({})
        manifest = MockManifest(optional_deps={"optional-pkg": "^1.0.0"})
        resolver = Resolver(registry)
        result = resolver.resolve(manifest)
        assert "optional-pkg" not in result

    def test_version_conflict(self):
        registry = MockRegistry({
            "pkg": [Version(1, 0, 0), Version(2, 0, 0)],
        })
        manifest = MockManifest(deps={"pkg": "^1.0.0"})
        # Manually pre-resolve a different version
        resolver = Resolver(registry)
        resolver._resolved["pkg"] = PackageNode("pkg", Version(2, 0, 0))
        resolver._resolve_package("pkg", "^1.0.0", [])
        assert len(resolver._conflicts) > 0

    def test_no_version_available(self):
        registry = MockRegistry({})
        manifest = MockManifest(deps={"nonexistent": "^1.0.0"})
        resolver = Resolver(registry)
        with pytest.raises(ConflictError):
            resolver.resolve(manifest)

    def test_topological_sort(self):
        graph = {
            "a": PackageNode("a", Version(1, 0, 0), deps={"b": "^1.0.0"}),
            "b": PackageNode("b", Version(1, 0, 0), deps={"c": "^1.0.0"}),
            "c": PackageNode("c", Version(1, 0, 0)),
        }
        resolver = Resolver()
        ordered = resolver.topological_sort(graph)
        names = [n.name for n in ordered]
        assert names.index("c") < names.index("b")
        assert names.index("b") < names.index("a")

    def test_to_dict(self):
        graph = {
            "a": PackageNode("a", Version(1, 0, 0), deps={"b": "^1.0.0"}),
            "b": PackageNode("b", Version(1, 5, 0)),
        }
        resolver = Resolver()
        d = resolver.to_dict(graph)
        assert d["a"]["version"] == "1.0.0"
        assert "b" in d["a"]["dependencies"]

    def test_build_deps(self):
        registry = MockRegistry({
            "build-tool": [Version(1, 0, 0)],
        })
        manifest = MockManifest(build_deps={"build-tool": "^1.0.0"})
        resolver = Resolver(registry)
        result = resolver.resolve(manifest)
        assert "build-tool" in result
        assert result["build-tool"].is_build
