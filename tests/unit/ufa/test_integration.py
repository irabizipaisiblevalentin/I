"""Integration tests for UFA Application core."""

import pytest
from ufa.core import Application, ApplicationContext
from ufa.lifecycle import Phase
from ufa.commands import Command, Query


class TestApplication:
    def test_create(self):
        app = Application("test", "1.0.0")
        assert app.name == "test"
        assert app.version == "1.0.0"

    def test_initial_phase(self):
        app = Application()
        assert app.lifecycle.phase == Phase.CREATED

    def test_configure(self):
        app = Application()
        app.configure({"server": {"port": 8080}})
        assert app.config.get("server.port") == 8080
        assert app.lifecycle.phase == Phase.CONFIGURED

    def test_context(self):
        app = Application()
        ctx = app.context
        assert isinstance(ctx, ApplicationContext)
        assert ctx.container is app.container
        assert ctx.config is app.config

    def test_context_singleton(self):
        app = Application()
        c1 = app.context
        c2 = app.context
        assert c1 is c2

    def test_run(self):
        app = Application()
        app.run()
        assert app.lifecycle.phase == Phase.RUNNING

    def test_stop(self):
        app = Application()
        app.run()
        app.stop()
        assert app.lifecycle.phase == Phase.STOPPED

    def test_shutdown(self):
        app = Application()
        app.run()
        app.shutdown()
        assert app.lifecycle.phase == Phase.DESTROYED

    def test_events(self):
        app = Application()
        received = []
        app.on("test.event", lambda e: received.append(e.data))
        app.emit("test.event", "payload")
        assert received == ["payload"]

    def test_lifecycle_events(self):
        app = Application()
        started = []
        app.on("app.started", lambda e: started.append(True))
        app.run()
        assert started == [True]

    def test_command(self):
        app = Application()
        class MyCmd(Command):
            pass
        app.command(MyCmd, lambda msg: "result")
        result = app.commands.dispatch(MyCmd())
        assert result.data == "result"

    def test_query(self):
        app = Application()
        class MyQuery(Query):
            pass
        app.query(MyQuery, lambda msg: {"data": 42})
        result = app.commands.dispatch(MyQuery())
        assert result.data == {"data": 42}

    def test_schedule_once(self):
        app = Application()
        result = [None]
        app.schedule_once(lambda: result.__setitem__(0, "done"), delay=0.0)
        app.scheduler.tick()
        assert result[0] == "done"

    def test_schedule_interval(self):
        app = Application()
        count = [0]
        app.schedule_interval(lambda: count.__setitem__(0, count[0] + 1), 0.01)
        app.scheduler.tick()
        assert count[0] >= 1

    def test_middleware(self):
        app = Application()
        order = []
        app.use(lambda ctx: order.append("m1"))
        ctx = app.middleware.execute(ApplicationContext(app) and __import__('ufa.middleware', fromlist=['MiddlewareContext']).MiddlewareContext())
        # just verify middleware was registered
        assert app.middleware.count() == 1

    def test_health_report(self):
        app = Application()
        app.health.register("test", lambda: True)
        report = app.health_report()
        assert report["status"] == "HEALTHY"

    def test_observability(self):
        app = Application()
        app.logger.info("test message")
        records = app.logger.records()
        assert len(records) == 1

    def test_metrics(self):
        app = Application()
        app.metrics.counter("requests")
        assert app.metrics.get_counter("requests") == 1.0

    def test_tracing(self):
        app = Application()
        span = app.tracer.start_span("test-op")
        assert span.name == "test-op"
        app.tracer.finish_span(span)
        assert len(app.tracer.completed_spans()) == 1

    def test_security(self):
        app = Application()
        ident = app.security.create_identity("admin", roles=["admin"])
        assert ident.username == "admin"

    def test_cache(self):
        app = Application()
        cache = app.cache.get_or_create("test")
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_localization(self):
        app = Application()
        app.localization.store.add_translations("en", {"hello": "Hello"})
        assert app.localization.t("hello") == "Hello"

    def test_ai(self):
        app = Application()
        assert app.ai.prompt_count() == 0

    def test_modules(self):
        app = Application()
        from ufa.modules import Module, ModuleMetadata
        m = Module()
        m.metadata = ModuleMetadata(name="test_mod")
        app.register_module(m)
        assert app.modules.has("test_mod")

    def test_plugin(self):
        app = Application()
        from ufa.plugins import Plugin, PluginMetadata
        p = Plugin()
        p.metadata = PluginMetadata(name="test_plugin")
        app.register_plugin(p)
        assert app.plugins.has("test_plugin")

    def test_container_services(self):
        app = Application()
        from ufa.configuration import Configuration
        resolved = app.container.resolve(Configuration)
        assert resolved is app.config

    def test_repr(self):
        app = Application("myapp", "2.0")
        r = repr(app)
        assert "myapp" in r
        assert "2.0" in r

    def test_uptime(self):
        app = Application()
        assert app.uptime == 0.0
