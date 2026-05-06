"""Session sources — pluggable adapters that produce :class:`Session` records.

Each tool (Claude Code, Codex, …) writes its own transcript format. A
``SessionSource`` adapts that format to the canonical ``Session`` dataclass
the rest of the pipeline (db, server, UI) consumes unchanged.
"""

from src.sources.base import SessionSource
from src.sources.claude_code import ClaudeCodeSource
from src.sources.codex import CodexSource

__all__ = ["SessionSource", "ClaudeCodeSource", "CodexSource"]
