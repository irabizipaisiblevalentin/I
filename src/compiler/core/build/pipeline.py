"""
Build pipeline orchestration.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .artifact import ArtifactManifest
from .cache import BuildCache
from .errors import BuildError
from .profile import BuildProfile
from .scheduler import ScheduleConfig, ScheduleResult, TaskScheduler
from .task import BuildTask


@dataclass
class BuildConfig:
    """Build configuration."""

    profile: BuildProfile = field(default_factory=BuildProfile.dev)
    targets: list[str] = field(default_factory=list)
    clean: bool = False
    verbose: bool = False
    parallel: bool = True
    max_workers: int | None = None


@dataclass
class BuildResult:
    """Build result summary."""

    success: bool
    config: BuildConfig
    schedule_result: ScheduleResult
    artifacts: ArtifactManifest
    duration: float = 0.0
    errors: list[BuildError] = field(default_factory=list)

    @property
    def tasks_executed(self) -> int:
        """Number of tasks executed."""
        return self.schedule_result.tasks_succeeded

    @property
    def tasks_cached(self) -> int:
        """Number of tasks cached."""
        return self.schedule_result.tasks_cached

    @property
    def tasks_failed(self) -> int:
        """Number of tasks failed."""
        return self.schedule_result.tasks_failed


class BuildPipeline:
    """
    Main build pipeline interface.

    Orchestrates the entire build process from source to output.
    """

    def __init__(
        self,
        workspace_root: Path,
        config: BuildConfig | None = None,
    ) -> None:
        """
        Initialize build pipeline.

        Args:
            workspace_root: Workspace root directory
            config: Build configuration
        """
        self._workspace_root = workspace_root
        self._config = config or BuildConfig()
        self._target_dir = workspace_root / "target"
        self._cache_dir = self._target_dir / "cache"
        self._cache = BuildCache(self._cache_dir)
        self._scheduler = TaskScheduler(
            ScheduleConfig(max_workers=self._config.max_workers)
        )
        self._artifacts = ArtifactManifest()
        self._task_factories: dict[str, Callable[[], BuildTask]] = {}

    @property
    def workspace_root(self) -> Path:
        """Workspace root directory."""
        return self._workspace_root

    @property
    def target_dir(self) -> Path:
        """Target directory."""
        return self._target_dir

    @property
    def config(self) -> BuildConfig:
        """Build configuration."""
        return self._config

    def register_task_factory(self, name: str, factory: Callable[[], BuildTask]) -> None:
        """
        Register a task factory.

        Args:
            name: Task name
            factory: Factory function that creates the task
        """
        self._task_factories[name] = factory

    def add_task(self, task: BuildTask) -> None:
        """
        Add task to build pipeline.

        Args:
            task: Task to add
        """
        self._scheduler.add_task(task)

    def add_dependency(self, task_name: str, depends_on: str) -> None:
        """
        Add dependency between tasks.

        Args:
            task_name: Task that depends on another
            depends_on: Task that is depended upon
        """
        self._scheduler.add_dependency(task_name, depends_on)

    def build(self, targets: list[str] | None = None) -> BuildResult:
        """
        Execute build pipeline.

        Args:
            targets: Optional list of target tasks (all if None)

        Returns:
            Build result
        """
        start = time.monotonic()

        try:
            # Ensure target directory exists
            self._target_dir.mkdir(parents=True, exist_ok=True)
            self._cache_dir.mkdir(parents=True, exist_ok=True)

            # Clean if requested
            if self._config.clean:
                self.clean()

            # Execute tasks
            schedule_result = self._scheduler.execute(targets)

            # Collect artifacts
            artifacts = self._collect_artifacts()

            # Save cache
            self._cache.save()

            duration = time.monotonic() - start

            return BuildResult(
                success=schedule_result.success,
                config=self._config,
                schedule_result=schedule_result,
                artifacts=artifacts,
                duration=duration,
            )

        except Exception as e:
            duration = time.monotonic() - start
            return BuildResult(
                success=False,
                config=self._config,
                schedule_result=ScheduleResult(success=False),
                artifacts=self._artifacts,
                duration=duration,
                errors=[BuildError(str(e))],
            )

    def clean(self) -> None:
        """Clean build artifacts."""
        import shutil

        if self._target_dir.exists():
            shutil.rmtree(self._target_dir)
            self._target_dir.mkdir(parents=True, exist_ok=True)

        self._artifacts.clear()
        self._cache.clear()

    def incremental(self, changed_files: list[Path]) -> BuildResult:
        """
        Perform incremental build.

        Args:
            changed_files: List of files that changed

        Returns:
            Build result
        """
        # For now, just do a full build
        # TODO: Implement proper incremental build
        return self.build()

    def _collect_artifacts(self) -> ArtifactManifest:
        """Collect all build artifacts."""
        # This is a placeholder - actual implementation will
        # collect artifacts from task outputs
        return self._artifacts

    def _should_rebuild(self, task: BuildTask) -> bool:
        """
        Check if task needs to be rebuilt.

        Args:
            task: Task to check

        Returns:
            True if task should be rebuilt
        """
        cache_key = task.get_cache_key()

        if not self._cache.has(cache_key):
            return True

        if not self._cache.is_valid(cache_key, task.inputs):
            return True

        return False
