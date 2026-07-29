"""ai — AI-native web features for urubuga.

Provides AI route handlers, prompt pipelines, streaming AI responses,
and AI middleware.
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict, List, Optional


class PromptStep:
    """A step in a prompt pipeline."""
    __slots__ = ("name", "prompt_template", "variables", "model",
                 "temperature", "max_tokens")

    def __init__(self, name: str, prompt_template: str,
                 variables: Optional[Dict[str, str]] = None,
                 model: str = "", temperature: float = 0.7,
                 max_tokens: int = 2048) -> None:
        self.name = name
        self.prompt_template = prompt_template
        self.variables = variables or {}
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def render(self, context: Dict[str, Any]) -> str:
        result = self.prompt_template
        for key, ctx_key in self.variables.items():
            ctx_value = context.get(ctx_key, ctx_key)
            result = result.replace(f"{{{key}}}", str(ctx_value))
        # Also resolve direct template variables from context
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


class PromptPipeline:
    """A chain of prompt steps for AI processing."""

    def __init__(self, name: str = "") -> None:
        self.name = name
        self._steps: List[PromptStep] = []
        self._pre_hooks: List[Callable] = []
        self._post_hooks: List[Callable] = []

    def add_step(self, step: PromptStep) -> "PromptPipeline":
        self._steps.append(step)
        return self

    def step(self, name: str, prompt_template: str,
             **kwargs: Any) -> "PromptPipeline":
        self._steps.append(PromptStep(name, prompt_template, **kwargs))
        return self

    def pre_hook(self, fn: Callable) -> "PromptPipeline":
        self._pre_hooks.append(fn)
        return self

    def post_hook(self, fn: Callable) -> "PromptPipeline":
        self._post_hooks.append(fn)
        return self

    def execute(self, context: Dict[str, Any],
                llm_fn: Optional[Callable] = None) -> Dict[str, Any]:
        results = {}
        current_context = dict(context)

        for hook in self._pre_hooks:
            hook(current_context)

        for step in self._steps:
            rendered = step.render(current_context)
            if llm_fn:
                response = llm_fn(rendered, model=step.model,
                                  temperature=step.temperature,
                                  max_tokens=step.max_tokens)
                results[step.name] = response
                current_context[step.name] = response
            else:
                results[step.name] = rendered
                current_context[step.name] = rendered

        for hook in self._post_hooks:
            hook(results)

        return results

    @property
    def step_count(self) -> int:
        return len(self._steps)


class AIStreamChunk:
    """A chunk of a streaming AI response."""
    __slots__ = ("text", "finish_reason", "usage", "index")

    def __init__(self, text: str = "", finish_reason: Optional[str] = None,
                 usage: Optional[Dict[str, int]] = None,
                 index: int = 0) -> None:
        self.text = text
        self.finish_reason = finish_reason
        self.usage = usage or {}
        self.index = index

    def to_sse(self) -> str:
        data = {"text": self.text}
        if self.finish_reason:
            data["finish_reason"] = self.finish_reason
        if self.usage:
            data["usage"] = self.usage
        return f"data: {json.dumps(data)}\n\n"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "index": self.index,
        }


class AIRouteHandler:
    """Handler for AI-powered routes."""

    def __init__(self, pipeline: Optional[PromptPipeline] = None,
                 llm_fn: Optional[Callable] = None,
                 system_prompt: str = "",
                 max_tokens: int = 2048,
                 temperature: float = 0.7) -> None:
        self.pipeline = pipeline
        self.llm_fn = llm_fn
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._request_count = 0
        self._total_tokens = 0

    def handle(self, prompt: str,
               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._request_count += 1
        ctx = dict(context or {})
        ctx["prompt"] = prompt
        ctx["system_prompt"] = self.system_prompt

        if self.pipeline:
            results = self.pipeline.execute(ctx, self.llm_fn)
            return {
                "response": results,
                "model": "pipeline",
            }

        if self.llm_fn:
            full_prompt = f"{self.system_prompt}\n\n{prompt}" if self.system_prompt else prompt
            response = self.llm_fn(full_prompt,
                                   max_tokens=self.max_tokens,
                                   temperature=self.temperature)
            return {
                "response": response,
                "model": "direct",
            }

        return {"response": f"Echo: {prompt}", "model": "fallback"}

    def stream(self, prompt: str,
               context: Optional[Dict[str, Any]] = None):
        """Generator yielding AIStreamChunks."""
        ctx = dict(context or {})
        ctx["prompt"] = prompt
        result = self.handle(prompt, ctx)
        text = result.get("response", "")
        if isinstance(text, dict):
            text = json.dumps(text)
        chunk_size = 20
        for i in range(0, len(text), chunk_size):
            yield AIStreamChunk(text=text[i:i + chunk_size], index=i)
        yield AIStreamChunk(finish_reason="stop", index=len(text))

    @property
    def request_count(self) -> int:
        return self._request_count


class AIMiddleware:
    """Middleware for AI route handling and inference caching."""

    def __init__(self, cache_ttl: int = 300) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = cache_ttl
        self._hit_count = 0
        self._miss_count = 0

    def get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(key)
        if entry and time.time() < entry.get("expires_at", 0):
            self._hit_count += 1
            return entry.get("data")
        self._miss_count += 1
        return None

    def set_cached(self, key: str, data: Any) -> None:
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + self._cache_ttl,
        }

    def clear_cache(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    @property
    def cache_stats(self) -> Dict[str, int]:
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "size": len(self._cache),
        }
