"""Tests for UFA lifecycle module."""

import pytest
from ufa.lifecycle import LifecycleManager, Phase


class TestLifecycleManager:
    def test_initial_phase(self):
        lm = LifecycleManager()
        assert lm.phase == Phase.CREATED

    def test_advance_to_starting(self):
        lm = LifecycleManager()
        lm.advance(Phase.STARTING)
        assert lm.phase == Phase.STARTING

    def test_hook_fires(self):
        lm = LifecycleManager()
        fired = []
        lm.on_start(lambda: fired.append(True))
        lm.advance(Phase.STARTING)
        assert fired == [True]

    def test_hook_priority(self):
        lm = LifecycleManager()
        order = []
        lm.on_start(lambda: order.append("low"), priority=-10)
        lm.on_start(lambda: order.append("high"), priority=10)
        lm.on_start(lambda: order.append("mid"), priority=0)
        lm.advance(Phase.STARTING)
        assert order == ["high", "mid", "low"]

    def test_once_hook(self):
        lm = LifecycleManager()
        count = [0]
        lm.on_start(lambda: count.__setitem__(0, count[0] + 1), once=True)
        lm.advance(Phase.STARTING)
        lm._set_phase(Phase.STARTING)
        assert count[0] == 1

    def test_uptime(self):
        lm = LifecycleManager()
        assert lm.uptime == 0.0

    def test_is_running(self):
        lm = LifecycleManager()
        assert not lm.is_running

    def test_history(self):
        lm = LifecycleManager()
        lm.advance(Phase.STARTING)
        assert len(lm.history) > 0

    def test_remove_hooks(self):
        lm = LifecycleManager()
        lm.on_start(lambda: None)
        lm.on_stop(lambda: None)
        removed = lm.remove_hooks(Phase.STARTING)
        assert removed == 1

    def test_reset(self):
        lm = LifecycleManager()
        lm.advance(Phase.STARTING)
        lm.reset()
        assert lm.phase == Phase.CREATED

    def test_error_hook(self):
        lm = LifecycleManager()
        errors = []
        lm.on_error(lambda e, h: errors.append(str(e)))
        lm.on_start(lambda: 1 / 0)
        lm.advance(Phase.STARTING)
        assert len(errors) == 1
