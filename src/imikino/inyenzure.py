"""inyenzure — AI integration: NPC intelligence, navmesh, pathfinding, behaviour trees, dialogue."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, Vector2
from .imiyoborere import Component, Entity, System


class AIState(str, Enum):
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    SEARCH = "search"
    TALK = "talk"
    GUARD = "guard"
    FOLLOW = "follow"
    CUSTOM = "custom"


@dataclass
class AIComponent(Component):
    state: AIState = AIState.IDLE
    perception_range: float = 10.0
    field_of_view: float = 90.0
    detection_interval: float = 0.5
    last_detection: float = 0.0
    alert_level: float = 0.0
    target_entity: str = ""
    home_position: Vector3 = field(default_factory=Vector3)
    patrol_points: List[Vector3] = field(default_factory=list)
    current_patrol_index: int = 0
    custom_data: Dict[str, Any] = field(default_factory=dict)
    personality: Dict[str, float] = field(default_factory=lambda: {
        "aggression": 0.5, "bravery": 0.5, "curiosity": 0.5, "sociability": 0.5,
    })


@dataclass
class NavigationMesh:
    vertices: List[Vector3] = field(default_factory=list)
    triangles: List[int] = field(default_factory=list)

    def find_path(self, start: Vector3, end: Vector3) -> List[Vector3]:
        return [start, end]


@dataclass
class NavMeshAgentComponent(Component):
    nav_mesh: Optional[NavigationMesh] = None
    destination: Optional[Vector3] = None
    speed: float = 5.0
    acceleration: float = 10.0
    stopping_distance: float = 0.5
    path: List[Vector3] = field(default_factory=list)
    current_path_index: int = 0
    velocity: Vector3 = field(default_factory=Vector3)
    avoidance_radius: float = 1.0
    obstacle_layer: int = 1
    auto_braking: bool = True
    reached: bool = False
    path_recalculated: bool = False

    def set_destination(self, destination: Vector3) -> None:
        self.destination = destination
        self.reached = False
        self.current_path_index = 0

    def stop(self) -> None:
        self.destination = None
        self.velocity = Vector3()


@dataclass
class BehaviourTreeNode:
    name: str = "Node"
    children: List[BehaviourTreeNode] = field(default_factory=list)

    def execute(self, entity: Entity, dt: float) -> str:
        return "success"


class BehaviourTree:
    def __init__(self, root: Optional[BehaviourTreeNode] = None):
        self.root = root
        self.blackboard: Dict[str, Any] = {}

    def execute(self, entity: Entity, dt: float) -> str:
        if self.root:
            return self.root.execute(entity, dt)
        return "failure"

    def set_value(self, key: str, value: Any) -> None:
        self.blackboard[key] = value

    def get_value(self, key: str, default: Any = None) -> Any:
        return self.blackboard.get(key, default)


class SelectorNode(BehaviourTreeNode):
    def execute(self, entity: Entity, dt: float) -> str:
        for child in self.children:
            result = child.execute(entity, dt)
            if result == "success":
                return "success"
        return "failure"


class SequenceNode(BehaviourTreeNode):
    def execute(self, entity: Entity, dt: float) -> str:
        for child in self.children:
            result = child.execute(entity, dt)
            if result == "failure":
                return "failure"
        return "success"


class ConditionNode(BehaviourTreeNode):
    def __init__(self, name: str = "Condition",
                 condition_fn: Optional[Callable[[Entity], bool]] = None):
        super().__init__(name=name)
        self.condition_fn = condition_fn

    def execute(self, entity: Entity, dt: float) -> str:
        if self.condition_fn and self.condition_fn(entity):
            return "success"
        return "failure"


class ActionNode(BehaviourTreeNode):
    def __init__(self, name: str = "Action",
                 action_fn: Optional[Callable[[Entity, float], str]] = None):
        super().__init__(name=name)
        self.action_fn = action_fn

    def execute(self, entity: Entity, dt: float) -> str:
        if self.action_fn:
            return self.action_fn(entity, dt)
        return "failure"


class DialogueNode:
    def __init__(self, text: str = "",
                 responses: Optional[Dict[str, DialogueNode]] = None):
        self.text = text
        self.responses = responses or {}
        self.on_enter: Optional[Callable] = None
        self.on_exit: Optional[Callable] = None


class DialogueSystem:
    def __init__(self):
        self.dialogues: Dict[str, DialogueNode] = {}
        self.active_dialogue: Optional[str] = None
        self.current_node: Optional[DialogueNode] = None

    def register(self, name: str, root: DialogueNode) -> None:
        self.dialogues[name] = root

    def start(self, name: str) -> Optional[DialogueNode]:
        dialogue = self.dialogues.get(name)
        if dialogue:
            self.active_dialogue = name
            self.current_node = dialogue
            if dialogue.on_enter:
                dialogue.on_enter()
            return dialogue
        return None

    def respond(self, choice: str) -> Optional[DialogueNode]:
        if self.current_node and choice in self.current_node.responses:
            if self.current_node.on_exit:
                self.current_node.on_exit()
            self.current_node = self.current_node.responses[choice]
            if self.current_node.on_enter:
                self.current_node.on_enter()
            return self.current_node
        return None

    def end(self) -> None:
        self.active_dialogue = None
        self.current_node = None


class AISystem(System):
    def __init__(self):
        super().__init__()
        self.ai_entities: Dict[str, AIComponent] = {}
        self.dialogue = DialogueSystem()
        self.behaviour_trees: Dict[str, BehaviourTree] = {}

    def on_entity_added(self, entity: Entity) -> None:
        ai = entity.get(AIComponent)
        if ai:
            self.ai_entities[entity.id] = ai

    def on_entity_removed(self, entity: Entity) -> None:
        self.ai_entities.pop(entity.id, None)

    def register_behaviour_tree(self, entity_id: str, tree: BehaviourTree) -> None:
        self.behaviour_trees[entity_id] = tree

    def update(self, dt: float) -> None:
        import time
        now = time.time()
        for eid, ai in list(self.ai_entities.items()):
            entity = None
            for e in self._entities:
                if e.id == eid:
                    entity = e
                    break
            if not entity:
                continue
            if now - ai.last_detection >= ai.detection_interval:
                ai.last_detection = now
                self._update_perception(entity, ai, dt)
            tree = self.behaviour_trees.get(eid)
            if tree:
                tree.execute(entity, dt)

    def _update_perception(self, entity: Entity, ai: AIComponent, dt: float) -> None:
        pass


_ai_system = AISystem()


def get_ai() -> AISystem:
    return _ai_system
