"""WebSocket client with auto-reconnect and heartbeat support."""

import asyncio
import json
import random
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

MessageCallback = Callable[[str], None]
EventCallback = Callable[[], None]
ErrorCallback = Callable[[Exception], None]


class WebSocketState(Enum):
    """WebSocket connection states."""

    CONNECTING = auto()
    """The WebSocket is attempting to connect."""
    CONNECTED = auto()
    """The WebSocket is connected and ready."""
    DISCONNECTING = auto()
    """The WebSocket is closing."""
    DISCONNECTED = auto()
    """The WebSocket is closed."""


class WebSocketClient:
    """WebSocket client with auto-reconnect and heartbeat.

    Args:
        url: WebSocket server URL.
        auto_reconnect: Whether to automatically reconnect on disconnect.
        max_reconnect_attempts: Maximum number of reconnect attempts.
        reconnect_delay: Base delay in seconds before reconnecting.
        heartbeat_interval: Interval in seconds for ping/pong heartbeat.
    """

    def __init__(
        self,
        url: str = "",
        auto_reconnect: bool = True,
        max_reconnect_attempts: int = 10,
        reconnect_delay: float = 1.0,
        heartbeat_interval: float = 30.0,
    ) -> None:
        self._url: str = url
        self._state: WebSocketState = WebSocketState.DISCONNECTED
        self._auto_reconnect: bool = auto_reconnect
        self._max_reconnect_attempts: int = max_reconnect_attempts
        self._reconnect_delay: float = reconnect_delay
        self._heartbeat_interval: float = heartbeat_interval
        self._reconnect_attempts: int = 0
        self._message_callbacks: List[MessageCallback] = []
        self._open_callbacks: List[EventCallback] = []
        self._close_callbacks: List[EventCallback] = []
        self._error_callbacks: List[ErrorCallback] = []
        self._connection: Optional[Any] = None
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._reconnect_task: Optional[asyncio.Task[None]] = None
        self._running: bool = False

    @property
    def url(self) -> str:
        """The WebSocket server URL."""
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value

    @property
    def state(self) -> WebSocketState:
        """Current connection state."""
        return self._state

    @property
    def reconnect_attempts(self) -> int:
        """Number of reconnect attempts made."""
        return self._reconnect_attempts

    @property
    def auto_reconnect(self) -> bool:
        """Whether auto-reconnect is enabled."""
        return self._auto_reconnect

    @auto_reconnect.setter
    def auto_reconnect(self, value: bool) -> None:
        self._auto_reconnect = value

    async def connect(self, url: Optional[str] = None) -> None:
        """Connect to the WebSocket server.

        Args:
            url: Optional URL override.
        """
        if url is not None:
            self._url = url
        if self._state == WebSocketState.CONNECTED:
            return

        self._state = WebSocketState.CONNECTING
        self._running = True
        self._reconnect_attempts = 0

        try:
            import asyncio
            # Simulate connection - real impl would use websockets library
            self._connection = asyncio.open_connection(self._url)
            self._state = WebSocketState.CONNECTED
            self._reconnect_attempts = 0
            for cb in self._open_callbacks:
                cb()
            await self._start_heartbeat()
        except Exception as e:
            self._state = WebSocketState.DISCONNECTED
            for cb in self._error_callbacks:
                cb(e)
            if self._auto_reconnect:
                await self._try_reconnect()

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        self._running = False
        self._state = WebSocketState.DISCONNECTING
        await self._stop_heartbeat()
        self._connection = None
        self._state = WebSocketState.DISCONNECTED
        for cb in self._close_callbacks:
            cb()

    async def send(self, message: str) -> None:
        """Send a text message.

        Args:
            message: The message string to send.

        Raises:
            ConnectionError: If not connected.
        """
        if self._state != WebSocketState.CONNECTED:
            raise ConnectionError("WebSocket is not connected")
        # Simulated send
        pass

    async def send_json(self, data: Any) -> None:
        """Send a JSON-encoded message.

        Args:
            data: Serializable data to send.
        """
        message = json.dumps(data)
        await self.send(message)

    def on_message(self, callback: MessageCallback) -> Callable[[], None]:
        """Register a message received callback.

        Args:
            callback: Called with the message text.

        Returns:
            A function to unregister the callback.
        """
        self._message_callbacks.append(callback)

        def remove() -> None:
            try:
                self._message_callbacks.remove(callback)
            except ValueError:
                pass

        return remove

    def on_open(self, callback: EventCallback) -> Callable[[], None]:
        """Register a connection opened callback.

        Args:
            callback: Called when the connection opens.

        Returns:
            A function to unregister the callback.
        """
        self._open_callbacks.append(callback)

        def remove() -> None:
            try:
                self._open_callbacks.remove(callback)
            except ValueError:
                pass

        return remove

    def on_close(self, callback: EventCallback) -> Callable[[], None]:
        """Register a connection closed callback.

        Args:
            callback: Called when the connection closes.

        Returns:
            A function to unregister the callback.
        """
        self._close_callbacks.append(callback)

        def remove() -> None:
            try:
                self._close_callbacks.remove(callback)
            except ValueError:
                pass

        return remove

    def on_error(self, callback: ErrorCallback) -> Callable[[], None]:
        """Register an error callback.

        Args:
            callback: Called with the exception on error.

        Returns:
            A function to unregister the callback.
        """
        self._error_callbacks.append(callback)

        def remove() -> None:
            try:
                self._error_callbacks.remove(callback)
            except ValueError:
                pass

        return remove

    async def _start_heartbeat(self) -> None:
        """Start the heartbeat loop for ping/pong."""
        if self._heartbeat_interval <= 0:
            return

        async def heartbeat_loop() -> None:
            while self._state == WebSocketState.CONNECTED and self._running:
                await asyncio.sleep(self._heartbeat_interval)
                if self._state == WebSocketState.CONNECTED:
                    await self._ping()

        self._heartbeat_task = asyncio.create_task(heartbeat_loop())

    async def _stop_heartbeat(self) -> None:
        """Stop the heartbeat loop."""
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    async def _ping(self) -> None:
        """Send a ping frame."""
        pass

    async def _try_reconnect(self) -> None:
        """Attempt to reconnect with exponential backoff."""
        while (
            self._auto_reconnect
            and self._running
            and self._reconnect_attempts < self._max_reconnect_attempts
        ):
            self._reconnect_attempts += 1
            delay = self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
            jitter = random.uniform(0, 0.5 * delay)
            await asyncio.sleep(delay + jitter)
            try:
                await self.connect()
                return
            except Exception:
                continue
