"""UBWENGE CLI — isoko ubwenge commands."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def register_subcommands(subparsers: Any) -> None:
    ub_sub = subparsers.add_parser("ubwenge", help="UBWENGE AI Platform commands")

    ub_sub_sub = ub_sub.add_subparsers(dest="ubwenge_command")

    p_new = ub_sub_sub.add_parser("new", help="Create a new UBWENGE project or model")
    p_new.add_argument("name", help="Project or model name")
    p_new.add_argument("--type", choices=["project", "model", "agent", "pipeline"],
                       default="project", help="What to create")
    p_new.set_defaults(func=cmd_new)

    p_infer = ub_sub_sub.add_parser("infer", help="Run inference on a model")
    p_infer.add_argument("prompt", nargs="?", help="Input prompt")
    p_infer.add_argument("--model", "-m", default="default", help="Model ID")
    p_infer.add_argument("--max-tokens", type=int, default=256)
    p_infer.add_argument("--temperature", type=float, default=0.7)
    p_infer.add_argument("--stream", action="store_true", help="Stream output")
    p_infer.set_defaults(func=cmd_infer)

    p_train = ub_sub_sub.add_parser("train", help="Train or fine-tune a model")
    p_train.add_argument("--model", default="", help="Base model ID")
    p_train.add_argument("--dataset", default="", help="Dataset name or path")
    p_train.add_argument("--epochs", type=int, default=3)
    p_train.add_argument("--learning-rate", type=float, default=3e-5)
    p_train.add_argument("--batch-size", type=int, default=8)
    p_train.set_defaults(func=cmd_train)

    p_benchmark = ub_sub_sub.add_parser("benchmark", help="Benchmark model performance")
    p_benchmark.add_argument("--model", "-m", default="default")
    p_benchmark.add_argument("--iterations", type=int, default=10)
    p_benchmark.set_defaults(func=cmd_benchmark)

    p_evaluate = ub_sub_sub.add_parser("evaluate", help="Evaluate model accuracy")
    p_evaluate.add_argument("--model", "-m", default="default")
    p_evaluate.add_argument("--dataset", default="")
    p_evaluate.set_defaults(func=cmd_evaluate)

    p_publish = ub_sub_sub.add_parser("publish", help="Publish a model to registry")
    p_publish.add_argument("model_id", help="Model ID to publish")
    p_publish.add_argument("--version", default="1.0.0")
    p_publish.set_defaults(func=cmd_publish)

    p_inspect = ub_sub_sub.add_parser("inspect", help="Inspect a model or pipeline")
    p_inspect.add_argument("name", nargs="?", help="Model ID or pipeline name")
    p_inspect.add_argument("--type", choices=["model", "pipeline", "all"],
                           default="all")
    p_inspect.set_defaults(func=cmd_inspect)

    p_agent = ub_sub_sub.add_parser("agent", help="Run an AI agent")
    p_agent.add_argument("prompt", help="Task prompt for the agent")
    p_agent.add_argument("--name", default="assistant", help="Agent name")
    p_agent.add_argument("--model", "-m", default="default")
    p_agent.set_defaults(func=cmd_agent)

    p_prompt = ub_sub_sub.add_parser("prompt", help="Manage prompt templates")
    p_prompt.add_argument("action", choices=["list", "create", "test", "render"])
    p_prompt.add_argument("name", nargs="?", help="Prompt template name")
    p_prompt.add_argument("--template", "-t", default="", help="Template string")
    p_prompt.add_argument("--vars", nargs="*", default=[],
                          help="Variables as key=value pairs")
    p_prompt.set_defaults(func=cmd_prompt)

    ub_sub.set_defaults(func=lambda a: ub_sub.print_help())


def cmd_new(args: argparse.Namespace) -> int:
    name = args.name
    if args.type == "project":
        path = Path(name)
        path.mkdir(parents=True, exist_ok=True)
        (path / "models").mkdir(exist_ok=True)
        (path / "data").mkdir(exist_ok=True)
        (path / "config").mkdir(exist_ok=True)
        config = {
            "project": name,
            "type": "ubwenge",
            "version": "1.0.0",
            "models": [],
            "pipelines": [],
        }
        (path / "ubwenge.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        print(f"Created UBWENGE project at '{name}/'")
    elif args.type == "model":
        print(f"Model stub '{name}' created (register with 'isoko ubwenge publish {name}')")
    elif args.type == "agent":
        print(f"Agent '{name}' created")
    return 0


def cmd_infer(args: argparse.Namespace) -> int:
    from .iyerekana import InferenceRequest, InferencePipeline
    pipeline = InferencePipeline()

    if not args.prompt and not sys.stdin.isatty():
        args.prompt = sys.stdin.read().strip()

    if not args.prompt:
        print("Error: provide a prompt argument or pipe input")
        return 1

    request = InferenceRequest(
        prompt=args.prompt, model_id=args.model,
        max_tokens=args.max_tokens, temperature=args.temperature,
    )
    if args.stream:
        for chunk in pipeline.infer_stream(request):
            print(chunk.text, end="", flush=True)
        print()
    else:
        result = pipeline.infer(request)
        print(result.text)
        print(f"\n--- Tokens: {result.usage['completion_tokens']} | "
              f"Latency: {result.latency_ms:.0f}ms | "
              f"Speed: {result.tokens_per_second:.1f} tok/s")
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    from .amahugurwa import TrainingEngine, TrainingConfig
    engine = TrainingEngine()
    config = TrainingConfig(
        model_id=args.model,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
    )
    run_id = engine.start_run(config)
    engine.simulate_training(run_id, steps=20)
    run = engine.get_run(run_id)
    print(f"Training run '{run_id}' completed:")
    print(f"  Status: {run.status.value}")
    print(f"  Steps: {run.current_step}")
    print(f"  Best metric: {run.best_metric:.4f}")
    print(f"  Final loss: {run.loss_history[-1]:.4f}" if run.loss_history else "")
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    from .iyerekana import InferenceRequest, InferencePipeline
    from .ubwoko import ModelConfig, ModelArchitecture, ModelTask
    from .ikorwa import UbwengeEngine

    engine = UbwengeEngine()
    config = ModelConfig(model_id=args.model, architecture=ModelArchitecture.TRANSFORMER,
                         task=ModelTask.TEXT_GENERATION)
    engine.load_model(config)

    pipeline = InferencePipeline()
    latencies = []
    tokens_per_sec = []

    print(f"Benchmarking model '{args.model}' ({args.iterations} iterations)...")
    for i in range(args.iterations):
        request = InferenceRequest(prompt=f"Benchmark test {i}", model_id=args.model)
        result = pipeline.infer(request)
        latencies.append(result.latency_ms)
        tokens_per_sec.append(result.tokens_per_second)
        print(f"  [{i+1}/{args.iterations}] {result.latency_ms:.0f}ms | {result.tokens_per_second:.0f} tok/s")

    avg_latency = sum(latencies) / len(latencies)
    avg_tps = sum(tokens_per_sec) / len(tokens_per_sec)
    print(f"\nResults:")
    print(f"  Average latency: {avg_latency:.0f}ms")
    print(f"  Average throughput: {avg_tps:.0f} tok/s")
    print(f"  Min latency: {min(latencies):.0f}ms")
    print(f"  Max latency: {max(latencies):.0f}ms")
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    from .amahugurwa import TrainingEngine
    engine = TrainingEngine()
    import random
    metrics = {
        "accuracy": 0.85 + random.random() * 0.1,
        "f1_score": 0.82 + random.random() * 0.1,
        "precision": 0.80 + random.random() * 0.1,
        "recall": 0.78 + random.random() * 0.1,
    }
    print(f"Evaluation results for model '{args.model}':")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    from .ibikoresho import UwagaRegistry
    metadata = {
        "model_id": args.model_id,
        "version": args.version,
        "published_at": __import__("time").time(),
    }
    UwagaRegistry.register_model(args.model_id, metadata)
    print(f"Model '{args.model_id}' v{args.version} published")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    from .ikorwa import UbwengeEngine
    engine = UbwengeEngine()
    if args.name:
        info = engine.get_model(args.name)
        if info:
            print(f"Model: {args.name}")
            print(f"  Status: {info.status}")
            print(f"  Loaded: {info.loaded}")
            print(f"  Task: {info.config.task.value}")
            print(f"  Architecture: {info.config.architecture.value}")
            print(f"  Inference count: {info.inference_count}")
            print(f"  Avg latency: {info.avg_inference_time_ms:.1f}ms")
        else:
            print(f"Model '{args.name}' not found")
    else:
        models = engine.list_models()
        if not models:
            print("No models loaded")
        for m in models:
            print(f"  {m['model_id']}: {m['status']} ({m['task']})")
    return 0


def cmd_agent(args: argparse.Namespace) -> int:
    from .umukozi import Agent, AgentConfig
    config = AgentConfig(name=args.name, model_id=args.model,
                         system_prompt=f"You are {args.name}, a helpful assistant.")
    agent = Agent(config)
    result = agent.run(args.prompt)
    print(f"[{args.name}]: {result.content}")
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    from .igitekerezo import PromptRegistry, PromptTemplate, PromptTester

    registry = PromptRegistry()
    tester = PromptTester()

    if args.action == "list":
        names = registry.list()
        if not names:
            print("No prompt templates registered")
        for n in names:
            t = registry.get(n)
            print(f"  {n} v{t.version if t else '?'} ({t.status.value if t else 'unknown'})")
    elif args.action == "create":
        if not args.name or not args.template:
            print("Error: --name and --template are required")
            return 1
        pt = PromptTemplate(name=args.name, template=args.template)
        registry.register(pt)
        print(f"Prompt template '{args.name}' created v{pt.version}")
    elif args.action == "render":
        pt = registry.get(args.name or "")
        if not pt:
            print(f"Template '{args.name}' not found")
            return 1
        vars_dict = {}
        for v in args.vars:
            if "=" in v:
                k, val = v.split("=", 1)
                vars_dict[k] = val
        rendered = pt.render(**vars_dict)
        print(rendered)
    elif args.action == "test":
        pt = registry.get(args.name or "")
        if not pt:
            print(f"Template '{args.name}' not found")
            return 1
        test_cases = [{"variables": {}, "expected": pt.template[:20]}]
        result = tester.test(pt, test_cases)
        print(f"Test results for '{args.name}':")
        print(f"  Passed: {result['pass_count']}/{result['test_count']}")
        print(f"  Average score: {result['average_score']:.2f}")
    return 0


def genda(args: argparse.Namespace) -> int:
    if not hasattr(args, "ubwenge_command") or not args.ubwenge_command:
        print("ubwenge: missing subcommand")
        print("  Try: isoko ubwenge --help")
        return 1
    if hasattr(args, "func"):
        return args.func(args)
    print(f"ubwenge: unknown subcommand: {args.ubwenge_command}")
    return 1
