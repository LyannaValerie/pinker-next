# Operação local e continuidade

Esta é uma implementação nova e delimitada dos conceitos da Forja. Não é cópia
da instalação antiga nem presume que seus comandos continuem disponíveis.

## Layout

| Caminho no checkout principal | Conteúdo |
|---|---|
| `.git/` | Git compartilhado e trava dos comandos de metadados |
| `agentes/aNNN/worktree/` | Branch e arquivos da tarefa, incluindo WIP |
| `agentes/aNNN/estado/00000001.json` etc. | Revisões completas e sequenciais da Task |
| `agentes/aNNN/memory/` | Notas factuais e entrada de checkpoint |
| `agentes/aNNN/artifacts/` | Evidências selecionadas |
| `agentes/aNNN/target/`, `tmp/` | Recursos recriáveis da tarefa |

`--repo` sempre recebe o checkout principal, que contém o diretório `.git/`.
Uma tarefa diferente recebe slot e branch diferentes. Trocar executor conserva
Task, slot, worktree, branch e issue/PR. As revisões registram a geração do responsável.

## Fluxo completo

No shell, escolha o checkout principal e uma issue de trabalho existente:

```bash
PINKER_REPO=/caminho/para/pinker-next
bash "$PINKER_REPO/scripts/tarefa" --repo "$PINKER_REPO" iniciar \
  --slot a002 --tarefa exemplo --executor agente-a \
  --issue https://github.com/LyannaValerie/pinker-next/issues/3 --base HEAD

cd "$PINKER_REPO/agentes/a002/worktree"
export CARGO_TARGET_DIR="$PINKER_REPO/agentes/a002/target"
export TMPDIR="$PINKER_REPO/agentes/a002/tmp"

cp templates/checkpoint.json ../memory/progresso.json
# Edite progresso.json: fatos concluídos, trabalho parcial, pendências e próximo passo.
bash scripts/tarefa --repo "$PINKER_REPO" checkpoint --slot a002 \
  --executor agente-a --geracao 1 --arquivo ../memory/progresso.json

bash scripts/tarefa --repo "$PINKER_REPO" retomar --slot a002
bash scripts/tarefa --repo "$PINKER_REPO" eventos --slot a002 > ../artifacts/eventos.jsonl
```

Os executores são identificadores lógicos, não contas Unix nem credenciais.
O operador escolhe a interface local aprovada e o sucessor usa sua própria sessão.
Os nomes de exemplo são substituíveis.

Depois de comprovar que o anterior não está mais modificando a worktree, um
operador autorizado pode transferir sem precisar do agente esgotado:

```bash
bash scripts/tarefa --repo "$PINKER_REPO" transferir --slot a002 \
  --executor agente-a --geracao 1 --para agente-b \
  --motivo "Sessão anterior interrompida; mutações encerradas e estado conferido" \
  --confirmar-exclusividade
bash scripts/tarefa --repo "$PINKER_REPO" retomar --slot a002
# Próximo checkpoint usa --executor agente-b --geracao 2.
```

`--executor` e `--geracao` precisam coincidir com o responsável anterior no ato
da transferência. O comando registra o novo responsável e incrementa a geração.
Checkpoint com geração antiga é recusado. `retomar` é leitura; não muda responsabilidade.

**A exclusividade é uma declaração do operador**, não uma prova automática.
A trava serializa estas operações de metadados; não bloqueia editores, Git ou
processos externos. Verifique sessões, comandos e efeitos pendentes antes da
troca. Se não for possível estabelecer exclusividade, preserve e interrompa a
mutação. Não use apenas a ausência de arquivos abertos como prova universal.

## Checkpoint e eventos

Entrada: `templates/checkpoint.json`, validada pelo comando antes da gravação.

