"""
Build System Example

Demonstrates how to use the build system to compile an I project.
"""

from pathlib import Path

from src.compiler.core.build import (
    BuildPipeline,
    BuildTask,
    TaskType,
    TaskResult,
    BuildProfile,
)
from src.compiler.core.workspace import Workspace


def example_simple_build():
    """Example: Simple build."""
    
    # Create a simple task
    def lex_action():
        print("Lexing source files...")
        return TaskResult.success([Path("output.tokens")])
    
    task = BuildTask(
        name="lex",
        task_type=TaskType.LEX,
        inputs=[Path("src/main.i")],
        outputs=[Path("target/tokens")],
        action=lex_action,
    )
    
    # Create pipeline
    pipeline = BuildPipeline(Path("."))
    pipeline.add_task(task)
    
    # Execute build
    result = pipeline.build()
    
    print(f"Build {'succeeded' if result.success else 'failed'}")
    print(f"Duration: {result.duration:.2f}s")


def example_multi_task_build():
    """Example: Multi-task build with dependencies."""
    
    # Define tasks
    def lex_action():
        print("Lexing...")
        return TaskResult.success([])
    
    def parse_action():
        print("Parsing...")
        return TaskResult.success([])
    
    def analyze_action():
        print("Analyzing...")
        return TaskResult.success([])
    
    # Create tasks
    lex = BuildTask(name="lex", task_type=TaskType.LEX, action=lex_action)
    parse = BuildTask(name="parse", task_type=TaskType.PARSE, action=parse_action)
    analyze = BuildTask(name="analyze", task_type=TaskType.ANALYZE, action=analyze_action)
    
    # Create pipeline
    pipeline = BuildPipeline(Path("."))
    
    # Add tasks
    pipeline.add_task(lex)
    pipeline.add_task(parse)
    pipeline.add_task(analyze)
    
    # Add dependencies
    pipeline.add_dependency("parse", "lex")
    pipeline.add_dependency("analyze", "parse")
    
    # Execute build
    result = pipeline.build()
    
    print(f"Build {'succeeded' if result.success else 'failed'}")
    print(f"Tasks executed: {result.tasks_executed}")
    print(f"Duration: {result.duration:.2f}s")


def example_profile_build():
    """Example: Build with different profiles."""
    
    # Development build
    dev_config = BuildConfig(profile=BuildProfile.dev())
    dev_pipeline = BuildPipeline(Path("."), dev_config)
    
    # Release build
    release_config = BuildConfig(profile=BuildProfile.release())
    release_pipeline = BuildPipeline(Path("."), release_config)
    
    print("Dev profile:", dev_pipeline.config.profile.name)
    print("Release profile:", release_pipeline.config.profile.name)


if __name__ == "__main__":
    print("=== Simple Build ===")
    example_simple_build()
    
    print("\n=== Multi-Task Build ===")
    example_multi_task_build()
    
    print("\n=== Profile Build ===")
    example_profile_build()
