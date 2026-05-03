"""Mission Control CLI entrypoint."""

import argparse
import threading
import time
import webbrowser
from pathlib import Path

from src.config import DB_FILE, load
from src.correlator import canonical_project, feature_from_branch
from src.db import delete_sessions_except, init_db, upsert_session
from src.scanner import parse_jsonl
from src.server import serve

VERSION = "0.2.1"


def scan_all(cfg: dict) -> int:
    """Scan all JSONL transcripts and upsert into the DB. Returns count of sessions touched.

    Feature is derived from each session's *dominant gitBranch* — the branch most
    frequently recorded across the session's records. This handles long sessions
    that switch worktrees, and works retroactively without filesystem lookup.
    """
    root = Path(cfg["claude_projects_dir"])
    if not root.exists():
        print(f"[warn] claude_projects_dir does not exist: {root}")
        return 0

    plan = cfg.get("pricing_plan", "api")
    count = 0
    seen_ids: set[str] = set()

    for project_dir in sorted(root.iterdir()):
        if not project_dir.is_dir():
            continue
        for jsonl in project_dir.glob("*.jsonl"):
            try:
                sessions = parse_jsonl(jsonl)
            except Exception as e:
                print(f"[warn] failed to parse {jsonl.name}: {e}")
                continue
            if not sessions:
                continue
            s = sessions[0]
            branch = s.dominant_branch
            feature = feature_from_branch(branch) if branch else "_no-feature"

            # Resolve canonical project from the session's dominant cwd.
            # This collapses worktrees to their parent repo and filters out
            # sessions that ran outside any git repo (claude-mem etc).
            canonical = canonical_project(s.dominant_cwd)
            if canonical is None:
                # Skip non-repo sessions (claude-mem observer, etc.)
                continue
            s.project = canonical

            upsert_session(
                DB_FILE,
                s,
                feature=feature,
                branch=branch,
                worktree_path=s.dominant_cwd,
                plan=plan,
            )
            seen_ids.add(s.session_id)
            count += 1

    # Sync: drop sessions no longer present (e.g. legacy rows from older
    # scanner versions, or transcripts deleted from disk)
    deleted = delete_sessions_except(DB_FILE, seen_ids)
    if deleted:
        print(f"[scan] cleaned {deleted} stale session(s)")
    return count


def scan_loop(cfg: dict) -> None:
    interval = int(cfg.get("scan_interval_seconds", 30))
    while True:
        try:
            n = scan_all(cfg)
            if n:
                print(f"[scan] processed {n} session(s)")
        except Exception as e:
            print(f"[scan] error: {e}")
        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(prog="mission-control")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dashboard", help="scan + serve web UI")
    scan_p = sub.add_parser("scan", help="run scanner")
    scan_p.add_argument("--once", action="store_true", help="exit after first pass")
    sub.add_parser("version")
    args = parser.parse_args()

    cfg = load()
    init_db(DB_FILE)

    if args.cmd == "version":
        print(f"mission-control {VERSION}")
        return 0

    if args.cmd == "scan":
        n = scan_all(cfg)
        print(f"[scan] processed {n} session(s)")
        if not args.once:
            scan_loop(cfg)
        return 0

    if args.cmd == "dashboard":
        # initial scan synchronously so the UI has data on first paint
        n = scan_all(cfg)
        print(f"[scan] initial pass processed {n} session(s)")

        threading.Thread(target=scan_loop, args=(cfg,), daemon=True).start()
        port = int(cfg.get("port", 8080))
        url = f"http://127.0.0.1:{port}"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        serve(DB_FILE, port=port)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
