# Pinker Next

Linguagem dinamicamente tipada, a ser implementada em **Pinker**, cuja tipagem
permanece estática. Ambas preservam sua finalidade educacional.

A Pinker existente continua seu desenvolvimento e a campanha
[#768](https://github.com/LyannaValerie/pinker-v0/issues/768). A Next será construída
com ela; não substituirá seu compilador por uma reconstrução em Rust.
Direção: [issue #1](https://github.com/LyannaValerie/pinker-next/issues/1).

## Estado desta entrega

- Base operacional local: slots, worktrees, checkpoints e transferência de responsável.
- Trama reduzida à localização de regiões do código, com saída JSONL.
- Contratos agênticos em POT/LPT e estado em JSON.
- Núcleo futuro da Next escrito em Pinker; Python permanece no ferramental.
  Rust/C são suporte justificado, não uma implementação paralela do núcleo:
  [contrato](docs/linguagens.pot).
- **A linguagem dinâmica ainda não está implementada.** Não há frontend ou
  runtime Next; a nova sintaxe permanece direção de projeto.
- [Bootstrap e horizonte educacional](docs/bootstrap-next.pot): construção da
  Next com Pinker e futuro percurso próprio inspirado em Nand2Tetris/SO.

A [Pinker](https://github.com/LyannaValerie/pinker-v0) fornece a implementação
estática que sustentará o bootstrap. [docs/reboot.pot](docs/reboot.pot) distingue decisões, implementação e próximos passos.

## Começar

Ambiente operacional: Linux ou Linux no WSL, Git, Bash e CPython 3.14.8
(referência em [.python-version](.python-version)). Sem pacotes Python externos.
Somente o ferramental Python está ativo. A versão/commit do compilador Pinker
para construir a Next ainda precisa de validação. Referências anteriores a Rust
1.99.1 e C23/GCC 16.2 ficam como histórico de infraestrutura; não são requisitos
para usar as ferramentas nem alteram a toolchain da Pinker v0. Execute a partir do checkout principal:

```bash
bash scripts/tarefa --repo "$PWD" iniciar --slot a002 --tarefa exemplo \
  --issue https://github.com/LyannaValerie/pinker-next/issues/3 --executor agente-a
bash scripts/tarefa --repo "$PWD" observar --slot a002
bash scripts/trama localizar tasks.checkpoint
bash scripts/trama mostrar tasks.checkpoint
```

O comando de exemplo cria uma worktree real; adapte tarefa, issue e slot ao trabalho
autorizado. Siga [o fluxo completo de checkpoint e retomada](docs/operacao.md).
Os launchers também podem ser chamados pelo Bash, sem instalação global.

## Entradas

| Fonte | Responsabilidade |
|---|---|
| [AGENTS.md](AGENTS.md) | Entrada curta dos agentes |
| [docs/operacao.md](docs/operacao.md) | Organização, comandos e limites |
| [docs/issues.pot](docs/issues.pot) | Issues-mãe, filhas/netas e históricos |
| [docs/linguagens.pot](docs/linguagens.pot) | Papéis, dependências e fronteiras entre linguagens |
| [docs/bootstrap-next.pot](docs/bootstrap-next.pot) | Pinker → implementação Next → programas Next; horizonte educacional |
| [toolchains.json](toolchains.json) | Referências de versões, fontes oficiais e estado de adoção |
| [templates/task.pot](templates/task.pot) | Contrato de tarefa |
| [templates/checkpoint.json](templates/checkpoint.json) | Conteúdo de continuidade |
| [docs/proveniencia.md](docs/proveniencia.md) | Fontes das ideias importadas |

## Validação operacional

```bash
python3 -m unittest discover -s tests -v
git diff --check
```

Esses testes exercitam continuidade e preservação de trabalho em repositórios Git
temporários. Não há suíte de testes da Trama, conforme direção da Founder.
