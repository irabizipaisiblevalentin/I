"""ibicu — Cloud infrastructure: containers, VMs, load balancing, orchestration, secrets management."""

from __future__ import annotations

import enum
import hashlib
import json
import os
import random
import string
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set


class ContainerState(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class VMState(Enum):
    POWERED_OFF = "off"
    POWERED_ON = "on"
    SUSPENDED = "suspended"
    MIGRATING = "migrating"
    ERROR = "error"


class LBAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED = "weighted"
    RANDOM = "random"


class DeploymentStrategy(Enum):
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


@dataclass
class NamespaceConfig:
    pid: bool = True
    net: bool = True
    mnt: bool = True
    uts: bool = True
    ipc: bool = True
    user: bool = False


@dataclass
class CGroupConfig:
    cpu_shares: int = 1024
    cpu_quota: int = -1
    cpu_period: int = 100000
    memory_limit_mb: int = 512
    memory_swap_mb: int = 1024
    pids_limit: int = 256
    io_weight: int = 500


@dataclass
class ContainerImage:
    name: str = ""
    tag: str = "latest"
    digest: str = ""
    layers: List[str] = field(default_factory=list)
    entrypoint: str = "/bin/sh"
    cmd: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    ports: List[int] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.name}:{self.tag}"


@dataclass
class Container:
    container_id: str = ""
    name: str = ""
    image: str = ""
    state: ContainerState = ContainerState.CREATED
    pid: int = 0
    namespace: NamespaceConfig = field(default_factory=NamespaceConfig)
    cgroups: CGroupConfig = field(default_factory=CGroupConfig)
    env: Dict[str, str] = field(default_factory=dict)
    ports: Dict[int, int] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    created_at: float = 0.0
    started_at: float = 0.0
    exit_code: int = 0
    resource_usage: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.container_id,
            "name": self.name,
            "image": self.image,
            "state": self.state.value,
            "pid": self.pid,
            "ports": self.ports,
            "created": self.created_at,
        }


class ContainerRuntime:
    def __init__(self):
        self._containers: Dict[str, Container] = {}
        self._images: Dict[str, ContainerImage] = {}
        self._lock = threading.Lock()

    def create_image(self, name: str, tag: str = "latest") -> ContainerImage:
        with self._lock:
            key = f"{name}:{tag}"
            if key not in self._images:
                img = ContainerImage(name=name, tag=tag)
                img.digest = hashlib.sha256(f"{name}:{tag}:{time.time()}".encode()).hexdigest()
                self._images[key] = img
            return self._images[key]

    def create_container(self, name: str, image: str,
                         config: Optional[Dict[str, Any]] = None) -> Container:
        with self._lock:
            c = Container(
                container_id=str(uuid.uuid4())[:12],
                name=name,
                image=image,
                state=ContainerState.CREATED,
                created_at=time.time(),
            )
            if config:
                if "ports" in config:
                    c.ports = config["ports"]
                if "env" in config:
                    c.env = config["env"]
                if "volumes" in config:
                    c.volumes = config["volumes"]
                if "cgroups" in config:
                    for k, v in config["cgroups"].items():
                        if hasattr(c.cgroups, k):
                            setattr(c.cgroups, k, v)
            self._containers[c.container_id] = c
            return c

    def start_container(self, container_id: str) -> bool:
        with self._lock:
            c = self._containers.get(container_id)
            if not c or c.state != ContainerState.CREATED:
                return False
            c.state = ContainerState.RUNNING
            c.pid = random.randint(1000, 60000)
            c.started_at = time.time()
            return True

    def stop_container(self, container_id: str) -> bool:
        with self._lock:
            c = self._containers.get(container_id)
            if not c or c.state != ContainerState.RUNNING:
                return False
            c.state = ContainerState.STOPPED
            c.exit_code = 0
            return True

    def pause_container(self, container_id: str) -> bool:
        with self._lock:
            c = self._containers.get(container_id)
            if not c or c.state != ContainerState.RUNNING:
                return False
            c.state = ContainerState.PAUSED
            return True

    def remove_container(self, container_id: str) -> bool:
        with self._lock:
            if container_id in self._containers:
                del self._containers[container_id]
                return True
            return False

    def get_container(self, container_id: str) -> Optional[Container]:
        with self._lock:
            return self._containers.get(container_id)

    def list_containers(self, state: Optional[ContainerState] = None) -> List[Container]:
        with self._lock:
            if state:
                return [c for c in self._containers.values() if c.state == state]
            return list(self._containers.values())

    def get_resource_usage(self, container_id: str) -> Dict[str, float]:
        c = self.get_container(container_id)
        if not c:
            return {}
        return {
            "cpu_percent": random.uniform(0.1, 50.0),
            "memory_mb": random.uniform(10, c.cgroups.memory_limit_mb),
            "network_rx_bytes": random.randint(1000, 1000000),
            "network_tx_bytes": random.randint(1000, 1000000),
        }

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            states: Dict[str, int] = {}
            for c in self._containers.values():
                s = c.state.value
                states[s] = states.get(s, 0) + 1
            return {"containers": len(self._containers), "states": states}


