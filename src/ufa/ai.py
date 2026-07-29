"""ai — AI integration base layer.

Provides abstraction for LLM providers, prompt management,
response handling, token tracking, and provider failover.
"""

from __future__ import annotations

import enum
import time
from typing import Any, Callable, Dict, List, Optional


class ProviderStatus(enum.IntEnum):
    UNKNOWN = 0
    READY = 1
    BUSY = 2
    ERROR = 3
    DISABLED = 4


class PromptTemplate:
    """A reusable prompt template with variable interpolation."""
    __slots__ = ("name", "template", "variables", "tags", "version")

    def __init__(self, name: str, template: str,
                 variables: Optional[List[str]] = None,
                 tags: Optional[List[str]] = None, version: str = "1.0") -> None:
        self.name = name
        self.template = template
        self.variables = variables or []
        self.tags = tags or []
        self.version = version

    def render(self, **kwargs: Any) -> str:
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def validate(self, **kwargs: Any) -> List[str]:
        missing = []
        for var in self.variables:
            if var not in kwargs:
                missing.append(var)
        return missing


class LLMResponse:
    """Response from an LLM provider."""
    __slots__ = ("text", "model", "provider", "tokens_in", "tokens_out",
                 "latency_ms", "finish_reason", "metadata", "error")

    def __init__(self, text: str = "", model: str = "", provider: str = "",
                 tokens_in: int = 0, tokens_out: int = 0,
                 latency_ms: float = 0.0, finish_reason: str = "stop",
                 metadata: Optional[Dict[str, Any]] = None,
                 error: Optional[str] = None) -> None:
        self.text = text
        self.model = model
        self.provider = provider
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.latency_ms = latency_ms
        self.finish_reason = finish_reason
        self.metadata = metadata or {}
        self.error = error

    @property
    def success(self) -> bool:
        return self.error is None

    @property
    def total_tokens(self) -> int:
        return self.tokens_in + self.tokens_out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "provider": self.provider,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "latency_ms": round(self.latency_ms, 2),
            "finish_reason": self.finish_reason,
            "success": self.success,
        }


class TokenUsage:
    """Tracks token consumption across providers."""
    __slots__ = ("total_in", "total_out", "by_provider", "by_model")

    def __init__(self) -> None:
        self.total_in = 0
        self.total_out = 0
        self.by_provider: Dict[str, Dict[str, int]] = {}
        self.by_model: Dict[str, int] = {}

    def record(self, response: LLMResponse) -> None:
        self.total_in += response.tokens_in
        self.total_out += response.tokens_out

        provider_stats = self.by_provider.setdefault(response.provider, {})
        provider_stats["in"] = provider_stats.get("in", 0) + response.tokens_in
        provider_stats["out"] = provider_stats.get("out", 0) + response.tokens_out

        self.by_model[response.model] = (
            self.by_model.get(response.model, 0) + response.total_tokens
        )

    def reset(self) -> None:
        self.total_in = 0
        self.total_out = 0
        self.by_provider.clear()
        self.by_model.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_in": self.total_in,
            "total_out": self.total_out,
            "total": self.total_in + self.total_out,
            "by_provider": self.by_provider,
            "by_model": self.by_model,
        }


class AIProvider:
    """Base for AI provider implementations."""

    def __init__(self, name: str, models: Optional[List[str]] = None) -> None:
        self.name = name
        self.models = models or []
        self.status = ProviderStatus.UNKNOWN
        self._config: Dict[str, Any] = {}

    def configure(self, config: Dict[str, Any]) -> None:
        self._config.update(config)

    def complete(self, prompt: str, model: str = "",
                 **kwargs: Any) -> LLMResponse:
        raise NotImplementedError

    def chat(self, messages: List[Dict[str, str]], model: str = "",
             **kwargs: Any) -> LLMResponse:
        raise NotImplementedError

    def health_check(self) -> bool:
        return self.status != ProviderStatus.ERROR


class AIManager:
    """Central manager for AI providers, prompts, and usage tracking."""

    def __init__(self) -> None:
        self._providers: Dict[str, AIProvider] = {}
        self._prompts: Dict[str, PromptTemplate] = {}
        self._usage = TokenUsage()
        self._default_provider: Optional[str] = None

    def register_provider(self, provider: AIProvider,
                          default: bool = False) -> None:
        self._providers[provider.name] = provider
        if default or not self._default_provider:
            self._default_provider = provider.name

    def get_provider(self, name: Optional[str] = None) -> Optional[AIProvider]:
        provider_name = name or self._default_provider
        if provider_name:
            return self._providers.get(provider_name)
        return None

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())

    def register_prompt(self, template: PromptTemplate) -> None:
        self._prompts[template.name] = template

    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        return self._prompts.get(name)

    def render_prompt(self, name: str, **kwargs: Any) -> str:
        template = self._prompts.get(name)
        if not template:
            raise KeyError(f"unknown prompt: {name}")
        missing = template.validate(**kwargs)
        if missing:
            raise ValueError(f"missing variables: {missing}")
        return template.render(**kwargs)

    def complete(self, prompt: str, provider: Optional[str] = None,
                 model: str = "", **kwargs: Any) -> LLMResponse:
        prov = self.get_provider(provider)
        if not prov:
            return LLMResponse(error=f"no provider available")

        start = time.time()
        try:
            response = prov.complete(prompt, model, **kwargs)
            response.provider = prov.name
            response.latency_ms = (time.time() - start) * 1000
            self._usage.record(response)
            return response
        except Exception as e:
            return LLMResponse(error=str(e), provider=prov.name,
                               latency_ms=(time.time() - start) * 1000)

    def chat(self, messages: List[Dict[str, str]],
             provider: Optional[str] = None,
             model: str = "", **kwargs: Any) -> LLMResponse:
        prov = self.get_provider(provider)
        if not prov:
            return LLMResponse(error="no provider available")

        start = time.time()
        try:
            response = prov.chat(messages, model, **kwargs)
            response.provider = prov.name
            response.latency_ms = (time.time() - start) * 1000
            self._usage.record(response)
            return response
        except Exception as e:
            return LLMResponse(error=str(e), provider=prov.name,
                               latency_ms=(time.time() - start) * 1000)

    @property
    def usage(self) -> TokenUsage:
        return self._usage

    def prompt_count(self) -> int:
        return len(self._prompts)
