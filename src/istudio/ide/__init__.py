"""I STUDIO IDE — the official I Programming Language IDE.

A browser-based IDE served by a local Python backend:

- React/TypeScript/Monaco frontend under ``ide/`` (built into ``ide/dist``)
- stdlib HTTP server with JSON REST + SSE streaming (run/terminal/debug)
- real compiler diagnostics, completion, hover, symbols, formatting
- subprocess-isolated execution with a source-level debugger
- Isoko package management and Git integration

Run with::

    python -m istudio.ide            # or ``istudio ide``
"""

from __future__ import annotations

__version__ = "1.0.0"
