"""HTTP server (stdlib only) serving JSON API + static UI."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.db import query_features, query_overview, query_sessions

STATIC_DIR = Path(__file__).parent.parent / "static"


def _make_handler(db_path: Path):
    """Build a Handler class bound to the given DB path."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (BaseHTTPRequestHandler API)
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                self._serve_static("index.html", "text/html; charset=utf-8")
            elif parsed.path.startswith("/static/"):
                self._serve_static_path(parsed.path[len("/static/") :])
            elif parsed.path == "/api/overview":
                self._json(query_overview(db_path))
            elif parsed.path == "/api/features":
                self._json(query_features(db_path))
            elif parsed.path == "/api/sessions":
                qs = parse_qs(parsed.query)
                limit = int(qs.get("limit", ["100"])[0])
                self._json(query_sessions(db_path, limit=limit))
            else:
                self.send_error(404)

        def _serve_static(self, name: str, mime: str):
            path = STATIC_DIR / name
            if not path.exists():
                self.send_error(404)
                return
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _serve_static_path(self, name: str):
            ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            mime = {
                "js": "text/javascript; charset=utf-8",
                "css": "text/css; charset=utf-8",
                "html": "text/html; charset=utf-8",
                "svg": "image/svg+xml",
            }.get(ext, "application/octet-stream")
            self._serve_static(name, mime)

        def _json(self, data):
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):  # noqa: A002 (override)
            pass  # silent

    return Handler


def serve(db_path: Path, port: int = 8080) -> None:
    handler = _make_handler(db_path)
    print(f"Mission Control serving on http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), handler).serve_forever()
