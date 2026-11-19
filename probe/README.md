# RevLabs Probe

CLI para capturar a primeira amostra real de telemetria do Gran Turismo 7.

## Requisitos

- Python 3.10+
- GT7 com telemetria UDP habilitada
- PS4/PS5 e PC na mesma LAN
- Firewall liberando UDP 33739/33740

## Uso

```bash
cd probe
uv venv .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe -m revlabs_probe probe --ps-ip 192.168.1.42 --out sample
```

Em Linux/macOS, use `.venv/bin/python`.

## Saída

- `sample/raw/packets.jsonl` — pacotes crus em base64
- `sample/decoded.jsonl` — campos decodificados
- `sample/frames_sample.json` — primeiros 300 frames para fixture
- `sample/summary.json` — resumo da captura

## Protocolo

- Heartbeat: UDP 33739, caractere `A` (ou `B`, `~`, `C`)
- Telemetria: UDP 33740
- Criptografia: Salsa20
- Tipos: A (296), B (316), ~ (344), C (368)

## Limitações

- GT7 expõe apenas o carro local.
- WSL2 pode não receber UDP da LAN; prefira captura nativa.
- O stream não é oficialmente documentado e pode mudar.
