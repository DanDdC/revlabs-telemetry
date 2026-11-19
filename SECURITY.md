# Security Policy

## Reportando uma vulnerabilidade

Não abra uma issue pública para vulnerabilidades. Envie um e-mail para o
mantenedor ou use o recurso de private vulnerability reporting do GitHub.

Inclua:

- descrição do problema;
- passos para reproduzir;
- impacto potencial;
- versão/commit afetado.

## Escopo

- API e site (`revlabs-expanded`)
- app de captura (`revlabs-telemetry`)
- schema (`revlabs-schema`)

## Boas práticas

- Nunca commite secrets.
- Use `.env.example` para documentar variáveis.
- Reporte dependências vulneráveis via Dependabot.
