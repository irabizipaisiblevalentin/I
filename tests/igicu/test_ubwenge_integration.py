"""Tests for IGICU AI Integration (Ubwenge)."""

from __future__ import annotations

import pytest

from igicu.ubwenge_integration import (
    UbwengeIntegration, ModelRegistry, InferenceDeployment,
    GPUScheduler, BatchInferenceProcessor,
)


class TestModelRegistry:
    def test_register(self):
        reg = ModelRegistry()
        model_id = reg.register("llama", "2.0", "transformer", "text_generation")
        assert "llama:2.0" == model_id

    def test_get(self):
        reg = ModelRegistry()
        reg.register("gpt", "1.0")
        model = reg.get("gpt:1.0")
        assert model is not None
        assert model["name"] == "gpt"

    def test_deploy(self):
        reg = ModelRegistry()
        reg.register("bert", "1.0")
        dep = reg.deploy("bert:1.0", replicas=2)
        assert dep.status == "running"
        assert dep.replicas == 2

    def test_list_deployments(self):
        reg = ModelRegistry()
        reg.register("model-a", "1.0")
        reg.deploy("model-a:1.0")
        deps = reg.list_deployments()
        assert len(deps) >= 1


class TestGPUScheduler:
    def test_add_gpu(self):
        sched = GPUScheduler()
        gpu_key = sched.add_gpu("node-1", "gpu-0", 16384)
        assert gpu_key is not None

    def test_allocate_release(self):
        sched = GPUScheduler()
        gpu_key = sched.add_gpu("node-1", "gpu-0")
        assert sched.allocate(gpu_key, "workload-1") is True
        assert sched.release(gpu_key) is True

    def test_get_utilization(self):
        sched = GPUScheduler()
        sched.add_gpu("n1", "g0")
        sched.add_gpu("n1", "g1")
        util = sched.get_utilization()
        assert util["total_gpus"] == 2


class TestBatchInferenceProcessor:
    def test_submit(self):
        bp = BatchInferenceProcessor()
        batch_id = bp.submit("model-1", ["input1", "input2"], priority=1)
        assert batch_id is not None

    def test_process(self):
        bp = BatchInferenceProcessor()
        bp.submit("m1", ["hello", "world"])
        result = bp.process_next()
        assert result is not None
        assert result["status"] == "completed"

    def test_queue_size(self):
        bp = BatchInferenceProcessor()
        assert bp.queue_size() == 0
        bp.submit("m1", ["t1"])
        assert bp.queue_size() == 1


class TestUbwengeIntegration:
    def test_deploy_model(self):
        integration = UbwengeIntegration()
        dep = integration.deploy_model("my-model", "1.0", replicas=3)
        assert dep.replicas == 3
        assert dep.status == "running"

    def test_infer_batch(self):
        integration = UbwengeIntegration()
        integration.deploy_model("batch-model")
        results = integration.infer_batch("batch-model:1.0", ["q1", "q2"])
        assert len(results) == 2
