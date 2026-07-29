"""
Configuration schema validation.
"""

from __future__ import annotations

from typing import Any


class ConfigError(Exception):
    """Configuration error."""

    def __init__(self, message: str, path: str | None = None) -> None:
        super().__init__(message)
        self.path = path


class ConfigSchema:
    """
    Configuration schema validator.

    Validates configuration dictionaries against expected structure.
    """

    REQUIRED_FIELDS: list[str] = []

    OPTIONAL_FIELDS: dict[str, type] = {
        "name": str,
        "version": str,
        "source_dirs": list,
        "output_dir": str,
        "stdlib_path": str,
        "build": dict,
        "features": dict,
    }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> list[str]:
        """
        Validate configuration data.

        Args:
            data: Configuration dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[str] = []

        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        for field, expected_type in cls.OPTIONAL_FIELDS.items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(
                    f"Invalid type for '{field}': "
                    f"expected {expected_type.__name__}, "
                    f"got {type(data[field]).__name__}"
                )

        return errors

    @classmethod
    def validate_build(cls, data: dict[str, Any]) -> list[str]:
        """Validate build configuration."""
        errors: list[str] = []

        valid_optimization = {"none", "basic", "standard", "aggressive"}
        if "optimization" in data:
            if data["optimization"] not in valid_optimization:
                errors.append(f"Invalid optimization level: {data['optimization']}")

        valid_debug = {"none", "line_numbers", "full"}
        if "debug_info" in data:
            if data["debug_info"] not in valid_debug:
                errors.append(f"Invalid debug level: {data['debug_info']}")

        return errors

    @classmethod
    def validate_features(cls, data: dict[str, Any]) -> list[str]:
        """Validate feature flags."""
        errors: list[str] = []

        valid_features = {
            "experimental_generics",
            "experimental_coroutines",
            "experimental_pattern_matching",
            "unsafe_mode",
        }

        for key in data:
            if key not in valid_features:
                errors.append(f"Unknown feature flag: {key}")
            elif not isinstance(data[key], bool):
                errors.append(f"Feature flag '{key}' must be boolean")

        return errors
