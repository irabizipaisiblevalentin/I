"""porogaramu — UAMApplication, the cross-platform application orchestrator."""

from __future__ import annotations

import importlib
import inspect
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Type

from ufa.core import Application as UFAApplication

from uam.inyandikorwande.inyandikorwande import ComponentRegistry
from uam import PlatformTarget, detect_platform


class UAMApplication(UFAApplication):
    """Cross-platform application that adapts to the target runtime.

    Extends the UFA Application with platform-aware component resolution,
    service registration, and build/run capabilities for web, desktop,
    and mobile targets.

    Attributes:
        name: Application name.
        version: Application version string.
        target: The target PlatformTarget.
        component_registry: Registry of UI components and overrides.
        shared_path: Path to shared/ directory.
        ui_path: Path to ui/ directory.
        platform_path: Path to platform-specific directory.
        services: Registered service implementations.
    """

    def __init__(self, name: str = "uam-app", version: str = "0.1.0",
                 target: Optional[PlatformTarget] = None) -> None:
        super().__init__(name, version)
        self._target: PlatformTarget = target or detect_platform()
        self._component_registry = ComponentRegistry(self._target)
        self._shared_path: str = ""
        self._ui_path: str = ""
        self._platform_path: str = ""
        self._services: Dict[str, Any] = {}
        self._build_output: str = ""

    @property
    def target(self) -> PlatformTarget:
        return self._target

    @target.setter
    def target(self, value: PlatformTarget) -> None:
        self._target = value
        self._component_registry = ComponentRegistry(value)

    @property
    def component_registry(self) -> ComponentRegistry:
        return self._component_registry

    @property
    def shared_path(self) -> str:
        return self._shared_path

    @property
    def ui_path(self) -> str:
        return self._ui_path

    @property
    def platform_path(self) -> str:
        return self._platform_path

    @property
    def services(self) -> Dict[str, Any]:
        return dict(self._services)

    def load_shared(self, path: str) -> List[str]:
        """Load all modules from the shared/ directory.

        Args:
            path: Path to the shared/ directory.

        Returns:
            List of module names successfully loaded.
        """
        self._shared_path = os.path.abspath(path)
        return self._load_modules(self._shared_path)

    def load_ui(self, path: str) -> List[str]:
        """Load all modules from the ui/ directory.

        Args:
            path: Path to the ui/ directory.

        Returns:
            List of module names successfully loaded.
        """
        self._ui_path = os.path.abspath(path)
        self._discover_components(self._ui_path)
        return self._load_modules(self._ui_path)

    def resolve_component(self, name: str) -> Optional[Any]:
        """Resolve a component using the registry's resolution order.

        Checks platform override first, then ui/, then framework default.

        Args:
            name: Component name.

        Returns:
            The resolved component class, or None if not found.
        """
        resolved = self._component_registry.resolve(name)
        if resolved is not None:
            return resolved

        try:
            module = importlib.import_module(f"ui.components.{name}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                return obj
        except (ImportError, ModuleNotFoundError):
            pass

        return None

    def register_service(self, name: str, impl: Any) -> None:
        """Register a service implementation.

        Args:
            name: Service name.
            impl: Service implementation instance or class.
        """
        self._services[name] = impl
        self.emit("service.registered", {"name": name, "service": impl})

    def get_service(self, name: str) -> Optional[Any]:
        """Retrieve a registered service by name.

        Args:
            name: Service name.

        Returns:
            The service implementation, or None if not found.
        """
        return self._services.get(name)

    def build(self) -> Dict[str, Any]:
        """Build the application for the configured target platform.

        Returns:
            Build result dictionary with status and metadata.
        """
        from uam.kubaka.kubaka import UAMBuildSystem
        builder = UAMBuildSystem(self._target)
        builder.shared_path = self._shared_path
        builder.ui_path = self._ui_path

        if self._target == PlatformTarget.URUBUGA:
            result = builder.build_web(self._build_output)
        elif self._target == PlatformTarget.IBIRO:
            result = builder.build_desktop(self._build_output)
        elif self._target == PlatformTarget.MOBILE:
            result = builder.build_mobile(self._build_output)
        else:
            result = builder.build_all(self._build_output)

        self.emit("app.built", {"target": self._target.value, "result": result})
        return result

    def run(self) -> None:
        """Run the application on the detected target platform."""
        self.emit("app.starting", {"target": self._target.value})
        super().run()
        self.logger.info(f"UAMApplication '{self.name}' running on {self._target.value}")
        self.emit("app.running", {"target": self._target.value})

    def detect_target(self) -> PlatformTarget:
        """Auto-detect target platform and update the application.

        Returns:
            The detected PlatformTarget.
        """
        detected = detect_platform()
        self._target = detected
        self._component_registry = ComponentRegistry(detected)
        return detected

    def _load_modules(self, base_path: str) -> List[str]:
        if not os.path.isdir(base_path):
            return []
        loaded: List[str] = []
        for root, _dirs, files in os.walk(base_path):
            for fname in files:
                if not fname.endswith((".py", ".i")):
                    continue
                rel_path = os.path.relpath(os.path.join(root, fname), base_path)
                mod_name = rel_path.replace(os.sep, ".").rsplit(".", 1)[0]
                if mod_name in sys.modules:
                    continue
                try:
                    importlib.import_module(mod_name)
                    loaded.append(mod_name)
                except (ImportError, ModuleNotFoundError):
                    pass
        return loaded

    def _discover_components(self, ui_path: str) -> None:
        components_dir = os.path.join(ui_path, "components")
        if not os.path.isdir(components_dir):
            return
        for fname in os.listdir(components_dir):
            if fname.endswith((".py", ".i")):
                name = fname.rsplit(".", 1)[0]
                self._component_registry.register(name, None)
