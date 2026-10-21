# Pinker Next — entrada dos agentes

```text
AUTHORITY
    Founder = direção e autorização humana
    issue da Task = objetivo, escopo e conclusão
    fonte + execução pertinente = implementação comprovada
    checkpoint = continuidade factual; reobservar antes de alterar
    histórico/Book = precedentes, nunca autoridade automática

WORK
    manter checkout principal sem alterações da Task
    usar agentes/<slot>/worktree em branch própria
    TASK_ID != SLOT != EXECUTOR
    uma Task conserva slot/worktree/branch na troca de executor
    uma worktree possui um escritor responsável por vez
    sem executor preferido para novas Tasks

FORMAT
    POT/LPT = missão, invariantes e decisões
    JSON = estado e checkpoint
    JSONL = sequência de eventos e evidências
    prosa curta = contexto que os campos não explicam

IMPLEMENTATION_LANGUAGES
    Rust = estrutura e integração da Pinker
    C = baixo nível e interfaces de máquina/ABI quando necessários
    Python = ferramental e automação
    papéis são preferências; combinações exigem problema concreto e contrato
    sem bibliotecas/pacotes externos, inclusive desenvolvimento e testes
    bibliotecas padrão e ferramentas do ambiente declaradas são permitidas
    usar releases estáveis mantidas e patches atuais; registrar versões reais
    C/unsafe/FFI exigem limites explícitos de memória, tipos e erros
    política canônica = docs/linguagens.pot
    referências de toolchain = toolchains.json e .python-version

CONTINUE
    ler issue, último checkpoint e Git observado
    preservar modificações e arquivos não rastreados
    conferir operações/processos pendentes antes de repetir comandos
    checkpoint após progresso material, antes de ação demorada e de handoff
    quota esgotada não encerra nem reinicia Task

TRAMA
    usar scripts/trama para localizar e mostrar regiões relevantes
    localização somente; sem suíte de testes própria
    resultado vazio não prova ausência; usar busca delimitada quando necessário
    nenhuma obrigação de cobertura, catálogo documental ou projeção histórica

DELIVER
    validar comportamento afetado e explicar limites
    distinguir CONFIRMADO / DOCUMENTADO / INFERIDO / PROPOSTO / DESCONHECIDO
    abrir PR; merge somente pela Founder
    não remover slots/WIP nem modificar credenciais para simplificar recuperação
```

Uso executável: [docs/operacao.md](docs/operacao.md).
Direção: [docs/reboot.pot](docs/reboot.pot).
Estrutura de issues: [docs/issues.pot](docs/issues.pot).
Linguagens e dependências: [docs/linguagens.pot](docs/linguagens.pot).
POT/LPT aqui é uma convenção de contrato legível, não um interpretador instalado.
