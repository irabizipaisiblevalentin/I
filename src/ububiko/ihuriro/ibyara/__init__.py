"""ibyara — Target generators for the IHuriro Unified Model Generator.

Each generator produces target-specific code/config from a CanonicalModel.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ububiko.ihuriro.ihuriro import CanonicalModel


class BaseGenerator:
    """Base class for all generators."""

    target_name: str = "base"

    @classmethod
    def generate(cls, model: CanonicalModel) -> Dict[str, str]:
        """Generate artifacts for a single model.

        Returns dict mapping filename to content string.
        """
        raise NotImplementedError

    @classmethod
    def target(cls) -> str:
        return cls.target_name


from ububiko.ihuriro.ibyara.amakubi import DatabaseGenerator
from ububiko.ihuriro.ibyara.kugenzura import ValidationGenerator
from ububiko.ihuriro.ibyara.rest import RestApiGenerator
from ububiko.ihuriro.ibyara.graphql import GraphQLGenerator
from ububiko.ihuriro.ibyara.urutonde import SerializationGenerator
from ububiko.ihuriro.ibyara.ifishi import FormGenerator
from ububiko.ihuriro.ibyara.admin import AdminGenerator
from ububiko.ihuriro.ibyara.inyandiko import DocumentationGenerator
from ububiko.ihuriro.ibyara.ikizamini import TestDataGenerator
from ububiko.ihuriro.ibyara.ubwenge import EmbeddingGenerator

__all__ = [
    "BaseGenerator",
    "DatabaseGenerator",
    "ValidationGenerator",
    "RestApiGenerator",
    "GraphQLGenerator",
    "SerializationGenerator",
    "FormGenerator",
    "AdminGenerator",
    "DocumentationGenerator",
    "TestDataGenerator",
    "EmbeddingGenerator",
]
