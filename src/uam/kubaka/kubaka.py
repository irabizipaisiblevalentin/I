"""kubaka — UAMBuildSystem for cross-platform builds."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uam import PlatformTarget, detect_platform
from uam.inyandikorwande.inyandikorwande import ComponentRegistry


@dataclass
class PlatformManifest:
    """Describes the files and services for a platform build.

    Attributes:
        files: List of file paths included in the build.
        overrides: Component overrides for this platform.
        services: Platform service registrations.
        entry_point: Main entry point file path.
    """

    files: List[str] = field(default_factory=list)
    overrides: Dict[str, str] = field(default_factory=dict)
    services: Dict[str, str] = field(default_factory=dict)
    entry_point: str = ""


@dataclass
class BuildConfig:
    """Build configuration loaded from uam.yaml.

    Attributes:
        name: Application name.
        version: Application version.
        author: Application author.
        shared_dirs: Directories containing shared code.
        platforms: Target platforms for building.
        output: Output directory path.
    """

    name: str = ""
    version: str = "0.1.0"
    author: str = ""
    shared_dirs: List[str] = field(default_factory=lambda: ["shared", "ui"])
    platforms: List[str] = field(default_factory=lambda: ["web", "desktop", "mobile"])
    output: str = "dist"


_PLATFORM_DIR_MAP: Dict[PlatformTarget, str] = {
    PlatformTarget.URUBUGA: "web",
    PlatformTarget.IBIRO: "desktop",
    PlatformTarget.MOBILE: "mobile",
}


class UAMBuildSystem:
    """Build system that compiles UAM applications for target platforms.

    Attributes:
        target: The target PlatformTarget.
        config: BuildConfig loaded from configuration.
        output_dir: Base output directory.
        shared_path: Path to shared/ directory.
        ui_path: Path to ui/ directory.
    """

    def __init__(self, target: Optional[PlatformTarget] = None,
                 config_path: str = "") -> None:
        self._target: PlatformTarget = target or detect_platform()
        self._config: BuildConfig = BuildConfig()
        self._output_dir: str = "dist"
        self.shared_path: str = ""
        self.ui_path: str = ""

        if config_path:
            self.load_config(config_path)

    @property
    def target(self) -> PlatformTarget:
        return self._target

    @property
    def config(self) -> BuildConfig:
        return self._config

    @property
    def output_dir(self) -> str:
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value: str) -> None:
        self._output_dir = value

    def load_config(self, path: str) -> BuildConfig:
        """Load build configuration from a uam.yaml file.

        Args:
            path: Path to uam.yaml configuration file.

        Returns:
            Loaded BuildConfig instance.
        """
        if not os.path.isfile(path):
            return self._config

        import yaml as _yaml
        with open(path, "r", encoding="utf-8") as f:
            data = _yaml.safe_load(f) or {}

        self._config.name = data.get("name", self._config.name)
        self._config.version = data.get("version", self._config.version)
        self._config.author = data.get("author", self._config.author)
        self._config.shared_dirs = data.get("shared_dirs", self._config.shared_dirs)
        self._config.platforms = data.get("platforms", self._config.platforms)
        self._config.output = data.get("output", self._config.output)
        self._output_dir = self._config.output

        return self._config

    def build(self) -> Dict[str, Any]:
        """Build the application for the configured target.

        Returns:
            Build result dictionary.
        """
        platform_dir = _PLATFORM_DIR_MAP.get(self._target, "web")
        output = os.path.join(self._output_dir, platform_dir)
        os.makedirs(output, exist_ok=True)

        self._copy_shared(output)
        self._copy_ui(output)
        self._copy_platform(output)
        self.generate_entry(self._target)

        return {
            "success": True,
            "target": self._target.value,
            "output": output,
            "config": {
                "name": self._config.name,
                "version": self._config.version,
            },
        }

    def build_web(self, output: str = "") -> Dict[str, Any]:
        """Build for web platform (urubuga).

        Args:
            output: Output directory.

        Returns:
            Build result dictionary.
        """
        self._target = PlatformTarget.URUBUGA
        if output:
            self._output_dir = output
        return self.build()

    def build_desktop(self, output: str = "") -> Dict[str, Any]:
        """Build for desktop platform (ibiro).

        Args:
            output: Output directory.

        Returns:
            Build result dictionary.
        """
        self._target = PlatformTarget.IBIRO
        if output:
            self._output_dir = output
        return self.build()

    def build_mobile(self, output: str = "") -> Dict[str, Any]:
        """Build for mobile platform (MOBILE).

        Args:
            output: Output directory.

        Returns:
            Build result dictionary.
        """
        self._target = PlatformTarget.MOBILE
        if output:
            self._output_dir = output
        return self.build()

    def build_all(self, output: str = "") -> Dict[str, Any]:
        """Build for all supported platforms.

        Args:
            output: Base output directory.

        Returns:
            Build result dictionary with per-platform results.
        """
        base_output = output or self._output_dir
        results: Dict[str, Any] = {}
        for platform in PlatformTarget:
            self._target = platform
            platform_out = os.path.join(base_output, platform.value)
            os.makedirs(platform_out, exist_ok=True)
            results[platform.value] = self.build()
        return {"success": True, "results": results}

    def run(self) -> Dict[str, Any]:
        """Run the application on the configured target platform.

        Returns:
            Result dictionary with status.
        """
        from uam.porogaramu.porogaramu import UAMApplication
        app = UAMApplication(self._config.name, self._config.version, self._target)
        app.run()
        return {"success": True, "target": self._target.value, "name": self._config.name}

    def analyze(self) -> Dict[str, Any]:
        """Analyze code sharing across platforms.

        Returns:
            Analysis dictionary with shared code statistics.
        """
        stats: Dict[str, Any] = {
            "shared_files": [],
            "platform_files": {p.value: [] for p in PlatformTarget},
            "overrides": {p.value: [] for p in PlatformTarget},
            "total_files": 0,
            "shared_percentage": 0.0,
        }

        for root, _dirs, files in os.walk("."):
            parts = root.replace(os.sep, "/").split("/")
            for f in files:
                if not f.endswith((".py", ".i", ".yaml", ".json")):
                    continue
                rel = os.path.join(root, f)
                stats["total_files"] += 1
                if "shared" in parts:
                    stats["shared_files"].append(rel)
                for p in PlatformTarget:
                    if _PLATFORM_DIR_MAP[p] in parts:
                        stats["platform_files"][p.value].append(rel)

        shared_count = len(stats["shared_files"])
        total = stats["total_files"]
        stats["shared_percentage"] = round((shared_count / max(total, 1)) * 100, 1)

        return stats

    def generate_entry(self, platform: PlatformTarget) -> str:
        """Generate a platform-specific entry point file.

        Args:
            platform: Target platform.

        Returns:
            Path to the generated entry point.
        """
        platform_dir = _PLATFORM_DIR_MAP.get(platform, "web")
        output = os.path.join(self._output_dir, platform_dir)
        os.makedirs(output, exist_ok=True)

        entry_name = f"main_{platform.value}.py"
        entry_path = os.path.join(output, entry_name)

        entry_content = f'''"""{self._config.name} — {platform.value} entry point."""

from uam.porogaramu.porogaramu import UAMApplication
from uam import PlatformTarget

app = UAMApplication(
    name="{self._config.name}",
    version="{self._config.version}",
    target=PlatformTarget.{platform.name},
)

app.load_shared("shared")
app.load_ui("ui")

if __name__ == "__main__":
    app.run()
'''

        with open(entry_path, "w", encoding="utf-8") as f:
            f.write(entry_content)

        return entry_path

    def validate(self) -> Dict[str, Any]:
        """Validate the UAM project structure.

        Checks for required directories and configuration.

        Returns:
            Validation result dictionary.
        """
        issues: List[str] = []
        checks: Dict[str, bool] = {}

        required_dirs = ["shared", "ui", "web", "desktop", "mobile"]
        for d in required_dirs:
            exists = os.path.isdir(d)
            checks[f"dir_{d}"] = exists
            if not exists:
                issues.append(f"Missing required directory: {d}/")

        checks["uam_yaml"] = os.path.isfile("uam.yaml")
        if not checks["uam_yaml"]:
            issues.append("Missing uam.yaml configuration file")

        return {
            "valid": len(issues) == 0,
            "checks": checks,
            "issues": issues,
        }

    def _copy_shared(self, output: str) -> None:
        if os.path.isdir(self.shared_path):
            dest = os.path.join(output, "shared")
            shutil.copytree(self.shared_path, dest, dirs_exist_ok=True)

    def _copy_ui(self, output: str) -> None:
        if os.path.isdir(self.ui_path):
            dest = os.path.join(output, "ui")
            shutil.copytree(self.ui_path, dest, dirs_exist_ok=True)

    def _copy_platform(self, output: str) -> None:
        platform_dir = _PLATFORM_DIR_MAP.get(self._target, "web")
        if os.path.isdir(platform_dir):
            shutil.copytree(platform_dir, output, dirs_exist_ok=True)
