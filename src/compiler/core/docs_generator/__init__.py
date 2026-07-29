"""
Documentation Generator

Generates documentation from code and AST.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DocItem:
    """A documentation item."""

    name: str
    kind: str  # "function", "struct", "class", etc.
    description: str = ""
    parameters: list[dict[str, str]] = field(default_factory=list)
    return_type: str | None = None
    source_file: str | None = None
    line: int | None = None

    def to_markdown(self) -> str:
        """Convert to markdown."""
        lines = [f"## {self.name}\n"]

        if self.description:
            lines.append(f"{self.description}\n")

        if self.parameters:
            lines.append("### Parameters\n")
            lines.append("| Name | Type | Description |")
            lines.append("|------|------|-------------|")
            for param in self.parameters:
                lines.append(
                    f"| {param.get('name', '')} | "
                    f"{param.get('type', '')} | "
                    f"{param.get('description', '')} |"
                )
            lines.append("")

        if self.return_type:
            lines.append(f"**Returns:** {self.return_type}\n")

        if self.source_file:
            location = f"`{self.source_file}`"
            if self.line:
                location += f":{self.line}"
            lines.append(f"**Defined in:** {location}\n")

        return "\n".join(lines)


class DocumentationGenerator:
    """
    Generates documentation from code.
    """

    def __init__(self) -> None:
        self._items: list[DocItem] = []

    def add_item(self, item: DocItem) -> None:
        """Add a documentation item."""
        self._items.append(item)

    def generate_markdown(self) -> str:
        """Generate markdown documentation."""
        lines = ["# I Language API Documentation\n"]

        # Group by kind
        by_kind: dict[str, list[DocItem]] = {}
        for item in self._items:
            by_kind.setdefault(item.kind, []).append(item)

        for kind, items in sorted(by_kind.items()):
            lines.append(f"\n## {kind.title()}s\n")
            for item in items:
                lines.append(item.to_markdown())

        return "\n".join(lines)

    def save(self, path: str) -> None:
        """Save documentation to file."""
        from pathlib import Path

        content = self.generate_markdown()
        Path(path).write_text(content, encoding="utf-8")
