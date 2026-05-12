# Backlog — Mission Control

Este arquivo é o “single source of truth” do que falta fazer. Mantém ideias, bugs, dívida técnica e itens priorizados.

## Now (próximo a atacar)

- [ ] Segurança: bloquear path traversal em `src/server.py` ao servir `/static/*`
- [ ] Config: validação de `~/.mission-control/config.json` (tipos, ranges, defaults)
- [ ] Scan: otimizar re-scan (evitar reparse completo quando nada mudou)

## Next (depois)

- [ ] Scan incremental por mtime (processar só JSONL alterados; lidar com deletes)
- [ ] SQLite: ativar `PRAGMA foreign_keys=ON` e reforçar integridade
- [ ] Features: wiring opcional de PR enrichment via `gh` (com cache e timeout curto)
- [ ] Export: endpoints e UI para export CSV/JSON por aba

## Later / Icebox

- [ ] Normalização de timestamps (ISO 8601 consistente entre sources)
- [ ] Mais filtros na UI (ex.: “somente ativas”, match exato de modelo)
- [ ] Métricas avançadas (ex.: custo por dia por feature, custo por ferramenta por feature)

## Bugs / Incidentes (com repro)

- (adicione aqui com passos de repro e expectativa)

## Dívida técnica

- (itens que não mudam features, mas reduzem risco/manutenção)

## Notas / Decisões

- (decisões arquiteturais curtas e o porquê)

