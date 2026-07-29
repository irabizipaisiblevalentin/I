"""Tests for IGICU Messaging (ubutumwa)."""

from __future__ import annotations

import pytest

from igicu.ubutumwa import (
    MessageBroker, MessageQueue, EventBus, StreamProcessor,
    MessagingPlatform, Message,
)
from igicu.ibikoreshingiro import (
    TopicSpec, MessageQueueSpec, DeliveryGuarantee,
    MessagingError,
)


class TestMessageBroker:
    def test_create_topic(self):
        broker = MessageBroker()
        name = broker.create_topic(TopicSpec(name="test", partitions=3))
        assert name == "test"
        topics = broker.list_topics()
        assert len(topics) == 1

    def test_create_duplicate_topic(self):
        broker = MessageBroker()
        broker.create_topic(TopicSpec(name="dup"))
        with pytest.raises(MessagingError):
            broker.create_topic(TopicSpec(name="dup"))

    def test_publish_and_consume(self):
        broker = MessageBroker()
        broker.create_topic(TopicSpec(name="orders", partitions=2))
        msg = Message(topic="orders", key="order-1", value="new order")
        offset = broker.publish("orders", msg)
        partition = hash(msg.key) % 2
        messages = broker.consume("orders", partition=partition, batch_size=10)
        assert len(messages) > 0

    def test_subscribe(self):
        broker = MessageBroker()
        broker.create_topic(TopicSpec(name="events"))
        received = []

        def handler(msg):
            received.append(msg)

        broker.subscribe("events", handler)
        broker.publish("events", Message(topic="events", value="test"))
        assert len(received) == 1

    def test_dead_letter(self):
        broker = MessageBroker()
        broker.create_topic(TopicSpec(name="fails"))

        def failing(msg):
            raise ValueError("handler failed")

        broker.subscribe("fails", failing)
        broker.publish("fails", Message(topic="fails", value="bad"))
        dls = broker.get_dead_letter_messages("fails")
        assert len(dls) > 0

    def test_delete_topic(self):
        broker = MessageBroker()
        broker.create_topic(TopicSpec(name="del"))
        assert broker.delete_topic("del") is True


class TestMessageQueue:
    def test_enqueue_dequeue(self):
        queue = MessageQueue(MessageQueueSpec(name="tasks"))
        msg = Message(topic="tasks", value="work")
        msg_id = queue.enqueue(msg)
        batch = queue.dequeue(batch_size=1)
        assert len(batch) == 1
        assert batch[0].id == msg_id

    def test_ack(self):
        queue = MessageQueue()
        msg = Message(topic="t", value="v")
        queue.enqueue(msg)
        batch = queue.dequeue()
        assert queue.ack(batch[0].id) is True

    def test_nack(self):
        queue = MessageQueue()
        msg = Message(topic="t", value="v")
        queue.enqueue(msg)
        batch = queue.dequeue()
        assert queue.nack(batch[0].id) is True

    def test_size(self):
        queue = MessageQueue()
        queue.enqueue(Message(topic="t", value="1"))
        queue.enqueue(Message(topic="t", value="2"))
        assert queue.size() == 2

    def test_purge(self):
        queue = MessageQueue()
        queue.enqueue(Message(topic="t", value="1"))
        assert queue.purge() == 1
        assert queue.size() == 0


class TestEventBus:
    def test_emit_and_history(self):
        bus = EventBus()
        event_id = bus.emit("user.created", {"id": 1})
        assert event_id is not None
        history = bus.history()
        assert len(history) == 1

    def test_on_event(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.on("test.event", handler)
        bus.emit("test.event", "data")
        assert len(received) == 1

    def test_wildcard_handler(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.on("*", handler)
        bus.emit("any.event", "data")
        assert len(received) == 1

    def test_off(self):
        bus = EventBus()

        def handler(event):
            pass

        bus.on("e", handler)
        assert bus.off("e", handler) is True

    def test_clear(self):
        bus = EventBus()
        bus.emit("e", "d")
        bus.clear()
        assert len(bus.history()) == 0


class TestMessagingPlatform:
    def test_create_queue(self):
        platform = MessagingPlatform()
        queue = platform.create_queue("tasks")
        assert queue is not None

    def test_create_topic_and_publish(self):
        platform = MessagingPlatform()
        platform.create_topic(TopicSpec(name="events"))
        offset = platform.publish("events", "key1", "value1")
        assert offset >= 0

    def test_emit_event(self):
        platform = MessagingPlatform()
        event_id = platform.emit("app.started", {"version": "1.0"})
        assert event_id is not None
