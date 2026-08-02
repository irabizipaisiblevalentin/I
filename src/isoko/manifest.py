"""manifest — Package manifest (ilang.toml) for isoko.

Defines the package.json-equivalent for the I programming language.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Manifest model
# ---------------------------------------------------------------------------

class Manifest:
    """Package manifest representing ilang.toml / ilang.json."""

    __slots__ = (
        "name", "version", "description", "authors", "license",
        "repository", "homepage", "keywords", "categories",
        "dependencies", "dev_dependencies", "build_dependencies",
        "features", "optional_dependencies",
        "scripts", "bin", "lib", "include", "exclude",
        "workspace", "publish_config", "engines",
        "_path", "_raw",
    )

    def __init__(self) -> None:
        self.name: str = ""
        self.version: str = "0.1.0"
        self.description: str = ""
        self.authors: List[Dict[str, str]] = []
        self.license: str = "MIT"
        self.repository: str = ""
        self.homepage: str = ""
        self.keywords: List[str] = []
        self.categories: List[str] = []
        self.dependencies: Dict[str, str] = {}
        self.dev_dependencies: Dict[str, str] = {}
        self.build_dependencies: Dict[str, str] = {}
        self.features: Dict[str, List[str]] = {}
        self.optional_dependencies: Dict[str, str] = {}
        self.scripts: Dict[str, str] = {}
        self.bin: Optional[str] = None
        self.lib: str = "lib"
        self.include: List[str] = ["lib/**"]
        self.exclude: List[str] = ["tests/**", "benchmarks/**"]
        self.workspace: Optional[str] = None
        self.publish_config: Dict[str, Any] = {}
        self.engines: Dict[str, str] = {}
        self._path: str = ""
        self._raw: Dict[str, Any] = {}

    @property
    def all_dependencies(self) -> Dict[str, str]:
        """All non-dev dependencies merged."""
        deps = dict(self.dependencies)
        deps.update(self.optional_dependencies)
        return deps

    @property
    def full_name(self) -> str:
        return f"{self.name}@{self.version}"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "package": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "license": self.license,
            }
        }
        if self.authors:
            d["package"]["authors"] = self.authors
        if self.repository:
            d["package"]["repository"] = self.repository
        if self.homepage:
            d["package"]["homepage"] = self.homepage
        if self.keywords:
            d["package"]["keywords"] = self.keywords
        if self.categories:
            d["package"]["categories"] = self.categories
        if self.engines:
            d["package"]["engines"] = self.engines

        if self.dependencies:
            d["dependencies"] = self.dependencies
        if self.dev_dependencies:
            d["dev-dependencies"] = self.dev_dependencies
        if self.build_dependencies:
            d["build-dependencies"] = self.build_dependencies
        if self.optional_dependencies:
            d["optional-dependencies"] = self.optional_dependencies
        if self.features:
            d["features"] = self.features
        if self.scripts:
            d["scripts"] = self.scripts
        if self.bin:
            d["bin"] = self.bin
        if self.lib:
            d["lib"] = self.lib
        if self.include:
            d["include"] = self.include
        if self.exclude:
            d["exclude"] = self.exclude
        if self.workspace:
            d["workspace"] = self.workspace
        if self.publish_config:
            d["publish"] = self.publish_config
        return d


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_toml_simple(text: str) -> Dict[str, Any]:
    """Minimal TOML parser for ilang.toml (handles our subset)."""
    result: Dict[str, Any] = {}
    current_table = result
    table_path: List[str] = []

    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Table header [package] or [dependencies]
        if line.startswith("[") and line.endswith("]"):
            inner = line[1:-1].strip()
            if inner.startswith("[["):
                continue  # array of tables — skip for now
            table_path = inner.split(".")
            current_table = result
            for key in table_path:
                current_table = current_table.setdefault(key, {})
            continue

        # Key = value
        if "=" in line:
            key, _, val = line.partition("=")
            key = key.strip().strip('"')
            val = val.strip()

            # Remove comments (but not inside strings)
            if val.startswith("#"):
                continue
            if "#" in val:
                in_string = False
                quote_char = ""
                for i, ch in enumerate(val):
                    if ch in ('"', "'") and not in_string:
                        in_string = True
                        quote_char = ch
                    elif ch == quote_char and in_string:
                        in_string = False
                        quote_char = ""
                if not in_string:
                    val = val[:val.rfind("#")].strip()

            parsed_val = _parse_toml_value(val)
            current_table[key] = parsed_val

    return result


def _parse_toml_value(val: str) -> Any:
    """Parse a TOML value."""
    val = val.strip()

    # String
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]

    # Boolean
    if val.lower() in ("true", "yes"):
        return True
    if val.lower() in ("false", "no"):
        return False

    # Integer
    try:
        return int(val)
    except ValueError:
        pass

    # Float
    try:
        return float(val)
    except ValueError:
        pass

    # Array
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        items = []
        for item in _split_toml_array(inner):
            items.append(_parse_toml_value(item))
        return items

    # Inline table
    if val.startswith("{") and val.endswith("}"):
        inner = val[1:-1].strip()
        if not inner:
            return {}
        d = {}
        for pair in _split_toml_array(inner):
            if "=" in pair:
                k, _, v = pair.partition("=")
                d[k.strip()] = _parse_toml_value(v.strip())
        return d

    return val


def _split_toml_array(s: str) -> List[str]:
    """Split a TOML array/inline-table content respecting nesting."""
    items = []
    depth = 0
    current = ""
    in_string = False
    for ch in s:
        if ch in ('"', "'") and not in_string:
            in_string = True
            current += ch
        elif ch in ('"', "'") and in_string:
            in_string = False
            current += ch
        elif ch in ("{", "[") and not in_string:
            depth += 1
            current += ch
        elif ch in ("}", "]") and not in_string:
            depth -= 1
            current += ch
        elif ch == "," and depth == 0 and not in_string:
            items.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        items.append(current.strip())
    return items


# ---------------------------------------------------------------------------
# Load / Save
# ---------------------------------------------------------------------------

def load(path: str) -> Manifest:
    """Load a manifest from ilang.toml or ilang.json."""
    m = Manifest()
    m._path = path

    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    elif path.endswith(".toml"):
        with open(path, "r", encoding="utf-8-sig") as f:
            data = _parse_toml_simple(f.read())
    else:
        # Try both
        toml_path = os.path.join(os.path.dirname(path) or ".", "ilang.toml")
        json_path = os.path.join(os.path.dirname(path) or ".", "ilang.json")
        if os.path.exists(toml_path):
            return load(toml_path)
        elif os.path.exists(json_path):
            return load(json_path)
        raise FileNotFoundError(f"manifest not found: {path}")

    m._raw = data
    pkg = data.get("package", {})
    m.name = pkg.get("name", "")
    m.version = pkg.get("version", "0.1.0")
    m.description = pkg.get("description", "")
    m.license = pkg.get("license", "MIT")
    m.repository = pkg.get("repository", "")
    m.homepage = pkg.get("homepage", "")
    m.keywords = pkg.get("keywords", [])
    m.categories = pkg.get("categories", [])
    m.authors = pkg.get("authors", [])
    m.engines = pkg.get("engines", {})

    m.dependencies = data.get("dependencies", {})
    m.dev_dependencies = data.get("dev-dependencies", {})
    m.build_dependencies = data.get("build-dependencies", {})
    m.optional_dependencies = data.get("optional-dependencies", {})
    m.features = data.get("features", {})
    m.scripts = data.get("scripts", {})
    m.bin = data.get("bin")
    m.lib = data.get("lib", "lib")
    m.include = data.get("include", ["lib/**"])
    m.exclude = data.get("exclude", ["tests/**", "benchmarks/**"])
    m.workspace = data.get("workspace")
    m.publish_config = data.get("publish", {})
    return m


def save(manifest: Manifest, path: str) -> None:
    """Save manifest to JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2)


def find_manifest(start: str = ".") -> Optional[str]:
    """Walk up directories to find ilang.toml or ilang.json."""
    current = os.path.abspath(start)
    for _ in range(50):
        for name in ("ilang.toml", "ilang.json"):
            path = os.path.join(current, name)
            if os.path.isfile(path):
                return path
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None
