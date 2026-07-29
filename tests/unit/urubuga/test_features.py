"""Tests for urubuga WebSocket, SSE, GraphQL, templates, AI, CLI."""

import asyncio
import pytest
from urubuga.http.request_response import StatusCode
from urubuga.realtime.websocket import (
    WebSocketConnection, WebSocketManager, WebSocketState,
    WebSocketMessage, Room, Presence,
)
from urubuga.realtime.sse import SSEEvent, SSEClient, SSEManager
from urubuga.graphql.schema import GraphQLSchema, TypeDef, FieldDef
from urubuga.templating.engine import TemplateEngine, Template
from urubuga.ai.features import (
    PromptPipeline, PromptStep, AIStreamChunk,
    AIRouteHandler, AIMiddleware,
)
from urubuga.cli.commands import UrubugaCLI
from urubuga.staticfiles import StaticFileHandler


class TestWebSocket:
    def test_connection(self):
        ws = WebSocketConnection()
        assert ws.state == WebSocketState.CONNECTING
        assert ws.id.startswith("ws_")

    def test_message(self):
        msg = WebSocketMessage("hello")
        assert str(msg) == "hello"

    def test_message_json(self):
        msg = WebSocketMessage.from_json({"key": "value"})
        assert msg.json() == {"key": "value"}

    def test_manager(self):
        mgr = WebSocketManager()
        conn = WebSocketConnection()
        mgr.add_connection(conn)
        assert conn.state == WebSocketState.OPEN
        assert mgr.connection_count() == 1

    def test_remove_connection(self):
        mgr = WebSocketManager()
        conn = WebSocketConnection()
        mgr.add_connection(conn)
        mgr.remove_connection(conn.id)
        assert mgr.connection_count() == 0

    def test_room(self):
        mgr = WebSocketManager()
        room = mgr.get_room("test")
        assert room.name == "test"

    def test_room_connections(self):
        room = Room("test")
        conn1 = WebSocketConnection()
        conn2 = WebSocketConnection()
        asyncio.run(room.join(conn1))
        asyncio.run(room.join(conn2))
        assert room.connection_count == 2

    def test_room_leave(self):
        room = Room("test")
        conn = WebSocketConnection()
        asyncio.run(room.join(conn))
        asyncio.run(room.leave(conn))
        assert room.connection_count == 0

    def test_room_names(self):
        mgr = WebSocketManager()
        mgr.get_room("room1")
        mgr.get_room("room2")
        assert set(mgr.room_names()) == {"room1", "room2"}

    def test_presence(self):
        p = Presence()
        p.join("user1", "conn1")
        assert p.is_online("user1")
        assert p.online_count() == 1

    def test_presence_leave(self):
        p = Presence()
        p.join("user1", "conn1")
        p.leave("user1")
        assert not p.is_online("user1")

    def test_presence_status(self):
        p = Presence()
        p.join("user1", "conn1", status="away")
        status = p.get_status("user1")
        assert status["status"] == "away"

    def test_connection_uptime(self):
        conn = WebSocketConnection()
        assert conn.uptime >= 0


class TestSSE:
    def test_event_to_string(self):
        event = SSEEvent(data="hello", event="message")
        s = event.to_string()
        assert "data: hello" in s
        assert "event: message" in s

    def test_json_event(self):
        event = SSEEvent.json({"key": "value"}, event="update")
        s = event.to_string()
        assert "data:" in s
        assert "event: update" in s

    def test_heartbeat(self):
        event = SSEEvent.heartbeat()
        s = event.to_string()
        assert ": heartbeat" in s

    def test_client(self):
        client = SSEClient()
        assert client.is_open
        assert client.id.startswith("sse_")

    def test_client_close(self):
        client = SSEClient()
        client.close()
        assert not client.is_open

    def test_manager(self):
        mgr = SSEManager()
        client = SSEClient()
        mgr.add_client(client)
        assert mgr.client_count() == 1

    def test_manager_remove(self):
        mgr = SSEManager()
        client = SSEClient()
        mgr.add_client(client)
        mgr.remove_client(client.id)
        assert mgr.client_count() == 0

    def test_subscribe_topic(self):
        mgr = SSEManager()
        client = SSEClient()
        mgr.add_client(client)
        mgr.subscribe(client.id, "news")
        assert mgr.topic_count() == 1

    def test_event_count(self):
        mgr = SSEManager()
        client = SSEClient()
        mgr.add_client(client)
        asyncio.run(
            mgr.broadcast(SSEEvent.heartbeat()))
        assert mgr.event_count == 1


