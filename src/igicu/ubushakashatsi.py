"""IGICU — Service Discovery: registry, load balancing, health checks, circuit breakers."""

from __future__ import annotations

import random
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    CircuitBreakerSpec, CircuitBreakerState, HealthCheckSpec,
    HealthStatus, LoadBalanceStrategy, RetrySpec,
    ServiceInfo, ServicePort, ServiceSpec,
    ServiceDiscoveryError, IGICU_VERSION,
)


class ServiceInstance:
    def __init__(self, service_name: str, host: str, port: int,
                 instance_id: Optional[str] = None):
        self.instance_id = instance_id or f"inst-{uuid.uuid4().hex[:8]}"
        self.service_name = service_name
        self.host = host
        self.port = port
        self.healthy = True
        self.weight = 100
        self.metadata: Dict[str, str] = {}
        self.registered_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.last_heartbeat = time.time()


class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, Dict[str, ServiceInstance]] = {}
        self._health_status: Dict[str, HealthStatus] = {}

    def register(self, service_name: str, host: str, port: int,
                 instance_id: Optional[str] = None,
                 metadata: Optional[Dict[str, str]] = None) -> str:
        if service_name not in self._services:
            self._services[service_name] = {}

        instance = ServiceInstance(service_name, host, port, instance_id)
        if metadata:
            instance.metadata = metadata
        self._services[service_name][instance.instance_id] = instance
        self._health_status[service_name] = HealthStatus.HEALTHY
        return instance.instance_id

    def deregister(self, service_name: str, instance_id: str) -> bool:
        services = self._services.get(service_name, {})
        if instance_id in services:
            del services[instance_id]
            return True
        return False

    def discover(self, service_name: str) -> List[Dict[str, Any]]:
        services = self._services.get(service_name, {})
        return [
            {
                "id": inst.instance_id,
                "host": inst.host,
                "port": inst.port,
                "healthy": inst.healthy,
                "weight": inst.weight,
                "metadata": inst.metadata,
                "registered_at": inst.registered_at,
            }
            for inst in services.values()
            if inst.healthy
        ]

    def get_instances(self, service_name: str,
                      healthy_only: bool = True) -> List[ServiceInstance]:
        services = self._services.get(service_name, {})
        if healthy_only:
            return [s for s in services.values() if s.healthy]
        return list(services.values())

    def list_services(self) -> List[Dict[str, Any]]:
        result = []
        for name, instances in self._services.items():
            healthy = sum(1 for i in instances.values() if i.healthy)
            result.append({
                "name": name,
                "instances": len(instances),
                "healthy": healthy,
                "status": self._health_status.get(name, HealthStatus.UNKNOWN).value,
            })
        return result

    def mark_healthy(self, service_name: str, instance_id: str) -> bool:
        inst = self._services.get(service_name, {}).get(instance_id)
        if not inst:
            return False
        inst.healthy = True
        return True

    def mark_unhealthy(self, service_name: str, instance_id: str) -> bool:
        inst = self._services.get(service_name, {}).get(instance_id)
        if not inst:
            return False
        inst.healthy = False
        return True

    def heartbeat(self, service_name: str, instance_id: str) -> bool:
        inst = self._services.get(service_name, {}).get(instance_id)
        if not inst:
            return False
        inst.last_heartbeat = time.time()
        inst.healthy = True
        return True

    def prune_stale(self, timeout_sec: int = 30) -> int:
        now = time.time()
        pruned = 0
        for service_name in list(self._services.keys()):
            instances = self._services[service_name]
            for inst_id in list(instances.keys()):
                if now - instances[inst_id].last_heartbeat > timeout_sec:
                    del instances[inst_id]
                    pruned += 1
        return pruned


class LoadBalancer:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self._next_index: Dict[str, int] = {}

    def get_endpoint(self, service_name: str,
                     strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN,
                     client_ip: Optional[str] = None) -> Optional[Dict[str, Any]]:
        instances = self.registry.get_instances(service_name)
        if not instances:
            return None

        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            idx = self._next_index.get(service_name, 0)
            instance = instances[idx % len(instances)]
            self._next_index[service_name] = idx + 1
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            instance = min(instances, key=lambda i: i.weight)
        elif strategy == LoadBalanceStrategy.RANDOM:
            instance = random.choice(instances)
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            total_weight = sum(i.weight for i in instances)
            r = random.uniform(0, total_weight)
            current = 0
            instance = instances[0]
            for i in instances:
                current += i.weight
                if r <= current:
                    instance = i
                    break
        elif strategy == LoadBalanceStrategy.IP_HASH:
            if client_ip:
                idx = hash(client_ip) % len(instances)
                instance = instances[idx]
            else:
                instance = instances[0]
        else:
            instance = instances[0]

        return {
            "host": instance.host,
            "port": instance.port,
            "instance_id": instance.instance_id,
        }

    def get_all_endpoints(self, service_name: str) -> List[Dict[str, Any]]:
        return self.registry.discover(service_name)


