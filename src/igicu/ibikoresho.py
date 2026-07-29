"""IGICU — Serverless Platform: Functions, Triggers, Scheduled Tasks."""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .ibikoreshingiro import (
    FunctionInfo, FunctionRuntime, FunctionSpec, TriggerSpec,
    TriggerType, FunctionError, IGICU_VERSION,
)


class FunctionRegistry:
    def __init__(self):
        self._functions: Dict[str, Dict[str, Any]] = {}

    def register(self, spec: FunctionSpec, code: Optional[str] = None) -> str:
        function_id = str(uuid.uuid4())
        self._functions[spec.name] = {
            "id": function_id,
            "spec": spec,
            "code": code or "",
            "status": "active",
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "invocations": 0,
            "last_invocation": None,
            "errors": 0,
        }
        return function_id

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self._functions.get(name)

    def list(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "runtime": data["spec"].runtime.value,
                "status": data["status"],
                "invocations": data["invocations"],
                "memory_mb": data["spec"].memory_mb,
                "timeout_sec": data["spec"].timeout_sec,
                "trigger_count": len(data["spec"].triggers),
                "created": data["created"],
            }
            for name, data in self._functions.items()
        ]

    def remove(self, name: str) -> bool:
        if name in self._functions:
            del self._functions[name]
            return True
        return False

    def __len__(self) -> int:
        return len(self._functions)


class FunctionRuntimeEngine:
    def __init__(self):
        self.registry = FunctionRegistry()
        self._handlers: Dict[str, Callable] = {}

    def deploy(self, spec: FunctionSpec, code: Optional[str] = None) -> str:
        return self.registry.register(spec, code)

    def invoke(self, name: str, event: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        func = self.registry.get(name)
        if not func:
            raise FunctionError(f"Function '{name}' not found")

        start = time.time()
        func["invocations"] += 1
        func["last_invocation"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            handler = self._handlers.get(name)
            if handler:
                result = handler(event or {})
            else:
                result = self._default_handler(func, event)

            latency_ms = (time.time() - start) * 1000
            return {
                "status": "success",
                "result": result,
                "latency_ms": round(latency_ms, 2),
                "execution_time_ms": round(latency_ms, 2),
            }
        except Exception as e:
            func["errors"] += 1
            latency_ms = (time.time() - start) * 1000
            return {
                "status": "error",
                "error": str(e),
                "latency_ms": round(latency_ms, 2),
            }

    def register_handler(self, name: str, handler: Callable) -> None:
        self._handlers[name] = handler

    def _default_handler(self, func: Dict[str, Any],
                         event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        spec = func["spec"]
        return {
            "message": f"Function '{spec.name}' executed successfully",
            "runtime": spec.runtime.value,
            "event": event or {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def get_invocation_count(self, name: str) -> int:
        func = self.registry.get(name)
        return func["invocations"] if func else 0

    def list(self) -> List[Dict[str, Any]]:
        return self.registry.list()


class TriggerManager:
    def __init__(self, engine: FunctionRuntimeEngine):
        self.engine = engine
        self._triggers: Dict[str, TriggerSpec] = {}

    def add_trigger(self, function_name: str, trigger: TriggerSpec) -> str:
        func = self.engine.registry.get(function_name)
        if not func:
            raise FunctionError(f"Function '{function_name}' not found")
        trigger_id = f"trg-{uuid.uuid4().hex[:8]}"
        func["spec"].triggers.append(trigger)
        self._triggers[trigger_id] = trigger
        return trigger_id

    def remove_trigger(self, trigger_id: str) -> bool:
        return self._triggers.pop(trigger_id, None) is not None

    def list_triggers(self, function_name: Optional[str] = None) -> List[Dict[str, Any]]:
        if function_name:
            func = self.engine.registry.get(function_name)
            if not func:
                return []
            return [
                {"type": t.type.value, "source": t.source, "schedule": t.schedule}
                for t in func["spec"].triggers
            ]
        return [{"id": tid, "type": t.type.value} for tid, t in self._triggers.items()]


class ScheduledTaskManager:
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def schedule(self, name: str, cron_expr: str,
                 function_name: str, payload: Optional[Dict[str, Any]] = None) -> str:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        self._tasks[task_id] = {
            "id": task_id,
            "name": name,
            "cron": cron_expr,
            "function": function_name,
            "payload": payload or {},
            "status": "active",
            "last_run": None,
            "next_run": self._next_cron(cron_expr),
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        return task_id

    def list(self) -> List[Dict[str, Any]]:
        return list(self._tasks.values())

    def pause(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task["status"] = "paused"
        return True

    def resume(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task["status"] = "active"
        return True

    def delete(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def _next_cron(self, cron_expr: str) -> str:
        parts = cron_expr.split()
        if len(parts) >= 5:
            return f"{parts[0]}:{parts[1]} UTC (next cycle)"
        return "every cycle"

    def get_tasks_for_function(self, function_name: str) -> List[Dict[str, Any]]:
        return [t for t in self._tasks.values() if t["function"] == function_name]


class ServerlessPlatform:
    def __init__(self):
        self.engine = FunctionRuntimeEngine()
        self.triggers = TriggerManager(self.engine)
        self.scheduler = ScheduledTaskManager()

    def create_function(self, spec: FunctionSpec,
                        code: Optional[str] = None) -> str:
        return self.engine.deploy(spec, code)

    def invoke(self, name: str, event: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.engine.invoke(name, event)

    def list_functions(self) -> List[Dict[str, Any]]:
        return self.engine.list()

    def delete_function(self, name: str) -> bool:
        return self.engine.registry.remove(name)

    def create_scheduled_task(self, name: str, cron: str,
                               function_name: str) -> str:
        return self.scheduler.schedule(name, cron, function_name)
