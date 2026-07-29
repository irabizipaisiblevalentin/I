"""IGICU — Container Runtime: images, registry, build, execution."""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    ContainerConfig, ContainerRuntimeType, ContainerStatus,
    ImageConfig, ImagePullPolicy, NetworkMode,
    ContainerError, IGICU_VERSION,
)


class ImageRegistry:
    def __init__(self, registry_dir: Optional[str] = None):
        self.registry_dir = registry_dir or os.path.join(
            os.path.expanduser("~"), ".igicu", "registry"
        )
        self._images: Dict[str, ImageConfig] = {}

    def register(self, config: ImageConfig) -> str:
        image_id = f"{config.name}:{config.tag}"
        self._images[image_id] = config
        self._save_metadata(image_id, config)
        return image_id

    def get(self, name: str, tag: str = "latest") -> Optional[ImageConfig]:
        image_id = f"{name}:{tag}"
        if image_id in self._images:
            return self._images[image_id]
        return self._load_metadata(image_id)

    def list(self) -> List[Dict[str, Any]]:
        result = []
        for image_id, config in self._images.items():
            result.append({
                "id": image_id,
                "tag": config.tag,
                "size_mb": config.size_mb,
                "created": config.created,
            })
        return result

    def remove(self, name: str, tag: str = "latest") -> bool:
        image_id = f"{name}:{tag}"
        if image_id in self._images:
            del self._images[image_id]
            meta_path = self._meta_path(image_id)
            if meta_path.exists():
                meta_path.unlink()
            return True
        return False

    def search(self, query: str) -> List[Dict[str, Any]]:
        results = []
        for image_id, config in self._images.items():
            if query.lower() in image_id.lower():
                results.append({
                    "id": image_id,
                    "tag": config.tag,
                    "size_mb": config.size_mb,
                })
        return results

    def _meta_path(self, image_id: str) -> Path:
        safe_name = image_id.replace(":", "_").replace("/", "_")
        return Path(self.registry_dir) / f"{safe_name}.json"

    def _save_metadata(self, image_id: str, config: ImageConfig) -> None:
        path = self._meta_path(image_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "name": config.name,
            "tag": config.tag,
            "digest": config.digest,
            "layers": config.layers,
            "size_mb": config.size_mb,
            "created": config.created or time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "runtime": config.runtime.value,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_metadata(self, image_id: str) -> Optional[ImageConfig]:
        path = self._meta_path(image_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ImageConfig(
                name=data["name"],
                tag=data.get("tag", "latest"),
                digest=data.get("digest"),
                layers=data.get("layers", []),
                size_mb=data.get("size_mb", 0.0),
                created=data.get("created"),
                runtime=ContainerRuntimeType(data.get("runtime", "igicu")),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def __len__(self) -> int:
        return len(self._images)


class ImageBuilder:
    def __init__(self, registry: Optional[ImageRegistry] = None):
        self.registry = registry or ImageRegistry()

    def build(self, name: str, context_dir: str, tag: str = "latest",
              layers: Optional[List[str]] = None) -> ImageConfig:
        context = Path(context_dir)
        if not context.exists():
            raise ContainerError(f"Build context '{context_dir}' not found")

        dockerfile = context / "Dockerfile"
        igicu_file = context / "igicu.json"

        config = ImageConfig(
            name=name,
            tag=tag,
            layers=layers or [],
            size_mb=0.0,
            created=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        if igicu_file.exists():
            try:
                build_config = json.loads(igicu_file.read_text(encoding="utf-8"))
                config.layers = build_config.get("layers", [])
                config.size_mb = sum(
                    os.path.getsize(os.path.join(context, f))
                    for f in build_config.get("files", [])
                    if os.path.exists(os.path.join(context, f))
                ) / (1024 * 1024)
            except (json.JSONDecodeError, KeyError):
                pass
        elif dockerfile.exists():
            layers = self._parse_dockerfile(str(dockerfile))
            config.layers = layers
            config.size_mb = sum(
                os.path.getsize(f) for f in context.rglob("*")
                if f.is_file()
            ) / (1024 * 1024)
        else:
            config.layers = [f"layer-{i}" for i in range(3)]
            config.size_mb = 10.0

        self.registry.register(config)
        return config

    def _parse_dockerfile(self, path: str) -> List[str]:
        layers = []
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.upper().startswith(("FROM ", "RUN ", "COPY ", "ADD ", "WORKDIR ")):
                        layers.append(line)
        except OSError:
            pass
        return layers

    def list_images(self) -> List[Dict[str, Any]]:
        return self.registry.list()


class ContainerRuntime:
    def __init__(self, runtime_type: ContainerRuntimeType = ContainerRuntimeType.IGICU):
        self.runtime_type = runtime_type
        self._containers: Dict[str, Dict[str, Any]] = {}

    def create(self, config: ContainerConfig) -> str:
        container_id = f"igicu-{uuid.uuid4().hex[:12]}"
        self._containers[container_id] = {
            "id": container_id,
            "config": config,
            "status": ContainerStatus.CREATED.value,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "started": None,
            "pid": None,
            "network": config.network,
        }
        return container_id

    def start(self, container_id: str) -> bool:
        container = self._containers.get(container_id)
        if not container:
            raise ContainerError(f"Container '{container_id}' not found")
        if container["status"] != ContainerStatus.CREATED.value:
            raise ContainerError(f"Cannot start container in state: {container['status']}")
        container["status"] = ContainerStatus.RUNNING.value
        container["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        return True

    def stop(self, container_id: str) -> bool:
        container = self._containers.get(container_id)
        if not container:
            raise ContainerError(f"Container '{container_id}' not found")
        container["status"] = ContainerStatus.STOPPED.value
        return True

    def remove(self, container_id: str) -> bool:
        if container_id in self._containers:
            del self._containers[container_id]
            return True
        return False

    def get(self, container_id: str) -> Optional[Dict[str, Any]]:
        return self._containers.get(container_id)

    def list(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [c for c in self._containers.values() if c["status"] == status]
        return list(self._containers.values())

    def exec(self, container_id: str, command: List[str]) -> Dict[str, Any]:
        container = self._containers.get(container_id)
        if not container:
            raise ContainerError(f"Container '{container_id}' not found")
        return {
            "container_id": container_id,
            "command": command,
            "output": f"[simulated] Executed: {' '.join(command)}",
            "exit_code": 0,
        }

    def logs(self, container_id: str, tail: int = 100) -> List[str]:
        container = self._containers.get(container_id)
        if not container:
            raise ContainerError(f"Container '{container_id}' not found")
        return [f"[{container['created']}] Container {container_id} created"]

    def inspect(self, container_id: str) -> Optional[Dict[str, Any]]:
        return self._containers.get(container_id)


class BuildPipeline:
    def __init__(self, registry: Optional[ImageRegistry] = None):
        self.registry = registry or ImageRegistry()
        self.builder = ImageBuilder(registry)

    def build_and_push(self, name: str, context_dir: str, tag: str = "latest") -> ImageConfig:
        config = self.builder.build(name, context_dir, tag)
        print(f"Built image {name}:{tag} ({config.size_mb:.1f}MB)")
        return config

    def deploy_container(self, config: ContainerConfig) -> str:
        runtime = ContainerRuntime()
        container_id = runtime.create(config)
        runtime.start(container_id)
        return container_id