| Campo | Conteúdo |
|---|---|
| `completed`, `partial`, `pending` | Listas factuais de itens |
| `next_actions` | Próximas ações concretas; ao menos uma |
| `decisions` | Decisões e motivos relevantes à continuação |
| `checks` | Objetos com `command`, `result`, `evidence` |
| `pending_effects` | Operações iniciadas, processos e efeitos ainda incertos |
| `continuation_notes` | Contexto indispensável, sem raciocínio privado ou segredos |

Resultados permitidos: `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`, `UNKNOWN`.
São relatos do executor; a ferramenta não executa nem certifica esses checks.
O envelope guarda executor, geração, HEAD, árvore commitada e status Git no
momento do checkpoint. **A árvore commitada não representa os bytes do WIP.**

O checkpoint não faz commit, stash, backup ou cópia dos arquivos. O trabalho
não commitado e os arquivos não rastreados continuam na worktree; preserve-a.
A retomada retorna o último checkpoint e uma observação Git atual, mesmo que
tenha havido progresso posterior ao checkpoint. Não exige árvore limpa.

Cada revisão é publicada integralmente por link atômico após `fsync`, sem
sobrescrever revisões anteriores. O histórico completo é validado na leitura;
revisão aceita corrompida ou sequência interrompida causa erro explícito.
Arquivos temporários `.pending-*` não são registros aceitos. `eventos` produz
JSONL a partir das revisões, evitando dois arquivos canônicos que divergem.
Essas garantias pressupõem filesystem local POSIX confiável; não autenticam o
autor nem resistem a alguém com acesso de escrita que adultere registros.

Interrupção antes do primeiro checkpoint ainda permite retomada pelo estado
inicial, issue, Git e arquivos. Registrar cedo reduz o trabalho de reconstrução.
Registre também antes de comandos demorados e após marcos relevantes.
Se uma operação terminou mas seu recibo não foi registrado, observe seus efeitos
antes de repetir. Um checkpoint não torna toda operação idempotente.

## Falhas e encerramento

- Início parcialmente falho preserva slot, branch e arquivos. Não tenta apagar
  recursos para esconder a falha. Observe Git e diretórios antes de decidir a recuperação.
- Slot existente, identidade duplicada, symlink no slot/worktree/estado,
  worktree de outro repositório ou branch divergente são recusados.
- Não há comandos de selo, limpeza, exclusão ou troca de permissões nesta versão.
  Conclusão semântica é registrada na issue/checkpoint. Remoção física é operação
  distinta, exige autorização e preservação prévia do que importa.
- A CLI foi desenhada para agentes sob a mesma identidade local ou acesso já
  provisionado. Ela não gerencia usuários, ACL, provider, quota nem autenticação.
- O shell precisa definir `TMPDIR`/`CARGO_TARGET_DIR`; os diretórios por si não
  confinam processos. Isolamento de worktree não é sandbox do sistema operacional.

## Trama de localização

```bash
bash scripts/trama mapa
bash scripts/trama localizar checkpoint
bash scripts/trama mostrar tasks.checkpoint
```

Saída JSONL com chave, arquivo, linhas e hash; `mostrar` inclui o trecho. Consulta
literal por chave/caminho, sem ranking semântico. Cada chamada lê o presente,
sem arquivo de índice persistente. Retornos: `0` encontrado, `4` vazio,
`1` fonte inválida, `2` uso inválido. Vazio não prova inexistência de código.

Raízes limitadas a `src/`, `runtime/`, `scripts/`, arquivos `.rs` e `.py`.
Marque regiões com `# @pinker-nav:start chave` / `end chave` em Python e `//`
em Rust. Python reconhece comentários pelo tokenizador da biblioteca padrão.
Rust usa marcadores de linha literais reservados: não coloque linhas com essa
forma dentro de strings ou comentários de bloco. Não se alega análise léxica
completa de Rust nem resolução semântica de símbolos. Chaves duplicadas,
aninhamento e marcadores sem par são erros. Não há cobertura obrigatória,
navegação documental, mapeamento de testes ou suíte dedicada à Trama.
