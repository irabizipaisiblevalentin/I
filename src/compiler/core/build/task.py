"""
Build task definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class TaskType(Enum):
    """Build task types."""
    
    LEX = "lex"
    PARSE = "parse"
    ANALYZE = "analyze"
    CHECK = "check"
    IRGEN = "irgen"
    OPTIMIZE = "optimize"
    CODEGEN = "codegen"
    LINK = "link"
    CUSTOM = "custom"


@dataclass(frozen=True)
class TaskResult:
    """Result of task execution."""
    
    success: bool
    outputs: List[Path] = field(default_factory=list)
    duration: float = 0.0
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(cls, outputs: List[Path], duration: float = 0.0, cached: bool = False) -> TaskResult:
        """Create successful result."""
        return cls(success=True, outputs=outputs, duration=duration, cached=cached)
    
    @classmethod
    def failure(cls, duration: float = 0.0) -> TaskResult:
        """Create failure result."""
        return cls(success=False, duration=duration)
    
    @classmethod
    def cached(cls, outputs: List[Path]) -> TaskResult:
        """Create cached result."""
        return cls(success=True, outputs=outputs, cached=True)


@dataclass
class BuildTask:
    """
    Single build task.
    
    Represents a unit of work in the build pipeline.
    """
    
    name: str
    task_type: TaskType
    inputs: List[Path] = field(default_factory=list)
    outputs: List[Path] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    action: Optional[Callable[[], TaskResult]] = None
    
    # Task metadata
    description: str = ""
    timeout: Optional[float] = None
    priority: int = 0
    
    def execute(self) -> TaskResult:
        """
        Execute the task.
        
        Returns:
            Task execution result
        """
        import time
        
        if self.action is None:
            raise ValueError(f"No action defined for task: {self.name}")
        
        start = time.monotonic()
        try:
            result = self.action()
            return result
        except Exception as e:
            duration = time.monotonic() - start
            return TaskResult.failure(duration)
    
    def get_cache_key(self) -> str:
        """
        Generate cache key for this task.
        
        Returns:
            Cache key string
        """
        import hashlib
        
        key_parts = [
            self.name,
            self.task_type.value,
            *[str(p) for p in sorted(self.inputs)],
        ]
        
        return hashlib.sha256("|".join(key_parts).encode()).hexdigest()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"BuildTask(name={self.name}, type={self.task_type.value})"
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash(self.name)


@dataclass
class TaskGraph:
    """
    Graph of build tasks with dependencies.
    
    Used for task scheduling and dependency resolution.
    """
    
    tasks: Dict[str, BuildTask] = field(default_factory=dict)
    _adjacency: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_task(self, task: BuildTask) -> None:
        """
        Add task to graph.
        
        Args:
            task: Task to add
        """
        self.tasks[task.name] = task
        if task.name not in self._adjacency:
            self._adjacency[task.name] = []
    
    def add_dependency(self, task_name: str, depends_on: str) -> None:
        """
        Add dependency between tasks.
        
        Args:
            task_name: Task that depends on another
            depends_on: Task that is depended upon
        """
        if task_name not in self._adjacency:
            self._adjacency[task_name] = []
        self._adjacency[task_name].append(depends_on)
    
    def get_dependencies(self, task_name: str) -> List[str]:
        """
        Get tasks that task_name depends on.
        
        Args:
            task_name: Task to get dependencies for
            
        Returns:
            List of dependency task names
        """
        return self._adjacency.get(task_name, [])
    
    def get_dependents(self, task_name: str) -> List[str]:
        """
        Get tasks that depend on task_name.
        
        Args:
            task_name: Task to get dependents for
            
        Returns:
            List of dependent task names
        """
        dependents = []
        for name, deps in self._adjacency.items():
            if task_name in deps:
                dependents.append(name)
        return dependents
    
    def topological_sort(self) -> List[str]:
        """
        Get tasks in topological order.
        
        Returns:
            List of task names in execution order
            
        Raises:
            CircularDependencyError: If cycle detected
        """
        visited = set()
        in_stack = set()
        order = []
        
        def dfs(name: str) -> None:
            if name in in_stack:
                raise CircularDependencyError([name])
            if name in visited:
                return
            
            in_stack.add(name)
            for dep in self.get_dependencies(name):
                dfs(dep)
            in_stack.remove(name)
            visited.add(name)
            order.append(name)
        
        for name in self.tasks:
            if name not in visited:
                dfs(name)
        
        return order
    
    def has_cycle(self) -> bool:
        """
        Check if graph has cycle.
        
        Returns:
            True if cycle exists
        """
        try:
            self.topological_sort()
            return False
        except CircularDependencyError:
            return True
