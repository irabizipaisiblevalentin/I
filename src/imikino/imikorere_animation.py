"""imikorere — Animation system: skeleton, blend trees, IK, morph targets, timeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, Quaternion, Transform, lerp, smoothstep


class AnimationWrapMode(str, Enum):
    ONCE = "once"
    LOOP = "loop"
    PING_PONG = "ping_pong"
    CLAMP = "clamp"


@dataclass
class Keyframe:
    time: float = 0.0
    value: float = 0.0
    in_tangent: float = 0.0
    out_tangent: float = 0.0


@dataclass
class AnimationCurve:
    keyframes: List[Keyframe] = field(default_factory=list)
    post_wrap: AnimationWrapMode = AnimationWrapMode.CLAMP
    pre_wrap: AnimationWrapMode = AnimationWrapMode.CLAMP

    def evaluate(self, time: float) -> float:
        if not self.keyframes:
            return 0.0
        if time <= self.keyframes[0].time:
            return self.keyframes[0].value
        if time >= self.keyframes[-1].time:
            if self.post_wrap == AnimationWrapMode.LOOP:
                time = time % self.keyframes[-1].time
            elif self.post_wrap == AnimationWrapMode.CLAMP:
                return self.keyframes[-1].value
        for i in range(len(self.keyframes) - 1):
            k0 = self.keyframes[i]
            k1 = self.keyframes[i + 1]
            if k0.time <= time <= k1.time:
                t = (time - k0.time) / (k1.time - k0.time)
                return lerp(k0.value, k1.value, t)
        return self.keyframes[-1].value


@dataclass
class Bone:
    name: str = ""
    parent_index: int = -1
    local_transform: Transform = field(default_factory=Transform)
    world_transform: Transform = field(default_factory=Transform)


@dataclass
class Skeleton:
    bones: List[Bone] = field(default_factory=list)
    root_bone: int = -1

    def add_bone(self, name: str, parent: int = -1) -> int:
        idx = len(self.bones)
        self.bones.append(Bone(name=name, parent_index=parent))
        if parent < 0:
            self.root_bone = idx
        return idx

    def get_bone(self, name: str) -> Optional[int]:
        for i, b in enumerate(self.bones):
            if b.name == name:
                return i
        return None


@dataclass
class AnimationClip:
    name: str = ""
    duration: float = 1.0
    curves: Dict[str, Dict[str, AnimationCurve]] = field(default_factory=dict)
    wrap_mode: AnimationWrapMode = AnimationWrapMode.LOOP
    events: List[Tuple[float, str]] = field(default_factory=list)
    speed: float = 1.0


@dataclass
class AnimationState:
    clip: Optional[AnimationClip] = None
    time: float = 0.0
    speed: float = 1.0
    weight: float = 1.0
    playing: bool = True
    wrap_mode: AnimationWrapMode = AnimationWrapMode.LOOP
    on_finish: Optional[Callable] = None


@dataclass
class AnimatorComponent:
    states: Dict[str, AnimationState] = field(default_factory=dict)
    current_state: str = ""
    parameters: Dict[str, float] = field(default_factory=dict)
    skeleton: Optional[Skeleton] = None

    def add_state(self, name: str, clip: AnimationClip) -> None:
        self.states[name] = AnimationState(clip=clip)
        if not self.current_state:
            self.current_state = name

    def play(self, name: str, cross_fade: float = 0.0) -> bool:
        if name in self.states:
            self.current_state = name
            self.states[name].playing = True
            self.states[name].time = 0.0
            return True
        return False

    def set_parameter(self, name: str, value: float) -> None:
        self.parameters[name] = value

    def get_parameter(self, name: str) -> float:
        return self.parameters.get(name, 0.0)


@dataclass
class BlendTreeNode:
    clip_name: str = ""
    weight: float = 1.0
    threshold: float = 0.0
    children: List[BlendTreeNode] = field(default_factory=list)


@dataclass
class BlendTree:
    parameter: str = ""
    nodes: List[BlendTreeNode] = field(default_factory=list)
    blend_type: str = "1d"
    min_threshold: float = 0.0
    max_threshold: float = 1.0

    def evaluate(self, param_value: float) -> Dict[str, float]:
        weights: Dict[str, float] = {}
        total = 0.0
        for node in self.nodes:
            dist = abs(param_value - node.threshold)
            w = 1.0 / (dist + 0.001)
            weights[node.clip_name] = w
            total += w
        if total > 0:
            for k in weights:
                weights[k] /= total
        return weights


@dataclass
class InverseKinematics:
    target_position: Vector3 = field(default_factory=Vector3)
    bone_chain: List[int] = field(default_factory=list)
    iterations: int = 10
    tolerance: float = 0.01
    enabled: bool = False


@dataclass
class TimelineTrack:
    name: str = ""
    clips: List[Tuple[float, AnimationClip]] = field(default_factory=list)


@dataclass
class Timeline:
    tracks: List[TimelineTrack] = field(default_factory=list)
    time: float = 0.0
    duration: float = 0.0
    playing: bool = False


class AnimationSystem:
    def __init__(self):
        self.clips: Dict[str, AnimationClip] = {}
        self.animators: List[AnimatorComponent] = []
        self.timelines: List[Timeline] = []

    def create_clip(self, name: str, duration: float = 1.0) -> AnimationClip:
        clip = AnimationClip(name=name, duration=duration)
        self.clips[name] = clip
        return clip

    def register_animator(self, animator: AnimatorComponent) -> None:
        self.animators.append(animator)

    def update(self, dt: float) -> None:
        for animator in self.animators:
            state = animator.states.get(animator.current_state)
            if not state or not state.playing:
                continue
            state.time += dt * state.speed * (state.clip.speed if state.clip else 1.0)
            if state.clip:
                if state.time >= state.clip.duration:
                    if state.wrap_mode == AnimationWrapMode.LOOP:
                        state.time = state.time % state.clip.duration
                    elif state.wrap_mode == AnimationWrapMode.ONCE:
                        state.time = state.clip.duration
                        state.playing = False
                        if state.on_finish:
                            state.on_finish()

    def summary(self) -> Dict[str, Any]:
        return {
            "clips": len(self.clips),
            "animators": len(self.animators),
            "timelines": len(self.timelines),
        }


_animation = AnimationSystem()


def get_animation() -> AnimationSystem:
    return _animation
