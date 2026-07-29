"""inyandikwa — Input system: keyboard, mouse, touch, game controller, VR."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable

from .ibikoreshingiro import Vector2, Vector3


class InputAction(str, Enum):
    PRESSED = "pressed"
    RELEASED = "released"
    HELD = "held"
    DOUBLE_TAP = "double_tap"


class MouseButton(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    X1 = "x1"
    X2 = "x2"


class GamepadButton(str, Enum):
    A = "a"
    B = "b"
    X = "x"
    Y = "y"
    LB = "left_bumper"
    RB = "right_bumper"
    LT = "left_trigger"
    RT = "right_trigger"
    START = "start"
    SELECT = "select"
    DPAD_UP = "dpad_up"
    DPAD_DOWN = "dpad_down"
    DPAD_LEFT = "dpad_left"
    DPAD_RIGHT = "dpad_right"
    L3 = "left_stick_click"
    R3 = "right_stick_click"


class TouchPhase(str, Enum):
    BEGAN = "began"
    MOVED = "moved"
    STATIONARY = "stationary"
    ENDED = "ended"
    CANCELLED = "cancelled"


@dataclass
class Touch:
    id: int = 0
    position: Vector2 = field(default_factory=Vector2)
    delta: Vector2 = field(default_factory=Vector2)
    pressure: float = 1.0
    phase: TouchPhase = TouchPhase.BEGAN


@dataclass
class KeyState:
    down: bool = False
    pressed: bool = False
    released: bool = False
    double_tap: bool = False
    hold_time: float = 0.0


@dataclass
class GamepadState:
    connected: bool = False
    buttons: Dict[str, bool] = field(default_factory=dict)
    left_stick: Vector2 = field(default_factory=Vector2)
    right_stick: Vector2 = field(default_factory=Vector2)
    left_trigger: float = 0.0
    right_trigger: float = 0.0


@dataclass
class InputActionBinding:
    name: str = ""
    keys: List[str] = field(default_factory=list)
    mouse_buttons: List[str] = field(default_factory=list)
    gamepad_buttons: List[str] = field(default_factory=list)
    axis: str = ""


class InputSystem:
    def __init__(self):
        self._keys: Dict[str, KeyState] = {}
        self._mouse_position: Vector2 = Vector2()
        self._mouse_delta: Vector2 = Vector2()
        self._mouse_buttons: Dict[str, bool] = {}
        self._mouse_scroll: Vector2 = Vector2()
        self._touches: List[Touch] = []
        self._gamepads: Dict[int, GamepadState] = {}
        self._actions: Dict[str, InputActionBinding] = {}
        self._action_states: Dict[str, bool] = {}
        self._text_input: str = ""
        self._last_key: str = ""
        self._last_key_time: float = 0.0

    def press_key(self, key: str) -> None:
        state = self._keys.setdefault(key, KeyState())
        if not state.down:
            state.pressed = True
            import time
            now = time.time()
            if key == self._last_key and now - self._last_key_time < 0.3:
                state.double_tap = True
            self._last_key = key
            self._last_key_time = now
        state.down = True

    def release_key(self, key: str) -> None:
        state = self._keys.get(key)
        if state:
            state.released = True
            state.down = False

    def is_key_down(self, key: str) -> bool:
        state = self._keys.get(key)
        return state.down if state else False

    def is_key_pressed(self, key: str) -> bool:
        state = self._keys.get(key)
        return state.pressed if state else False

    def is_key_released(self, key: str) -> bool:
        state = self._keys.get(key)
        return state.released if state else False

    def set_mouse_position(self, x: float, y: float) -> None:
        self._mouse_delta = Vector2(x - self._mouse_position.x, y - self._mouse_position.y)
        self._mouse_position = Vector2(x, y)

    def set_mouse_button(self, button: str, down: bool) -> None:
        self._mouse_buttons[button] = down

    def is_mouse_down(self, button: str = "left") -> bool:
        return self._mouse_buttons.get(button, False)

    def set_mouse_scroll(self, x: float, y: float) -> None:
        self._mouse_scroll = Vector2(x, y)

    def add_touch(self, touch: Touch) -> None:
        existing = [t for t in self._touches if t.id == touch.id]
        if existing:
            self._touches.remove(existing[0])
        self._touches.append(touch)

    def get_touches(self) -> List[Touch]:
        return list(self._touches)

    def get_gamepad(self, index: int = 0) -> Optional[GamepadState]:
        return self._gamepads.get(index)

    def register_action(self, binding: InputActionBinding) -> None:
        self._actions[binding.name] = binding
        self._action_states[binding.name] = False

    def get_action(self, name: str) -> bool:
        return self._action_states.get(name, False)

    def get_action_down(self, name: str) -> bool:
        binding = self._actions.get(name)
        if not binding:
            return False
        for key in binding.keys:
            if self.is_key_pressed(key):
                return True
        for btn in binding.mouse_buttons:
            if btn in self._mouse_buttons and self._mouse_buttons[btn]:
                return True
        return False

    def _update_actions(self) -> None:
        for name, binding in self._actions.items():
            down = False
            for key in binding.keys:
                if self.is_key_down(key):
                    down = True
                    break
            for btn in binding.mouse_buttons:
                if self._mouse_buttons.get(btn, False):
                    down = True
                    break
            self._action_states[name] = down

    def end_frame(self) -> None:
        for key, state in self._keys.items():
            state.pressed = False
            state.released = False
            state.double_tap = False
            if state.down:
                state.hold_time += 0.016
        self._mouse_delta = Vector2()
        self._mouse_scroll = Vector2()
        self._touches = [t for t in self._touches if t.phase != TouchPhase.ENDED]
        self._text_input = ""
        self._update_actions()

    @property
    def mouse_position(self) -> Vector2:
        return self._mouse_position

    @property
    def mouse_delta(self) -> Vector2:
        return self._mouse_delta

    @property
    def mouse_scroll(self) -> Vector2:
        return self._mouse_scroll

    @property
    def text_input(self) -> str:
        return self._text_input


_input = InputSystem()


def get_input() -> InputSystem:
    return _input
