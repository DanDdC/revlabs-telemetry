# RevLabs Telemetry

App de captura e exportação de telemetria do RevLabs.

## Objetivo

Capturar UDP do GT7, gravar sessões localmente, permitir anotação de condições e
exportar bundles compatíveis com o `revlabs-schema`.

Funciona offline. O upload para o site é opcional.

## Stack

- Tauri v2
- React + TypeScript
- Rust para UDP/parser/SQLite
- Probe Python para captura inicial e fixtures

## Modos

- `hotlap`
- `practice`
- `race` (stints, pneu, combustível)

## Escopo do MVP

- probe CLI;
- captura UDP;
- gravação local;
- HUD;
- lista de voltas;
- metadados de sessão;
- export `.revlabs`;
- upload futuro.

## Limitações conhecidas

- GT7 entrega apenas o carro do jogador via UDP.
- Assetto Corsa pode expor outros carros; a integração fica para o futuro.
- WSL2 pode não receber UDP da LAN; captura real é melhor nativa.

## Licença

MIT + Commons Clause. Veja [LICENSE](LICENSE).