class TestGraphQL:
    def test_type_def(self):
        td = TypeDef("User", [
            FieldDef("id", "ID"),
            FieldDef("name", "String"),
        ])
        assert td.name == "User"
        assert "id" in td.fields

    def test_type_sdl(self):
        td = TypeDef("User", [
            FieldDef("id", "ID"),
            FieldDef("name", "String"),
        ])
        sdl = td.toSDL()
        assert "type User" in sdl
        assert "id: ID" in sdl

    def test_schema(self):
        schema = GraphQLSchema()
        schema.type("User", fields=[
            FieldDef("id", "ID"),
            FieldDef("name", "String"),
        ])
        assert schema.type_count() == 1

    def test_query(self):
        schema = GraphQLSchema()
        @schema.query("hello", type_name="String")
        def resolve_hello():
            return "world"
        assert schema.query_count() == 1

    def test_mutation(self):
        schema = GraphQLSchema()
        @schema.mutation("createUser", type_name="User")
        def resolve_create():
            return {"id": "1", "name": "Alice"}
        assert schema.mutation_count() == 1

    def test_execute(self):
        schema = GraphQLSchema()
        @schema.query("hello", type_name="String")
        def resolve_hello():
            return "world"
        result = schema.execute("{ hello }")
        assert result["data"]["hello"] == "world"

    def test_sdl_generation(self):
        schema = GraphQLSchema()
        @schema.query("greeting", type_name="String")
        def resolve():
            return "hi"
        sdl = schema.toSDL()
        assert "type Query" in sdl
        assert "greeting" in sdl


class TestTemplateEngine:
    def test_render(self):
        engine = TemplateEngine()
        engine.add_string("hello.html", "<h1>Hello {{name}}</h1>")
        result = engine.render("hello.html", name="World")
        assert "<h1>Hello World</h1>" in result

    def test_if(self):
        engine = TemplateEngine()
        engine.add_string("t.html", "{% if show %}visible{% else %}hidden{% endif %}")
        result = engine.render("t.html", show=True)
        assert "visible" in result
        result2 = engine.render("t.html", show=False)
        assert "hidden" in result2

    def test_for_loop(self):
        engine = TemplateEngine()
        engine.add_string("t.html", "{% for item in items %}{{item}} {% endfor %}")
        result = engine.render("t.html", items=["a", "b", "c"])
        assert "a b c" in result

    def test_globals(self):
        engine = TemplateEngine()
        engine.set_global("site_name", "My Site")
        engine.add_string("t.html", "{{site_name}}")
        result = engine.render("t.html")
        assert "My Site" in result

    def test_template_count(self):
        engine = TemplateEngine()
        engine.add_string("a.html", "a")
        engine.add_string("b.html", "b")
        assert engine.template_count() == 2

    def test_clear_cache(self):
        engine = TemplateEngine()
        engine.add_string("t.html", "test")
        count = engine.clear_cache()
        assert count == 1

    def test_not_found(self):
        engine = TemplateEngine()
        with pytest.raises(FileNotFoundError):
            engine.render("nonexistent.html")


class TestTemplate:
    def test_simple_render(self):
        t = Template("test", "Hello {{name}}")
        result = t.render(name="World")
        assert result == "Hello World"

    def test_multiple_vars(self):
        t = Template("test", "{{greeting}} {{name}}!")
        result = t.render(greeting="Hi", name="Alice")
        assert result == "Hi Alice!"


