"""Codex (OpenAI) transcripts source — reads ``~/.codex/sessions/``.

Format: one JSONL file per session under
``<root>/<year>/<month>/<day>/rollout-<ts>-<uuid>.jsonl``.

Records carry a ``type`` field with four values worth tracking:

- ``session_meta`` (1 per file): provides the session UUID, ``cwd``,
  ``git.branch`` and ``git.commit_hash``.
- ``turn_context``: provides the active model (e.g. ``gpt-5.3-codex``);
  may change between turns when the user switches models.
- ``response_item``: user/assistant messages (no token data).
- ``event_msg``: carries cumulative ``total_token_usage`` AND per-turn
  ``last_token_usage`` under ``payload.info``.

Token usage is **cumulative** in Codex (unlike Claude Code which is per-msg).
We take the last ``total_token_usage`` we see as the session total, and treat
each ``last_token_usage`` as one Prompt for drill-down.

OpenAI does not bill cache create separately, so ``cache_create_tokens`` is
always 0 here. ``reasoning_output_tokens`` is folded into ``output_tokens``
since OpenAI bills it as output.
"""

import json
import logging
import re
from pathlib import Path
from typing import Iterator, Optional

from src.scanner import Prompt, Session
from src.sources.base import SessionSource

log = logging.getLogger("mc.source.codex")

# rollout-2026-02-10T08-12-12-019c4740-7379-7020-b4d5-8971a38dfb09.jsonl
# Filename's trailing UUID (after the timestamp) is the session id.
_FILENAME_RE = re.compile(
    r"^rollout-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-(?P<uuid>[0-9a-f-]+)$"
)


def _session_id_from_path(path: Path) -> str:
    """Extract the session UUID from a rollout filename, falling back to stem."""
    m = _FILENAME_RE.match(path.stem)
    return m.group("uuid") if m else path.stem


def _extract_usage(usage: dict) -> tuple[int, int, int]:
    """Map a Codex usage dict to ``(fresh_input, output_with_reasoning, cached)``.

    OpenAI's ``input_tokens`` is the **total** input that entered the call,
    including cached tokens. ``cached_input_tokens`` is a subset of that total.
    Mission Control's pricing tier expects ``input_tokens`` to mean *fresh*
    input only (Claude's convention) — otherwise cached tokens get billed
    twice (once at full input price, once at the cached rate). So we subtract.
    """
    total_input = int(usage.get("input_tokens") or 0)
    cached_t = int(usage.get("cached_input_tokens") or 0)
    output_t = int(usage.get("output_tokens") or 0)
    reasoning_t = int(usage.get("reasoning_output_tokens") or 0)
    # Defensive: never let cached exceed total (would yield a negative).
    fresh_input = max(total_input - cached_t, 0)
    # Reasoning tokens are billed as output.
    return fresh_input, output_t + reasoning_t, cached_t


def parse_codex_jsonl(path: Path) -> list[Session]:
    """Parse one Codex transcript into ``[Session]`` (or ``[]`` if no token data)."""
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = None

    session = Session(
        session_id=_session_id_from_path(path),
        # Project will be canonicalized upstream from cwd; raw value is unused.
        project="",
        source_path=str(path),
        source_mtime=mtime,
    )

    last_total_usage: Optional[dict] = None
    prev_total_total: Optional[int] = None
    saw_any_usage = False

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

            t = rec.get("type")
            payload = rec.get("payload")
            if not isinstance(payload, dict):
                continue

            if t == "session_meta":
                cwd = payload.get("cwd")
                if isinstance(cwd, str) and cwd:
                    session.cwd_counts[cwd] = session.cwd_counts.get(cwd, 0) + 1
                git = payload.get("git")
                if isinstance(git, dict):
                    branch = git.get("branch")
                    if isinstance(branch, str) and branch:
                        session.branch_counts[branch] = (
                            session.branch_counts.get(branch, 0) + 1
                        )

            elif t == "turn_context":
                model = payload.get("model")
                if isinstance(model, str) and model:
                    session.model = model
                    session.model_counts[model] = (
                        session.model_counts.get(model, 0) + 1
                    )

            elif t == "event_msg":
                info = payload.get("info")
                if not isinstance(info, dict):
                    continue
                # Emit a Prompt only when total_token_usage advances — Codex
                # writes multiple event_msg records per turn (task_started,
                # task_complete, etc.) all carrying the SAME last_token_usage,
                # which would otherwise duplicate every turn 3-5×.
                total_usage = info.get("total_token_usage")
                last_usage = info.get("last_token_usage")
                if isinstance(total_usage, dict):
                    cur_total = int(total_usage.get("total_tokens") or 0)
                    if cur_total != prev_total_total and isinstance(last_usage, dict):
                        inp, out, cached = _extract_usage(last_usage)
                        if inp or out or cached:
                            saw_any_usage = True
                            session.prompts.append(
                                Prompt(
                                    message_id=f"{session.session_id}:{ts or len(session.prompts)}",
                                    role="assistant",
                                    timestamp=ts or "",
                                    input_tokens=inp,
                                    output_tokens=out,
                                    cache_read_tokens=cached,
                                    cache_create_tokens=0,
                                )
                            )
                    prev_total_total = cur_total
                    last_total_usage = total_usage

    if not saw_any_usage and not last_total_usage:
        return []

    if last_total_usage:
        inp, out, cached = _extract_usage(last_total_usage)
        session.input_tokens = inp
        session.output_tokens = out
        session.cache_read_tokens = cached
        session.cache_create_tokens = 0

    return [session]


class CodexSource(SessionSource):
    name = "codex"

    def discover(self, cfg: dict) -> Iterator[Session]:
        raw = cfg.get("codex_sessions_dir")
        if not raw:
            return
        root = Path(raw).expanduser()
        if not root.exists():
            log.debug("codex_sessions_dir does not exist: %s", root)
            return

        for jsonl in root.rglob("rollout-*.jsonl"):
            try:
                sessions = parse_codex_jsonl(jsonl)
            except Exception as e:
                log.warning("failed to parse %s: %s", jsonl.name, e)
                continue
            yield from sessions
