"""scheduler — Task scheduling and background worker management.

Supports cron-like scheduling, delayed tasks, intervals,
background workers, and task lifecycle management.
"""

from __future__ import annotations

import enum
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class TaskState(enum.IntEnum):
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4
    PAUSED = 5


class ScheduleType(enum.IntEnum):
    ONCE = 0
    INTERVAL = 1
    CRON = 2


class TaskDefinition:
    """Definition of a scheduled task."""
    __slots__ = ("id", "name", "handler", "schedule_type", "interval_sec",
                 "cron_expr", "state", "last_run", "next_run", "run_count",
                 "error_count", "last_error", "enabled", "metadata")

    _counter = 0

    def __init__(self, handler: Callable, name: str = "",
                 schedule_type: ScheduleType = ScheduleType.ONCE,
                 interval_sec: float = 0.0, cron_expr: str = "") -> None:
        TaskDefinition._counter += 1
        self.id = TaskDefinition._counter
        self.name = name or getattr(handler, "__name__", f"task_{self.id}")
        self.handler = handler
        self.schedule_type = schedule_type
        self.interval_sec = interval_sec
        self.cron_expr = cron_expr
        self.state = TaskState.PENDING
        self.last_run: Optional[float] = None
        self.next_run: Optional[float] = None
        self.run_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.enabled = True
        self.metadata: Dict[str, Any] = {}

    @property
    def is_due(self) -> bool:
        if not self.enabled:
            return False
        if self.next_run is None:
            return True
        return time.time() >= self.next_run


class TaskResult:
    """Result of a task execution."""
    __slots__ = ("success", "data", "error", "elapsed_ms")

    def __init__(self, success: bool = True, data: Any = None,
                 error: Optional[str] = None,
                 elapsed_ms: float = 0.0) -> None:
        self.success = success
        self.data = data
        self.error = error
        self.elapsed_ms = elapsed_ms


class BackgroundWorker:
    """A long-running background worker."""
    __slots__ = ("id", "name", "handler", "state", "error_count",
                 "last_error", "started_at", "_stop_event")

    _counter = 0

    def __init__(self, handler: Callable, name: str = "") -> None:
        BackgroundWorker._counter += 1
        self.id = BackgroundWorker._counter
        self.name = name or f"worker_{self.id}"
        self.handler = handler
        self.state = TaskState.PENDING
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.started_at: Optional[float] = None
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    @property
    def should_stop(self) -> bool:
        return self._stop_event.is_set()


class TaskScheduler:
    """Scheduler for tasks and background workers."""

    def __init__(self) -> None:
        self._tasks: Dict[int, TaskDefinition] = {}
        self._workers: Dict[int, BackgroundWorker] = {}
        self._worker_threads: Dict[int, threading.Thread] = {}
        self._lock = threading.Lock()
        self._running = False
        self._tick_count = 0

    def schedule_once(self, handler: Callable, delay_sec: float = 0.0,
                      name: str = "") -> TaskDefinition:
        task = TaskDefinition(handler, name, ScheduleType.ONCE)
        task.next_run = time.time() + delay_sec
        with self._lock:
            self._tasks[task.id] = task
        return task

    def schedule_interval(self, handler: Callable, interval_sec: float,
                          name: str = "") -> TaskDefinition:
        task = TaskDefinition(handler, name, ScheduleType.INTERVAL, interval_sec)
        task.next_run = time.time()
        with self._lock:
            self._tasks[task.id] = task
        return task

    def schedule_cron(self, handler: Callable, cron_expr: str,
                      name: str = "") -> TaskDefinition:
        task = TaskDefinition(handler, name, ScheduleType.CRON, cron_expr=cron_expr)
        with self._lock:
            self._tasks[task.id] = task
        return task

    def cancel_task(self, task_id: int) -> bool:
        task = self._tasks.get(task_id)
        if task:
            task.state = TaskState.CANCELLED
            task.enabled = False
            return True
        return False

    def pause_task(self, task_id: int) -> bool:
        task = self._tasks.get(task_id)
        if task:
            task.state = TaskState.PAUSED
            task.enabled = False
            return True
        return False

    def resume_task(self, task_id: int) -> bool:
        task = self._tasks.get(task_id)
        if task:
            task.state = TaskState.PENDING
            task.enabled = True
            return True
        return False

    def start_worker(self, handler: Callable, name: str = "") -> BackgroundWorker:
        worker = BackgroundWorker(handler, name)
        worker.state = TaskState.RUNNING
        worker.started_at = time.time()

        def _run() -> None:
            try:
                handler(worker)
            except Exception as e:
                worker.error_count += 1
                worker.last_error = str(e)
            finally:
                worker.state = TaskState.COMPLETED

        thread = threading.Thread(target=_run, name=f"ufa-worker-{worker.name}",
                                  daemon=True)
        with self._lock:
            self._workers[worker.id] = worker
            self._worker_threads[worker.id] = thread
        thread.start()
        return worker

    def stop_worker(self, worker_id: int) -> bool:
        worker = self._workers.get(worker_id)
        if worker:
            worker.stop()
            return True
        return False

    def tick(self) -> int:
        """Execute all due tasks. Returns number of tasks executed."""
        self._tick_count += 1
        executed = 0

        with self._lock:
            due_tasks = [t for t in self._tasks.values() if t.is_due]

        for task in due_tasks:
            self._execute_task(task)
            executed += 1

        return executed

    def _execute_task(self, task: TaskDefinition) -> TaskResult:
        start = time.time()
        task.state = TaskState.RUNNING
        task.last_run = start

        try:
            result = task.handler()
            elapsed = (time.time() - start) * 1000
            task.run_count += 1
            task.state = TaskState.COMPLETED

            if task.schedule_type == ScheduleType.INTERVAL:
                task.next_run = time.time() + task.interval_sec
            elif task.schedule_type == ScheduleType.ONCE:
                task.enabled = False

            return TaskResult(success=True, data=result, elapsed_ms=elapsed)

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            task.error_count += 1
            task.last_error = str(e)
            task.state = TaskState.FAILED

            if task.schedule_type == ScheduleType.INTERVAL:
                task.next_run = time.time() + task.interval_sec

            return TaskResult(success=False, error=str(e), elapsed_ms=elapsed)

    def get_task(self, task_id: int) -> Optional[TaskDefinition]:
        return self._tasks.get(task_id)

    def get_worker(self, worker_id: int) -> Optional[BackgroundWorker]:
        return self._workers.get(worker_id)

    def list_tasks(self) -> List[TaskDefinition]:
        return list(self._tasks.values())

    def list_workers(self) -> List[BackgroundWorker]:
        return list(self._workers.values())

    def task_count(self) -> int:
        return len(self._tasks)

    def worker_count(self) -> int:
        return len(self._workers)

    @property
    def tick_count(self) -> int:
        return self._tick_count
