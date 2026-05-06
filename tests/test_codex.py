"""Tests for the Codex transcript parser.

Codex JSONL records have 4 types: ``session_meta``, ``turn_context``,
``response_item``, ``event_msg``. Token usage lives in
``event_msg.payload.info.total_token_usage`` (cumulative — last record wins)
and ``last_token_usage`` (per-turn — used for prompt drill-down).
"""

import json
from pathlib import Path

import pytest

from src.scanner import Session
from src.sources.codex import parse_codex_jsonl

FIXTURE = Path(__file__).parent / "fixtures" / "codex-sample.jsonl"


def test_returns_one_session():
    sessions = parse_codex_jsonl(FIXTURE)
    assert len(sessions) == 1
    assert isinstance(sessions[0], Session)


def test_session_id_extracted_from_filename(tmp_path):
    """Filename pattern is ``rollout-<ts>-<uuid>.jsonl``; the UUID is the id."""
    src = FIXTURE.read_text()
    # Use a real Codex-style filename
    target = tmp_path / "rollout-2026-02-10T08-12-12-019c4740-7379-7020-b4d5-8971a38dfb09.jsonl"
    target.write_text(src)
    sessions = parse_codex_jsonl(target)
    assert sessions[0].session_id == "019c4740-7379-7020-b4d5-8971a38dfb09"


def test_aggregates_total_tokens_from_last_event():
    """Codex writes cumulative usage; we must take the LAST value, not sum.

    Also: Codex's ``input_tokens`` includes cached, so we subtract to align
    with Claude's "fresh-only" semantic and avoid double-charging.
    """
    sessions = parse_codex_jsonl(FIXTURE)
    s = sessions[0]
    # Final total_token_usage in fixture: input=450 (incl 140 cached),
    # output=105+20(reasoning)=125. Fresh input = 450 - 140 = 310.
    assert s.input_tokens == 310
    assert s.output_tokens == 125  # output + reasoning_output
    assert s.cache_read_tokens == 140
    # OpenAI does not bill cache create separately — always 0.
    assert s.cache_create_tokens == 0


def test_input_tokens_subtracts_cached_no_double_charge():
    """Regression: a session of all-cached input should bill 0 fresh input."""
    import json
    fixture_path = Path(__file__).parent / "fixtures" / "_all_cached.jsonl"
    fixture_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "type": "event_msg",
                "payload": {
                    "info": {
                        "last_token_usage": {
                            "input_tokens": 1000,
                            "cached_input_tokens": 1000,
                            "output_tokens": 0,
                            "reasoning_output_tokens": 0,
                            "total_tokens": 1000,
                        },
                        "total_token_usage": {
                            "input_tokens": 1000,
                            "cached_input_tokens": 1000,
                            "output_tokens": 0,
                            "reasoning_output_tokens": 0,
                            "total_tokens": 1000,
                        },
                    },
                },
            }
        )
        + "\n"
    )
    try:
        sessions = parse_codex_jsonl(fixture_path)
        assert sessions[0].input_tokens == 0
        assert sessions[0].cache_read_tokens == 1000
    finally:
        fixture_path.unlink()


def test_extracts_branch_and_cwd_from_session_meta():
    sessions = parse_codex_jsonl(FIXTURE)
    s = sessions[0]
    assert s.dominant_branch == "feat/codex-source"
    assert s.dominant_cwd == "/Users/hugo/Developer/mission-control"


def test_extracts_model_from_turn_context():
    sessions = parse_codex_jsonl(FIXTURE)
    assert sessions[0].model == "gpt-5.3-codex"


def test_records_started_at_from_session_meta():
    sessions = parse_codex_jsonl(FIXTURE)
    s = sessions[0]
    assert s.started_at == "2026-02-10T11:12:12.211Z"
    # ended_at should be the timestamp of the last record we saw
    assert s.ended_at is not None


def test_creates_one_prompt_per_event_with_last_token_usage():
    """Each event_msg with last_token_usage maps to a Prompt for drill-down."""
    sessions = parse_codex_jsonl(FIXTURE)
    s = sessions[0]
    assert len(s.prompts) == 3
    # The middle event: input=200 (incl 80 cached), output=30+5=35.
    # Fresh input = 200 - 80 = 120.
    p = s.prompts[1]
    assert p.input_tokens == 120
    assert p.cache_read_tokens == 80
    assert p.output_tokens == 35


def test_tolerates_malformed_lines():
    # Fixture ends with a "not json" line — parser must not crash.
    sessions = parse_codex_jsonl(FIXTURE)
    assert len(sessions) == 1


def test_returns_empty_list_for_no_token_records(tmp_path):
    fixture = tmp_path / "rollout-2026-01-01T00-00-00-deadbeef.jsonl"
    fixture.write_text(
        json.dumps(
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "type": "session_meta",
                "payload": {"id": "deadbeef", "cwd": "/tmp"},
            }
        )
        + "\n"
    )
    sessions = parse_codex_jsonl(fixture)
    assert sessions == []


def test_records_source_mtime():
    sessions = parse_codex_jsonl(FIXTURE)
    assert sessions[0].source_mtime is not None
    assert sessions[0].source_mtime > 0
