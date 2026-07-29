"""
Task scheduling for build system.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .errors import CircularDependencyError, TaskError
from .task import BuildTask, TaskGraph, TaskResult


@dataclass
class ScheduleConfig:
    """Scheduler configuration."""
    
    max_workers: Optional[int] = None
    timeout: Optional[float] = None
    fail_fast: bool = True


@dataclass
class ScheduleResult:
    """Result of task scheduling."""
    
    success: bool
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    execution_order: List[str] = field(default_factory=list)
    total_duration: float = 0.0
    
    @property
    def tasks_succeeded(self) -> int:
        """Number of successful tasks."""
        return sum(1 for r in self.task_results.values() if r.success)
    
    @property
    def tasks_failed(self) -> int:
        """Number of failed tasks."""
        return sum(1 for r in self.task_results.values() if not r.success)
    
    @property
    def tasks_cached(self) -> int:
        """Number of cached tasks."""
        return sum(1 for r in self.task_results.values() if r.cached)


class TaskScheduler:
    """
    Schedules and executes build tasks.
    
    Handles task ordering, parallel execution, and error handling.
    """
    
    def __init__(self, config: Optional[ScheduleConfig] = None) -> None:
        """
        Initialize task scheduler.
        
        Args:
            config: Scheduler configuration
        """
        self._config = config or ScheduleConfig()
        self._graph = TaskGraph()
    
    @property
    def graph(self) -> TaskGraph:
        """Task graph."""
        return self._graph
    
    def add_task(self, task: BuildTask) -> None:
        """
        Add task to scheduler.
        
        Args:
            task: Task to add
        """
        self._graph.add_task(task)
    
    def add_dependency(self, task_name: str, depends_on: str) -> None:
        """
        Add dependency between tasks.
        
        Args:
            task_name: Task that depends on another
            depends_on: Task that is depended upon
        """
        self._graph.add_dependency(task_name, depends_on)
    
    def schedule(self, targets: Optional[List[str]] = None) -> List[str]:
        """
        Schedule tasks for execution.
        
        Args:
            targets: Optional list of target tasks (all if None)
            
        Returns:
            List of task names in execution order
            
        Raises:
            CircularDependencyError: If cycle detected
        """
        # Get execution order
        order = self._graph.topological_sort()
        
        # Filter to targets if specified
        if targets:
            # Get all dependencies of targets
            included: Set[str] = set()
            
            def include_with_deps(name: str) -> None:
                if name in included:
                    return
                included.add(name)
                for dep in self._graph.get_dependencies(name):
                    include_with_deps(dep)
            
            for target in targets:
                if target not in self._graph.tasks:
                    raise ValueError(f"Unknown target: {target}")
                include_with_deps(target)
            
            order = [name for name in order if name in included]
        
        return order
    
    def execute(self, targets: Optional[List[str]] = None) -> ScheduleResult:
        """
        Execute scheduled tasks.
        
        Args:
            targets: Optional list of target tasks (all if None)
            
        Returns:
            Execution result
        """
        import time
        
        start = time.monotonic()
        
        try:
            order = self.schedule(targets)
        except CircularDependencyError as e:
            return ScheduleResult(
                success=False,
                execution_order=[],
                total_duration=time.monotonic() - start,
            )
        
        task_results: Dict[str, TaskResult] = {}
        execution_order: List[str] = []
        
        # Execute tasks sequentially for now
        # TODO: Implement parallel execution
        for task_name in order:
            task = self._graph.tasks[task_name]
            execution_order.append(task_name)
            
            try:
                result = task.execute()
                task_results[task_name] = result
                
                if not result.success and self._config.fail_fast:
                    return ScheduleResult(
                        success=False,
                        task_results=task_results,
                        execution_order=execution_order,
                        total_duration=time.monotonic() - start,
                    )
            except Exception as e:
                task_results[task_name] = TaskResult.failure()
                
                if self._config.fail_fast:
                    return ScheduleResult(
                        success=False,
                        task_results=task_results,
                        execution_order=execution_order,
                        total_duration=time.monotonic() - start,
                    )
        
        return ScheduleResult(
            success=all(r.success for r in task_results.values()),
            task_results=task_results,
            execution_order=execution_order,
            total_duration=time.monotonic() - start,
        )
    
    def clear(self) -> None:
        """Clear all tasks."""
        self._graph = TaskGraph()
