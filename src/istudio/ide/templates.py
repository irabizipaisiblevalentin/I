"""I STUDIO IDE — project templates.

Every template ships a single self-contained ``main.i`` that compiles and runs
with the current compiler, plus an ``ilang.toml`` manifest so the Isoko package
manager can operate on the project.
"""

from __future__ import annotations

from typing import Any

_MANIFEST = """\
[package]
name = "{name}"
version = "0.1.0"
description = "{description}"
license = "MIT"
authors = ["Irabizi Paisible Valentin"]
engines = {{ i = ">=1.0.0" }}

[dependencies]
"""

_README = """\
# {title}

Created from the I Studio `{key}` template.

## Run

```bash
i src/main.i
```

## Build

```bash
i build
```
"""


def _console() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Console App — main.i\n'
            'andika "Muraho, Isi!"\n'
            'andika "I is a professional programming language from Rwanda."\n'
            'andika ""\n'
            'shyira x = 5\n'
            'shyira y = 7\n'
            'andika "5 + 7 = " + shobora_umuntu(x + y)\n'
            'andika "Finished."\n'
        ),
        "ilang.toml": _MANIFEST.format(name="console-app", description="A console application in I"),
        "README.md": _README.format(title="Console App", key="console"),
    }


def _desktop() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Desktop App — main.i\n'
            'andika "I Desktop Application"\n'
            'andika "================================="\n'
            'andika "Your desktop app template is ready."\n'
            'shyira window_title = "I Studio Desktop"\n'
            'shyira width = 800\n'
            'shyira height = 600\n'
            'andika "Window: " + window_title\n'
            'andika "Size: " + shobora_umuntu(width) + "x" + shobora_umuntu(height)\n'
        ),
        "ilang.toml": _MANIFEST.format(name="desktop-app", description="A desktop application in I"),
        "README.md": _README.format(title="Desktop App", key="desktop"),
    }


def _web() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Web App — main.i\n'
            'andika "I Web Application"\n'
            'andika "==========================="\n'
            'shyira host = "localhost"\n'
            'shyira port = 3000\n'
            'andika "Serving at http://" + host + ":" + shobora_umuntu(port)\n'
            'andika "Routes: /, /about, /api"\n'
        ),
        "ilang.toml": _MANIFEST.format(name="web-app", description="A web application in I"),
        "README.md": _README.format(title="Web App", key="web"),
    }


def _mobile() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Mobile App — main.i\n'
            'andika "I Mobile Application"\n'
            'shyira platform = "Android / iOS"\n'
            'andika "Target platform: " + platform\n'
            'andika "Screen: 390x844 (default device)"\n'
        ),
        "ilang.toml": _MANIFEST.format(name="mobile-app", description="A mobile application in I"),
        "README.md": _README.format(title="Mobile App", key="mobile"),
    }


def _api() -> dict[str, str]:
    return {
        "src/main.i": (
            '# API — main.i\n'
            'andika "I API Service (template)"\n'
            'andika "----------------------------------"\n'
            'kuri i muri 1 kugeza 3\n'
            '    andika "GET /api/" + shobora_umuntu(i) + " -> 200 OK"\n'
            'iherezo\n'
            'andika "Server listening on :8080"\n'
        ),
        "ilang.toml": _MANIFEST.format(name="api-service", description="An API service in I"),
        "README.md": _README.format(title="API Service", key="api"),
    }


def _ai() -> dict[str, str]:
    return {
        "src/main.i": (
            '# AI Project — main.i\n'
            'andika "I AI Assistant (template)"\n'
            'andika "-----------------------------------"\n'
            'shyira model = "I-LLM-7B"\n'
            'shyira prompt = "Describe the I language in one sentence."\n'
            'andika "Model: " + model\n'
            'andika "Prompt: " + prompt\n'
            'andika "> I is a Kinyarwanda-first programming language."\n'
        ),
        "ilang.toml": _MANIFEST.format(name="ai-project", description="An AI project in I"),
        "README.md": _README.format(title="AI Project", key="ai"),
    }


def _game() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Game — main.i\n'
            'andika "I Game (template)"\n'
            'andika "-------------------"\n'
            'shyira score = 0\n'
            'kuri level muri 1 kugeza 3\n'
            '    score = score + level * 10\n'
            '    andika "Level " + shobora_umuntu(level) + " cleared (+" + shobora_umuntu(level * 10) + ")"\n'
            'iherezo\n'
            'andika "Final score: " + shobora_umuntu(score)\n'
        ),
        "ilang.toml": _MANIFEST.format(name="game", description="A game in I"),
        "README.md": _README.format(title="Game", key="game"),
    }


