# Mission Control

Local dashboard for AI coding session analytics. Reads JSONL transcripts from Claude Code (`~/.claude/projects/`) and Codex (`~/.codex/sessions/`) and exposes per-feature/per-project token and cost analytics on a local web UI.

## What it does

- **Reads** existing Claude Code + Codex transcripts (no hooks, no behavior changes — purely observation)
- **Correlates** sessions to features via Conventional Commits branch name parsed from each project's worktree
- **Stores** in SQLite at `~/.mission-control/db.sqlite`
- **Serves** a web UI on `127.0.0.1:8080` with 5 tabs: Overview, Features, Sessions, Projects, Settings
- **Re-scans** every 30 seconds while the dashboard is open

Cursor support is intentionally skipped: Cursor doesn't write per-turn token usage to the local filesystem. Only model/conversation summaries live in `~/.cursor/ai-tracking/ai-code-tracking.db`, which doesn't expose the granularity needed for cost attribution.

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
  "codex_sessions_dir": "/Users/<you>/.codex/sessions",
  "scan_interval_seconds": 30,
  "pricing_plan": "api",
  "port": 8080,
  "worktree_root": "/Users/<you>/Developer"
}
```

- `pricing_plan`: `api` (per-token billing) | `pro` | `max` | `max20x` (flat-rate plans return $0). Affects Anthropic models only — OpenAI is always API-priced.
- `worktree_root`: where your project worktrees live; used to resolve branch → feature
- `codex_sessions_dir`: leave it pointing at the default location, or remove it from the config if you don't use Codex (the source skips silently when the path is missing)

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
  scanner.py      # parse Claude JSONL → Session (dedup by message.id)
  sources/
    base.py         # SessionSource abstract interface
    claude_code.py  # ClaudeCodeSource — walks ~/.claude/projects/
    codex.py        # CodexSource — walks ~/.codex/sessions/
  correlator.py   # branch → feature, canonical project resolution, gh PR lookup
  pricing.py      # cost per Anthropic + OpenAI rates (Jan 2026)
  db.py           # SQLite schema + upsert + queries
  server.py       # http.server stdlib + JSON API + static UI
  config.py       # ~/.mission-control/config.json
  log.py          # stdlib logging setup
static/
  index.html, styles.css, app.js   # vanilla JS + ECharts via CDN
cli.py            # entrypoint: dashboard | scan | version
tests/            # pytest, no external deps
```

Adding a new tool = one new file under `src/sources/` implementing `SessionSource.discover(cfg) -> Iterator[Session]`, then register it in `cli.SOURCES`. Canonical project resolution, feature derivation, dedup, and pricing are uniform downstream.

## Integrations (intake API)

External tools can push LLM usage data to Mission Control via a simple HTTP endpoint. This data appears in the **Integrations** tab, separate from Claude Code / Codex sessions.

### Endpoint

```
POST /api/intake/usage
Content-Type: application/json
Authorization: Bearer <intake_token>   # only required if intake_token is set in config
```

### Payload

Send a single object or an array of objects:

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | string | **yes** | Identifies the tool sending the data (e.g. `qe-workflows`) |
| `provider` | string | no | LLM provider (e.g. `cortex-anthropic`, `openai`). Defaults to `_unknown` |
| `model` | string | no | Model name (e.g. `claude-opus-4-6`). Defaults to `_unknown` |
| `agent` | string | no | Sub-system within the tool (e.g. `maintenance`, `validation`) |
| `task` | string | no | Logical operation being performed (e.g. `maintenance-fix`) |
| `input_tokens` | integer | no | Prompt tokens sent. Defaults to `0` |
| `output_tokens` | integer | no | Completion tokens returned. Defaults to `0` |
| `cost_usd` | float | no | Cost in USD. If omitted, Mission Control estimates it from the model's pricing |
| `metadata` | object | no | Arbitrary JSON — stored as-is, not displayed |
| `created_at` | string | no | ISO 8601 timestamp. Defaults to server time if omitted |

### Examples

**curl — single record:**
```bash
curl -s -X POST http://127.0.0.1:8080/api/intake/usage \
  -H "Content-Type: application/json" \
  -d '{
    "source": "qe-workflows",
    "provider": "cortex-anthropic",
    "model": "claude-opus-4-6",
    "agent": "maintenance",
    "task": "maintenance-fix",
    "input_tokens": 12000,
    "output_tokens": 800,
    "cost_usd": 0.195
  }'
```

**curl — batch:**
```bash
curl -s -X POST http://127.0.0.1:8080/api/intake/usage \
  -H "Content-Type: application/json" \
  -d '[
    {"source": "qe-workflows", "agent": "validation", "task": "run-checks", "input_tokens": 5000, "output_tokens": 200},
    {"source": "qe-workflows", "agent": "validation", "task": "run-checks", "input_tokens": 4800, "output_tokens": 180}
  ]'
```

