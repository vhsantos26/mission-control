"""Mission Control CLI entrypoint."""

import argparse
import logging
import threading
import time
import webbrowser
from dataclasses import dataclass

from src.config import DB_FILE, load
from src.correlator import canonical_project, feature_from_branch
from src.db import all_session_ids, delete_sessions_except, init_db, upsert_session
from src.log import setup as setup_logging
from src.server import serve
from src.sources import ClaudeCodeSource, CodexSource, SessionSource

# Sources are tried in order; each yields its own ``Session`` records and
# canonicalization runs uniformly downstream. Add a new tool here.
SOURCES: list[SessionSource] = [ClaudeCodeSource(), CodexSource()]

VERSION = "0.6.0"

log = logging.getLogger("mc.cli")


@dataclass
class ScanResult:
    """Outcome of one scan pass — used to log only when something changed.

    Parse failures are logged directly by each ``SessionSource``, so they
    don't need a separate counter here.
    """

    processed: int = 0       # total sessions touched (upserted) this pass
    new: int = 0             # session IDs not previously in the DB
    cleaned: int = 0         # rows dropped by the sync-delete step
    skipped_non_repo: int = 0  # sessions whose cwd doesn't resolve to a git repo

    @property
    def is_quiet(self) -> bool:
        """True when there's nothing worth surfacing to the user."""
        return self.new == 0 and self.cleaned == 0


def scan_all(cfg: dict) -> ScanResult:
    """Scan every configured source and upsert into the DB.

    Each ``SessionSource`` yields ``Session`` records; canonical project
    resolution + feature derivation + pricing are uniform downstream.
    Sessions whose cwd doesn't resolve to a git repo are dropped entirely.
    """
    result = ScanResult()
    plan = cfg.get("pricing_plan", "api")
    seen_ids: set[str] = set()
    prev_ids = all_session_ids(DB_FILE)

    for source in SOURCES:
        for s in source.discover(cfg):
            branch = s.dominant_branch
            feature = feature_from_branch(branch) if branch else "_no-feature"

            # Resolve canonical project from the session's dominant cwd.
            # Collapses worktrees to their parent repo; drops non-repo sessions
            # (claude-mem observer, scratch dirs, etc).
            canonical = canonical_project(s.dominant_cwd)
            if canonical is None:
                result.skipped_non_repo += 1
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
            result.processed += 1

    result.new = len(seen_ids - prev_ids)
    result.cleaned = delete_sessions_except(DB_FILE, seen_ids)
    return result


def _log_scan_result(r: ScanResult, *, prefix: str = "") -> None:
    """Emit one line summarizing the pass — only if something changed.

    Steady-state runs (no new/cleaned/warnings) stay silent so the terminal
    isn't flooded with identical lines every scan_interval_seconds.
    """
    if r.is_quiet:
        log.debug(
            "%sscan idle (processed=%d, skipped=%d)",
            prefix,
            r.processed,
            r.skipped_non_repo,
        )
        return

    parts: list[str] = []
    if r.new:
        parts.append(f"+{r.new} new")
    if r.cleaned:
        parts.append(f"-{r.cleaned} cleaned")
    log.info(
        "%sscan: %s (total=%d sessions tracked)",
        prefix,
        ", ".join(parts),
        r.processed,
    )


def scan_loop(cfg: dict) -> None:
    interval = int(cfg.get("scan_interval_seconds", 30))
    log.debug("scan loop starting (interval=%ds)", interval)
    while True:
        try:
            result = scan_all(cfg)
            _log_scan_result(result)
        except Exception as e:
            log.exception("scan loop error: %s", e)
        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(prog="mission-control")
    parser.add_argument(
        "--log-level",
        default=None,
        help="DEBUG | INFO | WARNING | ERROR (overrides MC_LOG_LEVEL env var)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dashboard", help="scan + serve web UI")
    scan_p = sub.add_parser("scan", help="run scanner")
    scan_p.add_argument("--once", action="store_true", help="exit after first pass")
    sub.add_parser("version")
    args = parser.parse_args()

    setup_logging(args.log_level)

    cfg = load()
    init_db(DB_FILE)

    if args.cmd == "version":
        print(f"mission-control {VERSION}")
        return 0

    if args.cmd == "scan":
        result = scan_all(cfg)
        _log_scan_result(result, prefix="initial ")
        if not args.once:
            scan_loop(cfg)
        return 0

    if args.cmd == "dashboard":
        # initial scan synchronously so the UI has data on first paint
        result = scan_all(cfg)
        _log_scan_result(result, prefix="initial ")

        threading.Thread(target=scan_loop, args=(cfg,), daemon=True).start()
        port = int(cfg.get("port", 8080))
        url = f"http://127.0.0.1:{port}"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        serve(DB_FILE, port=port)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
