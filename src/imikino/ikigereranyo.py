"""ikigereranyo — Simulation Core Framework: simulation engine, time management, scenarios, recording."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, Vector2, Quaternion, Color, Clock, clamp, lerp, smoothstep
from .imiyoborere import World, Entity, Component, System, EntityQuery


class SimulationMode(str, Enum):
    REALTIME = "realtime"
    STEPPED = "stepped"
    SCALED = "scaled"
    FIXED_STEP = "fixed_step"
    CATCH_UP = "catch_up"


class TimeUnit(str, Enum):
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    TICKS = "ticks"


@dataclass
class SimulationClock:
    mode: SimulationMode = SimulationMode.REALTIME
    time_scale: float = 1.0
    fixed_dt: float = 1.0 / 60.0
    max_catch_up: float = 0.1
    paused: bool = False
    _real_elapsed: float = 0.0
    _sim_elapsed: float = 0.0
    _step_count: int = 0
    _last_real: float = 0.0

    def start(self) -> None:
        self._last_real = time.perf_counter()
        self._real_elapsed = 0.0
        self._sim_elapsed = 0.0
        self._step_count = 0

    def tick(self) -> float:
        if self.paused:
            return 0.0
        now = time.perf_counter()
        real_dt = now - self._last_real
        self._last_real = now
        self._real_elapsed += real_dt

        if self.mode == SimulationMode.REALTIME:
            dt = real_dt * self.time_scale
        elif self.mode == SimulationMode.FIXED_STEP:
            dt = self.fixed_dt
        elif self.mode == SimulationMode.SCALED:
            dt = real_dt * self.time_scale
        elif self.mode == SimulationMode.CATCH_UP:
            dt = min(real_dt * self.time_scale, self.max_catch_up)
        elif self.mode == SimulationMode.STEPPED:
            dt = 0.0
        else:
            dt = real_dt

        self._sim_elapsed += dt
        self._step_count += 1
        return dt

    def step_once(self, dt: float = 0.016) -> float:
        self._sim_elapsed += dt
        self._step_count += 1
        return dt

    @property
    def elapsed(self) -> float:
        return self._sim_elapsed

    @property
    def steps(self) -> int:
        return self._step_count

    def reset(self) -> None:
        self._real_elapsed = 0.0
        self._sim_elapsed = 0.0
        self._step_count = 0
        self._last_real = time.perf_counter()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "time_scale": self.time_scale,
            "elapsed": self._sim_elapsed,
            "steps": self._step_count,
            "paused": self.paused,
        }


class SimulationEvent:
    def __init__(self, event_type: str, data: Optional[Dict[str, Any]] = None,
                 timestamp: float = 0.0):
        self.type = event_type
        self.data = data or {}
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "data": self.data, "timestamp": self.timestamp}


@dataclass
class SimulationRecorder:
    recording: bool = False
    events: List[SimulationEvent] = field(default_factory=list)
    _start_time: float = 0.0

    def start(self) -> None:
        self.recording = True
        self.events.clear()
        self._start_time = time.perf_counter()

    def stop(self) -> List[SimulationEvent]:
        self.recording = False
        return self.events

    def record(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        if self.recording:
            self.events.append(SimulationEvent(
                event_type, data, time.perf_counter() - self._start_time
            ))

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in self.events], f, indent=2)

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.events = [SimulationEvent(**d) for d in data]

    def replay(self, callback: Callable[[SimulationEvent], None]) -> None:
        for event in sorted(self.events, key=lambda e: e.timestamp):
            callback(event)


@dataclass
class ScenarioParameter:
    name: str = ""
    value: Any = None
    param_type: str = "float"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""


class Scenario:
    def __init__(self, name: str = "Scenario"):
        self.name = name
        self.description: str = ""
        self.parameters: Dict[str, ScenarioParameter] = {}
        self.setup_fn: Optional[Callable] = None
        self.teardown_fn: Optional[Callable] = None
        self.conditions: List[Callable[[], bool]] = []
        self.metadata: Dict[str, Any] = {}

    def add_parameter(self, name: str, default: Any = None,
                      param_type: str = "float",
                      min_v: Optional[float] = None,
                      max_v: Optional[float] = None,
                      description: str = "") -> ScenarioParameter:
        param = ScenarioParameter(
            name=name, value=default, param_type=param_type,
            min_value=min_v, max_value=max_v, description=description,
        )
        self.parameters[name] = param
        return param

    def set_parameter(self, name: str, value: Any) -> None:
        if name in self.parameters:
            self.parameters[name].value = value

    def get_parameter(self, name: str, default: Any = None) -> Any:
        param = self.parameters.get(name)
        return param.value if param else default

    def add_condition(self, condition: Callable[[], bool]) -> None:
        self.conditions.append(condition)

    def check_completion(self) -> bool:
        return all(c() for c in self.conditions)

    def setup(self, scene: Any) -> None:
        if self.setup_fn:
            self.setup_fn(scene)

    def teardown(self) -> None:
        if self.teardown_fn:
            self.teardown_fn()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {k: v.value for k, v in self.parameters.items()},
            "metadata": self.metadata,
        }


@dataclass
class SimulationResult:
    name: str = ""
    success: bool = False
    duration: float = 0.0
    steps: int = 0
    metrics: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "success": self.success,
            "duration": self.duration,
            "steps": self.steps,
            "metrics": self.metrics,
            "errors": self.errors,
        }


class Simulator:
    def __init__(self, name: str = "Simulator"):
        self.name = name
        self.clock = SimulationClock()
        self.world = World()
        self.scenario: Optional[Scenario] = None
        self.recorder = SimulationRecorder()
        self.results: List[SimulationResult] = []
        self._systems: List[System] = []
        self._hooks: Dict[str, List[Callable]] = {}
        self._running: bool = False
        self._deterministic: bool = False
        self._seed: int = 0

    def add_system(self, system: System) -> System:
        self._systems.append(system)
        return system

    def set_deterministic(self, enabled: bool = True, seed: int = 42) -> None:
        self._deterministic = enabled
        self._seed = seed
        if enabled:
            import random
            random.seed(seed)

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

    def load_scenario(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self._trigger("scenario_loaded", scenario=scenario)

    def start(self) -> None:
        self._running = True
        self.clock.start()
        if self.scenario:
            self.scenario.setup(self)
        self.recorder.record("simulation_start", {"name": self.name})
        self._trigger("simulation_start")

    def step(self, dt: Optional[float] = None) -> float:
        if not self._running:
            return 0.0
        if dt is not None:
            actual_dt = self.clock.step_once(dt)
        else:
            actual_dt = self.clock.tick()
        if actual_dt <= 0:
            return 0.0
        for system in self._systems:
            if hasattr(system, 'update'):
                system.update(actual_dt)
        self.world.update(actual_dt)
        self.recorder.record("step", {"dt": actual_dt, "elapsed": self.clock.elapsed})
        self._trigger("post_step", dt=actual_dt)
        return actual_dt

    def stop(self) -> SimulationResult:
        self._running = False
        if self.scenario:
            self.scenario.teardown()
        result = SimulationResult(
            name=self.name,
            success=self.scenario.check_completion() if self.scenario else True,
            duration=self.clock.elapsed,
            steps=self.clock.steps,
        )
        self.results.append(result)
        self.recorder.record("simulation_stop", {
            "duration": result.duration, "steps": result.steps,
        })
        self._trigger("simulation_stop", result=result)
        return result

    def run_for(self, duration: float, callback: Optional[Callable[[float], None]] = None) -> SimulationResult:
        self.start()
        elapsed = 0.0
        while elapsed < duration and self._running:
            dt = self.step()
            elapsed += dt
            if callback:
                callback(dt)
        return self.stop()

    def run_steps(self, steps: int, callback: Optional[Callable[[float], None]] = None) -> SimulationResult:
        self.start()
        for _ in range(steps):
            if not self._running:
                break
            dt = self.step()
            if callback:
                callback(dt)
        return self.stop()

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "running": self._running,
            "deterministic": self._deterministic,
            "seed": self._seed,
            "clock": self.clock.to_dict(),
            "systems": len(self._systems),
            "entities": len(self.world.entities),
            "results": len(self.results),
            "recorded_events": len(self.recorder.events),
        }


@dataclass
class SimulationComponent(Component):
    sim_type: str = ""
    sim_data: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    update_priority: int = 0


class SimulationSystem(System):
    def __init__(self):
        super().__init__()
        self.sim_entities: Dict[str, SimulationComponent] = {}

    def on_entity_added(self, entity: Entity) -> None:
        sim = entity.get(SimulationComponent)
        if sim:
            self.sim_entities[entity.id] = sim

    def on_entity_removed(self, entity: Entity) -> None:
        self.sim_entities.pop(entity.id, None)

    def update(self, dt: float) -> None:
        for eid, sim in list(self.sim_entities.items()):
            if not sim.enabled:
                continue


_simulator = Simulator()


def get_simulator() -> Simulator:
    return _simulator
