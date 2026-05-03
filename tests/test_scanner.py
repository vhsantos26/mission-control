from pathlib import Path

from src.scanner import Session, parse_jsonl

FIXTURE = Path(__file__).parent / "fixtures" / "session-sample.jsonl"


def test_parse_returns_one_session():
    sessions = parse_jsonl(FIXTURE)
    assert len(sessions) == 1
    assert isinstance(sessions[0], Session)


def test_session_id_from_filename():
    sessions = parse_jsonl(FIXTURE)
    assert sessions[0].session_id == "session-sample"


def test_aggregates_tokens_from_assistant_messages():
    sessions = parse_jsonl(FIXTURE)
    s = sessions[0]
    # 100 + 200 = 300 (one duplicate skipped)
    assert s.input_tokens == 300
    assert s.output_tokens == 60  # 20 + 40
    # cache_read: 50 + 500 = 550; cache_create: 0 + 1000 = 1000
    assert s.cache_read_tokens == 550
    assert s.cache_create_tokens == 1000
    # back-compat property
    assert s.cache_tokens == 1550


def test_records_source_mtime():
    sessions = parse_jsonl(FIXTURE)
    s = sessions[0]
    assert s.source_mtime is not None
    assert s.source_mtime > 0


def test_records_model_counts():
    sessions = parse_jsonl(FIXTURE)
    s = sessions[0]
    # All assistant messages in fixture use claude-sonnet-4-6
    assert s.model_counts.get("claude-sonnet-4-6", 0) >= 2


def test_dedup_by_message_id(tmp_path):
    import json
    msg = {
        "type": "assistant",
        "message": {
            "id": "msg_x",
            "model": "claude-sonnet-4-6",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
        },
        "timestamp": "2026-05-03T10:00:00Z",
    }
    fixture = tmp_path / "dup-test.jsonl"
    fixture.write_text(json.dumps(msg) + "\n" + json.dumps(msg) + "\n")
    sessions = parse_jsonl(fixture)
    assert sessions[0].input_tokens == 100  # not 200


def test_tolerates_malformed_lines():
    # The fixture has a "malformed line not json" at the end — should not crash.
    sessions = parse_jsonl(FIXTURE)
    assert len(sessions) == 1


def test_records_model():
    sessions = parse_jsonl(FIXTURE)
    assert sessions[0].model == "claude-sonnet-4-6"


def test_returns_empty_list_for_no_assistant_messages(tmp_path):
    fixture = tmp_path / "no-assistant.jsonl"
    fixture.write_text(
        '{"type":"user","message":{"role":"user","content":"hi"}}\n'
    )
    sessions = parse_jsonl(fixture)
    assert sessions == []


def test_dominant_branch_picks_most_frequent():
    sessions = parse_jsonl(FIXTURE)
    s = sessions[0]
    # Fixture has 5 records with feat/multi-agent-setup, 1 with staging
    assert s.dominant_branch == "feat/multi-agent-setup"


def test_dominant_cwd_picks_most_frequent():
    sessions = parse_jsonl(FIXTURE)
    s = sessions[0]
    assert s.dominant_cwd == (
        "/Users/hugo/Developer/example-app/.worktrees/multi-agent-setup"
    )


def test_dominant_branch_is_none_when_no_branches(tmp_path):
    import json
    fixture = tmp_path / "no-branch.jsonl"
    fixture.write_text(
        json.dumps(
            {
                "type": "assistant",
                "message": {
                    "id": "x",
                    "model": "claude-sonnet-4-6",
                    "usage": {"input_tokens": 1, "output_tokens": 1},
                },
                "timestamp": "2026-05-03T10:00:00Z",
            }
        )
        + "\n"
    )
    sessions = parse_jsonl(fixture)
    assert sessions[0].dominant_branch is None
    assert sessions[0].dominant_cwd is None


def test_branch_counts_track_per_record():
    sessions = parse_jsonl(FIXTURE)
    s = sessions[0]
    assert s.branch_counts.get("feat/multi-agent-setup", 0) >= 4
    assert s.branch_counts.get("staging", 0) >= 1
