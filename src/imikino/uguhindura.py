"""uguhindura — Editor: scene, material, animation, terrain, particle, UI, audio, profiler, debugger."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector2, Vector3, Color
from .ikorwa import Scene, Engine, Layer
from .ishushanyo import Material, Mesh, CameraComponent, LightComponent


class EditorTool(str, Enum):
    SELECT = "select"
    MOVE = "move"
    ROTATE = "rotate"
    SCALE = "scale"
    PAINT = "paint"
    TERRAIN = "terrain"
    PARTICLE = "particle"


class EditorWindow(str, Enum):
    SCENE = "scene"
    GAME = "game"
    HIERARCHY = "hierarchy"
    INSPECTOR = "inspector"
    PROJECT = "project"
    CONSOLE = "console"
    ANIMATION = "animation"
    MATERIAL = "material"
    AUDIO = "audio"
    PROFILER = "profiler"
    TERRAIN = "terrain"
    PREFAB = "prefab"


@dataclass
class EditorSelection:
    entity_ids: List[str] = field(default_factory=list)
    asset_guids: List[str] = field(default_factory=list)
    last_selected: str = ""


@dataclass
class EditorViewport:
    position: Vector2 = field(default_factory=Vector2)
    size: Vector2 = field(default_factory=lambda: Vector2(1280, 720))
    camera_position: Vector3 = field(default_factory=lambda: Vector3(0, 5, 10))
    camera_target: Vector3 = field(default_factory=Vector3)
    zoom: float = 1.0
    grid_enabled: bool = True
    snapping_enabled: bool = True
    snap_value: float = 0.5


class Editor:
    def __init__(self):
        self.active_tool: EditorTool = EditorTool.SELECT
        self.selection: EditorSelection = EditorSelection()
        self.viewport: EditorViewport = EditorViewport()
        self.open_windows: Dict[str, bool] = {
            w.value: True for w in EditorWindow
        }
        self.scene: Optional[Scene] = None
        self.drag_active: bool = False
        self.drag_start: Vector2 = Vector2()
        self.gizmo_enabled: bool = True
        self.snap_to_grid: bool = True
        self._history: List[Dict[str, Any]] = []
        self._history_index: int = -1
        self._copy_buffer: Dict[str, Any] = {}

    def select_entity(self, entity_id: str) -> None:
        if entity_id not in self.selection.entity_ids:
            self.selection.last_selected = entity_id
            self.selection.entity_ids = [entity_id]

    def deselect_all(self) -> None:
        self.selection.entity_ids.clear()
        self.selection.last_selected = ""

    def is_selected(self, entity_id: str) -> bool:
        return entity_id in self.selection.entity_ids

    def push_undo(self, state: Dict[str, Any]) -> None:
        self._history = self._history[:self._history_index + 1]
        self._history.append(state)
        self._history_index = len(self._history) - 1
        if len(self._history) > 100:
            self._history.pop(0)
            self._history_index -= 1

    def undo(self) -> Optional[Dict[str, Any]]:
        if self._history_index >= 0:
            state = self._history[self._history_index]
            self._history_index -= 1
            return state
        return None

    def redo(self) -> Optional[Dict[str, Any]]:
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            return self._history[self._history_index]
        return None

    def copy_selection(self) -> None:
        self._copy_buffer = {"entity_ids": list(self.selection.entity_ids)}

    def paste(self) -> List[str]:
        return []

    def duplicate_selection(self) -> List[str]:
        return []

    def toggle_window(self, window: str) -> None:
        self.open_windows[window] = not self.open_windows.get(window, True)

    def is_window_open(self, window: str) -> bool:
        return self.open_windows.get(window, False)


class EditorLayer(Layer):
    def __init__(self, editor: Optional[Editor] = None):
        super().__init__("Editor")
        self.editor = editor or Editor()

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        pass

    def gui(self) -> None:
        pass


_editor = Editor()


def get_editor() -> Editor:
    return _editor
