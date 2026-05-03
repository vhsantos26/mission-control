"""SQLite persistence layer for sessions, prompts, and features."""

import sqlite3
from pathlib import Path

from src.pricing import cost_for_session
from src.scanner import Session

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id              TEXT PRIMARY KEY,
  project         TEXT NOT NULL,
  feature         TEXT,
  branch          TEXT,
  worktree_path   TEXT,
  started_at      TEXT,
  ended_at        TEXT,
  model           TEXT,
  input_tokens    INTEGER DEFAULT 0,
  output_tokens   INTEGER DEFAULT 0,
  cache_tokens    INTEGER DEFAULT 0,
  cost_usd        REAL DEFAULT 0,
  source_path     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_project_feature ON sessions(project, feature);

CREATE TABLE IF NOT EXISTS prompts (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id      TEXT NOT NULL,
  ts              TEXT NOT NULL,
  role            TEXT NOT NULL,
  message_id      TEXT UNIQUE,
  input_tokens    INTEGER DEFAULT 0,
  output_tokens   INTEGER DEFAULT 0,
  cache_tokens    INTEGER DEFAULT 0,
  cost_usd        REAL DEFAULT 0,
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
"""


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
        cache_tokens=session.cache_tokens,
        plan=plan,
    )
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                id, project, feature, branch, worktree_path,
                started_at, ended_at, model,
                input_tokens, output_tokens, cache_tokens, cost_usd, source_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                feature = excluded.feature,
                branch = excluded.branch,
                worktree_path = excluded.worktree_path,
                ended_at = excluded.ended_at,
                model = excluded.model,
                input_tokens = excluded.input_tokens,
                output_tokens = excluded.output_tokens,
                cache_tokens = excluded.cache_tokens,
                cost_usd = excluded.cost_usd
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
                session.cache_tokens,
                cost,
                session.source_path,
            ),
        )

        for p in session.prompts:
            if not p.message_id:
                continue
            p_cost = cost_for_session(
                model=session.model or "",
                input_tokens=p.input_tokens,
                output_tokens=p.output_tokens,
                cache_tokens=p.cache_tokens,
                plan=plan,
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO prompts (
                    session_id, ts, role, message_id,
                    input_tokens, output_tokens, cache_tokens, cost_usd
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    p.timestamp,
                    p.role,
                    p.message_id,
                    p.input_tokens,
                    p.output_tokens,
                    p.cache_tokens,
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
            SUM(input_tokens + output_tokens + cache_tokens) AS total_tokens,
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


def query_overview(db_path: Path) -> dict:
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_sessions,
                COALESCE(SUM(input_tokens), 0) AS total_input_tokens,
                COALESCE(SUM(output_tokens), 0) AS total_output_tokens,
                COALESCE(SUM(cache_tokens), 0) AS total_cache_tokens,
                COALESCE(SUM(cost_usd), 0) AS total_cost
            FROM sessions
            """
        ).fetchone()
        return dict(row) if row else {}


def query_features(db_path: Path) -> list[dict]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT project, name, first_seen, last_seen, total_tokens, total_cost,
                   pr_url, pr_status
            FROM features
            ORDER BY last_seen DESC NULLS LAST
            """
        ).fetchall()
        return [dict(r) for r in rows]


def query_sessions(db_path: Path, limit: int = 100) -> list[dict]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id AS session_id, project, feature, branch, started_at, ended_at,
                   model, input_tokens, output_tokens, cache_tokens, cost_usd
            FROM sessions
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
