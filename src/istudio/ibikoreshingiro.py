"""I STUDIO — Core types, enums, and configuration for the IDE platform."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class EditorTheme(enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    SOLARIZED = "solarized"
    MONOKAI = "monokai"
    CUSTOM = "custom"

class CursorStyle(enum.Enum):
    LINE = "line"
    BLOCK = "block"
    UNDERLINE = "underline"

class TabSize(enum.Enum):
    TWO = 2
    FOUR = 4
    EIGHT = 8

class FileType(enum.Enum):
    I_LANG = "i"
    PYTHON = "py"
    JAVASCRIPT = "js"
    TYPESCRIPT = "ts"
    RUST = "rs"
    GO = "go"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    MARKDOWN = "md"
    TEXT = "txt"

class DiagnosticSeverity(enum.Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"

class SymbolKind(enum.Enum):
    FILE = "file"
    MODULE = "module"
    NAMESPACE = "namespace"
    PACKAGE = "package"
    CLASS = "class"
    METHOD = "method"
    PROPERTY = "property"
    FIELD = "field"
    CONSTRUCTOR = "constructor"
    ENUM = "enum"
    INTERFACE = "interface"
    FUNCTION = "function"
    VARIABLE = "variable"
    CONSTANT = "constant"
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    KEY = "key"
    NULL = "null"
    ENUM_MEMBER = "enum_member"
    STRUCT = "struct"
    EVENT = "event"
    OPERATOR = "operator"
    TYPE_PARAMETER = "type_parameter"

class CompletionKind(enum.Enum):
    TEXT = "text"
    METHOD = "method"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    FIELD = "field"
    VARIABLE = "variable"
    CLASS = "class"
    STRUCT = "struct"
    INTERFACE = "interface"
    MODULE = "module"
    PROPERTY = "property"
    UNIT = "unit"
    VALUE = "value"
    ENUM = "enum"
    KEYWORD = "keyword"
    SNIPPET = "snippet"
    COLOR = "color"
    FILE = "file"
    REFERENCE = "reference"

class BreakpointType(enum.Enum):
    LINE = "line"
    CONDITIONAL = "conditional"
    LOG_POINT = "log_point"
    FUNCTION = "function"
    EXCEPTION = "exception"
    DATA = "data"

class DebuggerState(enum.Enum):
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"
    STOPPED = "stopped"
    BREAKPOINT = "breakpoint"
    EXCEPTION = "exception"

class ProfilerType(enum.Enum):
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    NETWORK = "network"
    DATABASE = "database"
    AI = "ai"
    CLOUD = "cloud"
    FRAME = "frame"

class PluginState(enum.Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    ERROR = "error"
    LOADING = "loading"

class CollaborationRole(enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class ProjectType(enum.Enum):
    WEBSITE = "website"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    AI_PROJECT = "ai_project"
    GAME = "game"
    OPERATING_SYSTEM = "operating_system"
    CLOUD_SERVICE = "cloud_service"
    DATABASE_PROJECT = "database_project"
    SCIENTIFIC_COMPUTING = "scientific_computing"
    INDUSTRIAL_AUTOMATION = "industrial_automation"
    ROBOTICS = "robotics"
    LIBRARY = "library"


PROJECT_TYPE_DISPLAY = {
    ProjectType.WEBSITE: "Website (Urubuga)",
    ProjectType.DESKTOP_APP: "Desktop App (Ibiro)",
    ProjectType.MOBILE_APP: "Mobile App",
    ProjectType.AI_PROJECT: "AI Project (Ubwenge)",
    ProjectType.GAME: "Game (Imikino)",
    ProjectType.OPERATING_SYSTEM: "Operating System (Sisitemu)",
    ProjectType.CLOUD_SERVICE: "Cloud Service (Igicu)",
    ProjectType.DATABASE_PROJECT: "Database Project (Ububiko)",
    ProjectType.SCIENTIFIC_COMPUTING: "Scientific Computing",
    ProjectType.INDUSTRIAL_AUTOMATION: "Industrial Automation",
    ProjectType.ROBOTICS: "Robotics",
    ProjectType.LIBRARY: "Library / Package",
}


class PanelLocation(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    BOTTOM = "bottom"
    TOP = "top"
    CENTER = "center"

# ─── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class EditorConfig:
    theme: EditorTheme = EditorTheme.DARK
    font_size: int = 14
    font_family: str = "Cascadia Code, Fira Code, monospace"
    tab_size: TabSize = TabSize.FOUR
    cursor_style: CursorStyle = CursorStyle.LINE
    auto_save: bool = True
    auto_save_interval_sec: int = 30
    word_wrap: bool = False
    line_numbers: bool = True
    minimap: bool = True
    code_folding: bool = True
    bracket_matching: bool = True
    format_on_save: bool = True
    suggest_on_trigger: bool = True
    suggest_on_character: bool = True

@dataclass
class WorkspaceConfig:
    name: str = "untitled"
    root_path: str = ""
    projects: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    extensions: List[str] = field(default_factory=list)

@dataclass
class ProjectConfig:
    name: str
    version: str = "0.1.0"
    type: str = "application"
    project_type: ProjectType = ProjectType.LIBRARY
    language: str = "i"
    entry_point: str = "main.i"
    dependencies: Dict[str, str] = field(default_factory=dict)
    build_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentPosition:
    line: int = 0
    column: int = 0

@dataclass
class DocumentRange:
    start: DocumentPosition = field(default_factory=DocumentPosition)
    end: DocumentPosition = field(default_factory=DocumentPosition)

@dataclass
class Diagnostic:
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR
    message: str = ""
    range: DocumentRange = field(default_factory=DocumentRange)
    source: str = "i"
    code: str = ""
    related_information: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class CompletionItem:
    label: str
    kind: CompletionKind = CompletionKind.TEXT
    detail: str = ""
    documentation: str = ""
    insert_text: str = ""
    sort_text: str = ""
    filter_text: str = ""

@dataclass
class SymbolInfo:
    name: str
    kind: SymbolKind = SymbolKind.VARIABLE
    range: DocumentRange = field(default_factory=DocumentRange)
    selection_range: DocumentRange = field(default_factory=DocumentRange)
    detail: str = ""
    children: List[SymbolInfo] = field(default_factory=list)

@dataclass
class Breakpoint:
    file: str = ""
    line: int = 0
    type: BreakpointType = BreakpointType.LINE
    condition: str = ""
    log_message: str = ""
    enabled: bool = True
    hit_count: int = 0

@dataclass
class StackFrame:
    id: int = 0
    name: str = ""
    file: str = ""
    line: int = 0
    column: int = 0
    module: str = ""

@dataclass
class VariableInfo:
    name: str = ""
    value: str = ""
    type: str = ""
    reference: int = 0
    children: List[VariableInfo] = field(default_factory=list)

@dataclass
class ProfileResult:
    type: ProfilerType = ProfilerType.CPU
    total_time_ms: float = 0.0
    call_count: int = 0
    memory_used_kb: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PluginManifest:
    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    min_istudio_version: str = "1.0.0"
    entry_point: str = ""
    permissions: List[str] = field(default_factory=list)
    contributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExtensionPoint:
    name: str
    description: str = ""
    handlers: List[str] = field(default_factory=list)

@dataclass
class TabInfo:
    id: str = ""
    title: str = ""
    file_path: str = ""
    language: str = "i"
    is_dirty: bool = False
    is_readonly: bool = False
    cursor_position: DocumentPosition = field(default_factory=DocumentPosition)

@dataclass
class SearchResult:
    file: str = ""
    line: int = 0
    column: int = 0
    match_length: int = 0
    line_content: str = ""

@dataclass
class RefactoringAction:
    name: str = ""
    description: str = ""
    file_edits: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class CodeAction:
    title: str = ""
    kind: str = ""
    diagnostics: List[Diagnostic] = field(default_factory=list)
    edit: Optional[Dict[str, Any]] = None
    command: Optional[Dict[str, Any]] = None

@dataclass
class HoverInfo:
    contents: List[str] = field(default_factory=list)
    range: Optional[DocumentRange] = None

@dataclass
class BuildTarget:
    name: str = ""
    kind: str = "executable"
    source_files: List[str] = field(default_factory=list)
    output: str = ""
    dependencies: List[str] = field(default_factory=list)

@dataclass
class TestResult:
    name: str = ""
    passed: bool = True
    duration_ms: float = 0.0
    error_message: str = ""
    stack_trace: str = ""

@dataclass
class ChatMessage:
    role: str = "user"
    content: str = ""
    timestamp: str = ""

@dataclass
class AICompletionRequest:
    code: str = ""
    language: str = "i"
    cursor_position: DocumentPosition = field(default_factory=DocumentPosition)
    context_before: str = ""
    context_after: str = ""

# ─── Project Templates ───────────────────────────────────────────────────────

@dataclass
class ProjectTemplate:
    project_type: ProjectType = ProjectType.LIBRARY
    display_name: str = "Library / Package"
    description: str = ""
    recommended_frameworks: List[str] = field(default_factory=list)
    build_system: str = "i build"
    test_framework: str = "i test"
    ci_template: str = ""
    ai_context: str = ""
    deployment_workflow: str = ""
    source_extensions: List[str] = field(default_factory=lambda: [".i"])
    entry_point: str = "main.i"
    initial_dirs: List[str] = field(default_factory=lambda: ["src", "tests"])
    initial_files: Dict[str, str] = field(default_factory=dict)
    debug_config: Dict[str, Any] = field(default_factory=dict)
    profiler_type: str = "cpu"


PROJECT_TEMPLATES: Dict[ProjectType, ProjectTemplate] = {
    ProjectType.WEBSITE: ProjectTemplate(
        project_type=ProjectType.WEBSITE,
        display_name="Website (Urubuga)",
        description="Web application with frontend and backend components",
        recommended_frameworks=["I Web", "Urubuga SSR", "HTMX", "Tailwind CSS"],
        build_system="i build --target web",
        test_framework="i test --browser",
        ci_template="web-ci",
        ai_context="This is a web project. Focus on HTML, CSS, JavaScript/TypeScript, "
                   "routing, forms, API endpoints, responsive design, accessibility, "
                   "and browser compatibility.",
        deployment_workflow="static-site / docker",
        source_extensions=[".i", ".html", ".css", ".js"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/components", "src/pages", "src/styles", "public", "tests"],
        initial_files={
            "src/main.i": "// Website entry point\nimport \"web\"\n\nfunction main() {\n    \n}\n",
            "src/styles/main.css": "/* Website styles */\n",
            "public/index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>New Website</title>\n</head>\n<body>\n    <div id=\"app\"></div>\n</body>\n</html>\n",
        },
        debug_config={"runtime": "browser", "port": 9229},
        profiler_type="cpu",
    ),
    ProjectType.DESKTOP_APP: ProjectTemplate(
        project_type=ProjectType.DESKTOP_APP,
        display_name="Desktop App (Ibiro)",
        description="Cross-platform desktop application",
        recommended_frameworks=["I Desktop", "GTK", "Qt", "Tauri"],
        build_system="i build --target desktop",
        test_framework="i test --gui",
        ci_template="desktop-ci",
        ai_context="This is a desktop application project. Focus on GUI components, event-driven "
                   "programming, file I/O, system tray, cross-platform compatibility, "
                   "and native OS integration.",
        deployment_workflow="installer / portable",
        source_extensions=[".i", ".py"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/ui", "src/models", "resources", "tests"],
        initial_files={
            "src/main.i": "// Desktop app entry point\nimport \"desktop\"\n\nfunction main() {\n    \n}\n",
        },
        debug_config={"runtime": "native", "port": 0},
        profiler_type="cpu",
    ),
    ProjectType.MOBILE_APP: ProjectTemplate(
        project_type=ProjectType.MOBILE_APP,
        display_name="Mobile App",
        description="Mobile application for iOS and Android",
        recommended_frameworks=["I Mobile", "React Native", "Flutter"],
        build_system="i build --target mobile",
        test_framework="i test --mobile",
        ci_template="mobile-ci",
        ai_context="This is a mobile app project. Focus on touch interfaces, responsive layouts, "
                   "native device APIs (camera, GPS, sensors), offline-first architecture, "
                   "app store deployment, and performance optimization for mobile.",
        deployment_workflow="app-store / play-store",
        source_extensions=[".i", ".dart", ".swift"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/screens", "src/components", "src/services", "resources", "tests"],
        initial_files={
            "src/main.i": "// Mobile app entry point\nimport \"mobile\"\n\nfunction main() {\n    \n}\n",
        },
        debug_config={"runtime": "mobile-simulator", "port": 8081},
        profiler_type="memory",
    ),
    ProjectType.AI_PROJECT: ProjectTemplate(
        project_type=ProjectType.AI_PROJECT,
        display_name="AI Project (Ubwenge)",
        description="Artificial intelligence and machine learning project",
        recommended_frameworks=["Ubwenge", "PyTorch", "TensorFlow", "scikit-learn"],
        build_system="i build --target ai",
        test_framework="i test --ai",
        ci_template="ai-ci",
        ai_context="This is an AI/ML project. Focus on model architecture, training pipelines, "
                   "data preprocessing, evaluation metrics, hyperparameter tuning, "
                   "model serving, and responsible AI practices.",
        deployment_workflow="model-server / onnx-export",
        source_extensions=[".i", ".py"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/models", "src/data", "src/training", "notebooks", "tests"],
        initial_files={
            "src/main.i": "// AI project entry point\nimport \"ubwenge\"\n\nfunction main() {\n    \n}\n",
        },
        debug_config={"runtime": "python", "port": 0},
        profiler_type="ai",
    ),
    ProjectType.GAME: ProjectTemplate(
        project_type=ProjectType.GAME,
        display_name="Game (Imikino)",
        description="2D/3D game project",
        recommended_frameworks=["Imikino Engine", "Godot", "Unity", "Unreal"],
        build_system="i build --target game",
        test_framework="i test --game",
        ci_template="game-ci",
        ai_context="This is a game project. Focus on game loop, physics, rendering, asset "
                   "management, animation, input handling, audio, level design, "
                   "and performance profiling.",
        deployment_workflow="steam / itch-io / app-store",
        source_extensions=[".i"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/scenes", "src/entities", "assets", "assets/textures", "assets/audio", "tests"],
        initial_files={
            "src/main.i": "// Game entry point\nimport \"imikino\"\n\nfunction main() {\n    \n}\n",
        },
        debug_config={"runtime": "game-engine", "port": 0},
        profiler_type="frame",
    ),
    ProjectType.OPERATING_SYSTEM: ProjectTemplate(
        project_type=ProjectType.OPERATING_SYSTEM,
        display_name="Operating System (Sisitemu)",
        description="Operating system or kernel project",
        recommended_frameworks=["Sisitemu SDK", "Linux", "Zephyr"],
        build_system="i build --target kernel",
        test_framework="i test --kernel",
        ci_template="kernel-ci",
        ai_context="This is an operating system / kernel project. Focus on memory management, "
                   "process scheduling, hardware abstraction, driver interfaces, "
                   "system calls, boot process, and performance optimization.",
        deployment_workflow="iso-image / firmware-flash",
        source_extensions=[".i", ".c", ".asm"],
        entry_point="kernel/main.i",
        initial_dirs=["kernel", "kernel/drivers", "kernel/mm", "kernel/sched", "lib", "tests"],
        initial_files={
            "kernel/main.i": "// Kernel entry point\nimport \"sisitemu\"\n\nfunction kmain() {\n    \n}\n",
        },
        debug_config={"runtime": "qemu", "port": 1234},
        profiler_type="cpu",
    ),
    ProjectType.CLOUD_SERVICE: ProjectTemplate(
        project_type=ProjectType.CLOUD_SERVICE,
        display_name="Cloud Service (Igicu)",
        description="Cloud-native microservice or serverless application",
        recommended_frameworks=["Igicu SDK", "AWS CDK", "Terraform", "Docker"],
        build_system="i build --target cloud",
        test_framework="i test --integration",
        ci_template="cloud-ci",
        ai_context="This is a cloud service project. Focus on microservices architecture, "
                   "containerization, serverless functions, API design (REST/GraphQL), "
                   "scaling, monitoring, CI/CD pipelines, and cloud provider best practices.",
        deployment_workflow="docker / kubernetes / serverless",
        source_extensions=[".i", ".yaml", ".json"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/handlers", "src/services", "deploy", "deploy/k8s", "tests"],
        initial_files={
            "src/main.i": "// Cloud service entry point\nimport \"igicu\"\n\nfunction handler(event) {\n    \n}\n",
            "Dockerfile": "FROM i-lang/runtime:latest\nCOPY . /app\nWORKDIR /app\nCMD [\"i\", \"run\", \"src/main.i\"]\n",
        },
        debug_config={"runtime": "container", "port": 8080},
        profiler_type="cloud",
    ),
    ProjectType.DATABASE_PROJECT: ProjectTemplate(
        project_type=ProjectType.DATABASE_PROJECT,
        display_name="Database Project (Ububiko)",
        description="Database schema, migrations, and data pipeline project",
        recommended_frameworks=["Ububiko ORM", "SQLAlchemy", "Prisma"],
        build_system="i build --target db",
        test_framework="i test --db",
        ci_template="db-ci",
        ai_context="This is a database project. Focus on schema design, migrations, query "
                   "optimization, data modeling, indexing strategies, replication, "
                   "backup/restore, and data pipeline orchestration.",
        deployment_workflow="migration-run / seed",
        source_extensions=[".i", ".sql"],
        entry_point="src/schema.i",
        initial_dirs=["src", "src/migrations", "src/seeds", "src/queries", "tests"],
        initial_files={
            "src/schema.i": "// Database schema\nimport \"ububiko\"\n\nschema MyDatabase {\n    \n}\n",
        },
        debug_config={"runtime": "database", "port": 5432},
        profiler_type="database",
    ),
    ProjectType.SCIENTIFIC_COMPUTING: ProjectTemplate(
        project_type=ProjectType.SCIENTIFIC_COMPUTING,
        display_name="Scientific Computing",
        description="Scientific computing, simulation, and numerical analysis",
        recommended_frameworks=["I Math", "NumPy", "SciPy", "Jupyter"],
        build_system="i build --target scientific",
        test_framework="i test --scientific",
        ci_template="scientific-ci",
        ai_context="This is a scientific computing project. Focus on numerical algorithms, "
                   "data analysis, visualization, simulation, parallel computing, "
                   "and reproducibility.",
        deployment_workflow="package / container",
        source_extensions=[".i", ".py"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/algorithms", "src/experiments", "data", "notebooks", "tests"],
        initial_files={
            "src/main.i": "// Scientific computing entry point\nimport \"math\"\n\nfunction main() {\n    \n}\n",
        },
        debug_config={"runtime": "native", "port": 0},
        profiler_type="cpu",
    ),
    ProjectType.INDUSTRIAL_AUTOMATION: ProjectTemplate(
        project_type=ProjectType.INDUSTRIAL_AUTOMATION,
        display_name="Industrial Automation",
        description="PLC programming, SCADA, and industrial control systems",
        recommended_frameworks=["I PLC", "IEC 61131-3", "CODESYS"],
        build_system="i build --target plc",
        test_framework="i test --plc",
        ci_template="industrial-ci",
        ai_context="This is an industrial automation project. Focus on PLC logic, safety-critical "
                   "systems, real-time control, sensor integration, HMI design, "
                   "and industrial protocol communication.",
        deployment_workflow="plc-flash / scada-deploy",
        source_extensions=[".i"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/plc", "src/hmi", "src/protocols", "tests"],
        initial_files={
            "src/main.i": "// Industrial automation entry point\nimport \"plc\"\n\nfunction main() {\n    \n}\n",
        },
        debug_config={"runtime": "plc-simulator", "port": 0},
        profiler_type="cpu",
    ),
    ProjectType.ROBOTICS: ProjectTemplate(
        project_type=ProjectType.ROBOTICS,
        display_name="Robotics",
        description="Robotics software including ROS nodes, firmware, and control systems",
        recommended_frameworks=["ROS 2", "I Robotics", "MicroPython"],
        build_system="i build --target robotics",
        test_framework="i test --robotics",
        ci_template="robotics-ci",
        ai_context="This is a robotics project. Focus on sensor fusion, kinematics, path planning, "
                   "control loops, real-time constraints, ROS integration, "
                   "and embedded systems programming.",
        deployment_workflow="firmware-flash / ros-launch",
        source_extensions=[".i", ".py", ".cpp"],
        entry_point="src/main.i",
        initial_dirs=["src", "src/nodes", "src/controllers", "src/sensors", "config", "tests"],
        initial_files={
            "src/main.i": "// Robotics entry point\nimport \"robotics\"\n\nfunction main() {\n    \n}\n",
        },
        debug_config={"runtime": "ros2", "port": 0},
        profiler_type="cpu",
    ),
    ProjectType.LIBRARY: ProjectTemplate(
        project_type=ProjectType.LIBRARY,
        display_name="Library / Package",
        description="Reusable library or package for the I ecosystem",
        recommended_frameworks=[],
        build_system="i build --target library",
        test_framework="i test",
        ci_template="library-ci",
        ai_context="This is a library/package project. Focus on clean APIs, documentation, "
                   "backward compatibility, comprehensive testing, "
                   "and dependency management.",
        deployment_workflow="publish-to-registry",
        source_extensions=[".i"],
        entry_point="src/lib.i",
        initial_dirs=["src", "tests"],
        initial_files={
            "src/lib.i": "// Library entry point\nexport function hello() {\n    return \"Hello from library!\"\n}\n",
        },
        debug_config={"runtime": "native", "port": 0},
        profiler_type="cpu",
    ),
}


# ─── Errors ─────────────────────────────────────────────────────────────────

class IStudioError(Exception):
    pass

class EditorError(IStudioError):
    pass

class LanguageServerError(IStudioError):
    pass

class DebuggerError(IStudioError):
    pass

class ProjectError(IStudioError):
    pass

class PluginError(IStudioError):
    pass

class BuildError(IStudioError):
    pass

ISTUDIO_VERSION = "1.0.0"
