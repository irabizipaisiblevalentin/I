"""Core runtime — model lifecycle, pipeline orchestration, and the UBWENGE engine."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Type, Union

from .ubwoko import (
    ModelConfig, ModelInfo, ModelArchitecture, ModelTask, ModelSource,
    InferenceMode, Precision, DeviceType, register_model, get_model, MODEL_REGISTRY,
)
from .iyerekana import (
    InferencePipeline, InferenceRequest, InferenceResult, InferenceStatus,
    MockInferenceEngine, BaseInferenceEngine, get_pipeline,
)
from .ibikoresho import AIError, ModelLoadError, UwagaRegistry, generate_id


class PipelineStep:
    def __init__(self, name: str, fn: Callable, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.fn = fn
        self.config = config or {}

    def execute(self, context: Dict[str, Any]) -> Any:
        return self.fn(context)


class Pipeline:
    def __init__(self, name: str = "", steps: Optional[List[PipelineStep]] = None):
        self.name = name or generate_id("pipeline_")
        self.steps = steps or []

    def add_step(self, step: PipelineStep) -> Pipeline:
        self.steps.append(step)
        return self

    def add_step_fn(self, name: str, fn: Callable,
                    config: Optional[Dict[str, Any]] = None) -> Pipeline:
        self.steps.append(PipelineStep(name, fn, config))
        return self

    def run(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = dict(initial_context or {})
        context["_pipeline"] = self.name
        context["_started_at"] = time.time()
        for step in self.steps:
            try:
                result = step.execute(context)
                context[step.name] = result
            except Exception as e:
                context["_error"] = str(e)
                context["_failed_step"] = step.name
                raise
        context["_completed_at"] = time.time()
        return context


@dataclass
class RuntimeConfig:
    model_dir: str = "./models"
    cache_dir: str = "./cache/ubwenge"
    log_dir: str = "./logs/ubwenge"
    default_device: DeviceType = DeviceType.AUTO
    default_precision: Precision = Precision.AUTO
    max_concurrent_inferences: int = 8
    enable_monitoring: bool = True
    enable_model_caching: bool = True
    auto_unload_after_seconds: int = 0
    api_port: int = 8080
    metadata: Dict[str, Any] = field(default_factory=dict)


class UbwengeEngine:
    def __init__(self, config: Optional[RuntimeConfig] = None):
        self.config = config or RuntimeConfig()
        self.pipeline = get_pipeline()
        self._models: Dict[str, ModelInfo] = {}
        self._pipelines: Dict[str, Pipeline] = {}
        self._hooks: Dict[str, List[Callable]] = {}
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for d in [self.config.model_dir, self.config.cache_dir, self.config.log_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

    def load_model(self, config: ModelConfig) -> str:
        model_id = register_model(config)
        engine = MockInferenceEngine(config)
        self.pipeline.register_engine(model_id, engine)
        info = get_model(model_id)
        if info:
            info.loaded = True
            info.loaded_at = datetime.utcnow().isoformat()
            info.status = "loaded"
        self._models[model_id] = info or ModelInfo(config=config, loaded=True,
                                                     loaded_at=datetime.utcnow().isoformat())
        UwagaRegistry.register_model(model_id, config.to_dict())
        self._trigger_hook("model_loaded", model_id=model_id)
        return model_id

    def unload_model(self, model_id: str) -> bool:
        if model_id in self._models:
            info = self._models[model_id]
            info.loaded = False
            info.status = "unloaded"
            self._trigger_hook("model_unloaded", model_id=model_id)
            return True
        return False

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        return self._models.get(model_id) or get_model(model_id)

    def list_models(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for mid, info in self._models.items():
            if status and info.status != status:
                continue
            results.append({"model_id": mid, "status": info.status,
                            "task": info.config.task.value if info.config.task else "",
                            "loaded_at": info.loaded_at})
        return results

    def infer(self, prompt: str, model_id: str = "default",
              max_tokens: int = 1024, temperature: float = 0.7,
              stream: bool = False, **kwargs: Any) -> Union[InferenceResult, Generator]:
        request = InferenceRequest(
            prompt=prompt, model_id=model_id, max_tokens=max_tokens,
            temperature=temperature, stream=stream, **kwargs,
        )
        if stream:
            return self.pipeline.infer_stream(request)
        result = self.pipeline.infer(request)
        info = self._models.get(model_id)
        if info:
            info.inference_count += 1
            info.total_inference_time_ms += result.latency_ms
        self._trigger_hook("inference_completed", model_id=model_id, result=result)
        return result

    def create_pipeline(self, name: str,
                        steps: Optional[List[PipelineStep]] = None) -> Pipeline:
        pipeline = Pipeline(name=name, steps=steps)
        self._pipelines[name] = pipeline
        return pipeline

    def run_pipeline(self, name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pipeline = self._pipelines.get(name)
        if not pipeline:
            raise AIError(f"Pipeline not found: {name}")
        return pipeline.run(context)

    def register_hook(self, event: str, handler: Callable) -> None:
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(handler)

    def _trigger_hook(self, event: str, **kwargs: Any) -> None:
        for handler in self._hooks.get(event, []):
            try:
                handler(**kwargs)
            except Exception:
                pass

    def summary(self) -> Dict[str, Any]:
        return {
            "models_loaded": len([m for m in self._models.values() if m.loaded]),
            "models_total": len(self._models),
            "pipelines": list(self._pipelines.keys()),
            "hooks": {k: len(v) for k, v in self._hooks.items()},
            "config": {
                "model_dir": self.config.model_dir,
                "default_device": self.config.default_device.value,
            },
        }


_global_engine: Optional[UbwengeEngine] = None


def get_engine() -> UbwengeEngine:
    global _global_engine
    if _global_engine is None:
        _global_engine = UbwengeEngine()
    return _global_engine
