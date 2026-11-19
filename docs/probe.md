# Probe

Primeiro entregável do app: um CLI Python para capturar uma amostra real do GT7.

## Comando

```bash
revlabs-telemetry probe --ps-ip 192.168.1.42 --out sample/
```

## Requisitos

- Python 3.12+
- GT7 com telemetria UDP habilitada
- PS5 e PC na mesma LAN
- firewall liberando UDP

## Saída

- `raw/packets.jsonl`: pacotes crus com timestamp
- `summary.json`: tipos de pacote, contagem, taxa, campos vistos
- `sample.json`: amostra normalizada para fixture

## Critérios de aceite

- capturar pelo menos 60 segundos;
- identificar tipos A/B/~/C;
- listar velocidade, RPM, marcha, combustível e temperaturas;
- gerar fixture usada nos testes do parser Rust;
- funcionar em Windows e Linux (WSL com ressalva de rede).
