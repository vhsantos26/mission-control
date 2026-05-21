"""HTTP server (stdlib only) serving JSON API + static UI."""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.db import (
    query_by_model,
    query_daily_cost,
    query_distinct_models,
    query_distinct_projects,
    query_features,
    query_overview,
    query_session_prompts,
    query_sessions,
    query_tokens_by_project,
    query_tool_usage,
)

STATIC_DIR = Path(__file__).parent.parent / "static"

log = logging.getLogger("mc.server")


def _make_handler(db_path: Path):
    """Build a Handler class bound to the given DB path."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (BaseHTTPRequestHandler API)
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)

            def first(name: str) -> str | None:
                v = qs.get(name)
                return v[0] if v and v[0] else None

            def many(name: str) -> list[str] | None:
                v = qs.get(name)
                values = [x for x in v if x] if v else []
                return values or None

            if parsed.path in ("/", "/index.html"):
                self._serve_static("index.html", "text/html; charset=utf-8")
            elif parsed.path.startswith("/static/"):
                self._serve_static_path(parsed.path[len("/static/") :])
            elif parsed.path == "/api/overview":
                self._json(
                    query_overview(
                        db_path,
                        project=many("project"),
                        model=first("model"),
                        since=first("since"),
                        until=first("until"),
                    )
                )
            elif parsed.path == "/api/features":
                self._json(
                    query_features(
                        db_path,
                        project=many("project"),
                        model=first("model"),
                        since=first("since"),
                        until=first("until"),
                    )
                )
            elif parsed.path == "/api/sessions":
                limit = int(qs.get("limit", ["200"])[0])
                self._json(
                    query_sessions(
                        db_path,
                        limit=limit,
                        project=many("project"),
                        feature=first("feature"),
                        model=first("model"),
                        since=first("since"),
                        until=first("until"),
                    )
                )
            elif parsed.path.startswith("/api/sessions/") and parsed.path.endswith(
                "/prompts"
            ):
                sid = parsed.path[len("/api/sessions/") : -len("/prompts")]
                self._json(query_session_prompts(db_path, sid))
            elif parsed.path == "/api/daily-cost":
                days = int(qs.get("days", ["30"])[0])
                self._json(
                    query_daily_cost(
                        db_path,
                        days=days,
                        project=many("project"),
                        model=first("model"),
                    )
                )
            elif parsed.path == "/api/by-project":
                self._json(
                    query_tokens_by_project(
                        db_path,
                        project=many("project"),
                        model=first("model"),
                        since=first("since"),
                        until=first("until"),
                    )
                )
            elif parsed.path == "/api/by-model":
                self._json(
                    query_by_model(
                        db_path,
                        project=many("project"),
                        since=first("since"),
                        until=first("until"),
                    )
                )
            elif parsed.path == "/api/by-tool":
                self._json(
                    query_tool_usage(
                        db_path,
                        project=many("project"),
                        feature=first("feature"),
                        model=first("model"),
                        since=first("since"),
                        until=first("until"),
                        limit=int(qs.get("limit", ["20"])[0]),
                    )
                )
            elif parsed.path == "/api/projects":
                self._json(query_distinct_projects(db_path))
            elif parsed.path == "/api/models":
                self._json(query_distinct_models(db_path))
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
    log.info("serving on http://127.0.0.1:%d", port)
    HTTPServer(("127.0.0.1", port), handler).serve_forever()
