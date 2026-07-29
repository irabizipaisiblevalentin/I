"""Tests for UFA AI integration."""

import pytest
from ufa.ai import (
    AIManager, AIProvider, PromptTemplate, LLMResponse,
    TokenUsage, ProviderStatus
)


class MockProvider(AIProvider):
    def __init__(self):
        super().__init__("mock", ["model-a", "model-b"])
        self.status = ProviderStatus.READY

    def complete(self, prompt, model="", **kwargs):
        return LLMResponse(text=f"response to: {prompt}",
                           model=model or "model-a",
                           tokens_in=10, tokens_out=20)

    def chat(self, messages, model="", **kwargs):
        return LLMResponse(text="chat response",
                           model=model or "model-a",
                           tokens_in=5, tokens_out=15)


class TestPromptTemplate:
    def test_render(self):
        pt = PromptTemplate("g", "Hello {name}")
        assert pt.render(name="World") == "Hello World"

    def test_validate(self):
        pt = PromptTemplate("g", "{a} {b}", variables=["a", "b"])
        assert pt.validate(a="1") == ["b"]
        assert pt.validate(a="1", b="2") == []


class TestLLMResponse:
    def test_success(self):
        r = LLMResponse(text="hi")
        assert r.success

    def test_error(self):
        r = LLMResponse(error="fail")
        assert not r.success

    def test_total_tokens(self):
        r = LLMResponse(tokens_in=10, tokens_out=20)
        assert r.total_tokens == 30

    def test_to_dict(self):
        r = LLMResponse(text="hi", model="m")
        d = r.to_dict()
        assert d["text"] == "hi"


class TestTokenUsage:
    def test_record(self):
        usage = TokenUsage()
        usage.record(LLMResponse(tokens_in=10, tokens_out=20,
                                 provider="p", model="m"))
        assert usage.total_in == 10
        assert usage.total_out == 20

    def test_by_provider(self):
        usage = TokenUsage()
        usage.record(LLMResponse(tokens_in=5, tokens_out=5,
                                 provider="p", model="m"))
        assert "p" in usage.by_provider

    def test_reset(self):
        usage = TokenUsage()
        usage.record(LLMResponse(tokens_in=1, tokens_out=1,
                                 provider="p", model="m"))
        usage.reset()
        assert usage.total_in == 0

    def test_to_dict(self):
        usage = TokenUsage()
        d = usage.to_dict()
        assert "total_in" in d


class TestAIManager:
    def test_register_provider(self):
        mgr = AIManager()
        mgr.register_provider(MockProvider(), default=True)
        assert mgr.get_provider() is not None

    def test_list_providers(self):
        mgr = AIManager()
        mgr.register_provider(MockProvider())
        assert "mock" in mgr.list_providers()

    def test_complete(self):
        mgr = AIManager()
        mgr.register_provider(MockProvider(), default=True)
        resp = mgr.complete("hello")
        assert resp.success
        assert "hello" in resp.text

    def test_chat(self):
        mgr = AIManager()
        mgr.register_provider(MockProvider(), default=True)
        resp = mgr.chat([{"role": "user", "content": "hi"}])
        assert resp.success

    def test_no_provider(self):
        mgr = AIManager()
        resp = mgr.complete("x")
        assert not resp.success

    def test_register_prompt(self):
        mgr = AIManager()
        pt = PromptTemplate("greeting", "Hello {name}", variables=["name"])
        mgr.register_prompt(pt)
        assert mgr.prompt_count() == 1

    def test_render_prompt(self):
        mgr = AIManager()
        mgr.register_prompt(PromptTemplate("g", "Hi {x}", variables=["x"]))
        assert mgr.render_prompt("g", x="World") == "Hi World"

    def test_render_prompt_missing_vars(self):
        mgr = AIManager()
        mgr.register_prompt(PromptTemplate("g", "{a} {b}", variables=["a", "b"]))
        with pytest.raises(ValueError):
            mgr.render_prompt("g", a="1")

    def test_render_prompt_unknown(self):
        mgr = AIManager()
        with pytest.raises(KeyError):
            mgr.render_prompt("missing")

    def test_usage_tracking(self):
        mgr = AIManager()
        mgr.register_provider(MockProvider(), default=True)
        mgr.complete("test")
        assert mgr.usage.total_in > 0

    def test_provider_health(self):
        p = MockProvider()
        assert p.health_check()
        p.status = ProviderStatus.ERROR
        assert not p.health_check()

    def test_provider_configure(self):
        p = MockProvider()
        p.configure({"api_key": "test"})
        assert p._config["api_key"] == "test"
