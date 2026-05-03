"""Config loader: ~/.mission-control/{config.json,db.sqlite}."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".mission-control"
CONFIG_FILE = CONFIG_DIR / "config.json"
DB_FILE = CONFIG_DIR / "db.sqlite"

DEFAULTS: dict = {
    "claude_projects_dir": str(Path.home() / ".claude" / "projects"),
    "scan_interval_seconds": 30,
    "pricing_plan": "api",  # "api" | "pro" | "max" | "max20x"
    "port": 8080,
    "worktree_root": str(Path.home() / "Developer"),
}


def load() -> dict:
    """Load config from disk, creating defaults if missing."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULTS, indent=2) + "\n")
        return dict(DEFAULTS)
    user = json.loads(CONFIG_FILE.read_text())
    return {**DEFAULTS, **user}
