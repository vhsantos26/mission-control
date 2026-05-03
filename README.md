# Mission Control

Local dashboard for Claude Code session analytics. Reads JSONL transcripts from `~/.claude/projects/` and exposes per-feature/per-project token and cost analytics on a local web UI.

## What it does

- **Reads** existing Claude Code transcripts (no hooks, no behavior changes — purely observation)
- **Correlates** sessions to features via Conventional Commits branch name parsed from each project's worktree
- **Stores** in SQLite at `~/.mission-control/db.sqlite`
- **Serves** a web UI on `127.0.0.1:8080` with 5 tabs: Overview, Features, Sessions, Projects, Settings
- **Re-scans** every 30 seconds while the dashboard is open

## Privacy

100% local. No data leaves your machine. The dashboard binds to `127.0.0.1` only.

## Install

Requires Python 3.10+. No `pip install` needed (stdlib only). Optional: `gh` CLI for PR enrichment in the Features tab.

```bash
git clone <this-repo> ~/Developer/mission-control
cd ~/Developer/mission-control
```

## Run

```bash
python3 cli.py dashboard          # scan + serve web UI, opens browser
python3 cli.py scan --once        # one-shot scan without serving
python3 cli.py version
```

## Configuration

Edit `~/.mission-control/config.json` (created with defaults on first run):

```json
{
  "claude_projects_dir": "/Users/<you>/.claude/projects",
  "scan_interval_seconds": 30,
  "pricing_plan": "api",
  "port": 8080,
  "worktree_root": "/Users/<you>/Developer"
}
```

- `pricing_plan`: `api` (per-token billing) | `pro` | `max` | `max20x` (flat-rate plans return $0)
- `worktree_root`: where your project worktrees live; used to resolve branch → feature

## Feature detection

For each session, Mission Control derives the feature from the branch checked out in the matching worktree. Examples:

| Branch | Feature |
|---|---|
| `feat/multi-agent-setup` | `multi-agent-setup` |
| `fix/null-orgid` | `null-orgid` |
| `main` / `staging` / non-conventional | `_no-feature` |

If no worktree match is found, the session is grouped under `_no-feature`.

## Architecture

```
src/
  scanner.py      # parse JSONL → Session (dedup by message.id)
  correlator.py   # branch → feature, gh PR lookup
  pricing.py      # cost per Anthropic API rates (Jan 2026)
  db.py           # SQLite schema + upsert + queries
  server.py       # http.server stdlib + JSON API + static UI
  config.py       # ~/.mission-control/config.json
static/
  index.html, styles.css, app.js   # vanilla JS + ECharts via CDN
cli.py            # entrypoint: dashboard | scan | version
tests/            # pytest, ~26 tests, no external deps
```

## Tests

```bash
python3 -m pytest tests/ -v
```

## Known limitations

- **Cost is estimated** using Anthropic API pricing (Jan 2026). If you're on a flat-rate plan (Pro / Max / Max-20x), set `pricing_plan` to that value in `~/.mission-control/config.json` and all sessions show `$0`.
- **PR enrichment** requires `gh` CLI authenticated to the right org; it currently runs only via the INDEX.md generator in the Example App repo, not yet wired into the dashboard scan.

## Changelog

- **v0.3.0** — Filters (date range, project) in the header, applied to all tabs. Daily cost bar chart and project donut on Overview (ECharts). Drill-down: click a session in the Sessions tab to expand its per-prompt cost. Projects tab shows aggregate per-project with % of total. Feature search box filters the Features table.
- **v0.2.1** — Canonical project resolution via `git rev-parse --show-toplevel`: preserves hyphens (`acme-tool` no longer becomes `acme/tool`), collapses `.worktrees/X` and `.worktree/X` to the parent repo, filters out non-repo paths (`~/.claude-mem` etc). Full sync on every scan: stale rows from older versions are deleted. UPSERT now updates `project` column on conflict (was excluded). Validated: 175 sessions across 6 clean projects (from 828 across 13 mangled names).
- **v0.2.0** — Feature detection via `gitBranch` in JSONL records (every record carries it). Picks the *dominant* branch (most frequent across the session's records), correctly handling sessions that switch worktrees. Removed filesystem worktree lookup.
- **v0.1.0** — Initial release: scanner + correlator + pricing + SQLite + HTTP server + UI. Feature detection v1 used filesystem worktree lookup (only resolved sessions in the main worktree).

## License

MIT
