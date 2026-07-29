"""
Configuration validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import Config, Dependency, DependencySource, WorkspaceConfig

# Validation patterns
PACKAGE_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$")
EDITION_PATTERN = re.compile(r"^\d{4}$")


@dataclass(frozen=True)
class ValidationError:
    """Validation error details."""

    code: str
    message: str
    path: str | None = None
    suggestion: str | None = None

    def __str__(self) -> str:
        """Format error message."""
        result = f"[{self.code}] {self.message}"
        if self.path:
            result += f" (in {self.path})"
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
        return result


class ConfigValidator:
    """
    Validates I workspace configuration.

    Performs comprehensive validation of configuration files
    to catch errors early in the build process.
    """

    # Valid editions
    VALID_EDITIONS = {"1.0", "2024", "2025", "2026"}

    # Valid licenses (SPDX identifiers)
    COMMON_LICENSES = {
        "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
        "GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0",
        "ISC", "MPL-2.0", "Unlicense", "CC0-1.0",
    }

    def validate(self, config: Config, path: Path | None = None) -> list[ValidationError]:
        """
        Validate configuration.

        Args:
            config: Configuration to validate
            path: Optional path to configuration file (for error messages)

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[ValidationError] = []

        # Validate package information
        errors.extend(self._validate_package(config, path))

        # Validate dependencies
        errors.extend(self._validate_dependencies(config.dependencies, "dependencies", path))
        errors.extend(self._validate_dependencies(config.dev_dependencies, "dev-dependencies", path))
        errors.extend(self._validate_dependencies(config.build_dependencies, "build-dependencies", path))

        # Validate workspace
        if config.workspace:
            errors.extend(self._validate_workspace(config.workspace, path))

        return errors

    def is_valid(self, config: Config) -> bool:
        """
        Check if configuration is valid.

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        return len(self.validate(config)) == 0

    def _validate_package(self, config: Config, path: Path | None) -> list[ValidationError]:
        """
        Validate package information.

        Args:
            config: Configuration to validate
            path: Optional path for error messages

        Returns:
            List of validation errors
        """
        errors: list[ValidationError] = []
        path_str = str(path) if path else None

        # Validate name
        name_error = self._validate_name(config.name, path_str)
        if name_error:
            errors.append(name_error)

        # Validate version
        version_error = self._validate_version(config.version, path_str)
        if version_error:
            errors.append(version_error)

        # Validate edition
        edition_error = self._validate_edition(config.edition, path_str)
        if edition_error:
            errors.append(edition_error)

        # Validate license (if provided)
        if config.license:
            license_error = self._validate_license(config.license, path_str)
            if license_error:
                errors.append(license_error)

        return errors

    def _validate_name(self, name: str, path: str | None = None) -> ValidationError | None:
        """
        Validate package name.

        Args:
            name: Package name to validate
            path: Optional path for error message

        Returns:
            Validation error, or None if valid
        """
        if not name:
            return ValidationError(
                code="W001",
                message="Package name is required",
                path=path,
                suggestion="Add a name field to the [package] section",
            )

        if not PACKAGE_NAME_PATTERN.match(name):
            return ValidationError(
                code="W002",
                message=f"Invalid package name: {name}",
                path=path,
                suggestion="Package names must start with a letter and contain only letters, numbers, hyphens, and underscores",
            )

        return None

    def _validate_version(self, version: str, path: str | None = None) -> ValidationError | None:
        """
        Validate version string.

        Args:
            version: Version string to validate
            path: Optional path for error message

        Returns:
            Validation error, or None if valid
        """
        if not version:
            return ValidationError(
                code="W003",
                message="Package version is required",
                path=path,
                suggestion="Add a version field to the [package] section",
            )

        if not VERSION_PATTERN.match(version):
            return ValidationError(
                code="W004",
                message=f"Invalid version format: {version}",
                path=path,
                suggestion="Version must follow semantic versioning (e.g., 1.0.0, 0.1.0-beta.1)",
            )

        return None

    def _validate_edition(self, edition: str, path: str | None = None) -> ValidationError | None:
        """
        Validate edition.

        Args:
            edition: Edition to validate
            path: Optional path for error message

        Returns:
            Validation error, or None if valid
        """
        if not edition:
            return ValidationError(
                code="W005",
                message="Edition is required",
                path=path,
                suggestion="Add an edition field to the [package] section",
            )

        if edition not in self.VALID_EDITIONS:
            return ValidationError(
                code="W006",
                message=f"Invalid edition: {edition}",
                path=path,
                suggestion=f"Valid editions are: {', '.join(sorted(self.VALID_EDITIONS))}",
            )

        return None

    def _validate_license(self, license_id: str, path: str | None = None) -> ValidationError | None:
        """
        Validate license identifier.

        Args:
            license_id: License identifier to validate
            path: Optional path for error message

        Returns:
            Validation error, or None if valid
        """
        # Only warn for common licenses, don't enforce
        if license_id not in self.COMMON_LICENSES:
            return ValidationError(
                code="W011",
                message=f"Uncommon license identifier: {license_id}",
                path=path,
                suggestion="Consider using a standard SPDX license identifier",
            )

        return None

    def _validate_dependencies(
        self,
        dependencies: dict[str, Dependency],
        section: str,
        path: Path | None,
    ) -> list[ValidationError]:
        """
        Validate dependencies.

        Args:
            dependencies: Dependencies to validate
            section: Section name for error messages
            path: Optional path for error messages

        Returns:
            List of validation errors
        """
        errors: list[ValidationError] = []
        path_str = str(path) if path else None

        for name, dep in dependencies.items():
            # Validate dependency name
            if not PACKAGE_NAME_PATTERN.match(name):
                errors.append(ValidationError(
                    code="W007",
                    message=f"Invalid dependency name: {name}",
                    path=path_str,
                    suggestion="Dependency names must follow the same rules as package names",
                ))

            # Validate dependency version
            if dep.source == DependencySource.REGISTRY:
                version_error = self._validate_version(dep.version, path_str)
                if version_error:
                    errors.append(ValidationError(
                        code="W007",
                        message=f"Invalid version for dependency {name}: {dep.version}",
                        path=path_str,
                    ))

            # Validate path dependency
            if dep.path is not None:
                if not dep.path.exists():
                    errors.append(ValidationError(
                        code="W009",
                        message=f"Path dependency not found: {dep.path}",
                        path=path_str,
                        suggestion="Ensure the path exists and is correct",
                    ))

        return errors

    def _validate_workspace(
        self,
        workspace: WorkspaceConfig,
        path: Path | None,
    ) -> list[ValidationError]:
        """
        Validate workspace configuration.

        Args:
            workspace: Workspace configuration to validate
            path: Optional path for error messages

        Returns:
            List of validation errors
        """
        errors: list[ValidationError] = []
        path_str = str(path) if path else None

        for member in workspace.members:
            # Basic path validation
            if not member:
                errors.append(ValidationError(
                    code="W010",
                    message="Empty workspace member path",
                    path=path_str,
                ))

        return errors
