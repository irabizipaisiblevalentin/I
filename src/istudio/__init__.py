"""I STUDIO — Integrated Development Environment and Developer Experience Platform."""

from __future__ import annotations

from .ibikoreshingiro import (
    ISTUDIO_VERSION,
    EditorConfig,
    ProjectConfig,
    ProjectTemplate,
    ProjectType,
    PROJECT_TEMPLATES,
    PROJECT_TYPE_DISPLAY,
    WorkspaceConfig,
)
from .akazi import WorkspaceManager, ProjectManager
from .indura import EditorEngine
from .ururimi import LanguageServer
from .ugutunganya import Debugger
from .gupima import Profiler, CPUSampler, MemorySampler
from .igishushanyo import VisualDesigner, FormDesigner, UIComponent, FormField, FormLayout
from .umufasha import AIAssistant
from .ibikoresho_ububiko import DatabaseExplorer
from .ibikoresho_igicu import CloudExplorer
from .ibikoresho_imikino import GameDesigner
from .ibikoresho_sisitemu import SystemExplorer
from .porogaramu import ExtensionManager
from .iterambere import CollaborationManager
from .ibikoresho_rusange import EventBus, LRUCache

__all__ = [
    "ISTUDIO_VERSION",
    "EditorConfig",
    "WorkspaceConfig",
    "ProjectConfig",
    "ProjectTemplate",
    "ProjectType",
    "PROJECT_TEMPLATES",
    "PROJECT_TYPE_DISPLAY",
    "WorkspaceManager",
    "ProjectManager",
    "EditorEngine",
    "LanguageServer",
    "Debugger",
    "Profiler",
    "CPUSampler",
    "MemorySampler",
    "VisualDesigner",
    "FormDesigner",
    "UIComponent",
    "FormField",
    "FormLayout",
    "AIAssistant",
    "DatabaseExplorer",
    "CloudExplorer",
    "GameDesigner",
    "SystemExplorer",
    "ExtensionManager",
    "CollaborationManager",
    "EventBus",
    "LRUCache",
]
