# Diretório de trabalho dos agentes

Cada slot `aNNN/` contém `worktree/`, `estado/`, `memory/`, `artifacts/`,
`target/` e `tmp/`. A worktree é registrada pelo Git do checkout principal;
não é clone independente. Os slots são locais e ignorados pelo Git.

`TASK_ID` identifica o trabalho. O slot identifica sua localização física.
O executor é substituível. Nenhum nome de agente tem preferência permanente.

Não copie slots do legado, caminhos absolutos ou credenciais. Não retire uma
worktree para lidar com falta de quota. Consulte [a operação](../docs/operacao.md).
