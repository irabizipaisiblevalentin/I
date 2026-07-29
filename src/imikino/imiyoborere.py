"""imiyoborere — Entity Component System (ECS)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Type, TypeVar

from .ibikoreshingiro import generate_entity_id

T = TypeVar("T")


class Component:
    entity_id: str = ""

    def __post_init__(self) -> None:
        pass


@dataclass
class Entity:
    id: str = ""
    name: str = "Entity"
    active: bool = True
    components: Dict[str, Component] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = generate_entity_id()

    def add(self, component: Component) -> Component:
        component.entity_id = self.id
        key = type(component).__name__
        self.components[key] = component
        return component

    def get(self, component_type: Type[T]) -> Optional[T]:
        for comp in self.components.values():
            if isinstance(comp, component_type):
                return comp
        return None

    def has(self, component_type: Type) -> bool:
        return self.get(component_type) is not None

    def remove(self, component_type: Type) -> bool:
        key = component_type.__name__
        if key in self.components:
            del self.components[key]
            return True
        return False

    def add_tag(self, tag: str) -> None:
        self.tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


class System:
    priority: int = 0
    _entities: List[Entity] = []

    def start(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        pass

    def on_entity_added(self, entity: Entity) -> None:
        pass

    def on_entity_removed(self, entity: Entity) -> None:
        pass


class EntityQuery:
    def __init__(self, world: World, required: Optional[List[Type]] = None,
                 excluded: Optional[List[Type]] = None):
        self.world = world
        self.required = required or []
        self.excluded = excluded or []

    def execute(self) -> Generator[Entity, None, None]:
        for entity in self.world.entities.values():
            if not entity.active:
                continue
            if self.required:
                if not all(entity.has(t) for t in self.required):
                    continue
            if self.excluded:
                if any(entity.has(t) for t in self.excluded):
                    continue
            yield entity

    def first(self) -> Optional[Entity]:
        for e in self.execute():
            return e
        return None

    def count(self) -> int:
        return sum(1 for _ in self.execute())


class World:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.systems: List[System] = []

    def create_entity(self, name: str = "Entity") -> Entity:
        entity = Entity(name=name)
        self.entities[entity.id] = entity
        for system in self.systems:
            system.on_entity_added(entity)
        return entity

    def destroy_entity(self, entity_id: str) -> bool:
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            for system in self.systems:
                system.on_entity_removed(entity)
            del self.entities[entity_id]
            return True
        return False

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def find_by_tag(self, tag: str) -> List[Entity]:
        return [e for e in self.entities.values() if e.has_tag(tag)]

    def find_by_name(self, name: str) -> List[Entity]:
        return [e for e in self.entities.values() if e.name == name]

    def add_system(self, system: System) -> System:
        self.systems.append(system)
        self.systems.sort(key=lambda s: s.priority)
        system.start()
        return system

    def remove_system(self, system_type: Type) -> bool:
        for i, s in enumerate(self.systems):
            if isinstance(s, system_type):
                self.systems.pop(i)
                return True
        return False

    def get_system(self, system_type: Type) -> Optional[System]:
        for s in self.systems:
            if isinstance(s, system_type):
                return s
        return None

    def query(self, required: Optional[List[Type]] = None,
              excluded: Optional[List[Type]] = None) -> EntityQuery:
        return EntityQuery(self, required, excluded)

    def update(self, dt: float) -> None:
        for system in self.systems:
            if hasattr(system, 'update'):
                system.update(dt)

    def render(self) -> None:
        for system in self.systems:
            if hasattr(system, 'render'):
                system.render()

    def clear(self) -> None:
        self.entities.clear()
        self.systems.clear()