@dataclass
class VirtualMachine:
    vm_id: str = ""
    name: str = ""
    vcpus: int = 2
    memory_mb: int = 4096
    disk_gb: int = 50
    image: str = ""
    state: VMState = VMState.POWERED_OFF
    host: str = ""
    ip_address: str = ""
    mac_address: str = ""
    ssh_key: str = ""
    created_at: float = 0.0
    metadata: Dict[str, str] = field(default_factory=dict)


class VMManager:
    def __init__(self):
        self._vms: Dict[str, VirtualMachine] = {}
        self._lock = threading.Lock()

    def create_vm(self, name: str, image: str,
                  vcpus: int = 2, memory_mb: int = 4096, disk_gb: int = 50) -> VirtualMachine:
        with self._lock:
            vm = VirtualMachine(
                vm_id=str(uuid.uuid4())[:8],
                name=name,
                vcpus=vcpus,
                memory_mb=memory_mb,
                disk_gb=disk_gb,
                image=image,
                state=VMState.POWERED_OFF,
                mac_address=":".join(f"{random.randint(0, 255):02x}" for _ in range(6)),
                created_at=time.time(),
            )
            self._vms[vm.vm_id] = vm
            return vm

    def power_on(self, vm_id: str) -> bool:
        with self._lock:
            vm = self._vms.get(vm_id)
            if not vm:
                return False
            vm.state = VMState.POWERED_ON
            vm.ip_address = f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}"
            return True

    def power_off(self, vm_id: str) -> bool:
        with self._lock:
            vm = self._vms.get(vm_id)
            if not vm:
                return False
            vm.state = VMState.POWERED_OFF
            return True

    def suspend(self, vm_id: str) -> bool:
        with self._lock:
            vm = self._vms.get(vm_id)
            if not vm or vm.state != VMState.POWERED_ON:
                return False
            vm.state = VMState.SUSPENDED
            return True

    def migrate(self, vm_id: str, target_host: str) -> bool:
        with self._lock:
            vm = self._vms.get(vm_id)
            if not vm:
                return False
            old_state = vm.state
            vm.state = VMState.MIGRATING
            vm.host = target_host
            vm.state = old_state
            return True

    def list_vms(self, state: Optional[VMState] = None) -> List[VirtualMachine]:
        with self._lock:
            if state:
                return [vm for vm in self._vms.values() if vm.state == state]
            return list(self._vms.values())

    def get_vm(self, vm_id: str) -> Optional[VirtualMachine]:
        with self._lock:
            return self._vms.get(vm_id)

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total": len(self._vms),
                "states": {s.value: sum(1 for vm in self._vms.values() if vm.state == s)
                           for s in VMState},
            }


@dataclass
class Backend:
    host: str = ""
    port: int = 0
    weight: int = 1
    active_connections: int = 0
    healthy: bool = True
    last_check: float = 0.0


