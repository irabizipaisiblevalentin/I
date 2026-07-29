"""porogaramu — MobileApplication class for the I mobile platform.

Extends the UFA Application with mobile-specific lifecycle,
activity management, and platform integrations.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from ufa.core import Application
from ufa.lifecycle import Phase

from mobile.ikiganiro import ActivityState, Ikiganiro
from mobile.ubugenzuzi import NavigationEvent, Ubugenzuzi


class MobileApplication(Application):
    """Mobile application extending UFA Application with mobile lifecycle.

    Manages activities, navigation, state persistence, and platform services
    for mobile applications built on the I Programming Language.
    """

    def __init__(
        self,
        name: str = "i-mobile-app",
        version: str = "0.1.0",
        debug: bool = False,
    ) -> None:
        super().__init__(name, version)
        self._debug = debug
        self._activities: List[Ikiganiro] = []
        self._activity_stack: List[Ikiganiro] = []
        self._running = False
        self._saved_state: Dict[str, Any] = {}

        self._navigator = Ubugenzuzi()
        self._state_manager: _StateManager = _StateManager()
        self._mobile_umutekano: _SecurityManager = _SecurityManager()
        self._database: _DatabaseManager = _DatabaseManager()
        self._network: _NetworkManager = _NetworkManager()
        self._media: _MediaManager = _MediaManager()
        self._device: _DeviceManager = _DeviceManager()
        self._mobile_ubwenge: _AIAssistant = _AIAssistant()
        self._perf: _PerformanceMonitor = _PerformanceMonitor()

    # -- Properties -----------------------------------------------------------

    @property
    def debug(self) -> bool:
        """Whether debug mode is enabled."""
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        self._debug = value

    @property
    def activities(self) -> List[Ikiganiro]:
        """List of registered activities."""
        return list(self._activities)

    @property
    def navigator(self) -> Ubugenzuzi:
        """The navigation system."""
        return self._navigator

    @property
    def state_manager(self) -> _StateManager:
        """The state persistence manager."""
        return self._state_manager

    @property
    def umutekano(self) -> _SecurityManager:
        """The mobile security manager."""
        return self._mobile_umutekano

    @property
    def database(self) -> _DatabaseManager:
        """The local database manager."""
        return self._database

    @property
    def network(self) -> _NetworkManager:
        """The network connectivity manager."""
        return self._network

    @property
    def media(self) -> _MediaManager:
        """The media playback and capture manager."""
        return self._media

    @property
    def device(self) -> _DeviceManager:
        """The device hardware manager."""
        return self._device

    @property
    def ubwenge(self) -> _AIAssistant:
        """The on-device AI assistant."""
        return self._mobile_ubwenge

    @property
    def perf(self) -> _PerformanceMonitor:
        """The performance monitoring system."""
        return self._perf

    @property
    def current_activity(self) -> Optional[Ikiganiro]:
        """The top activity on the stack, if any."""
        if self._activity_stack:
            return self._activity_stack[-1]
        return None

    # -- Lifecycle ------------------------------------------------------------

    def run(self) -> None:
        """Start the mobile application lifecycle.

        Calls on_create, on_start, and on_resume in sequence.
        """
        self.on_create()
        super().run()
        self.on_start()
        self.on_resume()

    def stop(self) -> None:
        """Gracefully stop the mobile application."""
        self.on_pause()
        self.on_stop()
        super().stop()
        self.on_destroy()

    def load_config(self, path: str) -> bool:
        """Load mobile-specific configuration from a JSON file.

        Args:
            path: Path to the configuration file.

        Returns:
            True if the configuration was loaded successfully.
        """
        if not os.path.isfile(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                debug_val = data.get("debug", self._debug)
                if isinstance(debug_val, bool):
                    self._debug = debug_val
            return True
        except (json.JSONDecodeError, OSError):
            return False

    # -- Activity Management --------------------------------------------------

    def register_activity(self, activity: Ikiganiro) -> None:
        """Register an activity with the application.

        Args:
            activity: The Ikiganiro instance to register.
        """
        if activity not in self._activities:
            self._activities.append(activity)
            self.emit("activity.registered", {"activity_id": activity.id})

    def start_activity(self, activity: Ikiganiro, params: Optional[Dict[str, Any]] = None) -> None:
        """Start an activity, pushing it onto the stack.

        Pauses the current activity if one is active.

        Args:
            activity: The activity to start.
            params: Optional parameters to pass to the activity.
        """
        if activity not in self._activities:
            self.register_activity(activity)

        current = self.current_activity
        if current is not None:
            current.on_pause()

        if params:
            activity.params.update(params)

        activity.on_create()
        activity.on_start()
        activity.on_resume()
        self._activity_stack.append(activity)
        activity._state = ActivityState.KIGEZWEHO
        self.emit("activity.started", {"activity_id": activity.id})

    def finish_activity(self, activity: Optional[Ikiganiro] = None) -> None:
        """Finish (destroy) an activity and pop it from the stack.

        Args:
            activity: The activity to finish. Defaults to the current activity.
        """
        target = activity or self.current_activity
        if target is None or target not in self._activity_stack:
            return

        target.on_pause()
        target.on_stop()
        target.on_destroy()
        self._activity_stack.remove(target)
        target._state = ActivityState.KURASENZWE

        resumed = self.current_activity
        if resumed is not None:
            resumed.on_resume()

        self.emit("activity.finished", {"activity_id": target.id})

    # -- Lifecycle Callbacks --------------------------------------------------

    def on_create(self) -> None:
        """Called when the application is first created."""
        self.lifecycle.advance(Phase.CREATED, self.context)
        self.logger.info(f"MobileApplication '{self.name}' created")
        self.emit("app.create", {"name": self.name})

    def on_start(self) -> None:
        """Called when the application becomes visible."""
        self.lifecycle.advance(Phase.STARTING, self.context)
        self._running = True
        self.logger.info(f"MobileApplication '{self.name}' started")
        self.emit("app.start", {"name": self.name})

    def on_resume(self) -> None:
        """Called when the application comes to the foreground."""
        self.lifecycle.advance(Phase.RUNNING, self.context)
        current = self.current_activity
        if current is not None:
            current.on_resume()
        self.logger.info(f"MobileApplication '{self.name}' resumed")
        self.emit("app.resume", {"name": self.name})

    def on_pause(self) -> None:
        """Called when the application goes to the background."""
        current = self.current_activity
        if current is not None:
            current.on_pause()
        self.logger.info(f"MobileApplication '{self.name}' paused")
        self.emit("app.pause", {"name": self.name})

    def on_stop(self) -> None:
        """Called when the application is no longer visible."""
        for activity in self._activity_stack:
            activity.on_stop()
        self._running = False
        self.logger.info(f"MobileApplication '{self.name}' stopped")
        self.emit("app.stop", {"name": self.name})

    def on_destroy(self) -> None:
        """Called when the application is being destroyed."""
        for activity in list(self._activity_stack):
            self.finish_activity(activity)
        self._activities.clear()
        self.logger.info(f"MobileApplication '{self.name}' destroyed")
        self.emit("app.destroy", {"name": self.name})

    def on_save_state(self) -> Dict[str, Any]:
        """Save the current application state.

        Returns:
            A dictionary representing the saved state.
        """
        self._saved_state = {
            "activity_stack": [a.id for a in self._activity_stack],
            "activity_states": {
                a.id: a.save_state() for a in self._activities
            },
            "nav_history": self._navigator.history,
        }
        self.emit("app.save_state", {})
        return dict(self._saved_state)

    def on_restore_state(self, state: Dict[str, Any]) -> None:
        """Restore a previously saved application state.

        Args:
            state: The state dictionary from on_save_state.
        """
        self._saved_state = dict(state)
        nav_history = state.get("nav_history", [])
        if nav_history:
            self._navigator.restore_state(nav_history)
        activity_states = state.get("activity_states", {})
        for activity in self._activities:
            if activity.id in activity_states:
                activity.restore_state(activity_states[activity.id])
        self.emit("app.restore_state", {})

    def on_low_memory(self) -> None:
        """Called when the system is running low on memory."""
        self.logger.warning("Low memory warning received")
        for activity in reversed(self._activity_stack):
            if activity.state == ActivityState.KURAHAGARARA:
                self.finish_activity(activity)
        self.emit("app.low_memory", {})

    def on_back_pressed(self) -> bool:
        """Handle the system back button press.

        Returns:
            True if the back press was handled, False otherwise.
        """
        current = self.current_activity
        if current is not None:
            if self._navigator.can_go_back:
                self._navigator.pop()
                self.finish_activity(current)
                return True
        self.emit("app.back_pressed", {})
        return False


# ---------------------------------------------------------------------------
# Internal service stubs
# ---------------------------------------------------------------------------

class _StateManager:
    """Manages application state persistence and restoration."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def save(self, key: str, value: Any) -> None:
        self._data[key] = value

    def load(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def clear(self) -> None:
        self._data.clear()


class _SecurityManager:
    """Manages mobile security policies, encryption, and permissions."""

    def __init__(self) -> None:
        self._policies: Dict[str, Any] = {}

    def set_policy(self, name: str, policy: Any) -> None:
        self._policies[name] = policy

    def check_permission(self, permission: str) -> bool:
        return self._policies.get(permission, False)


class _DatabaseManager:
    """Manages local database connections and operations."""

    def __init__(self) -> None:
        self._connected = False

    def connect(self, connection_string: str) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False


class _NetworkManager:
    """Manages network connectivity monitoring and requests."""

    def __init__(self) -> None:
        self._online = True

    @property
    def is_online(self) -> bool:
        return self._online

    def set_online(self, value: bool) -> None:
        self._online = value


class _MediaManager:
    """Manages media playback, recording, and gallery access."""

    def __init__(self) -> None:
        self._playing = False

    def play(self, uri: str) -> None:
        self._playing = True

    def stop(self) -> None:
        self._playing = False


class _DeviceManager:
    """Provides access to device hardware features."""

    def __init__(self) -> None:
        self._battery_level: float = 100.0

    @property
    def battery_level(self) -> float:
        return self._battery_level


class _AIAssistant:
    """On-device AI inference and assistant capabilities."""

    def __init__(self) -> None:
        self._models: Dict[str, Any] = {}

    def load_model(self, name: str, path: str) -> bool:
        self._models[name] = path
        return True


class _PerformanceMonitor:
    """Monitors application performance metrics."""

    def __init__(self) -> None:
        self._metrics: Dict[str, float] = {}

    def record(self, metric: str, value: float) -> None:
        self._metrics[metric] = value

    def report(self) -> Dict[str, float]:
        return dict(self._metrics)
