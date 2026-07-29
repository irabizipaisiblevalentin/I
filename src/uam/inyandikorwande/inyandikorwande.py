"""inyandikorwande — Component Registry with platform override resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from uam import PlatformTarget


@dataclass
class ComponentDefinition:
    """Metadata for a registered component.

    Attributes:
        name: Component name.
        module: Module path where the component is defined.
        class_name: Class name of the component.
        platform: Target platform for this definition (None = default).
        priority: Resolution priority (higher = preferred).
    """

    name: str
    module: str = ""
    class_name: str = ""
    platform: Optional[PlatformTarget] = None
    priority: int = 0


class ComponentRegistry:
    """Manages component registration with platform-specific overrides.

    Resolution order: platform override > default > base.

    Attributes:
        components: Dict of default components by name.
        overrides: Dict of platform-specific overrides.
        platform: Current PlatformTarget for resolution.
    """

    def __init__(self, platform: Optional[PlatformTarget] = None) -> None:
        self._components: Dict[str, ComponentDefinition] = {}
        self._overrides: Dict[str, Dict[PlatformTarget, ComponentDefinition]] = {}
        self._platform: Optional[PlatformTarget] = platform

    @property
    def components(self) -> Dict[str, ComponentDefinition]:
        return dict(self._components)

    @property
    def overrides(self) -> Dict[str, Dict[PlatformTarget, ComponentDefinition]]:
        return {k: dict(v) for k, v in self._overrides.items()}

    @property
    def platform(self) -> Optional[PlatformTarget]:
        return self._platform

    @platform.setter
    def platform(self, value: Optional[PlatformTarget]) -> None:
        self._platform = value

    def register(self, name: str,
                 component_class: Optional[Type] = None,
                 module: str = "",
                 class_name: str = "") -> ComponentDefinition:
        """Register a default component.

        Args:
            name: Component name.
            component_class: The component class (optional).
            module: Module path if component_class not given.
            class_name: Class name if component_class not given.

        Returns:
            The created ComponentDefinition.
        """
        if component_class is not None:
            module = module or getattr(component_class, "__module__", "")
            class_name = class_name or getattr(component_class, "__name__", "")
        definition = ComponentDefinition(
            name=name,
            module=module,
            class_name=class_name,
            platform=None,
            priority=0,
        )
        self._components[name] = definition
        return definition

    def register_override(self, name: str,
                          component_class: Optional[Type] = None,
                          platform: Optional[PlatformTarget] = None,
                          module: str = "",
                          class_name: str = "") -> Optional[ComponentDefinition]:
        """Register a platform-specific component override.

        Args:
            name: Component name.
            component_class: The override component class.
            platform: Target platform for this override.
            module: Module path if component_class not given.
            class_name: Class name if component_class not given.

        Returns:
            The created ComponentDefinition, or None if platform is invalid.
        """
        if platform is None:
            return None
        if component_class is not None:
            module = module or getattr(component_class, "__module__", "")
            class_name = class_name or getattr(component_class, "__name__", "")
        definition = ComponentDefinition(
            name=name,
            module=module,
            class_name=class_name,
            platform=platform,
            priority=10,
        )
        platform_overrides = self._overrides.setdefault(name, {})
        platform_overrides[platform] = definition
        return definition

    def resolve(self, name: str) -> Optional[ComponentDefinition]:
        """Resolve a component for the current platform.

        Resolution order:
            1. Platform-specific override
            2. Default component
            3. None if not found

        Args:
            name: Component name.

        Returns:
            The resolved ComponentDefinition, or None.
        """
        if self._platform and name in self._overrides:
            platform_overrides = self._overrides[name]
            if self._platform in platform_overrides:
                return platform_overrides[self._platform]
        return self._components.get(name)

    def has_component(self, name: str) -> bool:
        """Check if a component exists in the registry.

        Args:
            name: Component name.

        Returns:
            True if the component or an override is registered.
        """
        return name in self._components or name in self._overrides

    def list_components(self) -> List[str]:
        """List all registered component names.

        Returns:
            Sorted list of component names.
        """
        return sorted(set(self._components.keys()) | set(self._overrides.keys()))

    def list_overrides(self, platform: PlatformTarget) -> List[ComponentDefinition]:
        """List all overrides registered for a specific platform.

        Args:
            platform: The platform to filter by.

        Returns:
            List of ComponentDefinition overrides for that platform.
        """
        result: List[ComponentDefinition] = []
        for overrides in self._overrides.values():
            if platform in overrides:
                result.append(overrides[platform])
        return result

    def clear(self) -> None:
        """Remove all component registrations and overrides."""
        self._components.clear()
        self._overrides.clear()
