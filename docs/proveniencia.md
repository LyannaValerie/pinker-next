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
| [Pipeline](https://github.com/LyannaValerie/pinker-v0/blob/9146fee66b9c63d8841b9ac60a64032b41fd11a7/docs/agents/architecture.compiler-pipeline.json) | Etapas reais inspecionáveis e validadores | Requisito para a implementação Next em Pinker, não claim de implementação atual |
| [Trama](https://github.com/LyannaValerie/pinker-v0/blob/9146fee66b9c63d8841b9ac60a64032b41fd11a7/docs/agents/reference.trama-code-navigation.json) | Chaves de regiões e localização seletiva | Localizador novo reduzido; sem transpor cobertura, história ou documentos |
| [#826](https://github.com/LyannaValerie/pinker-v0/issues/826) | Precedentes operacionais | Consulta contextual; não carregar todas as dívidas como gates |

Decisões da Founder em 20/10/2026 prevalecem sobre obrigações históricas:
pipeline educacional, Trama limitada sem testes próprios, hierarquia de issues,
históricos e formato agêntico estruturado desde o início.

Os scripts desta entrega são novos; nenhum script local da Forja foi copiado.
Na preparação do bootstrap foi usada uma worktree Git criada manualmente,
pois a ferramenta de Tasks ainda não existia no commit inicial. A publicação
remota mantém como pai o commit real do repositório novo.

## Revisão de direção — 21/10/2026

A Founder decidiu retomar a Pinker estática e implementar a Next dinâmica em
Pinker. Isso substitui a direção de reconstruir/importar um núcleo Next em Rust.
A infraestrutura entregue na PR #5 permanece. O percurso de bootstrap e o
horizonte de SO/Nand2Tetris estão em [bootstrap-next.pot](bootstrap-next.pot).
As referências Rust/C de 20/10 ficam históricas, sem atualizar a toolchain da v0.

Nesta revisão, a preparação local usou uma fotografia Git da main remota
`5a8d32aaab4a43fa4d5a1415422251346cf98b3f`, árvore
`871f6006959c11e96958fb2d4189094b8f861273`, e um slot criado pela CLI existente.
O commit de fotografia local não integra a história publicada: a PR usa o HEAD
remoto real como pai. Nenhuma execução de compilador Pinker foi alegada.