**Python:**
```python
import urllib.request, json

payload = json.dumps({
    "source": "qe-workflows",
    "provider": "cortex-anthropic",
    "model": "claude-sonnet-4-6",
    "agent": "analyze",
    "task": "analyze_impact",
    "input_tokens": 8000,
    "output_tokens": 400,
    "cost_usd": 0.1276,
}).encode()

req = urllib.request.Request(
    "http://127.0.0.1:8080/api/intake/usage",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
urllib.request.urlopen(req)
```

### Authentication

To restrict the endpoint, add `intake_token` to `~/.mission-control/config.json`:

```json
{
  "intake_token": "your-secret-token"
}
```

Then include it on every request:

```bash
-H "Authorization: Bearer your-secret-token"
```

Requests without a valid token receive `401`. If `intake_token` is absent from the config, the endpoint is open (suitable for local-only use).

## Tests

```bash
python3 -m pytest tests/ -v
```

## Known limitations

- **Cost is estimated** using Anthropic API pricing (Jan 2026). If you're on a flat-rate plan (Pro / Max / Max-20x), set `pricing_plan` to that value in `~/.mission-control/config.json` and all sessions show `$0`.
- **PR enrichment** requires `gh` CLI authenticated to the right org; it currently runs only via the INDEX.md generator in the Example App repo, not yet wired into the dashboard scan.

## Changelog

- **v0.5.0** — **Codex support**: new `SessionSource` interface under `src/sources/`, with parallel `claude_code` and `codex` implementations. Codex uses *last-wins* semantics for token totals (they are cumulative in the JSONL — summing would multiply by N). **OpenAI pricing** (gpt-5/-codex, gpt-4o, o1, o3) with longest-prefix resolve — `gpt-5.3-codex-2026-01` correctly resolves to `gpt-5.3-codex`. `cache_create` hard-coded to 0 for OpenAI (they don't bill cache creation separately); `cache_read` = 50% of input. **Top tools chart** on Overview, aggregating `tool_use` blocks from prompts (new `tool_uses` table, `/api/by-tool` endpoint). Sessions now sort by `started_at DESC` (mtime is the tiebreaker) — fixes dates jumping around in the 'Start' column while active sessions kept bumping mtime. Prompts drill-down also sorted DESC to match the parent table. Logging refactor: stdlib `logging` in `src/log.py`, `ScanResult` dataclass, steady-state scans stay silent (only log when there's `+new` or `-cleaned`). Bug fix: prompts now UPDATE on conflict (was `INSERT OR IGNORE`, lost token updates on re-scan). Bug fix: "Sessions" column in the Projects tab now populates (was `—`).
- **v0.4.0** — Cache READ vs CACHE CREATE split everywhere (prices differ 5×). New cards (Turns, Cache Read, Cache Create), educational accordion "What do these numbers mean", **model filter** (Opus/Sonnet/Haiku) inspired by phuryn/claude-usage, 4 charts on Overview (Daily work stacked, Daily cache reads, Tokens by project bar, Token usage by model donut), Recent sessions widget on Overview, **ACTIVE badge** with pulse animation on sessions with mtime < 5 min (answers "which of my 3 open sessions am I using right now?"). Date filter migrated from dropdown to pills (7d/30d/90d/All).
- **v0.3.0** — Filters (date range, project) in the header, applied to all tabs. Daily cost bar chart and project donut on Overview (ECharts). Drill-down: click a session in the Sessions tab to expand its per-prompt cost. Projects tab shows aggregate per-project with % of total. Feature search box filters the Features table.
- **v0.2.1** — Canonical project resolution via `git rev-parse --show-toplevel`: preserves hyphens (`acme-tool` no longer becomes `acme/tool`), collapses `.worktrees/X` and `.worktree/X` to the parent repo, filters out non-repo paths (`~/.claude-mem` etc). Full sync on every scan: stale rows from older versions are deleted. UPSERT now updates `project` column on conflict (was excluded). Validated: 175 sessions across 6 clean projects (from 828 across 13 mangled names).
- **v0.2.0** — Feature detection via `gitBranch` in JSONL records (every record carries it). Picks the *dominant* branch (most frequent across the session's records), correctly handling sessions that switch worktrees. Removed filesystem worktree lookup.
- **v0.1.0** — Initial release: scanner + correlator + pricing + SQLite + HTTP server + UI. Feature detection v1 used filesystem worktree lookup (only resolved sessions in the main worktree).

## License

MIT
