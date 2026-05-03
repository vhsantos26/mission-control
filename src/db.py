"""SQLite persistence layer for sessions, prompts, and features."""

import sqlite3
from pathlib import Path

from src.pricing import cost_for_session
from src.scanner import Session

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id                    TEXT PRIMARY KEY,
  project               TEXT NOT NULL,
  feature               TEXT,
  branch                TEXT,
  worktree_path         TEXT,
  started_at            TEXT,
  ended_at              TEXT,
  model                 TEXT,
  input_tokens          INTEGER DEFAULT 0,
  output_tokens         INTEGER DEFAULT 0,
  cache_read_tokens     INTEGER DEFAULT 0,
  cache_create_tokens   INTEGER DEFAULT 0,
  cost_usd              REAL DEFAULT 0,
  source_path           TEXT NOT NULL,
  source_mtime          REAL
);
CREATE INDEX IF NOT EXISTS idx_sessions_project_feature ON sessions(project, feature);
CREATE INDEX IF NOT EXISTS idx_sessions_model ON sessions(model);

CREATE TABLE IF NOT EXISTS prompts (
  id                    INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id            TEXT NOT NULL,
  ts                    TEXT NOT NULL,
  role                  TEXT NOT NULL,
  message_id            TEXT UNIQUE,
  input_tokens          INTEGER DEFAULT 0,
  output_tokens         INTEGER DEFAULT 0,
  cache_read_tokens     INTEGER DEFAULT 0,
  cache_create_tokens   INTEGER DEFAULT 0,
  cost_usd              REAL DEFAULT 0,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS features (
  project        TEXT NOT NULL,
  name           TEXT NOT NULL,
  first_seen     TEXT,
  last_seen      TEXT,
  total_tokens   INTEGER DEFAULT 0,
  total_cost     REAL DEFAULT 0,
  pr_url         TEXT,
  pr_status      TEXT,
  PRIMARY KEY (project, name)
);

CREATE TABLE IF NOT EXISTS tool_uses (
  session_id   TEXT NOT NULL,
  tool_name    TEXT NOT NULL,
  count        INTEGER NOT NULL,
  PRIMARY KEY (session_id, tool_name),
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_tool_uses_name ON tool_uses(tool_name);
"""

# A session is "active" if its source JSONL was modified within this many
# seconds. Heuristic — Claude Code keeps writing while you interact.
ACTIVE_THRESHOLD_SECONDS = 5 * 60


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_session(
    db_path: Path,
    session: Session,
    feature: str = "_no-feature",
    branch: str | None = None,
    worktree_path: str | None = None,
    plan: str = "api",
) -> None:
    cost = cost_for_session(
        model=session.model or "",
        input_tokens=session.input_tokens,
        output_tokens=session.output_tokens,
        cache_read_tokens=session.cache_read_tokens,
        cache_create_tokens=session.cache_create_tokens,
        plan=plan,
    )
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                id, project, feature, branch, worktree_path,
                started_at, ended_at, model,
                input_tokens, output_tokens, cache_read_tokens, cache_create_tokens,
                cost_usd, source_path, source_mtime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                project = excluded.project,
                feature = excluded.feature,
                branch = excluded.branch,
                worktree_path = excluded.worktree_path,
                ended_at = excluded.ended_at,
                model = excluded.model,
                input_tokens = excluded.input_tokens,
                output_tokens = excluded.output_tokens,
                cache_read_tokens = excluded.cache_read_tokens,
                cache_create_tokens = excluded.cache_create_tokens,
                cost_usd = excluded.cost_usd,
                source_mtime = excluded.source_mtime
            """,
            (
                session.session_id,
                session.project,
                feature,
                branch,
                worktree_path,
                session.started_at,
                session.ended_at,
                session.model,
                session.input_tokens,
                session.output_tokens,
                session.cache_read_tokens,
                session.cache_create_tokens,
                cost,
                session.source_path,
                session.source_mtime,
            ),
        )

        conn.execute(
            "DELETE FROM tool_uses WHERE session_id = ?", (session.session_id,)
        )
        for tool_name, count in session.tool_counts.items():
            conn.execute(
                """
                INSERT INTO tool_uses (session_id, tool_name, count)
                VALUES (?, ?, ?)
                """,
                (session.session_id, tool_name, count),
            )

        for p in session.prompts:
            if not p.message_id:
                continue
            p_cost = cost_for_session(
                model=session.model or "",
                input_tokens=p.input_tokens,
                output_tokens=p.output_tokens,
                cache_read_tokens=p.cache_read_tokens,
                cache_create_tokens=p.cache_create_tokens,
                plan=plan,
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO prompts (
                    session_id, ts, role, message_id,
                    input_tokens, output_tokens, cache_read_tokens, cache_create_tokens,
                    cost_usd
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    p.timestamp,
                    p.role,
                    p.message_id,
                    p.input_tokens,
                    p.output_tokens,
                    p.cache_read_tokens,
                    p.cache_create_tokens,
                    p_cost,
                ),
            )

        _recompute_feature(conn, session.project, feature)


def _recompute_feature(
    conn: sqlite3.Connection, project: str, feature: str
) -> None:
    row = conn.execute(
        """
        SELECT
            MIN(started_at) AS first_seen,
            MAX(ended_at) AS last_seen,
            SUM(input_tokens + output_tokens + cache_read_tokens + cache_create_tokens) AS total_tokens,
            SUM(cost_usd) AS total_cost
        FROM sessions
        WHERE project = ? AND feature = ?
        """,
        (project, feature),
    ).fetchone()
    if not row or row["first_seen"] is None:
        return
    conn.execute(
        """
        INSERT INTO features (project, name, first_seen, last_seen, total_tokens, total_cost)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(project, name) DO UPDATE SET
            first_seen = excluded.first_seen,
            last_seen = excluded.last_seen,
            total_tokens = excluded.total_tokens,
            total_cost = excluded.total_cost
        """,
        (
            project,
            feature,
            row["first_seen"],
            row["last_seen"],
            int(row["total_tokens"] or 0),
            float(row["total_cost"] or 0),
        ),
    )


def delete_sessions_except(db_path: Path, keep_ids: set[str]) -> int:
    """Delete all sessions whose ID is not in keep_ids. Returns count deleted.

    Use this after a full scan pass to drop stale rows from previous-version
    scans (e.g., sessions that no longer resolve to a valid project, or rows
    with old mangled project names).
    """
    with _connect(db_path) as conn:
        if not keep_ids:
            cursor = conn.execute("DELETE FROM sessions")
            conn.execute("DELETE FROM prompts")
            conn.execute("DELETE FROM tool_uses")
            conn.execute("DELETE FROM features")
            return cursor.rowcount
        placeholders = ",".join("?" for _ in keep_ids)
        ids_tuple = tuple(keep_ids)
        # Delete prompts and tool_uses of stale sessions first (FK ref)
        conn.execute(
            f"DELETE FROM prompts WHERE session_id NOT IN ({placeholders})",
            ids_tuple,
        )
        conn.execute(
            f"DELETE FROM tool_uses WHERE session_id NOT IN ({placeholders})",
            ids_tuple,
        )
        cursor = conn.execute(
            f"DELETE FROM sessions WHERE id NOT IN ({placeholders})",
            ids_tuple,
        )
        deleted = cursor.rowcount
        # Recompute features table from scratch (cheap) so it stays in sync
        conn.execute("DELETE FROM features")
        conn.execute(
            """
            INSERT INTO features (project, name, first_seen, last_seen, total_tokens, total_cost)
            SELECT
                project,
                COALESCE(feature, '_no-feature'),
                MIN(started_at),
                MAX(ended_at),
                COALESCE(SUM(input_tokens + output_tokens + cache_read_tokens + cache_create_tokens), 0),
                COALESCE(SUM(cost_usd), 0)
            FROM sessions
            GROUP BY project, feature
            """
        )
        return deleted


def _filter_clause(
    project: str | None = None,
    feature: str | None = None,
    model: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> tuple[str, list]:
    """Build WHERE clause + params for common filters.

    ``model`` matches by family substring: passing "opus" matches "claude-opus-4-7"
    and "claude-opus-4-6" alike.
    """
    conditions: list[str] = []
    params: list = []
    if project:
        conditions.append("project = ?")
        params.append(project)
    if feature:
        conditions.append("(feature = ? OR feature LIKE ?)")
        params.extend([feature, f"%{feature}%"])
    if model:
        conditions.append("model LIKE ?")
        params.append(f"%{model}%")
    if since:
        conditions.append("started_at >= ?")
        params.append(since)
    if until:
        conditions.append("started_at <= ?")
        params.append(until)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params


def query_overview(
    db_path: Path,
    project: str | None = None,
    model: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> dict:
    where, params = _filter_clause(
        project=project, model=model, since=since, until=until
    )
    with _connect(db_path) as conn:
        row = conn.execute(
            f"""
            SELECT
                COUNT(*) AS total_sessions,
                COALESCE(SUM(input_tokens), 0) AS total_input_tokens,
                COALESCE(SUM(output_tokens), 0) AS total_output_tokens,
                COALESCE(SUM(cache_read_tokens), 0) AS total_cache_read_tokens,
                COALESCE(SUM(cache_create_tokens), 0) AS total_cache_create_tokens,
                COALESCE(SUM(cache_read_tokens + cache_create_tokens), 0) AS total_cache_tokens,
                COALESCE(SUM(cost_usd), 0) AS total_cost
            FROM sessions
            {where}
            """,
            params,
        ).fetchone()
        # Also count total prompts (turns) within the same filter
        prompts_row = conn.execute(
            f"""
            SELECT COUNT(*) AS total_turns
            FROM prompts p
            WHERE p.session_id IN (SELECT id FROM sessions {where})
            """,
            params,
        ).fetchone()
        result = dict(row) if row else {}
        result["total_turns"] = prompts_row["total_turns"] if prompts_row else 0
        return result


def query_tool_usage(
    db_path: Path,
    project: str | None = None,
    feature: str | None = None,
    model: str | None = None,
    since: str | None = None,
    until: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Aggregate tool_use counts across sessions matching the filters.

    Returns rows of {tool_name, total_count, sessions} ordered by total_count DESC.
    """
    where, params = _filter_clause(
        project=project, feature=feature, model=model, since=since, until=until
    )
    join_where = where.replace("WHERE ", "WHERE ", 1) if where else ""
    params.append(limit)
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT t.tool_name AS tool_name,
                   SUM(t.count) AS total_count,
                   COUNT(DISTINCT t.session_id) AS sessions
            FROM tool_uses t
            INNER JOIN sessions s ON s.id = t.session_id
            {join_where}
            GROUP BY t.tool_name
            ORDER BY total_count DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [dict(r) for r in rows]


def query_features(
    db_path: Path,
    project: str | None = None,
    model: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> list[dict]:
    """Query features table, optionally aggregated only across sessions in date range or by model."""
    # When any filter that the pre-aggregated table doesn't support is in play,
    # recompute on the fly from sessions.
    needs_recompute = bool(since or until or model)
    if needs_recompute:
        where, params = _filter_clause(
            project=project, model=model, since=since, until=until
        )
        with _connect(db_path) as conn:
            rows = conn.execute(
                f"""
                SELECT
                    project,
                    COALESCE(feature, '_no-feature') AS name,
                    MIN(started_at) AS first_seen,
                    MAX(ended_at) AS last_seen,
                    SUM(input_tokens + output_tokens + cache_read_tokens + cache_create_tokens) AS total_tokens,
                    SUM(cost_usd) AS total_cost
                FROM sessions
                {where}
                GROUP BY project, feature
                ORDER BY total_cost DESC
                """,
                params,
            ).fetchall()
            return [dict(r) for r in rows]
    # Fast path: read pre-aggregated features table
    where_parts: list[str] = []
    params: list = []
    if project:
        where_parts.append("project = ?")
        params.append(project)
    where = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT project, name, first_seen, last_seen, total_tokens, total_cost,
                   pr_url, pr_status
            FROM features
            {where}
            ORDER BY total_cost DESC
            """,
            params,
        ).fetchall()
        return [dict(r) for r in rows]


def query_sessions(
    db_path: Path,
    limit: int = 100,
    project: str | None = None,
    feature: str | None = None,
    model: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> list[dict]:
    """Return sessions with an `is_active` flag (true if mtime within threshold)."""
    import time

    where, params = _filter_clause(
        project=project, feature=feature, model=model, since=since, until=until
    )
    params.append(limit)
    now = time.time()
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT id AS session_id, project, feature, branch, started_at, ended_at,
                   model, input_tokens, output_tokens,
                   cache_read_tokens, cache_create_tokens,
                   (cache_read_tokens + cache_create_tokens) AS cache_tokens,
                   cost_usd, source_mtime
            FROM sessions
            {where}
            ORDER BY started_at DESC, COALESCE(source_mtime, 0) DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            mtime = d.get("source_mtime")
            d["is_active"] = bool(
                mtime and (now - mtime) <= ACTIVE_THRESHOLD_SECONDS
            )
            result.append(d)
        return result


def query_session_prompts(db_path: Path, session_id: str) -> list[dict]:
    """Drill-down: list of prompts for a session, ordered chronologically."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT ts, role, message_id, input_tokens, output_tokens,
                   cache_read_tokens, cache_create_tokens,
                   (cache_read_tokens + cache_create_tokens) AS cache_tokens,
                   cost_usd
            FROM prompts
            WHERE session_id = ?
            ORDER BY ts ASC
            """,
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def query_daily_cost(
    db_path: Path,
    days: int = 30,
    project: str | None = None,
    model: str | None = None,
) -> list[dict]:
    """Daily breakdown for the last N days. Returns input/output/cache_create/cache_read split per day."""
    where_parts = ["started_at IS NOT NULL"]
    params: list = []
    if project:
        where_parts.append("project = ?")
        params.append(project)
    if model:
        where_parts.append("model LIKE ?")
        params.append(f"%{model}%")
    where = "WHERE " + " AND ".join(where_parts)
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT
                substr(started_at, 1, 10) AS day,
                COUNT(*) AS sessions,
                SUM(input_tokens) AS input_tokens,
                SUM(output_tokens) AS output_tokens,
                SUM(cache_create_tokens) AS cache_create_tokens,
                SUM(cache_read_tokens) AS cache_read_tokens,
                SUM(cost_usd) AS cost
            FROM sessions
            {where}
            GROUP BY day
            ORDER BY day DESC
            LIMIT ?
            """,
            (*params, days),
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))


def query_tokens_by_project(
    db_path: Path,
    model: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> list[dict]:
    """Per-project totals for stacked input/output bar chart."""
    where, params = _filter_clause(model=model, since=since, until=until)
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT
                project,
                SUM(input_tokens) AS input_tokens,
                SUM(output_tokens) AS output_tokens,
                SUM(cache_create_tokens) AS cache_create_tokens,
                SUM(cache_read_tokens) AS cache_read_tokens,
                SUM(cost_usd) AS cost
            FROM sessions
            {where}
            GROUP BY project
            ORDER BY cost DESC
            """,
            params,
        ).fetchall()
        return [dict(r) for r in rows]


def query_by_model(
    db_path: Path,
    project: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> list[dict]:
    """Per-model totals for the donut chart."""
    where, params = _filter_clause(project=project, since=since, until=until)
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT
                COALESCE(model, '_unknown') AS model,
                COUNT(*) AS sessions,
                SUM(input_tokens) AS input_tokens,
                SUM(output_tokens) AS output_tokens,
                SUM(cache_create_tokens) AS cache_create_tokens,
                SUM(cache_read_tokens) AS cache_read_tokens,
                SUM(input_tokens + output_tokens + cache_read_tokens + cache_create_tokens) AS total_tokens,
                SUM(cost_usd) AS cost
            FROM sessions
            {where}
            GROUP BY model
            ORDER BY cost DESC
            """,
            params,
        ).fetchall()
        return [dict(r) for r in rows]


def query_distinct_projects(db_path: Path) -> list[str]:
    """Return sorted list of distinct project names — useful to populate filter dropdown."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT DISTINCT project FROM sessions ORDER BY project"
        ).fetchall()
        return [r["project"] for r in rows]


def query_distinct_models(db_path: Path) -> list[str]:
    """Return sorted list of distinct model names with usage."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT DISTINCT model FROM sessions WHERE model IS NOT NULL ORDER BY model"
        ).fetchall()
        return [r["model"] for r in rows]