class LoadBalancer:
    def __init__(self, name: str = "default", algorithm: LBAlgorithm = LBAlgorithm.ROUND_ROBIN):
        self.name = name
        self.algorithm = algorithm
        self._backends: List[Backend] = []
        self._rr_index: int = 0
        self._lock = threading.Lock()

    def add_backend(self, host: str, port: int, weight: int = 1) -> None:
        with self._lock:
            self._backends.append(Backend(
                host=host, port=port, weight=weight,
            ))

    def remove_backend(self, host: str, port: int) -> bool:
        with self._lock:
            before = len(self._backends)
            self._backends = [b for b in self._backends if not (b.host == host and b.port == port)]
            return len(self._backends) < before

    def next_backend(self, client_ip: str = "") -> Optional[Backend]:
        with self._lock:
            healthy = [b for b in self._backends if b.healthy]
            if not healthy:
                return None
            if self.algorithm == LBAlgorithm.ROUND_ROBIN:
                idx = self._rr_index % len(healthy)
                self._rr_index += 1
                return healthy[idx]
            elif self.algorithm == LBAlgorithm.LEAST_CONNECTIONS:
                return min(healthy, key=lambda b: b.active_connections)
            elif self.algorithm == LBAlgorithm.IP_HASH:
                idx = abs(hash(client_ip)) % len(healthy)
                return healthy[idx]
            elif self.algorithm == LBAlgorithm.WEIGHTED:
                total = sum(b.weight for b in healthy)
                r = random.randint(1, total)
                cumulative = 0
                for b in healthy:
                    cumulative += b.weight
                    if r <= cumulative:
                        return b
            return random.choice(healthy)

    def health_check(self) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        with self._lock:
            for b in self._backends:
                key = f"{b.host}:{b.port}"
                b.last_check = time.time()
                b.healthy = random.random() > 0.1
                results[key] = b.healthy
        return results

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            healthy = sum(1 for b in self._backends if b.healthy)
            return {
                "name": self.name,
                "algorithm": self.algorithm.value,
                "backends": len(self._backends),
                "healthy": healthy,
                "unhealthy": len(self._backends) - healthy,
            }


@dataclass
class Deployment:
    deployment_id: str = ""
    name: str = ""
    image: str = ""
    replicas: int = 1
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    containers: List[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    desired_replicas: int = 1
    available_replicas: int = 0
    labels: Dict[str, str] = field(default_factory=dict)


class Orchestrator:
    def __init__(self, runtime: ContainerRuntime):
        self._runtime = runtime
        self._deployments: Dict[str, Deployment] = {}
        self._lock = threading.Lock()

    def create_deployment(self, name: str, image: str, replicas: int = 1,
                          strategy: DeploymentStrategy = DeploymentStrategy.ROLLING) -> Deployment:
        with self._lock:
            dep = Deployment(
                deployment_id=str(uuid.uuid4())[:12],
                name=name,
                image=image,
                replicas=replicas,
                strategy=strategy,
                desired_replicas=replicas,
                created_at=time.time(),
                updated_at=time.time(),
            )
            for i in range(replicas):
                c = self._runtime.create_container(f"{name}-{i}", image)
                self._runtime.start_container(c.container_id)
                dep.containers.append(c.container_id)
            dep.available_replicas = replicas
            self._deployments[dep.deployment_id] = dep
            return dep

    def scale(self, deployment_id: str, replicas: int) -> bool:
        with self._lock:
            dep = self._deployments.get(deployment_id)
            if not dep:
                return False
            current = len(dep.containers)
            if replicas > current:
                for i in range(current, replicas):
                    c = self._runtime.create_container(f"{dep.name}-{i}", dep.image)
                    self._runtime.start_container(c.container_id)
                    dep.containers.append(c.container_id)
            elif replicas < current:
                for cid in dep.containers[replicas:]:
                    self._runtime.stop_container(cid)
                    self._runtime.remove_container(cid)
                dep.containers = dep.containers[:replicas]
            dep.replicas = replicas
            dep.desired_replicas = replicas
            dep.available_replicas = replicas
            dep.updated_at = time.time()
            return True

    def rolling_update(self, deployment_id: str, new_image: str,
                       max_surge: int = 1) -> bool:
        with self._lock:
            dep = self._deployments.get(deployment_id)
            if not dep:
                return False
            old = list(dep.containers)
            dep.image = new_image
            for i, cid in enumerate(old):
                self._runtime.stop_container(cid)
                self._runtime.remove_container(cid)
                c = self._runtime.create_container(f"{dep.name}-{i}", new_image)
                self._runtime.start_container(c.container_id)
                dep.containers[i] = c.container_id
            dep.available_replicas = dep.replicas
            dep.updated_at = time.time()
            return True

    def get_deployment(self, deployment_id: str) -> Optional[Deployment]:
        with self._lock:
            return self._deployments.get(deployment_id)

    def list_deployments(self) -> List[Deployment]:
        with self._lock:
            return list(self._deployments.values())

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "deployments": len(self._deployments),
                "total_containers": sum(len(d.containers) for d in self._deployments.values()),
                "deployments": {
                    d.name: {"replicas": d.replicas, "available": d.available_replicas,
                             "image": d.image}
                    for d in self._deployments.values()
                },
            }


