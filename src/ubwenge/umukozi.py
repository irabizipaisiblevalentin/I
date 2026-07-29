"""Agent platform — single agents, multi-agent systems, tool calling, planning, memory, reflection."""

from __future__ import annotations

import json
import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Type
from collections import OrderedDict

from .iyerekana import InferenceRequest, InferenceResult
from .iyerekana import get_pipeline as _get_global_pipeline
from .ibikoresho import AIError, generate_id


class AgentRole(str, Enum):
    ASSISTANT = "assistant"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    SUMMARIZER = "summarizer"
    CUSTOM = "custom"


class AgentState(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    fn: Optional[Callable] = None
    required: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = ""
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0

    def __post_init__(self) -> None:
        if not self.call_id:
            self.call_id = generate_id("tc_")


@dataclass
class AgentMessage:
    role: str = "user"
    content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_call_id: str = ""
    name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class AgentConfig:
    name: str = ""
    role: AgentRole = AgentRole.ASSISTANT
    model_id: str = "default"
    system_prompt: str = "You are a helpful AI assistant."
    temperature: float = 0.7
    max_tokens: int = 2048
    max_iterations: int = 10
    tools: List[ToolSpec] = field(default_factory=list)
    memory_enabled: bool = True
    max_context_length: int = 100
    reflection_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class Agent:
    def __init__(self, config: AgentConfig, pipeline: Optional[InferencePipeline] = None):
        self.config = config
        self.pipeline = pipeline or _get_global_pipeline()
        self.messages: List[AgentMessage] = []
        self.state = AgentState.IDLE
        self._iteration = 0
        self._on_step: List[Callable] = []

    def add_tool(self, tool: ToolSpec) -> Agent:
        self.config.tools.append(tool)
        return self

    def add_tool_fn(self, name: str, description: str, fn: Callable,
                    parameters: Optional[Dict[str, Any]] = None) -> Agent:
        self.config.tools.append(ToolSpec(
            name=name, description=description, fn=fn,
            parameters=parameters or {},
        ))
        return self

    def on_step(self, handler: Callable) -> Agent:
        self._on_step.append(handler)
        return self

    def run(self, prompt: str, **kwargs: Any) -> AgentMessage:
        self.state = AgentState.THINKING
        self.messages.append(AgentMessage(role="user", content=prompt))
        final_message = AgentMessage(role="assistant", content="")

        for self._iteration in range(self.config.max_iterations):
            request = InferenceRequest(
                model_id=self.config.model_id,
                messages=[{"role": m.role, "content": m.content} for m in self.messages],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=[{"name": t.name, "description": t.description,
                        "parameters": t.parameters} for t in self.config.tools],
            )
            result = self.pipeline.infer(request)

            msg = AgentMessage(role="assistant", content=result.text)
            self.messages.append(msg)

            for handler in self._on_step:
                handler(self, msg)

            tool_calls = self._parse_tool_calls(result.text)
            if not tool_calls:
                final_message = msg
                self.state = AgentState.COMPLETED
                break

            self.state = AgentState.ACTING
            for tc in tool_calls:
                tool = self._find_tool(tc.tool_name)
                if tool and tool.fn:
                    try:
                        start = time.time()
                        tc.result = tool.fn(**tc.arguments)
                        tc.duration_ms = (time.time() - start) * 1000
                    except Exception as e:
                        tc.error = str(e)
                self.messages.append(AgentMessage(
                    role="tool", content=str(tc.result or tc.error or ""),
                    tool_call_id=tc.call_id,
                ))

            self.state = AgentState.OBSERVING
        else:
            final_message = self.messages[-1] if self.messages else AgentMessage(role="assistant", content="")

        return final_message

    def _parse_tool_calls(self, text: str) -> List[ToolCall]:
        calls = []
        for tool in self.config.tools:
            if tool.name in text and "{" in text:
                try:
                    start = text.index("{")
                    end = text.rindex("}") + 1
                    args = json.loads(text[start:end])
                    calls.append(ToolCall(tool_name=tool.name, arguments=args))
                except (ValueError, json.JSONDecodeError):
                    pass
        return calls

    def _find_tool(self, name: str) -> Optional[ToolSpec]:
        for t in self.config.tools:
            if t.name == name:
                return t
        return None


class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._lock = threading.RLock()

    def register(self, agent: Agent) -> str:
        with self._lock:
            name = agent.config.name or generate_id("agent_")
            self.agents[name] = agent
            return name

    def get(self, name: str) -> Optional[Agent]:
        return self.agents.get(name)

    def run_team(self, task: str, agent_names: List[str],
                 coordinator: Optional[str] = None) -> Dict[str, Any]:
        results = {}
        for name in agent_names:
            agent = self.agents.get(name)
            if agent:
                results[name] = agent.run(task)
        return results

    def run_debate(self, topic: str, agent_names: List[str],
                   rounds: int = 2) -> List[Dict[str, Any]]:
        history = []
        for r in range(rounds):
            round_results = {}
            for name in agent_names:
                agent = self.agents.get(name)
                if agent:
                    context = f"Round {r+1}: {topic}\n" + "\n".join(
                        f"{n}: {h[n]['content']}" for h in history[-1:] if isinstance(h, dict)
                        for n in h if isinstance(h, dict)
                    ) if history else topic
                    round_results[name] = agent.run(context)
            history.append(round_results)
        return history


_global_orchestrator = AgentOrchestrator()


def create_agent(name: str, model_id: str = "default",
                 system_prompt: Optional[str] = None,
                 tools: Optional[List[ToolSpec]] = None) -> Agent:
    config = AgentConfig(
        name=name,
        model_id=model_id,
        system_prompt=system_prompt or f"You are {name}, a helpful AI assistant.",
        tools=tools or [],
    )
    agent = Agent(config)
    _global_orchestrator.register(agent)
    return agent
