"""IGICU — Messaging: queues, pub/sub, streaming, event bus."""

from __future__ import annotations

import json
import time
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from .ibikoreshingiro import (
    DeliveryGuarantee, MessageInfo, MessageProtocol,
    MessageQueueSpec, TopicSpec, MessagingError, IGICU_VERSION,
)


class Message:
    def __init__(self, topic: str, key: str = "", value: Any = None,
                 headers: Optional[Dict[str, str]] = None):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.key = key
        self.value = value
        self.headers = headers or {}
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        self._offset: int = 0


class MessageBroker:
    def __init__(self):
        self._topics: Dict[str, TopicSpec] = {}
        self._partitions: Dict[str, Dict[int, List[Message]]] = {}
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._offsets: Dict[str, Dict[str, int]] = defaultdict(dict)
        self._dead_letters: Dict[str, List[Message]] = defaultdict(list)

    def create_topic(self, spec: TopicSpec) -> str:
        if spec.name in self._topics:
            raise MessagingError(f"Topic '{spec.name}' already exists")
        self._topics[spec.name] = spec
        self._partitions[spec.name] = {p: [] for p in range(spec.partitions)}
        self._subscriptions[spec.name] = []
        return spec.name

    def delete_topic(self, topic: str) -> bool:
        if topic in self._topics:
            del self._topics[topic]
            self._partitions.pop(topic, None)
            self._subscriptions.pop(topic, None)
            return True
        return False

    def publish(self, topic: str, message: Message) -> int:
        topic_spec = self._topics.get(topic)
        if not topic_spec:
            raise MessagingError(f"Topic '{topic}' not found")

        partition = hash(message.key or message.id) % topic_spec.partitions
        message._offset = len(self._partitions[topic][partition])
        self._partitions[topic][partition].append(message)

        for handler in self._subscriptions.get(topic, []):
            try:
                handler(message)
            except Exception:
                self._dead_letters[topic].append(message)

        return message._offset

    def subscribe(self, topic: str, handler: Callable) -> str:
        if topic not in self._topics:
            raise MessagingError(f"Topic '{topic}' not found")
        sub_id = str(uuid.uuid4())
        self._subscriptions[topic].append(handler)
        return sub_id

    def consume(self, topic: str, partition: int = 0,
                offset: int = 0, batch_size: int = 10,
                consumer_id: str = "") -> List[Dict[str, Any]]:
        partitions = self._partitions.get(topic, {})
        messages = partitions.get(partition, [])

        consumer_key = f"{consumer_id or 'default'}"
        current_offset = self._offsets[topic].get(consumer_key, offset)

        batch = []
        for i in range(current_offset, min(current_offset + batch_size, len(messages))):
            msg = messages[i]
            batch.append({
                "id": msg.id,
                "topic": msg.topic,
                "key": msg.key,
                "value": msg.value,
                "headers": msg.headers,
                "timestamp": msg.timestamp,
                "partition": partition,
                "offset": i,
            })
            self._offsets[topic][consumer_key] = i + 1

        return batch

    def commit_offset(self, topic: str, consumer_id: str, offset: int) -> None:
        self._offsets[topic][consumer_id] = offset

    def get_dead_letter_messages(self, topic: str) -> List[Dict[str, Any]]:
        return [
            {
                "id": m.id,
                "topic": m.topic,
                "key": m.key,
                "value": m.value,
                "timestamp": m.timestamp,
            }
            for m in self._dead_letters.get(topic, [])
        ]

    def list_topics(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "partitions": spec.partitions,
                "retention_hours": spec.retention_hours,
                "messages": sum(len(p) for p in self._partitions.get(name, {}).values()),
            }
            for name, spec in self._topics.items()
        ]


class MessageQueue:
    def __init__(self, spec: Optional[MessageQueueSpec] = None):
        self.spec = spec or MessageQueueSpec(name="default")
        self._messages: List[Message] = []
        self._consumed: Set[str] = set()
        self._dead_letters: List[Message] = []

    def enqueue(self, message: Message) -> str:
        self._messages.append(message)
        return message.id

    def dequeue(self, batch_size: int = 1) -> List[Message]:
        batch = []
        for msg in self._messages:
            if msg.id not in self._consumed:
                batch.append(msg)
                self._consumed.add(msg.id)
                if len(batch) >= batch_size:
                    break
        return batch

    def ack(self, message_id: str) -> bool:
        return message_id in self._consumed

    def nack(self, message_id: str) -> bool:
        if message_id in self._consumed:
            self._consumed.remove(message_id)
            msg = next((m for m in self._messages if m.id == message_id), None)
            if msg and self.spec.dead_letter:
                self._dead_letters.append(msg)
            return True
        return False

    def size(self) -> int:
        return len(self._messages) - len(self._consumed)

    def total(self) -> int:
        return len(self._messages)

    def purge(self) -> int:
        count = len(self._messages)
        self._messages.clear()
        self._consumed.clear()
        return count

    def get_dead_letters(self) -> List[Dict[str, Any]]:
        return [
            {"id": m.id, "topic": m.topic, "key": m.key, "timestamp": m.timestamp}
            for m in self._dead_letters
        ]


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._history: List[Dict[str, Any]] = []
        self._max_history = 1000

    def emit(self, event_type: str, data: Any = None,
             source: str = "") -> str:
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "type": event_type,
            "data": data,
            "source": source,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass
        for wildcard_handler in self._handlers.get("*", []):
            try:
                wildcard_handler(event)
            except Exception:
                pass

        return event_id

    def on(self, event_type: str, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def off(self, event_type: str, handler: Callable) -> bool:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def history(self, event_type: Optional[str] = None,
                limit: int = 100) -> List[Dict[str, Any]]:
        if event_type:
            filtered = [e for e in self._history if e["type"] == event_type]
            return filtered[-limit:]
        return self._history[-limit:]

    def clear(self) -> None:
        self._history.clear()


class StreamProcessor:
    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self._processors: Dict[str, Callable] = {}

    def add_processor(self, topic: str, processor: Callable) -> str:
        proc_id = str(uuid.uuid4())
        self._processors[proc_id] = processor

        def handler(message: Message) -> None:
            try:
                processor(message)
            except Exception:
                pass

        self.broker.subscribe(topic, handler)
        return proc_id

    def remove_processor(self, processor_id: str) -> bool:
        return self._processors.pop(processor_id, None) is not None


class MessagingPlatform:
    def __init__(self):
        self.broker = MessageBroker()
        self.event_bus = EventBus()
        self._queues: Dict[str, MessageQueue] = {}
        self.stream_processor = StreamProcessor(self.broker)

    def create_queue(self, name: str, spec: Optional[MessageQueueSpec] = None) -> MessageQueue:
        if name in self._queues:
            raise MessagingError(f"Queue '{name}' already exists")
        queue = MessageQueue(spec or MessageQueueSpec(name=name))
        self._queues[name] = queue
        return queue

    def get_queue(self, name: str) -> Optional[MessageQueue]:
        return self._queues.get(name)

    def create_topic(self, spec: TopicSpec) -> str:
        return self.broker.create_topic(spec)

    def publish(self, topic: str, key: str = "",
                value: Any = None) -> int:
        msg = Message(topic=topic, key=key, value=value)
        return self.broker.publish(topic, msg)

    def subscribe(self, topic: str, handler: Callable) -> str:
        return self.broker.subscribe(topic, handler)

    def emit(self, event_type: str, data: Any = None) -> str:
        return self.event_bus.emit(event_type, data)
