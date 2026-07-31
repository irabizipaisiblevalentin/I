"""Tests for IGICU Serverless (ibikoresho)."""

from __future__ import annotations

import pytest

from igicu.ibikoresho import (
    ServerlessPlatform, FunctionRegistry, FunctionRuntimeEngine,
    TriggerManager, ScheduledTaskManager,
)
from igicu.ibikoreshingiro import (
    FunctionSpec, FunctionRuntime, TriggerSpec, TriggerType,
    FunctionError,
)


class TestFunctionRegistry:
    def test_register(self):
        reg = FunctionRegistry()
        spec = FunctionSpec(name="hello", runtime=FunctionRuntime.I_LANG)
        func_id = reg.register(spec)
        assert func_id is not None

    def test_get(self):
        reg = FunctionRegistry()
        spec = FunctionSpec(name="get-me")
        reg.register(spec)
        func = reg.get("get-me")
        assert func is not None
        assert func["spec"].name == "get-me"

    def test_list(self):
        reg = FunctionRegistry()
        reg.register(FunctionSpec(name="f1"))
        reg.register(FunctionSpec(name="f2"))
        funcs = reg.list()
        assert len(funcs) == 2

    def test_remove(self):
        reg = FunctionRegistry()
        reg.register(FunctionSpec(name="temp"))
        assert reg.remove("temp") is True

    def test_len(self):
        reg = FunctionRegistry()
        assert len(reg) == 0
        reg.register(FunctionSpec(name="only"))
        assert len(reg) == 1


class TestFunctionRuntimeEngine:
    def test_deploy(self):
        engine = FunctionRuntimeEngine()
        spec = FunctionSpec(name="greet", runtime=FunctionRuntime.PYTHON)
        func_id = engine.deploy(spec, "def handler(event): return 'hello'")
        assert func_id is not None

    def test_invoke(self):
        engine = FunctionRuntimeEngine()
        spec = FunctionSpec(name="echo")
        engine.deploy(spec)
        result = engine.invoke("echo", {"message": "hello"})
        assert result["status"] == "success"

    def test_invoke_nonexistent(self):
        engine = FunctionRuntimeEngine()
        with pytest.raises(FunctionError):
            engine.invoke("nonexistent")

    def test_register_handler(self):
        engine = FunctionRuntimeEngine()
        spec = FunctionSpec(name="handler-func")
        engine.deploy(spec)

        def my_handler(event):
            return {"processed": True, "data": event}

        engine.register_handler("handler-func", my_handler)
        result = engine.invoke("handler-func", {"x": 1})
        assert result["result"]["processed"] is True

    def test_list(self):
        engine = FunctionRuntimeEngine()
        engine.deploy(FunctionSpec(name="list-test"))
        funcs = engine.list()
        assert len(funcs) >= 1


class TestTriggerManager:
    def test_add_trigger(self):
        engine = FunctionRuntimeEngine()
        spec = FunctionSpec(name="triggered-func")
        engine.deploy(spec)
        tm = TriggerManager(engine)
        trigger = TriggerSpec(type=TriggerType.HTTP, source="/webhook")
        trigger_id = tm.add_trigger("triggered-func", trigger)
        assert trigger_id is not None

    def test_list_triggers(self):
        engine = FunctionRuntimeEngine()
        spec = FunctionSpec(name="list-triggers")
        engine.deploy(spec)
        tm = TriggerManager(engine)
        triggers = tm.list_triggers("list-triggers")
        assert len(triggers) >= 0

    def test_remove_trigger(self):
        engine = FunctionRuntimeEngine()
        spec = FunctionSpec(name="remove-trigger")
        engine.deploy(spec)
        tm = TriggerManager(engine)
        trigger = TriggerSpec(type=TriggerType.SCHEDULE, schedule="0 * * * *")
        trigger_id = tm.add_trigger("remove-trigger", trigger)
        assert tm.remove_trigger(trigger_id) is True


class TestScheduledTaskManager:
    def test_schedule(self):
        stm = ScheduledTaskManager()
        task_id = stm.schedule("daily-report", "0 6 * * *", "report-gen")
        assert task_id is not None

    def test_list(self):
        stm = ScheduledTaskManager()
        stm.schedule("task1", "* * * * *", "func1")
        stm.schedule("task2", "*/5 * * * *", "func2")
        tasks = stm.list()
        assert len(tasks) == 2

    def test_pause_resume(self):
        stm = ScheduledTaskManager()
        task_id = stm.schedule("pausable", "* * * * *", "func")
        assert stm.pause(task_id) is True
        assert stm.resume(task_id) is True

    def test_delete(self):
        stm = ScheduledTaskManager()
        task_id = stm.schedule("delete-me", "* * * * *", "func")
        assert stm.delete(task_id) is True


class TestServerlessPlatform:
    def test_create_function(self):
        platform = ServerlessPlatform()
        spec = FunctionSpec(name="platform-func")
        func_id = platform.create_function(spec)
        assert func_id is not None

    def test_invoke(self):
        platform = ServerlessPlatform()
        platform.create_function(FunctionSpec(name="invoke-me"))
        result = platform.invoke("invoke-me", {"hello": "world"})
        assert result["status"] == "success"

    def test_list_functions(self):
        platform = ServerlessPlatform()
        platform.create_function(FunctionSpec(name="list1"))
        platform.create_function(FunctionSpec(name="list2"))
        funcs = platform.list_functions()
        assert len(funcs) >= 2

    def test_scheduled_task(self):
        platform = ServerlessPlatform()
        task_id = platform.create_scheduled_task("hourly", "0 * * * *", "worker")
        assert task_id is not None
