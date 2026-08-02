"""I STUDIO IDE — Server-Sent Events hub.

A tiny thread-safe pub/sub used to stream run output, terminal I/O and debugger
events to the browser over ``EventSource`` (SSE). Zero dependencies.
"""

from __future__ import annotations

import json
import queue
import threading
from collections import deque
from typing import Any


class SSEHub:
    def __init__(self, max_buffer: int = 2000, stream_history: int = 500):
        self._clients: dict[str, set[queue.Queue]] = {}
        self._history: dict[str, deque[str]] = {}
        self._lock = threading.Lock()
        self._max_buffer = max_buffer
        self._stream_history = stream_history

    def subscribe(self, stream_id: str) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=self._max_buffer)
        with self._lock:
            self._clients.setdefault(stream_id, set()).add(q)
            history = list(self._history.get(stream_id, ()))
        for frame in history:
            try:
                q.put_nowait(frame)
            except queue.Full:
                break
        return q

    def unsubscribe(self, stream_id: str, q: queue.Queue) -> None:
        with self._lock:
            clients = self._clients.get(stream_id)
            if clients:
                clients.discard(q)
                if not clients:
                    self._clients.pop(stream_id, None)

    def publish(self, stream_id: str, event: str, data: Any = None) -> str:
        frame = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"
        with self._lock:
            self._clients.setdefault(stream_id, set())
            clients = list(self._clients[stream_id])
            history = self._history.setdefault(stream_id, deque(maxlen=self._stream_history))
            history.append(frame)
        for q in clients:
            try:
                q.put_nowait(frame)
            except queue.Full:
                try:
                    q.get_nowait()
                    q.put_nowait(frame)
                except (queue.Empty, queue.Full):
                    pass
        return frame

    def close_stream(self, stream_id: str) -> None:
        with self._lock:
            self._clients.pop(stream_id, None)
            self._history.pop(stream_id, None)


def sse_frame(event: str, data: Any = None) -> bytes:
    body = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"
    return body.encode("utf-8")
