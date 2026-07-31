"""templates — Project templates for isoko."""

from __future__ import annotations

import os
from typing import Dict, List, Optional


class Template:
    """A project template."""
    __slots__ = ("name", "description", "files")

    def __init__(self, name: str = "", description: str = "") -> None:
        self.name = name
        self.description = description
        self.files: Dict[str, str] = {}  # path -> content

    def render(self, project_name: str, project_dir: str) -> List[str]:
        """Render template files to disk. Returns list of created files."""
        created = []
        for rel_path, content in self.files.items():
            rendered = content.replace("{{project_name}}", project_name)
            rendered_path = rel_path.replace("{{project_name}}", project_name)
            full_path = os.path.join(project_dir, rendered_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(rendered)
            created.append(full_path)
        return created


# ---------------------------------------------------------------------------
# Built-in templates
# ---------------------------------------------------------------------------

_CONSOLE = Template("console", "A console application")
_CONSOLE.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} console application",
    "license": "MIT"
  },
  "dependencies": {},
  "scripts": {
    "run": "lib/{{project_name}}.i",
    "test": "i test"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Entry point
andika "Hello, World!"
""",
    "tests/test_{{project_name}}.i": """# Tests for {{project_name}}
# Write tests here
""",
}

_LIBRARY = Template("library", "A reusable library")
_LIBRARY.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} library",
    "license": "MIT"
  },
  "dependencies": {},
  "lib": "lib",
  "scripts": {
    "test": "i test",
    "bench": "i bench"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Library
# Export public API here
""",
    "tests/test_{{project_name}}.i": """# Tests for {{project_name}}
""",
}

_WEB_API = Template("web-api", "A web API service")
_WEB_API.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} web API",
    "license": "MIT"
  },
  "dependencies": {
    "isoko-web": ">=0.1.0"
  },
  "scripts": {
    "run": "lib/{{project_name}}.i",
    "dev": "lib/{{project_name}}.i"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Web API
andika "Starting {{project_name}} API server..."
""",
    "tests/test_{{project_name}}.i": """# Tests for {{project_name}}
""",
}

_AI_PROJECT = Template("ai", "An AI/ML project")
_AI_PROJECT.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} AI project",
    "license": "MIT"
  },
  "dependencies": {
    "isoko-ml": ">=0.1.0"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — AI Project
""",
    "data/.gitkeep": "",
}

_GAME = Template("game", "A game project")
_GAME.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} game",
    "license": "MIT"
  },
  "dependencies": {
    "isoko-gfx": ">=0.1.0"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Game
""",
    "assets/.gitkeep": "",
}

_DESKTOP = Template("desktop", "A desktop application")
_DESKTOP.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} desktop application",
    "license": "MIT"
  },
  "dependencies": {
    "isoko-gui": ">=0.1.0"
  },
  "scripts": {
    "run": "lib/{{project_name}}.i"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Desktop Application
""",
    "assets/.gitkeep": "",
}

_MOBILE = Template("mobile", "A mobile application")
_MOBILE.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} mobile application",
    "license": "MIT"
  },
  "dependencies": {
    "isoko-mobile": ">=0.1.0"
  },
  "scripts": {
    "run": "lib/{{project_name}}.i"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Mobile Application
""",
    "platforms/.gitkeep": "",
}

_WEBSITE = Template("website", "A website project")
_WEBSITE.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} website",
    "license": "MIT"
  },
  "dependencies": {
    "isoko-web": ">=0.1.0"
  },
  "scripts": {
    "dev": "lib/{{project_name}}.i",
    "build": "python -m compiler.compiler lib/{{project_name}}.i"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Website
""",
    "static/.gitkeep": "",
    "templates/.gitkeep": "",
}

_CLOUD = Template("cloud", "A cloud service")
_CLOUD.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} cloud service",
    "license": "MIT"
  },
  "dependencies": {
    "isoko-cloud": ">=0.1.0"
  },
  "scripts": {
    "run": "lib/{{project_name}}.i",
    "deploy": "ideploy push"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Cloud Service
""",
}

_EMBEDDED = Template("embedded", "An embedded/IoT project")
_EMBEDDED.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} embedded project",
    "license": "MIT"
  },
  "dependencies": {},
  "engines": {
    "target": "embedded"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Embedded Project
""",
}

_OS = Template("os", "An operating system / kernel project")
_OS.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} operating system",
    "license": "MIT"
  },
  "dependencies": {},
  "engines": {
    "target": "bare-metal"
  }
}""",
    "kernel/{{project_name}}.i": """# {{project_name}} — Kernel
""",
    "drivers/.gitkeep": "",
    "boot/.gitkeep": "",
}

_FRAMEWORK = Template("framework", "A reusable framework")
_FRAMEWORK.files = {
    "ilang.json": """{
  "package": {
    "name": "{{project_name}}",
    "version": "0.1.0",
    "description": "{{project_name}} framework",
    "license": "MIT"
  },
  "dependencies": {},
  "lib": "lib",
  "scripts": {
    "test": "i test",
    "bench": "i bench"
  }
}""",
    "lib/{{project_name}}.i": """# {{project_name}} — Framework
""",
    "tests/test_{{project_name}}.i": """# Tests for {{project_name}}
""",
    "examples/.gitkeep": "",
}

_TEMPLATES: Dict[str, Template] = {
    "console": _CONSOLE,
    "library": _LIBRARY,
    "web-api": _WEB_API,
    "website": _WEBSITE,
    "desktop": _DESKTOP,
    "mobile": _MOBILE,
    "ai": _AI_PROJECT,
    "game": _GAME,
    "cloud": _CLOUD,
    "embedded": _EMBEDDED,
    "os": _OS,
    "framework": _FRAMEWORK,
}


def list_templates() -> List[Dict[str, str]]:
    """List all available templates."""
    return [{"name": t.name, "description": t.description} for t in _TEMPLATES.values()]


def get_template(name: str) -> Optional[Template]:
    return _TEMPLATES.get(name)


def render_template(name: str, project_name: str, project_dir: str) -> List[str]:
    """Render a template to disk."""
    tpl = get_template(name)
    if tpl is None:
        raise ValueError(f"unknown template: {name!r}")
    os.makedirs(project_dir, exist_ok=True)
    return tpl.render(project_name, project_dir)