class TestAIFeatures:
    def test_prompt_step(self):
        step = PromptStep("intro", "You are a helper. User says: {prompt}")
        rendered = step.render({"prompt": "hello"})
        assert "hello" in rendered

    def test_pipeline(self):
        pipeline = PromptPipeline("test")
        pipeline.step("step1", "Process: {prompt}")
        pipeline.step("step2", "Based on: {step1}")
        results = pipeline.execute({"prompt": "hello"})
        assert "step1" in results
        assert "step2" in results

    def test_pipeline_step_count(self):
        p = PromptPipeline()
        p.step("a", "t1")
        p.step("b", "t2")
        assert p.step_count == 2

    def test_stream_chunk(self):
        chunk = AIStreamChunk(text="hello", index=0)
        sse = chunk.to_sse()
        assert "data:" in sse
        assert "hello" in sse

    def test_stream_chunk_finish(self):
        chunk = AIStreamChunk(finish_reason="stop")
        d = chunk.to_dict()
        assert d["finish_reason"] == "stop"

    def test_ai_handler(self):
        handler = AIRouteHandler()
        result = handler.handle("test prompt")
        assert "response" in result

    def test_ai_handler_with_llm(self):
        handler = AIRouteHandler(llm_fn=lambda p, **kw: f"Response to: {p}")
        result = handler.handle("hello")
        assert "Response to: hello" in result["response"]

    def test_ai_handler_stream(self):
        handler = AIRouteHandler()
        chunks = list(handler.stream("test"))
        assert len(chunks) > 0
        assert chunks[-1].finish_reason == "stop"

    def test_ai_middleware(self):
        mw = AIMiddleware()
        mw.set_cached("key1", "value1")
        result = mw.get_cached("key1")
        assert result == "value1"

    def test_ai_middleware_cache_stats(self):
        mw = AIMiddleware()
        mw.set_cached("k", "v")
        mw.get_cached("k")
        mw.get_cached("miss")
        stats = mw.cache_stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_request_count(self):
        handler = AIRouteHandler()
        handler.handle("a")
        handler.handle("b")
        assert handler.request_count == 2


class TestCLI:
    def test_new_project(self):
        import tempfile, os
        cli = UrubugaCLI()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli.new("myapp", output_dir=tmpdir)
            assert result["success"]
            assert os.path.isdir(result["directory"])

    def test_new_rest_api(self):
        import tempfile, os
        cli = UrubugaCLI()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli.new("myapi", template="rest-api",
                             output_dir=tmpdir)
            assert result["success"]
            assert "rest-api" in result["template"]

    def test_list_templates(self):
        cli = UrubugaCLI()
        templates = cli.list_templates()
        assert len(templates) >= 4
        names = [t["name"] for t in templates]
        assert "website" in names
        assert "rest-api" in names

    def test_doctor(self):
        cli = UrubugaCLI()
        result = cli.doctor()
        assert result["healthy"]

    def test_build(self):
        import tempfile, json, os
        cli = UrubugaCLI()
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"name": "test", "type": "website", "version": "0.1.0"}
            with open(os.path.join(tmpdir, "config.json"), "w") as f:
                json.dump(config, f)
            result = cli.build(tmpdir)
            assert result["success"]

    def test_analyze(self):
        import tempfile, json, os
        cli = UrubugaCLI()
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"name": "test", "type": "website", "version": "0.1.0"}
            with open(os.path.join(tmpdir, "config.json"), "w") as f:
                json.dump(config, f)
            result = cli.analyze(tmpdir)
            assert result["success"]

    def test_new_invalid_template(self):
        cli = UrubugaCLI()
        result = cli.new("test", template="nonexistent")
        assert not result["success"]


class TestStaticFiles:
    def test_serve(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.txt"), "w") as f:
                f.write("hello")
            handler = StaticFileHandler(tmpdir, "/static")
            resp = handler.serve("/static/test.txt")
            assert resp is not None
            assert resp.body == b"hello"

    def test_not_found(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = StaticFileHandler(tmpdir, "/static")
            resp = handler.serve("/static/nonexistent.txt")
            assert resp is None

    def test_path_traversal(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = StaticFileHandler(tmpdir, "/static")
            resp = handler.serve("/static/../secret.txt")
            assert resp.status == StatusCode.FORBIDDEN
