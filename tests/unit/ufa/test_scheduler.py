"""Tests for UFA task scheduler."""

import time
import pytest
from ufa.scheduler import TaskScheduler, TaskState, ScheduleType


class TestTaskScheduler:
    def test_schedule_once(self):
        s = TaskScheduler()
        result = [None]
        s.schedule_once(lambda: result.__setitem__(0, "done"))
        s.tick()
        assert result[0] == "done"

    def test_schedule_interval(self):
        s = TaskScheduler()
        count = [0]
        s.schedule_interval(lambda: count.__setitem__(0, count[0] + 1), 0.01)
        s.tick()
        s.tick()
        assert count[0] >= 1

    def test_cancel_task(self):
        s = TaskScheduler()
        count = [0]
        task = s.schedule_interval(lambda: count.__setitem__(0, count[0] + 1), 0.01)
        s.tick()
        s.cancel_task(task.id)
        assert not task.enabled

    def test_pause_resume(self):
        s = TaskScheduler()
        task = s.schedule_once(lambda: None)
        s.pause_task(task.id)
        assert task.state == TaskState.PAUSED
        s.resume_task(task.id)
        assert task.enabled

    def test_start_worker(self):
        s = TaskScheduler()
        worker = s.start_worker(lambda w: time.sleep(0.01))
        assert worker.state == TaskState.RUNNING
        worker.stop()
        time.sleep(0.05)

    def test_worker_count(self):
        s = TaskScheduler()
        assert s.worker_count() == 0

    def test_tick_count(self):
        s = TaskScheduler()
        s.tick()
        assert s.tick_count == 1

    def test_task_count(self):
        s = TaskScheduler()
        s.schedule_once(lambda: None)
        assert s.task_count() == 1

    def test_get_task(self):
        s = TaskScheduler()
        task = s.schedule_once(lambda: None)
        assert s.get_task(task.id) is task

    def test_list_tasks(self):
        s = TaskScheduler()
        s.schedule_once(lambda: None)
        s.schedule_once(lambda: None)
        assert len(s.list_tasks()) == 2

    def test_task_error(self):
        s = TaskScheduler()
        task = s.schedule_once(lambda: 1 / 0)
        s.tick()
        assert task.state == TaskState.FAILED
        assert task.error_count == 1
