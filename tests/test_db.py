from src.db import (
    init_db,
    query_features,
    query_overview,
    query_session_prompts,
    query_sessions,
    query_tokens_by_project,
    query_tool_usage,
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


def test_query_sessions_orders_by_started_at_desc(tmp_path):
    """Sessions tab orders newest-started first (matches the column user sees).

    Regression: v0.4.0 ordered by source_mtime DESC, which made started_at
    column appear to bounce dates when long sessions had mtime updated past
    later-started sessions. Issue #1 reproduces the perceived 'ASC bug'.
    """
    db = tmp_path / "test.sqlite"
    init_db(db)
    s_old_started_recent_mtime = _make_session("s_old", mtime=2000.0)
    s_old_started_recent_mtime.started_at = "2026-04-01T10:00:00Z"
    s_new_started_old_mtime = _make_session("s_new", mtime=1000.0)
    s_new_started_old_mtime.started_at = "2026-05-02T10:00:00Z"
    upsert_session(db, s_old_started_recent_mtime, feature="foo")
    upsert_session(db, s_new_started_old_mtime, feature="foo")
    sessions = query_sessions(db)
    assert sessions[0]["session_id"] == "s_new", "newest started_at must be first"
    assert sessions[1]["session_id"] == "s_old"


def test_query_session_prompts_orders_by_ts_desc(tmp_path):
    """Drill-down rows show newest message first to mirror the parent table.

    Active sessions update continuously; the user expects to see the most
    recent activity at the top, not the start of the conversation.
    """
    db = tmp_path / "test.sqlite"
    init_db(db)
    s = _make_session("s1", feature="foo")
    s.prompts = [
        Prompt(
            message_id="msg_old",
            role="assistant",
            timestamp="2026-05-04T10:57:00Z",
            input_tokens=100,
            output_tokens=10,
        ),
        Prompt(
            message_id="msg_mid",
            role="assistant",
            timestamp="2026-05-04T10:59:00Z",
            input_tokens=200,
            output_tokens=20,
        ),
        Prompt(
            message_id="msg_new",
            role="assistant",
            timestamp="2026-05-04T11:01:00Z",
            input_tokens=300,
            output_tokens=30,
        ),
    ]
    upsert_session(db, s, feature="foo")
    prompts = query_session_prompts(db, "s1")
    assert [p["message_id"] for p in prompts] == ["msg_new", "msg_mid", "msg_old"]


def test_query_sessions_uses_mtime_as_tiebreaker(tmp_path):
    """When two sessions started at the same instant, mtime DESC breaks the tie."""
    db = tmp_path / "test.sqlite"
    init_db(db)
    s_lower_mtime = _make_session("s_lower", mtime=1000.0)
    s_higher_mtime = _make_session("s_higher", mtime=2000.0)
    upsert_session(db, s_lower_mtime, feature="foo")
    upsert_session(db, s_higher_mtime, feature="foo")
    sessions = query_sessions(db)
    assert sessions[0]["session_id"] == "s_higher"
    assert sessions[1]["session_id"] == "s_lower"


def test_query_tool_usage_aggregates_across_sessions(tmp_path):
    """tool_uses table is upserted from session.tool_counts and aggregated
    by query_tool_usage with standard filters."""
    db = tmp_path / "test.sqlite"
    init_db(db)
    s1 = _make_session("s1")
    s1.tool_counts = {"Bash": 5, "Read": 3}
    s2 = _make_session("s2")
    s2.tool_counts = {"Bash": 2, "Edit": 1}
    upsert_session(db, s1, feature="foo")
    upsert_session(db, s2, feature="foo")
    rows = query_tool_usage(db)
    by_name = {r["tool_name"]: r for r in rows}
    assert by_name["Bash"]["total_count"] == 7
    assert by_name["Bash"]["sessions"] == 2
    assert by_name["Read"]["total_count"] == 3
    assert by_name["Read"]["sessions"] == 1
    assert by_name["Edit"]["total_count"] == 1


def test_query_tool_usage_idempotent_on_re_upsert(tmp_path):
    """Re-upserting a session must replace tool_uses, not double-count."""
    db = tmp_path / "test.sqlite"
    init_db(db)
    s1 = _make_session("s1")
    s1.tool_counts = {"Bash": 5}
    upsert_session(db, s1, feature="foo")
    upsert_session(db, s1, feature="foo")  # second upsert
    rows = query_tool_usage(db)
    assert rows[0]["total_count"] == 5  # not 10


def test_query_overview_returns_totals(tmp_path):
    db = tmp_path / "test.sqlite"
    init_db(db)
    upsert_session(db, _make_session("s1"), feature="foo")
    overview = query_overview(db)
    assert overview["total_sessions"] == 1
    assert overview["total_input_tokens"] >= 1000


def test_query_tokens_by_project_includes_session_count(tmp_path):
    """Regression: the Projects tab needs a per-project session count.

    The UI binds to ``d.sessions`` directly; if the SQL forgets ``COUNT(*)``,
    the column silently shows ``—`` (NaN.toLocaleString -> "NaN" hidden by
    fmt(null)). Don't drop the column from the SELECT.
    """
    db = tmp_path / "test.sqlite"
    init_db(db)
    upsert_session(db, _make_session("s1", project="alpha"), feature="foo")
    upsert_session(db, _make_session("s2", project="alpha"), feature="bar")
    upsert_session(db, _make_session("s3", project="beta"), feature="foo")

    rows = query_tokens_by_project(db)
    by_project = {r["project"]: r for r in rows}
    assert by_project["alpha"]["sessions"] == 2
    assert by_project["beta"]["sessions"] == 1
