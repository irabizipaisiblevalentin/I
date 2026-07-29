"""
Tests for build system.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.compiler.core.build import (
    BuildPipeline,
    BuildTask,
    TaskType,
    TaskResult,
    TaskScheduler,
    BuildCache,
    BuildProfile,
    BuildArtifact,
    ArtifactType,
)


# ============================================================================
# Task Tests
# ============================================================================


class TestBuildTask:
    """Tests for BuildTask."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = BuildTask(
            name="test-task",
            task_type=TaskType.LEX,
            inputs=[Path("input.i")],
            outputs=[Path("output.tokens")],
        )
        
        assert task.name == "test-task"
        assert task.task_type == TaskType.LEX
        assert len(task.inputs) == 1
        assert len(task.outputs) == 1
    
    def test_task_execution(self):
        """Test executing a task."""
        executed = []
        
        def action():
            executed.append(True)
            return TaskResult.success([Path("output")])
        
        task = BuildTask(
            name="test-task",
            task_type=TaskType.LEX,
            action=action,
        )
        
        result = task.execute()
        
        assert result.success is True
        assert len(executed) == 1
    
    def test_task_cache_key(self):
        """Test cache key generation."""
        task1 = BuildTask(
            name="test-task",
            task_type=TaskType.LEX,
            inputs=[Path("input.i")],
        )
        
        task2 = BuildTask(
            name="test-task",
            task_type=TaskType.LEX,
            inputs=[Path("input.i")],
        )
        
        task3 = BuildTask(
            name="different-task",
            task_type=TaskType.LEX,
            inputs=[Path("input.i")],
        )
        
        assert task1.get_cache_key() == task2.get_cache_key()
        assert task1.get_cache_key() != task3.get_cache_key()


# ============================================================================
# TaskGraph Tests
# ============================================================================


class TestTaskGraph:
    """Tests for TaskGraph."""
    
    def test_add_task(self):
        """Test adding task to graph."""
        from src.compiler.core.build.task import TaskGraph
        
        graph = TaskGraph()
        task = BuildTask(name="task1", task_type=TaskType.LEX)
        
        graph.add_task(task)
        
        assert "task1" in graph.tasks
    
    def test_add_dependency(self):
        """Test adding dependency."""
        from src.compiler.core.build.task import TaskGraph
        
        graph = TaskGraph()
        task1 = BuildTask(name="task1", task_type=TaskType.LEX)
        task2 = BuildTask(name="task2", task_type=TaskType.PARSE)
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_dependency("task2", "task1")
        
        assert "task1" in graph.get_dependencies("task2")
    
    def test_topological_sort(self):
        """Test topological sort."""
        from src.compiler.core.build.task import TaskGraph
        
        graph = TaskGraph()
        task1 = BuildTask(name="task1", task_type=TaskType.LEX)
        task2 = BuildTask(name="task2", task_type=TaskType.PARSE)
        task3 = BuildTask(name="task3", task_type=TaskType.ANALYZE)
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_task(task3)
        graph.add_dependency("task2", "task1")
        graph.add_dependency("task3", "task2")
        
        order = graph.topological_sort()
        
        assert order.index("task1") < order.index("task2")
        assert order.index("task2") < order.index("task3")
    
    def test_circular_dependency(self):
        """Test circular dependency detection."""
        from src.compiler.core.build.task import TaskGraph
        from src.compiler.core.build.errors import CircularDependencyError
        
        graph = TaskGraph()
        task1 = BuildTask(name="task1", task_type=TaskType.LEX)
        task2 = BuildTask(name="task2", task_type=TaskType.PARSE)
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_dependency("task1", "task2")
        graph.add_dependency("task2", "task1")
        
        with pytest.raises(CircularDependencyError):
            graph.topological_sort()


# ============================================================================
# Scheduler Tests
# ============================================================================


class TestTaskScheduler:
    """Tests for TaskScheduler."""
    
    def test_scheduler_execution(self):
        """Test scheduler execution."""
        executed = []
        
        def action1():
            executed.append("task1")
            return TaskResult.success([])
        
        def action2():
            executed.append("task2")
            return TaskResult.success([])
        
        scheduler = TaskScheduler()
        
        task1 = BuildTask(name="task1", task_type=TaskType.LEX, action=action1)
        task2 = BuildTask(name="task2", task_type=TaskType.PARSE, action=action2)
        
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        scheduler.add_dependency("task2", "task1")
        
        result = scheduler.execute()
        
        assert result.success is True
        assert executed == ["task1", "task2"]


# ============================================================================
# Cache Tests
# ============================================================================


