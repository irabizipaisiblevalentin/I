"""
Configuration data structures for I workspace.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class DependencySource(Enum):
    """Source of a dependency."""
    
    REGISTRY = "registry"
    PATH = "path"
    GIT = "git"


@dataclass(frozen=True)
class Dependency:
    """Dependency specification."""
    
    name: str
    version: str
    source: DependencySource = DependencySource.REGISTRY
    path: Optional[Path] = None
    git_url: Optional[str] = None
    git_rev: Optional[str] = None
    
    @classmethod
    def parse(cls, name: str, spec: Union[str, Dict[str, Any]]) -> Dependency:
        """
        Parse dependency from string or dictionary.
        
        Args:
            name: Dependency name
            spec: Version string or dictionary specification
            
        Returns:
            Parsed dependency
            
        Raises:
            ValueError: If specification is invalid
        """
        if isinstance(spec, str):
            return cls(
                name=name,
                version=spec,
                source=DependencySource.REGISTRY,
            )
        
        if isinstance(spec, dict):
            version = spec.get("version", "*")
            source = DependencySource.REGISTRY
            path = None
            git_url = None
            git_rev = None
            
            if "path" in spec:
                source = DependencySource.PATH
                path = Path(spec["path"])
            elif "git" in spec:
                source = DependencySource.GIT
                git_url = spec["git"]
                git_rev = spec.get("rev")
            
            return cls(
                name=name,
                version=version,
                source=source,
                path=path,
                git_url=git_url,
                git_rev=git_rev,
            )
        
        raise ValueError(f"Invalid dependency specification for {name}")


@dataclass(frozen=True)
class WorkspaceConfig:
    """Workspace configuration."""
    
    members: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    resolver: str = "default"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkspaceConfig:
        """Create from dictionary."""
        return cls(
            members=data.get("members", []),
            exclude=data.get("exclude", []),
            resolver=data.get("resolver", "default"),
        )


@dataclass(frozen=True)
class ProfileConfig:
    """Build profile configuration."""
    
    opt_level: int = 0
    debug: bool = False
    lto: bool = False
    codegen_units: Optional[int] = None
    panic: str = "unwind"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProfileConfig:
        """Create from dictionary."""
        return cls(
            opt_level=data.get("opt-level", 0),
            debug=data.get("debug", False),
            lto=data.get("lto", False),
            codegen_units=data.get("codegen-units"),
            panic=data.get("panic", "unwind"),
        )


@dataclass(frozen=True)
class Config:
    """
    Immutable workspace configuration.
    
    This is the main configuration structure for an I project.
    It is immutable after creation to ensure consistency.
    """
    
    # Package information
    name: str
    version: str
    edition: str = "1.0"
    authors: List[str] = field(default_factory=list)
    description: str = ""
    license: str = "MIT"
    repository: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Dependencies
    dependencies: Dict[str, Dependency] = field(default_factory=dict)
    dev_dependencies: Dict[str, Dependency] = field(default_factory=dict)
    build_dependencies: Dict[str, Dependency] = field(default_factory=dict)
    
    # Workspace
    workspace: Optional[WorkspaceConfig] = None
    
    # Profiles
    profile_dev: ProfileConfig = field(default_factory=ProfileConfig)
    profile_release: ProfileConfig = field(default_factory=lambda: ProfileConfig(opt_level=3, lto=True))
    
    # Paths (relative to workspace root)
    src_dir: str = "src"
    test_dir: str = "tests"
    example_dir: str = "examples"
    bench_dir: str = "benches"
    doc_dir: str = "docs"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Config:
        """
        Create config from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Configuration instance
        """
        package = data.get("package", {})
        
        # Parse dependencies
        dependencies = {}
        for name, spec in data.get("dependencies", {}).items():
            dependencies[name] = Dependency.parse(name, spec)
        
        dev_dependencies = {}
        for name, spec in data.get("dev-dependencies", {}).items():
            dev_dependencies[name] = Dependency.parse(name, spec)
        
        build_dependencies = {}
        for name, spec in data.get("build-dependencies", {}).items():
            build_dependencies[name] = Dependency.parse(name, spec)
        
        # Parse workspace
        workspace = None
        if "workspace" in data:
            workspace = WorkspaceConfig.from_dict(data["workspace"])
        
        # Parse profiles
        profile_dev = ProfileConfig.from_dict(data.get("profile", {}).get("dev", {}))
        profile_release = ProfileConfig.from_dict(data.get("profile", {}).get("release", {}))
        
        return cls(
            name=package.get("name", ""),
            version=package.get("version", "0.0.0"),
            edition=package.get("edition", "1.0"),
            authors=package.get("authors", []),
            description=package.get("description", ""),
            license=package.get("license", "MIT"),
            repository=package.get("repository"),
            keywords=package.get("keywords", []),
            categories=package.get("categories", []),
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            build_dependencies=build_dependencies,
            workspace=workspace,
            profile_dev=profile_dev,
            profile_release=profile_release,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert config to dictionary.
        
        Returns:
            Configuration dictionary
        """
        result: Dict[str, Any] = {
            "package": {
                "name": self.name,
                "version": self.version,
                "edition": self.edition,
                "authors": self.authors,
                "description": self.description,
                "license": self.license,
            }
        }
        
        if self.repository:
            result["package"]["repository"] = self.repository
        
        if self.keywords:
            result["package"]["keywords"] = self.keywords
        
        if self.categories:
            result["package"]["categories"] = self.categories
        
        # Dependencies
        if self.dependencies:
            result["dependencies"] = {
                name: dep.version if dep.source == DependencySource.REGISTRY else {"path": str(dep.path)}
                for name, dep in self.dependencies.items()
            }
        
        if self.dev_dependencies:
            result["dev-dependencies"] = {
                name: dep.version if dep.source == DependencySource.REGISTRY else {"path": str(dep.path)}
                for name, dep in self.dev_dependencies.items()
            }
        
        if self.build_dependencies:
            result["build-dependencies"] = {
                name: dep.version if dep.source == DependencySource.REGISTRY else {"path": str(dep.path)}
                for name, dep in self.build_dependencies.items()
            }
        
        # Workspace
        if self.workspace:
            result["workspace"] = {
                "members": self.workspace.members,
            }
        
        return result
    
    def get_all_dependencies(self) -> Dict[str, Dependency]:
        """
        Get all dependencies (main + dev + build).
        
        Returns:
            Combined dependencies dictionary
        """
        all_deps = {}
        all_deps.update(self.dependencies)
        all_deps.update(self.dev_dependencies)
        all_deps.update(self.build_dependencies)
        return all_deps
