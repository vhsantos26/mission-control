# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Stdlib-only Python 3.10+. **No `pip install` needed** for the app itself; pytest is the only dev dependency.

```bash
python3 cli.py dashboard           # one-shot scan + serve UI on 127.0.0.1:8080 + open browser
python3 cli.py scan --once         # single scan pass, no server, no loop
python3 cli.py scan                # scan + loop forever every scan_interval_seconds
python3 cli.py version

python3 -m pytest tests/ -v                                  # full suite
python3 -m pytest tests/test_scanner.py -v                   # one file
python3 -m pytest tests/test_scanner.py::test_dedup_by_message_id -v   # one test
```

`pyproject.toml` sets `pythonpath = ["."]` so tests import from `src/` without an editable install.

State lives outside the repo at `~/.mission-control/` (`config.json`, `db.sqlite`). Wipe that directory to fully reset.

## Architecture

The pipeline is a one-way fan-in from each tool's transcript files into a single SQLite DB that the UI reads from. **Read-only with respect to source directories** — Mission Control never modifies transcripts.

```
~/.claude/projects/<slug>/<session>.jsonl   ─┐
~/.codex/sessions/<y>/<m>/<d>/rollout-*.jsonl┘
        │
        ▼ src/sources/<tool>.discover(cfg)    (walks dir, parses, yields Session)
   Session dataclass (canonical, source-agnostic)
        │
        ▼ correlator.feature_from_branch + canonical_project   (git rev-parse, collapse worktrees)
        ▼ db.upsert_session    (writes sessions + prompts; recomputes features row)
        ▼ db.delete_sessions_except    (drops rows for transcripts no longer on disk)
   ~/.mission-control/db.sqlite
        │
        ▼ server.py (stdlib http.server)  →  /api/*  →  static/app.js  →  ECharts (CDN)
```

**Adding a new tool**: implement `SessionSource.discover(cfg) -> Iterator[Session]` under `src/sources/`, register the instance in `cli.SOURCES`. Everything downstream is uniform — sources do not need to touch the DB, pricing, or canonicalization. The base `Session` dataclass is the only contract.

`cli.py dashboard` runs the **initial scan synchronously** before serving (so the first paint has data), then spawns a daemon thread that re-scans every `scan_interval_seconds`. The UI also polls every 30s.

### Domain model invariants

- **A session = one JSONL file.** Identity is the filename stem (Claude) or the trailing UUID parsed out of `rollout-<ts>-<uuid>.jsonl` (Codex); it's the SQLite primary key. Re-scans UPSERT.
- **Dedup is by `message.id`** for Claude Code (per-record), and by **last-wins** for Codex (token totals are cumulative — taking the last `total_token_usage` is the only correct path; summing across records would multiply by N).
- **`dominant_branch` / `dominant_cwd` / `model` come from per-record counts.** A long session that switches worktrees still gets one canonical attribution (the most frequent value wins). Don't switch to first/last-record heuristics.
- **`canonical_project()` is the single source of truth for the `project` column.** It runs `git rev-parse --show-toplevel`, then collapses any path containing `.worktrees/` or `.worktree/` to the parent repo. Sessions whose cwd isn't inside any git repo (e.g. `~/.claude-mem` observers) are **dropped entirely** — not stored under a fake project name. If you change this resolution, expect every aggregate to shift.
- **Full-sync semantics on every scan.** `delete_sessions_except(seen_ids)` removes rows for transcripts that disappeared from disk *or* sessions that no longer canonicalize to a project. This is how stale rows from older scanner versions get cleaned up; don't replace it with an incremental-only update.
- **`features` table is derived state.** It's recomputed on every upsert and after every sync. Treat it as a cache — `sessions` is authoritative.

### Pricing — keep cache reads and cache creates separated

`pricing.py` distinguishes four token classes per model: `input`, `output`, `cache_create` (≈1.25× input for Anthropic, **always 0 for OpenAI**), `cache_read` (≈0.1× input for Anthropic; input × 0.5 for OpenAI). The 5× spread between Anthropic's `cache_create` and `cache_read` is large enough that lumping them — as v0.3 did — produces meaningfully wrong totals. Preserve the four-way split everywhere.

For Codex sessions: `reasoning_output_tokens` is folded into `output_tokens` (OpenAI bills it as output). `cached_input_tokens` becomes `cache_read_tokens`. `cache_create_tokens` is hard-coded to 0.

`_resolve_pricing(model)` does longest-prefix matching, so `gpt-5.3-codex-2026-01` resolves to the `gpt-5.3-codex` row. Order entries with the more specific keys present (e.g. `gpt-5.1-codex-mini` *before* `gpt-5`-family entries are too generic to catch it). The OpenAI rows for `gpt-5.x-codex` are estimates — OpenAI hasn't published official prices for these models yet. Update when they do.

Flat-rate plans (`pro`, `max`, `max20x` in `FLAT_PLANS`) return `0.0` cost — that's intentional, not a bug to "fix." This affects Anthropic only; OpenAI is always API-priced.

### Active-session heuristic

A session is flagged `is_active` in API responses iff its source JSONL `mtime` is within `ACTIVE_THRESHOLD_SECONDS` (5 min). This drives the "Ativa" badge. Session rows are sorted by `source_mtime DESC`, not `started_at DESC` — the latter would bury the live session under stale ones with later wall-clock starts.

### UI

`static/app.js` is plain ES modules-free vanilla JS, ECharts loaded from a CDN in `index.html`. There is **no bundler, no build step, no framework**. Filters (project, model, date-range pills) live in module-scoped `filters` and `refresh()` re-fetches every API in parallel. Chart instances are memoized in `charts` and resized on `window.resize` and on tab activation.

### Server

`src/server.py` is one `BaseHTTPRequestHandler` with a hand-written path router. Adding an endpoint = add a branch in `do_GET` and a query function in `db.py`. Filters are uniformly threaded through `_filter_clause(project, feature, model, since, until)` — reuse it instead of inlining new WHERE clauses.

## Project conventions

- **Feature names are derived from Conventional-Commits branch prefixes** (`feat/`, `fix/`, `chore/`, `refactor/`, `hotfix/`, `docs/`, `test/`, `perf/`, `build/`, `revert/`, `wip/`). Anything else (`main`, `staging`, ad-hoc names) becomes the sentinel `_no-feature`. The leading `_` is what makes these sort/group correctly in the UI — keep it.
- **Tests use real `git init` / `git worktree`** in `tmp_path` rather than mocking subprocess. This catches the regressions the canonical-project logic was written to prevent (e.g. `acme-tool` becoming `acme/tool`). Don't replace with mocks.
- **Failures during scan must not abort the loop.** `scan_all` catches per-file exceptions and prints `[warn] failed to parse …`, then keeps going. JSONL files are often partially flushed — tolerance is required.
- **No external services in the hot path.** The optional `gh` CLI lookup in `correlator.find_pr_for_branch` is the only subprocess call beyond `git`, and it's not yet wired into the scan. Keep new dependencies behind a similar opt-in.

## Versioning

`VERSION` lives in `cli.py` and `version` in `pyproject.toml`. Bump both together when shipping. The README's Changelog section is the public record — append a new entry there for any user-visible change.
