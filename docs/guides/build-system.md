# Build System

## Overview

The Build System manages the compilation pipeline for I projects. It handles task scheduling, dependency resolution, incremental builds, and build caching.

## Quick Start

### Basic Build

```python
from pathlib import Path
from src.compiler.core.build import BuildPipeline, BuildTask, TaskType, TaskResult

# Create a task
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
```

### Multi-Task Build

```python
from src.compiler.core.build import BuildPipeline, BuildTask, TaskType, TaskResult

# Define tasks with dependencies
lex = BuildTask(name="lex", task_type=TaskType.LEX, action=lex_action)
parse = BuildTask(name="parse", task_type=TaskType.PARSE, action=parse_action)
analyze = BuildTask(name="analyze", task_type=TaskType.ANALYZE, action=analyze_action)

# Create pipeline
pipeline = BuildPipeline(Path("."))
pipeline.add_task(lex)
pipeline.add_task(parse)
pipeline.add_task(analyze)

# Add dependencies
pipeline.add_dependency("parse", "lex")
pipeline.add_dependency("analyze", "parse")

# Execute
result = pipeline.build()
```

## API Reference

### BuildPipeline

```python
class BuildPipeline:
    """Main build pipeline interface."""
    
    def __init__(self, workspace_root: Path, config: Optional[BuildConfig] = None):
        """Initialize build pipeline."""
    
    def add_task(self, task: BuildTask) -> None:
        """Add task to pipeline."""
    
    def add_dependency(self, task_name: str, depends_on: str) -> None:
        """Add dependency between tasks."""
    
    def build(self, targets: Optional[List[str]] = None) -> BuildResult:
        """Execute build pipeline."""
    
    def clean(self) -> None:
        """Clean build artifacts."""
    
    def incremental(self, changed_files: List[Path]) -> BuildResult:
        """Perform incremental build."""
```

### BuildTask

```python
@dataclass
class BuildTask:
    """Single build task."""
    
    name: str
    task_type: TaskType
    inputs: List[Path] = field(default_factory=list)
    outputs: List[Path] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    action: Optional[Callable[[], TaskResult]] = None
    
    def execute(self) -> TaskResult:
        """Execute the task."""
    
    def get_cache_key(self) -> str:
        """Generate cache key for this task."""
```

### TaskType

```python
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
```

### BuildProfile

```python
@dataclass(frozen=True)
class BuildProfile:
    """Build profile configuration."""
    
    name: str
    optimization: OptimizationLevel
    debug: DebugLevel
    lto: bool
    codegen_units: Optional[int]
    panic: str
    incremental: bool
    
    @classmethod
    def dev(cls) -> BuildProfile:
        """Create development profile."""
    
    @classmethod
    def release(cls) -> BuildProfile:
        """Create release profile."""
    
    @classmethod
    def test(cls) -> BuildProfile:
        """Create test profile."""
    
    @classmethod
    def bench(cls) -> BuildProfile:
        """Create benchmark profile."""
```

## Build Pipeline Stages

```
Source Files
    ↓
[LEX] Tokenization
    ↓
[PARSE] AST Generation
    ↓
[ANALYZE] Semantic Analysis
    ↓
[CHECK] Type Checking
    ↓
[IRGEN] IR Generation
    ↓
[OPTIMIZE] Optimization
    ↓
[CODEGEN] Code Generation
    ↓
[LINK] Linking
    ↓
Output Binary
```

## Caching

The build system caches artifacts to enable incremental builds.

### Cache Keys

Cache keys are computed from:
- Task type
- Input file contents
- Configuration hash

### Cache Storage

```
target/
├── cache/
│   ├── build-cache.json
│   └── ...
└── output/
    └── {binary}
```

## Error Codes

| Code | Description |
|------|-------------|
| B001 | Build task failed |
| B002 | Missing input file |
| B003 | Invalid build target |
| B004 | Circular dependency detected |
| B005 | Cache corruption detected |
| B006 | Build timeout exceeded |
| B007 | Out of memory |
| B008 | Disk space insufficient |

## Examples

### Development Build

```python
config = BuildConfig(profile=BuildProfile.dev())
pipeline = BuildPipeline(Path("."), config)
result = pipeline.build()
```

### Release Build

```python
config = BuildConfig(profile=BuildProfile.release())
pipeline = BuildPipeline(Path("."), config)
result = pipeline.build()
```

### Clean Build

```python
pipeline = BuildPipeline(Path("."))
pipeline.clean()
result = pipeline.build()
```

### Build Specific Target

```python
pipeline = BuildPipeline(Path("."))
result = pipeline.build(targets=["parse", "analyze"])
```

## Security Considerations

1. **Sandboxing**: Build tasks run in sandboxed environment
2. **File permissions**: Only write to designated directories
3. **Network access**: No network access during builds
4. **Resource limits**: CPU and memory limits enforced

## Performance Considerations

1. **Parallel execution**: Tasks run in parallel when possible
2. **Incremental builds**: Only rebuild changed files
3. **Caching**: Cache and reuse build artifacts
4. **Memory management**: Stream large files instead of loading

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije*