@dataclass
class Secret:
    secret_id: str = ""
    name: str = ""
    value: str = ""
    version: int = 1
    created_at: float = 0.0
    expires_at: Optional[float] = None
    rotation_days: int = 90
    labels: Dict[str, str] = field(default_factory=dict)


class SecretManager:
    def __init__(self):
        self._secrets: Dict[str, List[Secret]] = {}
        self._lock = threading.Lock()
        self._master_key = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]

    def store(self, name: str, value: str,
              labels: Optional[Dict[str, str]] = None) -> Secret:
        with self._lock:
            secret = Secret(
                secret_id=str(uuid.uuid4())[:12],
                name=name,
                value=self._encrypt(value),
                version=len(self._secrets.get(name, [])) + 1,
                created_at=time.time(),
                labels=labels or {},
            )
            if name not in self._secrets:
                self._secrets[name] = []
            self._secrets[name].append(secret)
            return secret

    def retrieve(self, name: str, version: Optional[int] = None) -> Optional[str]:
        with self._lock:
            versions = self._secrets.get(name)
            if not versions:
                return None
            secret = versions[-1] if version is None else (
                versions[version - 1] if version <= len(versions) else None
            )
            if not secret:
                return None
            if secret.expires_at and time.time() > secret.expires_at:
                return None
            return self._decrypt(secret.value)

    def rotate(self, name: str, new_value: str) -> Optional[Secret]:
        with self._lock:
            versions = self._secrets.get(name)
            if not versions:
                return self.store(name, new_value)
            current = versions[-1]
            if time.time() - current.created_at < current.rotation_days * 86400:
                return None
            return self.store(name, new_value)

    def delete(self, name: str) -> bool:
        with self._lock:
            if name in self._secrets:
                del self._secrets[name]
                return True
            return False

    def list_secrets(self) -> List[str]:
        with self._lock:
            return list(self._secrets.keys())

    def _encrypt(self, value: str) -> str:
        key = self._master_key.encode()
        data = value.encode()
        cipher = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
        return cipher.hex()

    def _decrypt(self, value: str) -> str:
        key = self._master_key.encode()
        cipher = bytes.fromhex(value)
        data = bytes(a ^ b for a, b in zip(cipher, key * (len(cipher) // len(key) + 1)))
        return data.decode()


@dataclass
class ConfigEntry:
    key: str = ""
    value: str = ""
    version: int = 1
    updated_at: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)


class ConfigManager:
    def __init__(self):
        self._configs: Dict[str, ConfigEntry] = {}
        self._lock = threading.Lock()
        self._watchers: Dict[str, List[Callable]] = {}

    def set(self, key: str, value: str, labels: Optional[Dict[str, str]] = None) -> ConfigEntry:
        with self._lock:
            entry = ConfigEntry(
                key=key,
                value=value,
                version=self._configs[key].version + 1 if key in self._configs else 1,
                updated_at=time.time(),
                labels=labels or {},
            )
            self._configs[key] = entry
            for handler in self._watchers.get(key, []):
                try:
                    handler(entry)
                except Exception:
                    pass
            return entry

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            entry = self._configs.get(key)
            return entry.value if entry else None

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._configs:
                del self._configs[key]
                return True
            return False

    def watch(self, key: str, handler: Callable[[ConfigEntry], None]) -> None:
        with self._lock:
            if key not in self._watchers:
                self._watchers[key] = []
            self._watchers[key].append(handler)

    def list_configs(self, prefix: str = "") -> List[ConfigEntry]:
        with self._lock:
            if prefix:
                return [e for k, e in self._configs.items() if k.startswith(prefix)]
            return list(self._configs.values())


def get_container_runtime() -> ContainerRuntime:
    return ContainerRuntime()


def get_vm_manager() -> VMManager:
    return VMManager()


def get_load_balancer(name: str = "default") -> LoadBalancer:
    return LoadBalancer(name)


def get_orchestrator() -> Orchestrator:
    return Orchestrator(ContainerRuntime())


def get_secret_manager() -> SecretManager:
    return SecretManager()
