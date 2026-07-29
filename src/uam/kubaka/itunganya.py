"""itunganya — ProjectAnalyzer for cross-platform coverage analysis."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Set

from uam import PlatformTarget
from uam.inyandikorwande.inyandikorwande import ComponentRegistry


_PLATFORM_DIRS: Dict[PlatformTarget, str] = {
    PlatformTarget.URUBUGA: "web",
    PlatformTarget.IBIRO: "desktop",
    PlatformTarget.MOBILE: "mobile",
}


class ProjectAnalyzer:
    """Analyzes UAM project structure for cross-platform coverage.

    Provides statistics on shared code percentages, unresolved components,
    orphan overrides, and generates coverage reports.
    """

    def __init__(self, root_path: str = ".") -> None:
        self._root = os.path.abspath(root_path)
        self._registry: ComponentRegistry = ComponentRegistry()

    @property
    def root(self) -> str:
        return self._root

    def analyze_project(self, path: str = "") -> Dict[str, Any]:
        """Analyze project structure and return statistics.

        Args:
            path: Path to project root. Defaults to current.

        Returns:
            Dictionary with project statistics.
        """
        base = os.path.abspath(path or self._root)
        stats: Dict[str, Any] = {
            "root": base,
            "directories": {},
            "files": {},
            "total_files": 0,
            "total_dirs": 0,
        }

        for root, dirs, files in os.walk(base):
            rel = os.path.relpath(root, base)
            if rel == ".":
                rel = ""
            for d in dirs:
                stats["total_dirs"] += 1
            for f in files:
                if f.endswith((".py", ".i")):
                    cat = self._categorize_file(rel)
                    stats["files"].setdefault(cat, []).append(
                        os.path.join(rel, f) if rel else f
                    )
                    stats["total_files"] += 1

        for root, dirs, _files in os.walk(base):
            rel = os.path.relpath(root, base)
            if rel == ".":
                rel = ""
            for d in dirs:
                cat = self._categorize_file(os.path.join(rel, d) if rel else d)
                stats["directories"].setdefault(cat, []).append(d)

        return stats

    def calculate_shared_percentage(self, path: str = "") -> float:
        """Calculate the percentage of code shared across platforms.

        Args:
            path: Path to project root.

        Returns:
            Percentage of files in shared/ and ui/ (shared code).
        """
        base = os.path.abspath(path or self._root)
        total = 0
        shared = 0

        for root, _dirs, files in os.walk(base):
            for f in files:
                if not f.endswith((".py", ".i")):
                    continue
                total += 1
                rel = os.path.relpath(root, base)
                parts = rel.replace(os.sep, "/").split("/")
                if "shared" in parts or "ui" in parts:
                    shared += 1

        return round((shared / max(total, 1)) * 100, 1)

    def find_unresolved_components(self, path: str = "") -> List[str]:
        """Find components registered but lacking implementations.

        Scans ui/components/ for declared components and checks
        if each has a corresponding implementation.

        Args:
            path: Path to project root.

        Returns:
            List of component names without implementations.
        """
        base = os.path.abspath(path or self._root)
        unresolved: List[str] = []

        ui_components_dir = os.path.join(base, "ui", "components")
        if not os.path.isdir(ui_components_dir):
            return unresolved

        for fname in os.listdir(ui_components_dir):
            if not fname.endswith((".py", ".i")):
                continue
            name = fname.rsplit(".", 1)[0]
            self._registry.register(name)
            resolved = self._resolve_implementation(base, name)
            if resolved is None:
                unresolved.append(name)

        return unresolved

    def find_orphan_overrides(self, path: str = "") -> List[str]:
        """Find platform overrides without a base component.

        Args:
            path: Path to project root.

        Returns:
            List of override component names missing a base.
        """
        base = os.path.abspath(path or self._root)
        orphans: List[str] = []

        for platform, dir_name in _PLATFORM_DIRS.items():
            overrides_dir = os.path.join(base, dir_name, "components")
            if not os.path.isdir(overrides_dir):
                continue
            for fname in os.listdir(overrides_dir):
                if not fname.endswith((".py", ".i")):
                    continue
                name = fname.rsplit(".", 1)[0]
                base_path = os.path.join(base, "ui", "components", fname)
                if not os.path.isfile(base_path):
                    orphans.append(f"{name} ({platform.value})")

        return orphans

    def generate_report(self, path: str = "") -> str:
        """Generate a human-readable cross-platform coverage report.

        Args:
            path: Path to project root.

        Returns:
            Formatted report string.
        """
        base = os.path.abspath(path or self._root)
        stats = self.analyze_project(base)
        shared_pct = self.calculate_shared_percentage(base)
        unresolved = self.find_unresolved_components(base)
        orphans = self.find_orphan_overrides(base)

        lines: List[str] = []
        lines.append("=" * 60)
        lines.append(f"  UAM Cross-Platform Coverage Report")
        lines.append(f"  Project: {base}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"  Total files:       {stats['total_files']}")
        lines.append(f"  Shared code:       {shared_pct}%")
        lines.append("")
        lines.append("  Files by category:")
        for cat, files in sorted(stats["files"].items()):
            lines.append(f"    {cat:12s}: {len(files)}")
        lines.append("")
        lines.append(f"  Unresolved components: {len(unresolved)}")
        for c in unresolved:
            lines.append(f"    - {c}")
        lines.append("")
        lines.append(f"  Orphan overrides:     {len(orphans)}")
        for o in orphans:
            lines.append(f"    - {o}")
        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _categorize_file(self, rel_path: str) -> str:
        parts = rel_path.replace(os.sep, "/").split("/")
        for p in parts:
            if p == "shared":
                return "shared"
            if p == "ui":
                return "ui"
            if p == "web":
                return "web"
            if p == "desktop":
                return "desktop"
            if p == "mobile":
                return "mobile"
        return "other"

    def _resolve_implementation(self, base: str, name: str) -> Optional[str]:
        for platform, dir_name in _PLATFORM_DIRS.items():
            override_path = os.path.join(base, dir_name, "components", f"{name}.py")
            if os.path.isfile(override_path):
                return override_path
            override_path_i = os.path.join(base, dir_name, "components", f"{name}.i")
            if os.path.isfile(override_path_i):
                return override_path_i
        ui_path = os.path.join(base, "ui", "components", f"{name}.py")
        if os.path.isfile(ui_path):
            return ui_path
        ui_path_i = os.path.join(base, "ui", "components", f"{name}.i")
        if os.path.isfile(ui_path_i):
            return ui_path_i
        return None
