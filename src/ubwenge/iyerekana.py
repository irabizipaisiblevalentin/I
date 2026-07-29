"""Inference engine — streaming, batch, GPU, CPU, distributed, hybrid."""

from __future__ import annotations

import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional, Tuple, Union
from enum import Enum

from .ubwoko import ModelConfig, InferenceMode, DeviceType, Precision
from .ibikoresho import AIError, InferenceError, generate_id, TimeHelpers


class InferenceStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STREAMING = "streaming"


@dataclass
class InferenceRequest:
    prompt: str = ""
    messages: List[Dict[str, str]] = field(default_factory=list)
    model_id: str = ""
    mode: InferenceMode = InferenceMode.REAL_TIME
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    top_k: int = 40
    stop_sequences: List[str] = field(default_factory=list)
    stream: bool = False
    images: List[str] = field(default_factory=list)
    audio: List[str] = field(default_factory=list)
    tools: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = ""

    def __post_init__(self) -> None:
        if not self.request_id:
            self.request_id = generate_id("inf_")


@dataclass
class InferenceResult:
    text: str = ""
    tokens: List[int] = field(default_factory=list)
    logprobs: List[float] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
    })
    model_id: str = ""
    request_id: str = ""
    status: InferenceStatus = InferenceStatus.COMPLETED
    latency_ms: float = 0.0
    tokens_per_second: float = 0.0
    error: Optional[str] = None


class BaseInferenceEngine:
    def infer(self, request: InferenceRequest) -> InferenceResult:
        raise NotImplementedError

    def infer_stream(self, request: InferenceRequest) -> Generator[InferenceResult, None, None]:
        raise NotImplementedError

    async def infer_async(self, request: InferenceRequest) -> InferenceResult:
        raise NotImplementedError

    async def infer_stream_async(self, request: InferenceRequest) -> AsyncGenerator[InferenceResult, None]:
        raise NotImplementedError

    def infer_batch(self, requests: List[InferenceRequest]) -> List[InferenceResult]:
        results = []
        for req in requests:
            results.append(self.infer(req))
        return results

    def infer_concurrent(self, requests: List[InferenceRequest],
                         max_workers: int = 4) -> List[InferenceResult]:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(self.infer, req) for req in requests]
            return [f.result() for f in futures]


class MockInferenceEngine(BaseInferenceEngine):
    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self._call_count = 0

    def infer(self, request: InferenceRequest) -> InferenceResult:
        start = time.time()
        self._call_count += 1
        prompt_len = len(request.prompt.split()) if request.prompt else 50
        completion_len = min(request.max_tokens, 100)
        latency = 0.01 * completion_len
        time.sleep(min(latency, 0.5))

        return InferenceResult(
            text=f"[{self.config.model_id}] Generated {completion_len} tokens for: {request.prompt[:80]}...",
            finish_reason="length" if completion_len >= request.max_tokens else "stop",
            usage={
                "prompt_tokens": prompt_len,
                "completion_tokens": completion_len,
                "total_tokens": prompt_len + completion_len,
            },
            model_id=self.config.model_id,
            request_id=request.request_id,
            latency_ms=latency * 1000,
            tokens_per_second=completion_len / latency if latency > 0 else 0,
        )

    def infer_stream(self, request: InferenceRequest) -> Generator[InferenceResult, None, None]:
        for i in range(min(request.max_tokens, 20)):
            time.sleep(0.01)
            yield InferenceResult(
                text=f"token_{i} ",
                status=InferenceStatus.STREAMING,
                model_id=self.config.model_id,
                request_id=request.request_id,
            )


class InferencePipeline:
    def __init__(self) -> None:
        self._engines: Dict[str, BaseInferenceEngine] = {}
        self._lock = threading.RLock()

    def register_engine(self, model_id: str, engine: BaseInferenceEngine) -> None:
        with self._lock:
            self._engines[model_id] = engine

    def get_engine(self, model_id: str) -> Optional[BaseInferenceEngine]:
        return self._engines.get(model_id)

    def infer(self, request: InferenceRequest) -> InferenceResult:
        engine = self.get_engine(request.model_id)
        if not engine:
            raise InferenceError(f"No engine registered for model: {request.model_id}")
        return engine.infer(request)

    def infer_stream(self, request: InferenceRequest) -> Generator[InferenceResult, None, None]:
        engine = self.get_engine(request.model_id)
        if not engine:
            raise InferenceError(f"No engine registered for model: {request.model_id}")
        yield from engine.infer_stream(request)

    def infer_batch(self, requests: List[InferenceRequest]) -> List[InferenceResult]:
        return [self.infer(req) for req in requests]

    def infer_concurrent(self, requests: List[InferenceRequest],
                         max_workers: int = 4) -> List[InferenceResult]:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = []
            for req in requests:
                engine = self.get_engine(req.model_id)
                if not engine:
                    raise InferenceError(f"No engine registered for model: {req.model_id}")
                futures.append(pool.submit(engine.infer, req))
            return [f.result() for f in futures]


_global_pipeline = InferencePipeline()


def get_pipeline() -> InferencePipeline:
    return _global_pipeline


def infer(prompt: str, model_id: str = "default",
          max_tokens: int = 1024, temperature: float = 0.7,
          stream: bool = False, **kwargs: Any) -> Union[InferenceResult, Generator]:
    request = InferenceRequest(
        prompt=prompt,
        model_id=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        **kwargs,
    )
    if stream:
        return _global_pipeline.infer_stream(request)
    return _global_pipeline.infer(request)
