"""ikorwa — Core engine: scene graph, game loop, application lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Clock, Transform, Vector3, Quaternion, Color
from .imiyoborere import World, Entity, Component, System, generate_entity_id


@dataclass
class TransformComponent(Component):
    transform: Transform = field(default_factory=Transform)
    parent_id: str = ""
    children_ids: List[str] = field(default_factory=list)


@dataclass
class TagComponent(Component):
    tags: List[str] = field(default_factory=list)


@dataclass
class NameComponent(Component):
    name: str = ""


class SceneNode:
    def __init__(self, name: str = "Node"):
        self.name = name
        self.entity_id: str = ""
        self.children: List[SceneNode] = []

    def add_child(self, child: SceneNode) -> None:
        self.children.append(child)

    def find(self, name: str) -> Optional[SceneNode]:
        if self.name == name:
            return self
        for child in self.children:
            result = child.find(name)
            if result:
                return result
        return None

    def traverse(self, fn: Callable[[SceneNode], None]) -> None:
        fn(self)
        for child in self.children:
            child.traverse(fn)


class Scene:
    def __init__(self, name: str = "Untitled"):
        self.name = name
        self.world = World()
        self.root = SceneNode("root")
        self.active: bool = True
        self.clear_color: Color = Color(0.1, 0.1, 0.15, 1.0)

    def create_entity(self, name: str = "Entity",
                      parent: Optional[SceneNode] = None) -> Entity:
        entity = self.world.create_entity(name=name)
        entity.add(TransformComponent())
        entity.add(NameComponent(name=name))
        node = SceneNode(name)
        node.entity_id = entity.id
        (parent or self.root).add_child(node)
        return entity

    def find_entity(self, name: str) -> Optional[Entity]:
        node = self.root.find(name)
        if node and node.entity_id:
            return self.world.get_entity(node.entity_id)
        return None

    def get_transform(self, entity: Entity) -> Transform:
        tc = entity.get(TransformComponent)
        return tc.transform if tc else Transform()

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.world.update(dt)

    def render(self) -> None:
        if not self.active:
            return
        self.world.render()


class Layer:
    def __init__(self, name: str = "Layer"):
        self.name = name
        self.enabled: bool = True
        self.on_create: Optional[Callable] = None
        self.on_update: Optional[Callable[[float], None]] = None
        self.on_render: Optional[Callable] = None
        self.on_gui: Optional[Callable] = None

    def create(self) -> None:
        if self.on_create:
            self.on_create()

    def update(self, dt: float) -> None:
        if self.enabled and self.on_update:
            self.on_update(dt)

    def render(self) -> None:
        if self.enabled and self.on_render:
            self.on_render()

    def gui(self) -> None:
        if self.enabled and self.on_gui:
            self.on_gui()


@dataclass
class EngineConfig:
    title: str = "IMIKINO Engine"
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    vsync: bool = True
    max_fps: int = 0
    target_dt: float = 1.0 / 60.0
    asset_dir: str = "./assets"
    plugin_dirs: List[str] = field(default_factory=list)


class Engine:
    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self.clock = Clock()
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        self.layers: List[Layer] = []
        self._running: bool = False
        self._plugins: Dict[str, Any] = {}
        self._hooks: Dict[str, List[Callable]] = {}

    def create_scene(self, name: str = "Scene") -> Scene:
        scene = Scene(name)
        self.scenes[name] = scene
        return scene

    def load_scene(self, name: str) -> bool:
        if name in self.scenes:
            self.active_scene = self.scenes[name]
            return True
        return False

    def push_layer(self, layer: Layer) -> Layer:
        self.layers.append(layer)
        layer.create()
        return layer

    def register_plugin(self, name: str, plugin: Any) -> None:
        self._plugins[name] = plugin
        if hasattr(plugin, 'on_register'):
            plugin.on_register(self)

    def get_plugin(self, name: str) -> Optional[Any]:
        return self._plugins.get(name)

    def register_hook(self, event: str, handler: Callable) -> None:
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(handler)

    def _trigger(self, event: str, **kwargs: Any) -> None:
        for handler in self._hooks.get(event, []):
            try:
                handler(**kwargs)
            except Exception:
                pass

    def start(self) -> None:
        self._running = True
        self._trigger("engine_start")
        for layer in self.layers:
            layer.create()

    def stop(self) -> None:
        self._running = False
        self._trigger("engine_stop")

    def step(self) -> float:
        dt = self.clock.tick()
        if self.config.max_fps > 0:
            target = 1.0 / self.config.max_fps
            if dt < target:
                import time
                time.sleep(target - dt)
                dt = self.clock.tick()

        self._trigger("pre_update", dt=dt)
        if self.active_scene:
            self.active_scene.update(dt)
        for layer in self.layers:
            layer.update(dt)
        self._trigger("post_update", dt=dt)
        return dt

    def render_frame(self) -> None:
        self._trigger("pre_render")
        if self.active_scene:
            self.active_scene.render()
        for layer in self.layers:
            layer.render()
        for layer in self.layers:
            layer.gui()
        self._trigger("post_render")

    def run(self) -> None:
        self.start()
        while self._running:
            self.step()
            self.render_frame()
        self._cleanup()

    def _cleanup(self) -> None:
        self._trigger("engine_cleanup")
        self.scenes.clear()

    @property
    def fps(self) -> float:
        return self.clock.fps

    @property
    def delta(self) -> float:
        return self.clock.delta

    def summary(self) -> Dict[str, Any]:
        return {
            "title": self.config.title,
            "resolution": f"{self.config.width}x{self.config.height}",
            "fps": self.fps,
            "scenes": list(self.scenes.keys()),
            "active_scene": self.active_scene.name if self.active_scene else None,
            "layers": len(self.layers),
            "plugins": list(self._plugins.keys()),
            "entities": len(self.active_scene.world.entities) if self.active_scene else 0,
        }


_global_engine: Optional[Engine] = None


def get_engine() -> Engine:
    global _global_engine
    if _global_engine is None:
        _global_engine = Engine()
    return _global_engine
