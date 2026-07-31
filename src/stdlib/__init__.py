"""I Standard Library (ISTDLIB) — The official runtime foundation for I applications.

Every implementation of the I Programming Language must conform to this API.
The Standard Library is part of the language specification.

Modules are organized in layers:
  - Foundation: text, math, numbers, collections, random, unicode
  - Core: time, date, io, paths, filesystem, json, csv, xml, yaml
  - System: system, process, environment, configuration, logging, terminal
  - Data: serialization, compression, archive, database, crypto, security
  - Network: network, http, websocket
  - Media: image, audio, video, graphics, window
  - Advanced: reflection, testing, benchmark, debug, localization
  - Meta: package, compiler, vm
"""

__version__ = "1.0.0"
__all__ = [
    "text", "math", "numbers", "collections", "random", "unicode",
    "time", "date", "io", "paths", "filesystem", "json", "csv", "xml", "yaml",
    "system", "process", "environment", "configuration", "logging", "terminal",
    "serialization", "compression", "archive", "database", "crypto", "security",
    "network", "http", "websocket",
    "image", "audio", "video", "graphics", "window",
    "reflection", "testing", "benchmark", "debug", "localization",
    "package", "compiler", "vm",
]


class StdlibError(Exception):
    """Base exception for all ISTDLIB errors."""

    def __init__(self, message: str, code: str = "STDERR", module: str = "") -> None:
        self.code = code
        self.module = module
        self.bilingual = message
        super().__init__(message)

    def format(self) -> str:
        prefix = f"[{self.module}]" if self.module else ""
        return f"{prefix} {self.bilingual} ({self.code})"