def _library() -> dict[str, str]:
    return {
        "src/lib.i": (
            '# Library — lib.i\n'
            '# A small pure-I library with no side effects.\n'
            'umurimo fibonacci(n: int) -> int\n'
            '    niba n munsi_ya 2\n'
            '        subira n\n'
            '    iherezo\n'
            '    subira fibonacci(n - 1) + fibonacci(n - 2)\n'
            'iherezo\n'
            'kuri i muri 0 kugeza 8\n'
            '    andika "fib(" + shobora_umuntu(i) + ") = " + shobora_umuntu(fibonacci(i))\n'
            'iherezo\n'
        ),
        "ilang.toml": _MANIFEST.format(name="i-library", description="A reusable library written in I"),
        "README.md": _README.format(title="Library", key="library"),
    }


def _package() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Package — main.i\n'
            'andika "I package (template)"\n'
            'umurimo package_info() -> string\n'
            '    subira "i-hello v0.1.0"\n'
            'iherezo\n'
            'andika "Loaded package: " + package_info()\n'
        ),
        "ilang.toml": _MANIFEST.format(name="i-hello", description="An example I package"),
        "README.md": _README.format(title="Package", key="package"),
    }


def _sisitemu() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Operating System Module (sisitemu) — main.i\n'
            'andika "I Operating System Module (sisitemu)"\n'
            'andika "------------------------------------------"\n'
            'shyira kernel = "I-Kernel"\n'
            'shyira version = "0.1.0"\n'
            'shyira arch = "wasm"\n'
            'andika "Kernel: " + kernel + " v" + version\n'
            'andika "Architecture: " + arch\n'
        ),
        "ilang.toml": _MANIFEST.format(name="sisitemu-module", description="An operating system module in I"),
        "README.md": _README.format(title="OS Module (sisitemu)", key="sisitemu"),
    }


def _plugin() -> dict[str, str]:
    return {
        "src/main.i": (
            '# Compiler Plugin — main.i\n'
            'andika "I Compiler Plugin (template)"\n'
            'andika "------------------------------------"\n'
            'umurimo plugin_info() -> string\n'
            '    subira "I-Plugin v0.1.0"\n'
            'iherezo\n'
            'andika "Loaded: " + plugin_info()\n'
        ),
        "ilang.toml": _MANIFEST.format(name="i-plugin", description="A compiler plugin in I"),
        "README.md": _README.format(title="Compiler Plugin", key="plugin"),
    }


TEMPLATES: dict[str, dict[str, Any]] = {
    "console": {
        "name": "Console App",
        "description": "A command-line application in I.",
        "category": "Application",
        "icon": "Terminal",
        "files": _console(),
    },
    "desktop": {
        "name": "Desktop App",
        "description": "A desktop (GUI) application scaffold for I.",
        "category": "Application",
        "icon": "Monitor",
        "files": _desktop(),
    },
    "web": {
        "name": "Web App",
        "description": "A web application scaffold for I.",
        "category": "Application",
        "icon": "Globe",
        "files": _web(),
    },
    "mobile": {
        "name": "Mobile App",
        "description": "A mobile application scaffold for I.",
        "category": "Application",
        "icon": "Smartphone",
        "files": _mobile(),
    },
    "api": {
        "name": "API",
        "description": "A JSON API service scaffold for I.",
        "category": "Application",
        "icon": "Server",
        "files": _api(),
    },
    "ai": {
        "name": "AI Project",
        "description": "An AI/assistant project scaffold for I.",
        "category": "Application",
        "icon": "Sparkles",
        "files": _ai(),
    },
    "game": {
        "name": "Game",
        "description": "A game project scaffold for I.",
        "category": "Application",
        "icon": "Gamepad2",
        "files": _game(),
    },
    "library": {
        "name": "Library",
        "description": "A reusable I library.",
        "category": "Package",
        "icon": "BookOpen",
        "files": _library(),
    },
    "package": {
        "name": "Package",
        "description": "An installable I package (Isoko).",
        "category": "Package",
        "icon": "Package",
        "files": _package(),
    },
    "sisitemu": {
        "name": "OS Module (sisitemu)",
        "description": "An operating system module for I.",
        "category": "System",
        "icon": "Cpu",
        "files": _sisitemu(),
    },
    "plugin": {
        "name": "Compiler Plugin",
        "description": "A compiler plugin for I.",
        "category": "System",
        "icon": "Wrench",
        "files": _plugin(),
    },
}


def template_keys() -> list[str]:
    return sorted(TEMPLATES)


def get_template(key: str) -> dict[str, Any]:
    try:
        return TEMPLATES[key]
    except KeyError:
        raise KeyError(f"unknown template: {key!r}") from None


def template_files(key: str) -> dict[str, str]:
    return dict(get_template(key)["files"])
