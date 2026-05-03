"""Parse Claude Code JSONL transcripts into Session records.

The Claude Code CLI writes one JSONL file per session in
``~/.claude/projects/<project-slug>/<session-uuid>.jsonl``. Lines have varying
``type`` values; the ones that contribute to billing carry token usage under
``message.usage`` (assistant messages with a unique ``message.id``).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json


@dataclass
class Prompt:
    message_id: Optional[str]
    role: str
    timestamp: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_tokens: int = 0


@dataclass
class Session:
    session_id: str
    project: str
    source_path: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    model: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_tokens: int = 0
    prompts: list[Prompt] = field(default_factory=list)
    branch_counts: dict[str, int] = field(default_factory=dict)
    cwd_counts: dict[str, int] = field(default_factory=dict)

    @property
    def dominant_branch(self) -> Optional[str]:
        """Most frequent gitBranch across records, or None if no branch info."""
        if not self.branch_counts:
            return None
        return max(self.branch_counts.items(), key=lambda kv: kv[1])[0]

    @property
    def dominant_cwd(self) -> Optional[str]:
        """Most frequent cwd across records, or None if no cwd info."""
        if not self.cwd_counts:
            return None
        return max(self.cwd_counts.items(), key=lambda kv: kv[1])[0]


def _project_from_path(path: Path) -> str:
    """Extract human-readable project name from a Claude Code project dir.

    Claude Code mangles paths to single-segment dir names like
    ``-Users-hugo-Developer-licitai``. We rebuild the original path-ish form
    for display purposes — exact accuracy is not critical here.
    """
    parent = path.parent.name
    if parent.startswith("-"):
        return parent[1:].replace("-", "/")
    return parent


def parse_jsonl(path: Path) -> list[Session]:
    """Parse one JSONL transcript into a list of Session (currently always 0 or 1).

    Returns an empty list if the file has no assistant messages with token usage.
    Tolerates malformed lines (skips them silently) so a partially-flushed file
    still yields whatever was parseable.
    """
    session_id = path.stem
    project = _project_from_path(path)
    session = Session(
        session_id=session_id,
        project=project,
        source_path=str(path),
    )
    seen_message_ids: set[str] = set()

    with path.open() as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(rec, dict):
                continue

            ts = rec.get("timestamp")
            if isinstance(ts, str):
                if not session.started_at:
                    session.started_at = ts
                session.ended_at = ts

            branch = rec.get("gitBranch")
            if isinstance(branch, str) and branch:
                session.branch_counts[branch] = (
                    session.branch_counts.get(branch, 0) + 1
                )
            cwd = rec.get("cwd")
            if isinstance(cwd, str) and cwd:
                session.cwd_counts[cwd] = session.cwd_counts.get(cwd, 0) + 1

            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue

            msg_id = msg.get("id")
            if msg_id and msg_id in seen_message_ids:
                continue
            if msg_id:
                seen_message_ids.add(msg_id)

            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue

            input_t = int(usage.get("input_tokens") or 0)
            output_t = int(usage.get("output_tokens") or 0)
            cache_read = int(usage.get("cache_read_input_tokens") or 0)
            cache_create = int(usage.get("cache_creation_input_tokens") or 0)
            cache_t = cache_read + cache_create

            model = msg.get("model")
            if isinstance(model, str):
                session.model = model

            session.input_tokens += input_t
            session.output_tokens += output_t
            session.cache_tokens += cache_t

            session.prompts.append(
                Prompt(
                    message_id=msg_id,
                    role=rec.get("type", "unknown"),
                    timestamp=ts or "",
                    input_tokens=input_t,
                    output_tokens=output_t,
                    cache_tokens=cache_t,
                )
            )

    return [session] if session.prompts else []
