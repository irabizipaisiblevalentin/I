"""staticfiles — Static file serving."""

from __future__ import annotations

import mimetypes
import os
from typing import Optional

from urubuga.http.request_response import Response, StatusCode


class StaticFileHandler:
    """Serves static files from a directory."""

    def __init__(self, root_dir: str = "static",
                 url_prefix: str = "/static",
                 index_files: Optional[list] = None,
                 cache_max_age: int = 86400) -> None:
        self.root_dir = root_dir
        self.url_prefix = url_prefix.rstrip("/")
        self.index_files = index_files or ["index.html", "index.htm"]
        self.cache_max_age = cache_max_age
        self._file_count = 0

    def serve(self, path: str) -> Optional[Response]:
        relative = path[len(self.url_prefix):].lstrip("/")
        if not relative:
            for index in self.index_files:
                full = os.path.join(self.root_dir, index)
                if os.path.isfile(full):
                    return self._serve_file(full)
            return None

        full = os.path.join(self.root_dir, relative)
        full = os.path.normpath(full)

        if not full.startswith(os.path.normpath(self.root_dir)):
            return Response.error(StatusCode.FORBIDDEN, "Access denied")

        if os.path.isfile(full):
            return self._serve_file(full)
        return None

    def _serve_file(self, path: str) -> Response:
        content_type, _ = mimetypes.guess_type(path)
        content_type = content_type or "application/octet-stream"

        with open(path, "rb") as f:
            body = f.read()

        headers = {
            "content-type": content_type,
            "content-length": str(len(body)),
            "cache-control": f"public, max-age={self.cache_max_age}",
        }
        self._file_count += 1
        return Response(StatusCode.OK, headers, body)

    @property
    def file_count(self) -> int:
        return self._file_count
