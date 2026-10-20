# Proveniência das ideias

Legado consultado: `LyannaValerie/pinker-v0`, commit
`9146fee66b9c63d8841b9ac60a64032b41fd11a7`. Fontes remotas inspecionadas;
as ferramentas host-side da Forja não estavam disponíveis neste ambiente.

| Fonte | Ideia reaproveitada | Adaptação |
|---|---|---|
| [AGENTS.md](https://github.com/LyannaValerie/pinker-v0/blob/9146fee66b9c63d8841b9ac60a64032b41fd11a7/AGENTS.md) e [agentes/README.md](https://github.com/LyannaValerie/pinker-v0/blob/9146fee66b9c63d8841b9ac60a64032b41fd11a7/agentes/README.md) | Task isolada e identidade independente do slot | Caminhos relativos ao checkout escolhido; sem instalação global antiga |
| [#690](https://github.com/LyannaValerie/pinker-v0/issues/690) e [#803](https://github.com/LyannaValerie/pinker-v0/issues/803) | Continuidade, geração e checkpoints estruturados | CLI delimitada, sem coordenador de providers; arquivos do slot preservados |
| [#799](https://github.com/LyannaValerie/pinker-v0/issues/799) | Conclusão não implica exclusão segura | Nenhuma limpeza automática nesta entrega |
| [#631 e comentários](https://github.com/LyannaValerie/pinker-v0/issues/631) | Nova superfície da linguagem | Direção preservada; gramática ainda não implementada |
| [Pipeline](https://github.com/LyannaValerie/pinker-v0/blob/9146fee66b9c63d8841b9ac60a64032b41fd11a7/docs/agents/architecture.compiler-pipeline.json) | Etapas reais inspecionáveis e validadores | Requisito para futura migração, não claim de implementação atual |
| [Trama](https://github.com/LyannaValerie/pinker-v0/blob/9146fee66b9c63d8841b9ac60a64032b41fd11a7/docs/agents/reference.trama-code-navigation.json) | Chaves de regiões e localização seletiva | Localizador novo reduzido; sem transpor cobertura, história ou documentos |
| [#826](https://github.com/LyannaValerie/pinker-v0/issues/826) | Precedentes operacionais | Consulta contextual; não carregar todas as dívidas como gates |

Decisões da Founder em 20/10/2026 prevalecem sobre obrigações históricas:
pipeline educacional, Trama limitada sem testes próprios, hierarquia de issues,
históricos e formato agêntico estruturado desde o início.

Os scripts desta entrega são novos; nenhum script local da Forja foi copiado.
Na preparação do bootstrap foi usada uma worktree Git criada manualmente,
pois a ferramenta de Tasks ainda não existia no commit inicial. A publicação
remota mantém como pai o commit real do repositório novo.
