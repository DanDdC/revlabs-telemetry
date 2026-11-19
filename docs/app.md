# App

## Arquitetura

```
GT7 UDP -> UdpSource -> Parser -> Recorder -> SQLite + JSONL.gz
                                      |
                                      +-> React UI (Tauri)
                                      |
                                      +-> Export .revlabs / Upload API
```

## Sessão

Campos mínimos:

- modo (`hotlap`, `practice`, `race`);
- carro e pista;
- composto de pneu;
- multiplicadores de desgaste/consumo;
- combustível inicial;
- idade inicial do pneu;
- clima/temperatura;
- assists;
- setup.

## Limites

- GT7: apenas o carro local.
- AC: preparar `TelemetrySource` para outros carros.
- Sem multi-carro ao vivo no MVP.
