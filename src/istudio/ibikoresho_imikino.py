"""I STUDIO — Game Tools (IMIKINO Integration)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GameAsset:
    name: str
    type: str = "sprite"
    path: str = ""
    width: int = 0
    height: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GameScene:
    name: str
    objects: List[Dict[str, Any]] = field(default_factory=list)
    background: str = ""
    physics: bool = False
    gravity_x: float = 0.0
    gravity_y: float = 9.8

@dataclass
class Animation:
    name: str
    frames: List[str] = field(default_factory=list)
    frame_duration_ms: int = 100
    loop: bool = True


class GameDesigner:
    def __init__(self):
        self._assets: Dict[str, GameAsset] = {}
        self._scenes: Dict[str, GameScene] = {}
        self._animations: Dict[str, Animation] = {}
        self._active_scene: Optional[str] = None

    def add_asset(self, asset: GameAsset) -> str:
        self._assets[asset.name] = asset
        return asset.name

    def get_asset(self, name: str) -> Optional[GameAsset]:
        return self._assets.get(name)

    def list_assets(self) -> List[GameAsset]:
        return list(self._assets.values())

    def remove_asset(self, name: str) -> bool:
        return self._assets.pop(name, None) is not None

    def create_scene(self, name: str, background: str = "", physics: bool = False) -> GameScene:
        scene = GameScene(name=name, background=background, physics=physics)
        self._scenes[name] = scene
        self._active_scene = name
        return scene

    def get_scene(self, name: str) -> Optional[GameScene]:
        return self._scenes.get(name)

    def list_scenes(self) -> List[GameScene]:
        return list(self._scenes.values())

    def remove_scene(self, name: str) -> bool:
        return self._scenes.pop(name, None) is not None

    def add_object_to_scene(self, scene_name: str, obj: Dict[str, Any]) -> bool:
        scene = self._scenes.get(scene_name)
        if not scene:
            return False
        scene.objects.append(obj)
        return True

    def create_animation(self, name: str, frames: List[str], frame_duration_ms: int = 100, loop: bool = True) -> Animation:
        anim = Animation(name=name, frames=frames, frame_duration_ms=frame_duration_ms, loop=loop)
        self._animations[name] = anim
        return anim

    def get_animation(self, name: str) -> Optional[Animation]:
        return self._animations.get(name)

    def generate_scene_code(self, scene_name: str, language: str = "i") -> str:
        scene = self._scenes.get(scene_name)
        if not scene:
            return ""
        code = f"scene = create_scene(\"{scene.name}\")\n"
        if scene.background:
            code += f"scene.set_background(\"{scene.background}\")\n"
        if scene.physics:
            code += f"scene.enable_physics(gravity_x={scene.gravity_x}, gravity_y={scene.gravity_y})\n"
        for obj in scene.objects:
            code += f"scene.add_object({obj})\n"
        return code
