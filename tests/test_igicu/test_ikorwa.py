"""Tests for IGICU Container Runtime (ikorwa)."""

from __future__ import annotations

import pytest

from igicu.ikorwa import ImageRegistry, ImageBuilder, ContainerRuntime, BuildPipeline
from igicu.ibikoreshingiro import (
    ContainerConfig, ContainerRuntimeType, ContainerStatus, ImageConfig,
)


class TestImageRegistry:
    def test_register_and_get(self):
        reg = ImageRegistry()
        config = ImageConfig(name="test-image", tag="v1")
        image_id = reg.register(config)
        assert image_id == "test-image:v1"
        retrieved = reg.get("test-image", "v1")
        assert retrieved is not None
        assert retrieved.name == "test-image"

    def test_list(self):
        reg = ImageRegistry()
        reg.register(ImageConfig(name="img1", tag="latest"))
        reg.register(ImageConfig(name="img2", tag="v2"))
        images = reg.list()
        assert len(images) == 2

    def test_remove(self):
        reg = ImageRegistry()
        reg.register(ImageConfig(name="temp", tag="latest"))
        assert reg.remove("temp", "latest") is True
        assert reg.get("temp", "latest") is None

    def test_search(self):
        reg = ImageRegistry()
        reg.register(ImageConfig(name="my-app", tag="v1"))
        reg.register(ImageConfig(name="my-db", tag="v2"))
        results = reg.search("my-")
        assert len(results) == 2

    def test_len(self):
        reg = ImageRegistry()
        assert len(reg) == 0
        reg.register(ImageConfig(name="a", tag="1"))
        assert len(reg) == 1


class TestImageBuilder:
    def test_build_without_context_fails(self):
        builder = ImageBuilder()
        with pytest.raises(Exception):
            builder.build("test", "/nonexistent")

    def test_build_in_current_dir(self):
        builder = ImageBuilder()
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            config = builder.build("test-build", tmpdir, "test")
            assert config.name == "test-build"
            assert config.tag == "test"
            assert config.size_mb >= 0


class TestContainerRuntime:
    def test_create_and_start(self):
        runtime = ContainerRuntime()
        config = ContainerConfig(image="nginx:latest", name="web")
        cid = runtime.create(config)
        assert cid.startswith("igicu-")
        assert runtime.start(cid) is True

    def test_stop_container(self):
        runtime = ContainerRuntime()
        config = ContainerConfig(image="redis:latest", name="cache")
        cid = runtime.create(config)
        runtime.start(cid)
        assert runtime.stop(cid) is True

    def test_remove_container(self):
        runtime = ContainerRuntime()
        config = ContainerConfig(image="alpine:latest", name="tmp")
        cid = runtime.create(config)
        assert runtime.remove(cid) is True
        assert runtime.get(cid) is None

    def test_list_containers(self):
        runtime = ContainerRuntime()
        runtime.create(ContainerConfig(image="a", name="c1"))
        runtime.create(ContainerConfig(image="b", name="c2"))
        assert len(runtime.list()) == 2

    def test_list_by_status(self):
        runtime = ContainerRuntime()
        cid = runtime.create(ContainerConfig(image="a", name="c1"))
        runtime.start(cid)
        running = runtime.list(status="running")
        assert len(running) >= 1

    def test_exec(self):
        runtime = ContainerRuntime()
        config = ContainerConfig(image="ubuntu", name="worker")
        cid = runtime.create(config)
        result = runtime.exec(cid, ["echo", "hello"])
        assert result["exit_code"] == 0

    def test_logs(self):
        runtime = ContainerRuntime()
        config = ContainerConfig(image="app", name="logger")
        cid = runtime.create(config)
        logs = runtime.logs(cid)
        assert len(logs) > 0

    def test_inspect(self):
        runtime = ContainerRuntime()
        config = ContainerConfig(image="app", name="inspected")
        cid = runtime.create(config)
        info = runtime.inspect(cid)
        assert info is not None
        assert info["config"].name == "inspected"


class TestBuildPipeline:
    def test_pipeline_creation(self):
        pipeline = BuildPipeline()
        assert pipeline is not None
        assert pipeline.registry is not None
