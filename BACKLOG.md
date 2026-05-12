# Backlog — Mission Control

This file is the single source of truth for pending work. Tracks ideas, bugs, tech debt, and prioritized items.

## Now (next to tackle)

- [ ] Security: block path traversal in `src/server.py` when serving `/static/*`
- [ ] Config: validate `~/.mission-control/config.json` (types, ranges, defaults)
- [ ] Scan: optimize re-scan (avoid full reparse when nothing changed)

## Next (after)

- [ ] Incremental scan by mtime (process only changed JSONLs; handle deletes)
- [ ] SQLite: enable `PRAGMA foreign_keys=ON` and tighten integrity
- [ ] Features: optional PR enrichment wiring via `gh` (with cache and short timeout)
- [ ] Export: endpoints and UI for CSV/JSON export per tab

## Later / Icebox

- [ ] Timestamp normalization (consistent ISO 8601 across sources)
- [ ] More UI filters (e.g., "active only", exact model match)
- [ ] Advanced metrics (e.g., cost per day per feature, cost per tool per feature)

## Bugs / Incidents (with repro)

- (add here with repro steps and expectation)

## Tech debt

- (items that don't change features but reduce risk/maintenance)

## Notes / Decisions

- (short architectural decisions and the why)
