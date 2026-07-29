"""Tests for UFA event bus."""

import pytest
from ufa.events import EventBus, Event, EventPriority


class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus()
        received = []
        bus.subscribe("test", lambda e: received.append(e.data))
        bus.emit("test", "hello")
        assert received == ["hello"]

    def test_multiple_subscribers(self):
        bus = EventBus()
        count = [0]
        bus.subscribe("x", lambda e: count.__setitem__(0, count[0] + 1))
        bus.subscribe("x", lambda e: count.__setitem__(0, count[0] + 1))
        bus.emit("x")
        assert count[0] == 2

    def test_priority_order(self):
        bus = EventBus()
        order = []
        bus.subscribe("x", lambda e: order.append("low"), priority=EventPriority.LOW)
        bus.subscribe("x", lambda e: order.append("high"), priority=EventPriority.HIGH)
        bus.emit("x")
        assert order == ["high", "low"]

    def test_once(self):
        bus = EventBus()
        count = [0]
        bus.once("x", lambda e: count.__setitem__(0, count[0] + 1))
        bus.emit("x")
        bus.emit("x")
        assert count[0] == 1

    def test_stop_propagation(self):
        bus = EventBus()
        received = []
        def stopper(e):
            e.stop_propagation()
        bus.subscribe("x", stopper, priority=100)
        bus.subscribe("x", lambda e: received.append(1))
        bus.emit("x")
        assert received == []

    def test_wildcard(self):
        bus = EventBus()
        received = []
        bus.subscribe("*", lambda e: received.append(e.name))
        bus.emit("a")
        bus.emit("b")
        assert received == ["a", "b"]

    def test_unsubscribe(self):
        bus = EventBus()
        count = [0]
        sub = bus.subscribe("x", lambda e: count.__setitem__(0, count[0] + 1))
        bus.emit("x")
        bus.unsubscribe(sub)
        bus.emit("x")
        assert count[0] == 1

    def test_history(self):
        bus = EventBus()
        bus.emit("a")
        bus.emit("b")
        history = bus.history()
        assert len(history) == 2

    def test_history_filtered(self):
        bus = EventBus()
        bus.emit("a")
        bus.emit("b")
        bus.emit("a")
        history = bus.history("a")
        assert len(history) == 2

    def test_subscription_count(self):
        bus = EventBus()
        bus.subscribe("a", lambda e: None)
        bus.subscribe("b", lambda e: None)
        assert bus.subscription_count() == 2
        assert bus.subscription_count("a") == 1

    def test_event_names(self):
        bus = EventBus()
        bus.subscribe("x", lambda e: None)
        bus.subscribe("y", lambda e: None)
        names = bus.event_names()
        assert "x" in names
        assert "y" in names

    def test_clear(self):
        bus = EventBus()
        bus.subscribe("x", lambda e: None)
        bus.emit("x")
        bus.clear()
        assert bus.subscription_count() == 0

    def test_emit_count(self):
        bus = EventBus()
        bus.emit("a")
        bus.emit("b")
        assert bus.emit_count == 2

    def test_filter_fn(self):
        bus = EventBus()
        received = []
        bus.subscribe("x", lambda e: received.append(e.data),
                       filter_fn=lambda e: e.data > 5)
        bus.emit("x", 3)
        bus.emit("x", 10)
        assert received == [10]
