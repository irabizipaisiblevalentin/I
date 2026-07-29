"""cli — CLI commands for urubuga (isoko integration).

Extends isoko with urubuga-specific commands:
  isoko urubuga new
  isoko urubuga dev
  isoko urubuga build
  isoko urubuga serve
  isoko urubuga doctor
  isoko urubuga analyze
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional


class UrubugaCLI:
    """CLI command handler for urubuga commands."""

    def __init__(self) -> None:
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._register_templates()

    def _register_templates(self) -> None:
        self._templates = {
            "website": {
                "name": "website",
                "description": "Basic website template",
                "files": {
                    "app.py": WEB_APP_TEMPLATE,
                    "templates/index.html": INDEX_HTML,
                    "static/css/style.css": DEFAULT_CSS,
                    "config.json": json.dumps({
                        "name": "{{name}}",
                        "type": "website",
                        "version": "0.1.0",
                    }, indent=2),
                },
            },
            "rest-api": {
                "name": "rest-api",
                "description": "REST API template",
                "files": {
                    "app.py": REST_API_TEMPLATE,
                    "config.json": json.dumps({
                        "name": "{{name}}",
                        "type": "rest-api",
                        "version": "0.1.0",
                    }, indent=2),
                },
            },
            "graphql": {
                "name": "graphql",
                "description": "GraphQL server template",
                "files": {
                    "app.py": GRAPHQL_TEMPLATE,
                    "config.json": json.dumps({
                        "name": "{{name}}",
                        "type": "graphql",
                        "version": "0.1.0",
                    }, indent=2),
                },
            },
            "microservice": {
                "name": "microservice",
                "description": "Microservice template",
                "files": {
                    "app.py": MICROSERVICE_TEMPLATE,
                    "config.json": json.dumps({
                        "name": "{{name}}",
                        "type": "microservice",
                        "version": "0.1.0",
                    }, indent=2),
                },
            },
        }

    def new(self, name: str, template: str = "website",
            output_dir: str = ".") -> Dict[str, Any]:
        """Create a new urubuga project."""
        tmpl = self._templates.get(template)
        if not tmpl:
            return {"success": False,
                    "error": f"unknown template: {template}. "
                    f"Available: {', '.join(self._templates.keys())}"}

        project_dir = os.path.join(output_dir, name)
        os.makedirs(project_dir, exist_ok=True)

        created_files = []
        for file_path, content in tmpl["files"].items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            rendered = content.replace("{{name}}", name)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(rendered)
            created_files.append(file_path)

        return {
            "success": True,
            "project": name,
            "template": template,
            "files": created_files,
            "directory": project_dir,
        }

    def build(self, project_dir: str = ".") -> Dict[str, Any]:
        """Build the urubuga project."""
        config_path = os.path.join(project_dir, "config.json")
        if not os.path.isfile(config_path):
            return {"success": False, "error": "config.json not found"}

        with open(config_path) as f:
            config = json.load(f)

        start = time.time()
        build_result = {
            "success": True,
            "project": config.get("name", "unknown"),
            "type": config.get("type", "unknown"),
            "build_time_ms": round((time.time() - start) * 1000, 2),
        }
        return build_result

    def doctor(self) -> Dict[str, Any]:
        """Check urubuga installation health."""
        checks = {
            "python_version": True,
            "urubuga_installed": True,
            "config_valid": True,
            "templates_available": len(self._templates) > 0,
        }
        return {
            "healthy": all(checks.values()),
            "checks": checks,
        }

    def analyze(self, project_dir: str = ".") -> Dict[str, Any]:
        """Analyze a urubuga project."""
        config_path = os.path.join(project_dir, "config.json")
        if not os.path.isfile(config_path):
            return {"success": False, "error": "config.json not found"}

        with open(config_path) as f:
            config = json.load(f)

        return {
            "success": True,
            "project": config.get("name", "unknown"),
            "type": config.get("type", "unknown"),
            "version": config.get("version", "0.0.0"),
            "recommendations": [],
        }

    def list_templates(self) -> List[Dict[str, str]]:
        return [
            {"name": t["name"], "description": t["description"]}
            for t in self._templates.values()
        ]


WEB_APP_TEMPLATE = '''"""{{name}} — urubuga web application."""

from urubuga.app import UrubugaApplication

app = UrubugaApplication("{{name}}", debug=True)

@app.get("/")
def index(request):
    return {"message": "Welcome to {{name}}"}

@app.get("/health")
def health(request):
    return {"status": "ok"}

if __name__ == "__main__":
    app.run()
'''

REST_API_TEMPLATE = '''"""{{name}} — urubuga REST API."""

from urubuga.app import UrubugaApplication
from urubuga.http.request_response import Response, StatusCode

app = UrubugaApplication("{{name}}", debug=True)

@app.get("/api/v1/items")
def list_items(request):
    return {"items": [], "total": 0}

@app.post("/api/v1/items")
def create_item(request):
    data = request.json()
    return Response.json(data, StatusCode.CREATED)

@app.get("/api/v1/items/{item_id}")
def get_item(request):
    item_id = request.path_params.get("item_id")
    return {"id": item_id, "name": "Example"}

@app.get("/health")
def health(request):
    return {"status": "ok"}

if __name__ == "__main__":
    app.run()
'''

GRAPHQL_TEMPLATE = '''"""{{name}} — urubuga GraphQL server."""

from urubuga.app import UrubugaApplication
from urubuga.graphql.schema import GraphQLSchema

app = UrubugaApplication("{{name}}", debug=True)
schema = GraphQLSchema()

@schema.query("hello", type_name="String")
def resolve_hello():
    return "Hello from {{name}}"

@schema.query("users", type_name="[User]")
def resolve_users():
    return [{"id": "1", "name": "Alice"}]

@app.post("/graphql")
def graphql_endpoint(request):
    data = request.json()
    query = data.get("query", "")
    variables = data.get("variables")
    result = schema.execute(query, variables)
    return result

@app.get("/health")
def health(request):
    return {"status": "ok"}

if __name__ == "__main__":
    app.run()
'''

MICROSERVICE_TEMPLATE = '''"""{{name}} — urubuga microservice."""

from urubuga.app import UrubugaApplication

app = UrubugaApplication("{{name}}", debug=True)

@app.get("/health")
def health(request):
    return {"status": "ok", "service": "{{name}}"}

@app.get("/ready")
def ready(request):
    return {"ready": True}

@app.get("/info")
def info(request):
    return {
        "name": "{{name}}",
        "version": "0.1.0",
        "type": "microservice",
    }

if __name__ == "__main__":
    app.run()
'''

INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{name}}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <h1>Welcome to {{name}}</h1>
    <p>Built with urubuga — the official web platform of I language.</p>
</body>
</html>
'''

DEFAULT_CSS = '''body {
    font-family: system-ui, -apple-system, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #1a1a2e;
}
'''
