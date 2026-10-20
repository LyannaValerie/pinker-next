# Pinker Next

Reboot da Pinker: uma linguagem cuja implementação também possa ser estudada.
Direção: [issue #1](https://github.com/LyannaValerie/pinker-next/issues/1).

## Estado desta entrega

- Base operacional local: slots, worktrees, checkpoints e transferência de responsável.
- Trama reduzida à localização de regiões do código, com saída JSONL.
- Contratos agênticos em POT/LPT e estado em JSON.
- **Compilador e runtime ainda não migrados.** A nova sintaxe é direção de projeto.

O [legado arquivado](https://github.com/LyannaValerie/pinker-v0) preserva a implementação
anterior. [docs/reboot.pot](docs/reboot.pot) distingue decisões, implementação e próximos passos.

## Começar

Ambiente operacional: Linux ou Linux no WSL, Git, Bash e Python 3.10+.
Sem pacotes Python externos. Execute a partir do checkout principal:

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
