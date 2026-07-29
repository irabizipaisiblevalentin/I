"""Tests for UFA middleware pipeline."""

import pytest
from ufa.middleware import MiddlewarePipeline, MiddlewareContext, MiddlewarePhase


class TestMiddlewarePipeline:
    def test_single_middleware(self):
        pipe = MiddlewarePipeline()
        results = []
        pipe.use(lambda ctx: results.append("m1"))
        ctx = MiddlewareContext()
        pipe.execute(ctx)
        assert results == ["m1"]

    def test_ordering(self):
        pipe = MiddlewarePipeline()
        order = []
        pipe.use(lambda ctx: order.append(1), priority=1)
        pipe.use(lambda ctx: order.append(2), priority=2)
        pipe.execute(MiddlewareContext())
        assert order == [2, 1]

    def test_stop(self):
        pipe = MiddlewarePipeline()
        results = []
        pipe.use(lambda ctx: (ctx.stop(), results.append("a")))
        pipe.use(lambda ctx: results.append("b"))
        pipe.execute(MiddlewareContext())
        assert results == ["a"]

    def test_terminal(self):
        pipe = MiddlewarePipeline()
        pipe.use(lambda ctx: None)
        ctx = MiddlewareContext()
        result = pipe.execute(ctx, terminal=lambda ctx: "done")
        assert ctx.get("_result") == "done"

    def test_error_handling(self):
        pipe = MiddlewarePipeline()
        errors = []
        pipe.use_error_handler(lambda ctx, e: errors.append(str(e)))
        pipe.use(lambda ctx: 1 / 0)
        pipe.execute(MiddlewareContext())
        assert len(errors) == 1

    def test_context_data(self):
        pipe = MiddlewarePipeline()
        pipe.use(lambda ctx: ctx.set("key", "value"))
        ctx = MiddlewareContext()
        pipe.execute(ctx)
        assert ctx.get("key") == "value"

    def test_execute_chain(self):
        pipe = MiddlewarePipeline()
        order = []
        handlers = [
            lambda ctx: order.append(1),
            lambda ctx: order.append(2),
        ]
        pipe.execute_chain(MiddlewareContext(), handlers)
        assert order == [1, 2]

    def test_count(self):
        pipe = MiddlewarePipeline()
        pipe.use(lambda ctx: None, phase=MiddlewarePhase.PRE)
        pipe.use(lambda ctx: None, phase=MiddlewarePhase.POST)
        assert pipe.count() == 2
        assert pipe.count(MiddlewarePhase.PRE) == 1

    def test_clear(self):
        pipe = MiddlewarePipeline()
        pipe.use(lambda ctx: None)
        pipe.clear()
        assert pipe.count() == 0