class TestBuildCache:
    """Tests for BuildCache."""
    
    def test_cache_put_get(self):
        """Test putting and getting cache entries."""
        with TemporaryDirectory() as tmpdir:
            cache = BuildCache(Path(tmpdir))
            
            entry = CacheEntry(
                key="test-key",
                outputs=["output1", "output2"],
            )
            
            cache.put(entry)
            retrieved = cache.get("test-key")
            
            assert retrieved is not None
            assert retrieved.key == "test-key"
            assert len(retrieved.outputs) == 2
    
    def test_cache_has(self):
        """Test checking cache existence."""
        with TemporaryDirectory() as tmpdir:
            cache = BuildCache(Path(tmpdir))
            
            assert cache.has("nonexistent") is False
            
            entry = CacheEntry(key="test-key", outputs=[])
            cache.put(entry)
            
            assert cache.has("test-key") is True
    
    def test_cache_invalidate(self):
        """Test cache invalidation."""
        with TemporaryDirectory() as tmpdir:
            cache = BuildCache(Path(tmpdir))
            
            entry = CacheEntry(key="test-key", outputs=[])
            cache.put(entry)
            
            assert cache.has("test-key") is True
            
            cache.invalidate("test-key")
            
            assert cache.has("test-key") is False
    
    def test_cache_save_load(self):
        """Test saving and loading cache."""
        with TemporaryDirectory() as tmpdir:
            cache1 = BuildCache(Path(tmpdir))
            entry = CacheEntry(key="test-key", outputs=["output"])
            cache1.put(entry)
            cache1.save()
            
            cache2 = BuildCache(Path(tmpdir))
            retrieved = cache2.get("test-key")
            
            assert retrieved is not None
            assert retrieved.key == "test-key"
    
    def test_compute_key(self):
        """Test cache key computation."""
        with TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.i"
            input_file.write_text("test content")
            
            key1 = BuildCache.compute_key("lex", [input_file])
            key2 = BuildCache.compute_key("lex", [input_file])
            key3 = BuildCache.compute_key("parse", [input_file])
            
            assert key1 == key2
            assert key1 != key3


# ============================================================================
# Profile Tests
# ============================================================================


class TestBuildProfile:
    """Tests for BuildProfile."""
    
    def test_dev_profile(self):
        """Test development profile."""
        profile = BuildProfile.dev()
        
        assert profile.name == "dev"
        assert profile.optimization.value == 0
        assert profile.incremental is True
    
    def test_release_profile(self):
        """Test release profile."""
        profile = BuildProfile.release()
        
        assert profile.name == "release"
        assert profile.optimization.value == 3
        assert profile.lto is True
        assert profile.incremental is False
    
    def test_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            "opt-level": 2,
            "debug": "line-tables",
            "lto": True,
        }
        
        profile = BuildProfile.from_dict("custom", data)
        
        assert profile.name == "custom"
        assert profile.optimization.value == 2
        assert profile.lto is True
    
    def test_to_dict(self):
        """Test converting profile to dictionary."""
        profile = BuildProfile.release()
        data = profile.to_dict()
        
        assert data["opt-level"] == 3
        assert data["lto"] is True


# ============================================================================
# Artifact Tests
# ============================================================================


class TestBuildArtifact:
    """Tests for BuildArtifact."""
    
    def test_artifact_creation(self):
        """Test creating an artifact."""
        artifact = BuildArtifact(
            name="test",
            artifact_type=ArtifactType.TOKENS,
            path=Path("test.tokens"),
        )
        
        assert artifact.name == "test"
        assert artifact.artifact_type == ArtifactType.TOKENS
    
    def test_artifact_manifest(self):
        """Test artifact manifest."""
        from src.compiler.core.build.artifact import ArtifactManifest
        
        manifest = ArtifactManifest()
        
        artifact1 = BuildArtifact(
            name="tokens",
            artifact_type=ArtifactType.TOKENS,
            path=Path("tokens.dat"),
        )
        artifact2 = BuildArtifact(
            name="ast",
            artifact_type=ArtifactType.AST,
            path=Path("ast.dat"),
        )
        
        manifest.add(artifact1)
        manifest.add(artifact2)
        
        assert manifest.count == 2
        assert manifest.get("tokens") is not None
        assert manifest.get("ast") is not None


# ============================================================================
# Pipeline Tests
# ============================================================================


class TestBuildPipeline:
    """Tests for BuildPipeline."""
    
    def test_pipeline_creation(self):
        """Test creating a pipeline."""
        with TemporaryDirectory() as tmpdir:
            pipeline = BuildPipeline(Path(tmpdir))
            
            assert pipeline.workspace_root == Path(tmpdir)
            assert pipeline.target_dir == Path(tmpdir) / "target"
    
    def test_pipeline_clean(self):
        """Test cleaning build artifacts."""
        with TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "target"
            target_dir.mkdir()
            (target_dir / "test.txt").write_text("test")
            
            pipeline = BuildPipeline(Path(tmpdir))
            pipeline.clean()
            
            assert not target_dir.exists() or not list(target_dir.iterdir())
