from src.db import (
    init_db,
    query_features,
    query_overview,
    query_sessions,
    upsert_session,
)
from src.scanner import Prompt, Session


def _make_session(
    sid: str,
    feature: str = "foo",
    project: str = "test/project",
    input_t: int = 1000,
    output_t: int = 200,
    model: str = "claude-sonnet-4-6",
    mtime: float | None = None,
) -> Session:
    s = Session(
        session_id=sid,
        project=project,
        source_path=f"/tmp/{sid}.jsonl",
        started_at="2026-05-03T10:00:00Z",
        ended_at="2026-05-03T11:00:00Z",
        model=model,
        input_tokens=input_t,
        output_tokens=output_t,
        cache_read_tokens=0,
        cache_create_tokens=0,
        source_mtime=mtime,
    )
    s.prompts = [
        Prompt(
            message_id=f"msg_{sid}",
            role="assistant",
            timestamp="2026-05-03T10:00:01Z",
            input_tokens=input_t,
            output_tokens=output_t,
        )
    ]
    return s


def test_init_creates_tables(tmp_path):
    db = tmp_path / "test.sqlite"
    init_db(db)
    assert db.exists()


def test_upsert_session_persists(tmp_path):
    db = tmp_path / "test.sqlite"
    init_db(db)
    s = _make_session("s1", feature="foo")
    upsert_session(db, s, feature="foo")
    sessions = query_sessions(db)
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == "s1"
    assert sessions[0]["feature"] == "foo"


def test_upsert_is_idempotent(tmp_path):
    db = tmp_path / "test.sqlite"
    init_db(db)
    s = _make_session("s1", feature="foo")
    upsert_session(db, s, feature="foo")
    upsert_session(db, s, feature="foo")  # second time should not duplicate
    sessions = query_sessions(db)
    assert len(sessions) == 1


def test_query_features_aggregates_by_feature(tmp_path):
    db = tmp_path / "test.sqlite"
    init_db(db)
    upsert_session(db, _make_session("s1", input_t=1000), feature="foo")
    upsert_session(db, _make_session("s2", input_t=2000), feature="foo")
    upsert_session(db, _make_session("s3", input_t=500), feature="bar")
    features = query_features(db)
    by_name = {f["name"]: f for f in features}
    assert by_name["foo"]["total_tokens"] >= 3000
    assert by_name["bar"]["total_tokens"] >= 500


def test_query_overview_returns_totals(tmp_path):
    db = tmp_path / "test.sqlite"
    init_db(db)
    upsert_session(db, _make_session("s1"), feature="foo")
    overview = query_overview(db)
    assert overview["total_sessions"] == 1
    assert overview["total_input_tokens"] >= 1000