class HealthChecker:
    def __init__(self):
        self._check_history: Dict[str, List[Dict[str, Any]]] = {}

    def check(self, spec: HealthCheckSpec, host: str, port: int) -> Dict[str, Any]:
        start = time.time()
        import random
        is_healthy = random.random() > 0.05
        latency_ms = (time.time() - start) * 1000

        result = {
            "host": host,
            "port": port,
            "healthy": is_healthy,
            "latency_ms": round(latency_ms, 2),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "path": spec.path,
            "status_code": 200 if is_healthy else 503,
        }

        key = f"{host}:{port}"
        if key not in self._check_history:
            self._check_history[key] = []
        self._check_history[key].append(result)
        return result

    def get_history(self, host: str, port: int) -> List[Dict[str, Any]]:
        return self._check_history.get(f"{host}:{port}", [])

    def aggregate(self, hosts: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = [self.check(HealthCheckSpec(), h["host"], h["port"]) for h in hosts]
        healthy = sum(1 for r in results if r["healthy"])
        return {
            "total": len(results),
            "healthy": healthy,
            "unhealthy": len(results) - healthy,
            "avg_latency_ms": round(
                sum(r["latency_ms"] for r in results) / len(results), 2
            ) if results else 0,
        }


class CircuitBreaker:
    def __init__(self, spec: CircuitBreakerSpec):
        self.spec = spec
        self.state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_state_change = time.time()

    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self._last_state_change > self.spec.timeout_sec:
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise ServiceDiscoveryError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.spec.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                self._last_state_change = time.time()
        elif self.state == CircuitBreakerState.CLOSED:
            self._failure_count = 0

    def _on_failure(self) -> None:
        self._failure_count += 1
        if self.state == CircuitBreakerState.CLOSED:
            if self._failure_count >= self.spec.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self._last_state_change = time.time()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self._last_state_change = time.time()

    def reset(self) -> None:
        self.state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0

    def get_state(self) -> CircuitBreakerState:
        return self.state


class RetryHandler:
    def __init__(self, spec: RetrySpec):
        self.spec = spec

    def execute(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        import time as _time
        last_exception = None
        for attempt in range(1, self.spec.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.spec.max_retries:
                    backoff = min(
                        self.spec.backoff_sec * (2 ** (attempt - 1)),
                        self.spec.max_backoff_sec,
                    )
                    _time.sleep(backoff)
        raise ServiceDiscoveryError(f"All retries failed: {last_exception}") from last_exception


class ServiceMesh:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer(self.registry)
        self.health_checker = HealthChecker()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._retry_handlers: Dict[str, RetryHandler] = {}

    def create_service(self, spec: ServiceSpec) -> str:
        service_id = f"svc-{uuid.uuid4().hex[:8]}"
        for port in spec.ports:
            for i in range(3):
                self.registry.register(
                    spec.name,
                    f"{spec.name}-{i}.local",
                    port.target_port,
                    metadata={"service_id": service_id, "port_name": port.name},
                )
        if spec.circuit_breaker:
            self._circuit_breakers[spec.name] = CircuitBreaker(spec.circuit_breaker)
        if spec.retry:
            self._retry_handlers[spec.name] = RetryHandler(spec.retry)
        return service_id

    def resolve(self, service_name: str,
                strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN,
                client_ip: Optional[str] = None) -> Optional[Dict[str, Any]]:
        cb = self._circuit_breakers.get(service_name)
        if cb and cb.state == CircuitBreakerState.OPEN:
            raise ServiceDiscoveryError(f"Service '{service_name}' circuit breaker is OPEN")
        return self.load_balancer.get_endpoint(service_name, strategy, client_ip)

    def health_check(self, service_name: str) -> Dict[str, Any]:
        instances = self.registry.discover(service_name)
        if not instances:
            return {"service": service_name, "healthy": False, "instances": 0}
        return self.health_checker.aggregate(instances)
