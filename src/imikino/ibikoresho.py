"""ibikoresho — Asset pipeline: import, textures, meshes, materials, scenes, prefabs."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .ibikoreshingiro import Color, Vector2, Vector3
from .ishushanyo import Mesh, Material


class AssetType(str, Enum):
    TEXTURE = "texture"
    MESH = "mesh"
    MATERIAL = "material"
    SHADER = "shader"
    AUDIO = "audio"
    FONT = "font"
    SCENE = "scene"
    PREFAB = "prefab"
    SCRIPT = "script"
    ANIMATION = "animation"
    CONFIG = "config"
    UNKNOWN = "unknown"


@dataclass
class AssetMeta:
    path: str = ""
    name: str = ""
    asset_type: AssetType = AssetType.UNKNOWN
    guid: str = ""
    size_bytes: int = 0
    imported: bool = False
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Texture2D:
    name: str = ""
    path: str = ""
    width: int = 0
    height: int = 0
    channels: int = 4
    format: str = "rgba"
    mipmaps: bool = True
    filter: str = "linear"
    wrap: str = "repeat"
    data: Optional[bytes] = None
    loaded: bool = False


@dataclass
class Prefab:
    name: str = ""
    root_entity: Dict[str, Any] = field(default_factory=dict)
    components: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Font:
    name: str = ""
    path: str = ""
    size: int = 32
    character_set: str = "ascii"
    loaded: bool = False


class AssetImporter:
    def __init__(self):
        self.importers: Dict[str, Callable] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(".png", self._import_image)
        self.register(".jpg", self._import_image)
        self.register(".jpeg", self._import_image)
        self.register(".glb", self._import_model)
        self.register(".gltf", self._import_model)
        self.register(".obj", self._import_model)
        self.register(".wav", self._import_audio)
        self.register(".mp3", self._import_audio)
        self.register(".ttf", self._import_font)
        self.register(".otf", self._import_font)

    def register(self, extension: str, importer: Callable) -> None:
        self.importers[extension.lower()] = importer

    def import_asset(self, path: str) -> Optional[AssetMeta]:
        ext = Path(path).suffix.lower()
        importer = self.importers.get(ext)
        if importer:
            return importer(path)
        return None

    def _import_image(self, path: str) -> AssetMeta:
        meta = AssetMeta(path=path, name=Path(path).stem,
                         asset_type=AssetType.TEXTURE, imported=True)
        return meta

    def _import_model(self, path: str) -> AssetMeta:
        meta = AssetMeta(path=path, name=Path(path).stem,
                         asset_type=AssetType.MESH, imported=True)
        return meta

    def _import_audio(self, path: str) -> AssetMeta:
        meta = AssetMeta(path=path, name=Path(path).stem,
                         asset_type=AssetType.AUDIO, imported=True)
        return meta

    def _import_font(self, path: str) -> AssetMeta:
        meta = AssetMeta(path=path, name=Path(path).stem,
                         asset_type=AssetType.FONT, imported=True)
        return meta


class AssetDatabase:
    def __init__(self, asset_dir: str = "./assets"):
        self.asset_dir = Path(asset_dir)
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        self.assets: Dict[str, AssetMeta] = {}
        self.cache: Dict[str, Any] = {}
        self.importer = AssetImporter()

    def scan(self) -> List[AssetMeta]:
        self.assets.clear()
        for f in self.asset_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in self.importer.importers:
                meta = self.importer.import_asset(str(f))
                if meta:
                    self.assets[meta.guid or str(f)] = meta
        return list(self.assets.values())

    def get(self, guid_or_path: str) -> Optional[AssetMeta]:
        return self.assets.get(guid_or_path)

    def find_by_type(self, asset_type: AssetType) -> List[AssetMeta]:
        return [a for a in self.assets.values() if a.asset_type == asset_type]

    def find_by_name(self, name: str) -> Optional[AssetMeta]:
        for a in self.assets.values():
            if a.name == name:
                return a
        return None

    def create_material(self, name: str, albedo: Color = Color.white) -> Material:
        mat = Material(name=name, albedo=albedo)
        return mat

    def create_mesh(self, name: str) -> Mesh:
        mesh = Mesh(name=name)
        return mesh

    def save_prefab(self, name: str, data: Dict[str, Any]) -> str:
        path = str(self.asset_dir / f"{name}.prefab")
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def load_prefab(self, name: str) -> Optional[Dict[str, Any]]:
        path = self.asset_dir / f"{name}.prefab"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def refresh(self) -> None:
        self.cache.clear()
        self.scan()


_assets = AssetDatabase()


def get_assets() -> AssetDatabase:
    return _assets
