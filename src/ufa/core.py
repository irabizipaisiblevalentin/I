"""core — Application bootstrap and context.

The central Application class that orchestrates the entire UFA lifecycle,
wiring together all subsystems into a unified framework context.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from ufa.lifecycle import LifecycleManager, Phase
from ufa.container import Container, Scope
from ufa.configuration import Configuration, Profiles
from ufa.plugins import PluginRegistry
from ufa.events import EventBus
from ufa.middleware import MiddlewarePipeline, MiddlewareContext
from ufa.commands import MessageBus, Message, CommandResult
from ufa.scheduler import TaskScheduler
from ufa.observability import Logger, MetricsCollector, Tracer, LogLevel
from ufa.security import SecurityManager
from ufa.cache import CacheManager
from ufa.health import HealthMonitor
from ufa.localization import Localizer
from ufa.ai import AIManager
from ufa.modules import ModuleRegistry


class ApplicationContext:
    """The runtime context passed to all UFA subsystems and frameworks."""

    def __init__(self, app: "Application") -> None:
        self.app = app
        self.container = app.container
        self.config = app.config
        self.events = app.events
        self.plugins = app.plugins
        self.commands = app.commands
        self.scheduler = app.scheduler
        self.logger = app.logger
        self.metrics = app.metrics
        self.tracer = app.tracer
        self.security = app.security
        self.cache = app.cache
        self.health = app.health
        self.localization = app.localization
        self.ai = app.ai
        self.modules = app.modules
        self.middleware = app.middleware

    def get(self, service_type: type, name: str = "") -> Any:
        return self.container.resolve(service_type, name)

    def publish(self, event_name: str, data: Any = None) -> None:
        self.events.emit(event_name, data)

    def log(self, message: str, level: LogLevel = LogLevel.INFO,
            **kw: Any) -> None:
        self.logger.log(level, message, kw.get("data"), kw.get("correlation_id", ""))


class Application:
    """The UFA Application — top-level orchestrator.

    Every framework creates an Application and uses it to bootstrap
    the entire system lifecycle.
    """

    def __init__(self, name: str = "ufa-app",
                 version: str = "0.1.0") -> None:
        self.name = name
        self.version = version
        self._started_at: float = 0.0

        self.lifecycle = LifecycleManager()
        self.container = Container()
        self.config = Configuration()
        self.profiles = Profiles()
        self.plugins = PluginRegistry()
        self.events = EventBus()
        self.middleware = MiddlewarePipeline()
        self.commands = MessageBus()
        self.scheduler = TaskScheduler()
        self.logger = Logger(name)
        self.metrics = MetricsCollector()
        self.tracer = Tracer()
        self.security = SecurityManager()
        self.cache = CacheManager()
        self.health = HealthMonitor()
        self.localization = Localizer()
        self.ai = AIManager()
        self.modules = ModuleRegistry()

        self._context: Optional[ApplicationContext] = None

        self._register_core_services()

    @property
    def context(self) -> ApplicationContext:
        if self._context is None:
            self._context = ApplicationContext(self)
        return self._context

    @property
    def uptime(self) -> float:
        return self.lifecycle.uptime

    def configure(self, config: Dict[str, Any]) -> None:
        """Merge configuration into the application."""
        self.config.merge(config)
        self.lifecycle.advance(Phase.CONFIGURED, self.context)

    def load_config(self, path: str) -> bool:
        return self.config.load_file(path)

    def load_env(self, prefix: str = "I_") -> int:
        return self.config.load_env(prefix)

    def register_plugin(self, plugin: Any) -> None:
        self.plugins.register(plugin)

    def register_module(self, module: Any) -> None:
        self.modules.register(module)

    def use(self, handler: Callable, **kw: Any) -> None:
        """Register middleware."""
        from ufa.middleware import MiddlewarePhase
        phase = kw.pop("phase", MiddlewarePhase.PRE)
        self.middleware.use(handler, phase, **kw)

    def on(self, event_name: str, handler: Callable,
           priority: int = 0) -> None:
        """Subscribe to an event."""
        self.events.subscribe(event_name, handler, priority)

    def emit(self, event_name: str, data: Any = None) -> None:
        self.events.emit(event_name, data)

    def command(self, message_class: type, handler: Callable) -> None:
        self.commands.register_command(message_class, handler)

    def query(self, message_class: type, handler: Callable) -> None:
        self.commands.register_query(message_class, handler)

    def schedule_once(self, handler: Callable, delay: float = 0.0,
                      name: str = "") -> Any:
        return self.scheduler.schedule_once(handler, delay, name)

    def schedule_interval(self, handler: Callable, interval: float,
                          name: str = "") -> Any:
        return self.scheduler.schedule_interval(handler, interval, name)

    def run(self) -> None:
        """Run the application lifecycle through all phases."""
        self.lifecycle.advance(Phase.INITIALIZED, self.context)

        self.plugins.initialize_all(self.context)
        self.modules.initialize_all(self.context)

        self.lifecycle.advance(Phase.STARTING, self.context)

        self.plugins.start_all()
        self.modules.start_all()

        self.lifecycle.advance(Phase.RUNNING, self.context)
        self._started_at = time.time()

        self.emit("app.started", {"name": self.name, "version": self.version})

    def stop(self) -> None:
        """Gracefully stop the application."""
        self.emit("app.stopping", {})
        self.lifecycle.advance(Phase.STOPPING, self.context)

        self.modules.stop_all()
        self.plugins.stop_all()

        self.lifecycle.advance(Phase.STOPPED, self.context)
        self.emit("app.stopped", {"uptime": self.uptime})

    def shutdown(self) -> None:
        """Full shutdown including destruction."""
        if self.lifecycle.phase in (Phase.RUNNING, Phase.STARTING):
            self.stop()
        self.lifecycle.advance(Phase.DESTROYING, self.context)
        self.lifecycle.advance(Phase.DESTROYED, self.context)
        self.emit("app.destroyed", {})

    def health_report(self) -> Dict[str, Any]:
        report = self.health.report()
        return report.to_dict()

    def _register_core_services(self) -> None:
        self.container.register_instance(Configuration, self.config)
        self.container.register_instance(EventBus, self.events)
        self.container.register_instance(MessageBus, self.commands)
        self.container.register_instance(TaskScheduler, self.scheduler)
        self.container.register_instance(Logger, self.logger)
        self.container.register_instance(MetricsCollector, self.metrics)
        self.container.register_instance(Tracer, self.tracer)
        self.container.register_instance(SecurityManager, self.security)
        self.container.register_instance(CacheManager, self.cache)
        self.container.register_instance(HealthMonitor, self.health)
        self.container.register_instance(Localizer, self.localization)
        self.container.register_instance(AIManager, self.ai)
        self.container.register_instance(ModuleRegistry, self.modules)
        self.container.register_instance(PluginRegistry, self.plugins)

    def __repr__(self) -> str:
        return (f"Application({self.name!r}, v={self.version}, "
                f"phase={self.lifecycle.phase.name})")
