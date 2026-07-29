"""IGICU — Core types, enums, and configuration for the Cloud & Distributed Computing Platform."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ─── Container Types ────────────────────────────────────────────────────────

class ContainerStatus(enum.Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    EXITED = "exited"
    FAILED = "failed"

class ContainerRuntimeType(enum.Enum):
    DOCKER = "docker"
    CONTAINERD = "containerd"
    CRIO = "crio"
    PODMAN = "podman"
    IGICU = "igicu"

class ImagePullPolicy(enum.Enum):
    ALWAYS = "always"
    IF_NOT_PRESENT = "if_not_present"
    NEVER = "never"

class NetworkMode(enum.Enum):
    BRIDGE = "bridge"
    HOST = "host"
    OVERLAY = "overlay"
    NONE = "none"

# ─── Orchestration Types ────────────────────────────────────────────────────

class WorkloadType(enum.Enum):
    DEPLOYMENT = "deployment"
    STATEFUL_SET = "stateful_set"
    DAEMON_SET = "daemon_set"
    JOB = "job"
    CRON_JOB = "cron_job"

class ScalingPolicy(enum.Enum):
    MANUAL = "manual"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"

class UpdateStrategy(enum.Enum):
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"

class NodeStatus(enum.Enum):
    READY = "ready"
    NOT_READY = "not_ready"
    DRAINING = "draining"
    CORDONED = "cordoned"
    OFFLINE = "offline"

class HealthStatus(enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

# ─── Serverless Types ───────────────────────────────────────────────────────

class FunctionRuntime(enum.Enum):
    PYTHON = "python"
    NODEJS = "nodejs"
    GO = "go"
    RUST = "rust"
    I_LANG = "i_lang"
    CUSTOM = "custom"

class TriggerType(enum.Enum):
    HTTP = "http"
    QUEUE = "queue"
    SCHEDULE = "schedule"
    EVENT = "event"
    DATABASE = "database"
    STREAM = "stream"
    TOPIC = "topic"

# ─── Service Discovery Types ────────────────────────────────────────────────

class LoadBalanceStrategy(enum.Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    CONSISTENT_HASH = "consistent_hash"
    WEIGHTED = "weighted"
    RANDOM = "random"

class CircuitBreakerState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# ─── Messaging Types ────────────────────────────────────────────────────────

class DeliveryGuarantee(enum.Enum):
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"

class MessageProtocol(enum.Enum):
    HTTP = "http"
    GRPC = "grpc"
    MQTT = "mqtt"
    AMQP = "amqp"
    KAFKA = "kafka"
    NATS = "nats"
    WEBSOCKET = "websocket"

# ─── Observability Types ────────────────────────────────────────────────────

class LogLevel(enum.Enum):
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"

class MetricType(enum.Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"

class AlertSeverity(enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    INFO = "info"

# ─── Security Types ─────────────────────────────────────────────────────────

class AuthMethod(enum.Enum):
    TOKEN = "token"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    MTLS = "mtls"
    API_KEY = "api_key"
    LDAP = "ldap"
    OIDC = "oidc"

class SecretProvider(enum.Enum):
    VAULT = "vault"
    AWS_SECRETS = "aws_secrets"
    AZURE_KEYVAULT = "azure_keyvault"
    GCP_SECRETS = "gcp_secrets"
    ENVIRONMENT = "environment"
    FILE = "file"

# ─── Edge Types ─────────────────────────────────────────────────────────────

class EdgeNodeTier(enum.Enum):
    LIGHT = "light"
    STANDARD = "standard"
    HEAVY = "heavy"
    AI = "ai"

# ─── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class ContainerConfig:
    image: str
    name: str
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    environment: Dict[str, str] = field(default_factory=dict)
    ports: Dict[int, int] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    network: str = "bridge"
    memory_limit: str = "256m"
    cpu_limit: str = "0.5"
    restart_policy: str = "always"
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class ImageConfig:
    name: str
    tag: str = "latest"
    digest: Optional[str] = None
    layers: List[str] = field(default_factory=list)
    size_mb: float = 0.0
    created: Optional[str] = None
    runtime: ContainerRuntimeType = ContainerRuntimeType.IGICU

@dataclass
class ClusterSpec:
    name: str
    namespace: str = "default"
    node_count: int = 1
    version: str = "1.0.0"
    region: str = "default"
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class DeploymentSpec:
    name: str
    image: str
    replicas: int = 1
    ports: Dict[str, int] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, str] = field(default_factory=lambda: {"cpu": "0.5", "memory": "256m"})
    health_check: Optional[HealthCheckSpec] = None
    scaling: Optional[ScalingSpec] = None
    update_strategy: UpdateStrategy = UpdateStrategy.ROLLING_UPDATE
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class HealthCheckSpec:
    path: str = "/health"
    port: int = 8080
    interval_sec: int = 10
    timeout_sec: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3

@dataclass
class ScalingSpec:
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu: float = 80.0
    target_memory: float = 80.0
    cooldown_sec: int = 60
    policy: ScalingPolicy = ScalingPolicy.HORIZONTAL

@dataclass
class FunctionSpec:
    name: str
    runtime: FunctionRuntime = FunctionRuntime.I_LANG
    handler: str = "main"
    memory_mb: int = 128
    timeout_sec: int = 30
    environment: Dict[str, str] = field(default_factory=dict)
    triggers: List[TriggerSpec] = field(default_factory=list)

@dataclass
class TriggerSpec:
    type: TriggerType = TriggerType.HTTP
    source: str = ""
    schedule: str = ""
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceSpec:
    name: str
    selector: Dict[str, str] = field(default_factory=dict)
    ports: List[ServicePort] = field(default_factory=list)
    strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    health_check: Optional[HealthCheckSpec] = None
    circuit_breaker: Optional[CircuitBreakerSpec] = None
    retry: Optional[RetrySpec] = None

@dataclass
class ServicePort:
    name: str = "http"
    protocol: str = "tcp"
    port: int = 80
    target_port: int = 8080

@dataclass
class CircuitBreakerSpec:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_sec: int = 30
    half_open_max: int = 3

@dataclass
class RetrySpec:
    max_retries: int = 3
    backoff_sec: float = 1.0
    max_backoff_sec: float = 30.0
    retryable_statuses: List[int] = field(default_factory=lambda: [500, 502, 503, 504])

@dataclass
class MessageQueueSpec:
    name: str
    durable: bool = True
    max_size_mb: int = 1024
    delivery: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    dead_letter: Optional[str] = None
    retention_hours: int = 72

@dataclass
class TopicSpec:
    name: str
    partitions: int = 1
    replication_factor: int = 2
    retention_hours: int = 168
    cleanup_policy: str = "delete"

@dataclass
class ObservabilityConfig:
    log_level: LogLevel = LogLevel.INFO
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    sampling_rate: float = 0.1
    export_endpoint: str = ""
    dashboard_enabled: bool = True
    alert_channels: List[str] = field(default_factory=list)

@dataclass
class SecurityConfig:
    auth_method: AuthMethod = AuthMethod.JWT
    tls_enabled: bool = True
    mTLS_enabled: bool = False
    secret_provider: SecretProvider = SecretProvider.ENVIRONMENT
    encryption_enabled: bool = True
    audit_enabled: bool = True
    policy_enforcement: bool = True

@dataclass
class EdgeNodeConfig:
    node_id: str
    tier: EdgeNodeTier = EdgeNodeTier.STANDARD
    storage_gb: int = 100
    memory_gb: int = 4
    cpu_cores: int = 2
    offline_sync: bool = True
    local_ai: bool = False
    region: str = "default"

@dataclass
class ClusterInfo:
    name: str
    namespace: str = "default"
    node_count: int = 1
    status: str = "created"
    version: str = "1.0.0"
    deployments: int = 0
    services: int = 0
    functions: int = 0
    created_at: str = ""
    health: str = "unknown"

@dataclass
class DeploymentInfo:
    name: str
    image: str
    replicas: int = 0
    available: int = 0
    status: str = "pending"
    strategy: str = "rolling"
    created_at: str = ""
    updated_at: str = ""

@dataclass
class FunctionInfo:
    name: str
    runtime: str = "i_lang"
    invocations: int = 0
    last_invocation: str = ""
    status: str = "active"
    memory_mb: int = 128
    timeout_sec: int = 30

@dataclass
class ServiceInfo:
    name: str
    endpoints: List[str] = field(default_factory=list)
    instances: int = 0
    status: str = "healthy"
    uptime: float = 0.0

@dataclass
class MessageInfo:
    id: str = ""
    topic: str = ""
    partition: int = 0
    offset: int = 0
    key: str = ""
    value_size: int = 0
    timestamp: str = ""

# ─── Error Types ────────────────────────────────────────────────────────────

class IgicuError(Exception):
    pass

class ContainerError(IgicuError):
    pass

class ClusterError(IgicuError):
    pass

class DeploymentError(IgicuError):
    pass

class FunctionError(IgicuError):
    pass

class ServiceDiscoveryError(IgicuError):
    pass

class MessagingError(IgicuError):
    pass

class SecurityError(IgicuError):
    pass

class EdgeError(IgicuError):
    pass

IGICU_VERSION = "0.1.0"
