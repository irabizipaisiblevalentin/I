# Agent Guide — Building AI Agents

## Creating a Single Agent

```python
from ubwenge.umukozi import Agent, AgentConfig, ToolSpec

def search_web(query: str) -> str:
    return f"Search results for: {query}"

agent = Agent(AgentConfig(
    name="researcher",
    model_id="default",
    system_prompt="You are a research assistant.",
))
agent.add_tool(ToolSpec(
    name="search",
    description="Search the web",
    parameters={"query": {"type": "string"}},
    fn=search_web,
))

result = agent.run("Research the latest AI breakthroughs")
print(result.content)
```

## Multi-Agent Orchestration

```python
from ubwenge.umukozi import AgentOrchestrator

orchestrator = AgentOrchestrator()

planner = Agent(AgentConfig(name="planner", system_prompt="You plan tasks."))
coder = Agent(AgentConfig(name="coder", system_prompt="You write code."))
reviewer = Agent(AgentConfig(name="reviewer", system_prompt="You review code."))

orchestrator.register(planner)
orchestrator.register(coder)
orchestrator.register(reviewer)

results = orchestrator.run_team("Build a calculator app",
                                 agent_names=["planner", "coder", "reviewer"])
```

## Agent with Memory

Agents automatically use the memory system when `memory_enabled=True` in the config.
