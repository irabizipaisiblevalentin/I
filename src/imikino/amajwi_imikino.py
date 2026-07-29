"""amajwi — Audio engine: 3D audio, spatial, streaming, effects, mixing."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import Vector3


class AudioState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    LOADING = "loading"


@dataclass
class AudioClip:
    name: str = ""
    path: str = ""
    duration: float = 0.0
    sample_rate: int = 44100
    channels: int = 2
    format: str = "wav"
    data: Optional[bytes] = None
    loaded: bool = False


@dataclass
class AudioSourceComponent:
    clip: Optional[AudioClip] = None
    volume: float = 1.0
    pitch: float = 1.0
    loop: bool = False
    spatial: bool = True
    min_distance: float = 1.0
    max_distance: float = 50.0
    rolloff: float = 1.0
    pan: float = 0.0
    state: AudioState = AudioState.STOPPED
    position: Vector3 = field(default_factory=Vector3)
    priority: int = 0


@dataclass
class AudioListenerComponent:
    position: Vector3 = field(default_factory=Vector3)
    velocity: Vector3 = field(default_factory=Vector3)
    forward: Vector3 = field(default_factory=lambda: Vector3(0, 0, -1))
    up: Vector3 = field(default_factory=lambda: Vector3(0, 1, 0))
    gain: float = 1.0


class AudioEffect:
    def __init__(self, name: str = "Effect"):
        self.name = name
        self.enabled: bool = True
        self.parameters: Dict[str, float] = {}

    def process(self, samples: List[float]) -> List[float]:
        return samples


class ReverbEffect(AudioEffect):
    def __init__(self):
        super().__init__("reverb")
        self.parameters = {"room_size": 0.5, "damping": 0.5, "wet": 0.3, "dry": 0.7}


class EchoEffect(AudioEffect):
    def __init__(self):
        super().__init__("echo")
        self.parameters = {"delay": 0.3, "decay": 0.5, "wet": 0.3}


class LowPassFilter(AudioEffect):
    def __init__(self):
        super().__init__("lowpass")
        self.parameters = {"cutoff": 1000.0, "resonance": 0.5}


@dataclass
class AudioMixerGroup:
    name: str = ""
    volume: float = 1.0
    mute: bool = False
    solo: bool = False
    effects: List[AudioEffect] = field(default_factory=list)
    children: List[AudioMixerGroup] = field(default_factory=list)


class AudioEngine:
    def __init__(self):
        self.master_volume: float = 1.0
        self.sources: List[AudioSourceComponent] = []
        self.listener: Optional[AudioListenerComponent] = None
        self.clips: Dict[str, AudioClip] = {}
        self.mixer_groups: Dict[str, AudioMixerGroup] = {}
        self._active_sounds: int = 0

    def load_clip(self, path: str, name: Optional[str] = None) -> AudioClip:
        clip = AudioClip(
            name=name or path.split("/")[-1],
            path=path,
            duration=1.0,
            loaded=True,
        )
        self.clips[clip.name] = clip
        return clip

    def play(self, clip_name: str, source: Optional[AudioSourceComponent] = None) -> AudioSourceComponent:
        clip = self.clips.get(clip_name)
        if not clip:
            raise ValueError(f"Audio clip not found: {clip_name}")
        src = source or AudioSourceComponent(clip=clip, state=AudioState.PLAYING)
        self.sources.append(src)
        self._active_sounds += 1
        return src

    def stop(self, source: AudioSourceComponent) -> None:
        source.state = AudioState.STOPPED
        self._active_sounds = max(0, self._active_sounds - 1)

    def stop_all(self) -> None:
        for src in self.sources:
            src.state = AudioState.STOPPED
        self._active_sounds = 0

    def create_mixer_group(self, name: str, parent: Optional[str] = None) -> AudioMixerGroup:
        group = AudioMixerGroup(name=name)
        self.mixer_groups[name] = group
        return group

    def update(self, dt: float) -> None:
        self.sources = [s for s in self.sources if s.state != AudioState.STOPPED]

    @property
    def active_sounds(self) -> int:
        return self._active_sounds

    def summary(self) -> Dict[str, Any]:
        return {
            "clips": len(self.clips),
            "active_sounds": self._active_sounds,
            "mixer_groups": list(self.mixer_groups.keys()),
        }


_audio = AudioEngine()


def get_audio() -> AudioEngine:
    return _audio
