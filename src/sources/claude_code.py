"""Claude Code transcripts source — reads ``~/.claude/projects/``.

Format: one JSONL file per session under ``<projects-dir>/<slug>/<uuid>.jsonl``.
Each record carries ``timestamp``, ``gitBranch``, ``cwd``, plus an assistant
``message`` with ``message.id`` and ``message.usage``. See ``scanner.parse_jsonl``
for the line-level parser; this class only handles directory walking.
"""

import logging
from pathlib import Path
from typing import Iterator

from src.scanner import Session, parse_jsonl
from src.sources.base import SessionSource

log = logging.getLogger("mc.source.claude")


class ClaudeCodeSource(SessionSource):
    name = "claude"

    def discover(self, cfg: dict) -> Iterator[Session]:
        root = Path(cfg["claude_projects_dir"])
        if not root.exists():
            log.warning("claude_projects_dir does not exist: %s", root)
            return

        for project_dir in sorted(root.iterdir()):
            if not project_dir.is_dir():
                continue
            for jsonl in project_dir.glob("*.jsonl"):
                try:
                    sessions = parse_jsonl(jsonl)
                except Exception as e:
                    log.warning("failed to parse %s: %s", jsonl.name, e)
                    continue
                yield from sessions
