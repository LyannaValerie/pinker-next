#!/usr/bin/env python3
"""Organização local de Tasks; Git + Python stdlib. Não é sandbox de processos."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


# @pinker-nav:start tasks.storage
def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    require(p.returncode == 0, p.stderr.strip() or "Git falhou")
    return p.stdout.strip()


def identifier(value):
    require(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", value), "Identificador inválido")
    return value


def object_json(path):
    require(path.is_file() and not path.is_symlink(), f"Arquivo regular requerido: {path}")
    require(path.stat().st_size <= 1024 * 1024, "JSON maior que 1 MiB")
    def unique(pairs):
        out = {}
        for k, v in pairs:
            require(k not in out, f"Chave JSON duplicada: {k}")
            out[k] = v
        return out
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    require(isinstance(value, dict), "Objeto JSON requerido")
    return value


def directory(path):
    require(path.is_dir() and not path.is_symlink(), f"Diretório real requerido: {path}")


def root_of(path):
    root = Path(path).resolve()
    directory(root / ".git")
    require(Path(git(root, "rev-parse", "--show-toplevel")).resolve() == root,
            "--repo precisa apontar ao checkout principal")
    return root


@contextmanager
def locked(root):
    # Serializa somente a CLI de metadados, nunca os testes ou editores.
    path = root / ".git" / "pinker-next-tasks.lock"
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def slot_path(root, slot):
    require(re.fullmatch(r"a[0-9]{3,}", slot), "Slot esperado: a001, a002, ...")
    directory(root / "agentes")
    path = root / "agentes" / slot
    directory(path)
    directory(path / "estado")
    return path


def history(slot):
    records = []
    for seq, path in enumerate(sorted((slot / "estado").glob("*.json")), 1):
        require(path.name == f"{seq:08d}.json", "Histórico descontínuo ou arquivo inesperado")
        s = object_json(path)
        require(s.get("schema") == "pinker.task/1" and s.get("sequence") == seq,
                "Estado inválido")
        for field in ("task_id", "slot", "branch", "base_commit", "executor", "issue", "event", "time"):
            require(isinstance(s.get(field), str) and s[field], f"Campo ausente: {field}")
        require(type(s.get("generation")) is int and s["generation"] >= 1, "Geração inválida")
        require(s["slot"] == slot.name, "Slot diverge do registro")
        require(s.get("status") == "ACTIVE", "Estado de lifecycle não suportado")
        require(s.get("event") in ("START", "CHECKPOINT", "TRANSFER"), "Evento desconhecido")
        require("checkpoint" in s, "Checkpoint ausente no envelope")
        if s["checkpoint"] is not None:
            check_payload(s["checkpoint"]["payload"])
        if records:
            prev = records[-1]
            for field in ("task_id", "slot", "branch", "base_commit", "issue"):
                require(s[field] == prev[field], f"Identidade alterada: {field}")
            transfer = s["event"] == "TRANSFER"
            require(s["generation"] == prev["generation"] + int(transfer), "Geração descontínua")
            require((s["executor"] != prev["executor"]) == transfer, "Executor inconsistente")
        else:
            require(s["event"] == "START" and s["generation"] == 1, "Início inválido")
        records.append(s)
    require(records, f"Slot sem registro concluído; preservar e investigar: {slot}")
    return records


def write_revision(slot, state, event):
    state = dict(state)
    state["sequence"] += 1
    state["event"] = event
    state["time"] = datetime.now(timezone.utc).isoformat()
    parent = slot / "estado"
    target = parent / f'{state["sequence"]:08d}.json'
    data = json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    require(len(data.encode()) <= 1024 * 1024, "Registro maior que 1 MiB")
    fd, name = tempfile.mkstemp(prefix=".pending-", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        # Publica arquivo completo, sem sobrescrever revisão aceita.
        os.link(name, target)
        dfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        os.unlink(name)
    return state
# @pinker-nav:end tasks.storage


# @pinker-nav:start tasks.checkpoint
PAYLOAD_FIELDS = {"schema", "completed", "partial", "pending", "next_actions",
                  "decisions", "checks", "pending_effects", "continuation_notes"}


def check_payload(p):
    require(isinstance(p, dict) and set(p) == PAYLOAD_FIELDS, "Campos do checkpoint inválidos")
    require(p["schema"] == "pinker.checkpoint/1", "Schema do checkpoint inválido")
    for field in PAYLOAD_FIELDS - {"schema", "continuation_notes", "checks"}:
        require(isinstance(p[field], list) and all(isinstance(v, str) and v.strip() for v in p[field]),
                f"Lista de textos requerida: {field}")
    require(p["next_actions"], "Informe ao menos uma próxima ação")
    require(isinstance(p["continuation_notes"], str), "Notas precisam ser texto")
    require(isinstance(p["checks"], list), "checks precisa ser lista")
    for c in p["checks"]:
        require(isinstance(c, dict) and set(c) == {"command", "result", "evidence"}, "Check inválido")
        require(all(isinstance(v, str) and v.strip() for v in c.values()), "Check incompleto")
        require(c["result"] in {"PASS", "FAIL", "NOT_RUN", "BLOCKED", "UNKNOWN"}, "Resultado inválido")


def observed(root, slot, state):
    wt = slot / "worktree"
    directory(wt)
    common = Path(git(wt, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    require(common == root / ".git", "Worktree pertence a outro repositório")
    require(Path(git(wt, "rev-parse", "--show-toplevel")).resolve() == wt,
            "Caminho não é raiz da worktree")
    branch = git(wt, "symbolic-ref", "--short", "HEAD")
    require(branch == state["branch"], "Branch diverge da tarefa")
    return {"head": git(wt, "rev-parse", "HEAD"),
            "committed_tree": git(wt, "rev-parse", "HEAD^{tree}"),
            "git_status": git(wt, "status", "--porcelain=v1", "--untracked-files=all"),
            "worktree": str(wt), "target": str(slot / "target"), "tmp": str(slot / "tmp")}


def guard(state, args):
    require(state["generation"] == args.geracao, "Geração antiga; releia o estado")
    require(state["executor"] == args.executor, "Executor diverge do responsável registrado")
# @pinker-nav:end tasks.checkpoint


# @pinker-nav:start tasks.start
def start(root, args):
    identifier(args.tarefa)
    identifier(args.executor)
    require(re.fullmatch(r"a[0-9]{3,}", args.slot), "Slot inválido")
    require(args.issue.startswith("https://github.com/") and "/issues/" in args.issue, "URL de issue requerida")
    agents = root / "agentes"
    if not agents.exists():
        agents.mkdir()
    directory(agents)
    for candidate in agents.iterdir():
        if re.fullmatch(r"a[0-9]{3,}", candidate.name):
            directory(candidate)
            directory(candidate / "estado")
            require(history(candidate)[-1]["task_id"] != args.tarefa, "Tarefa já possui slot")
    slot = agents / args.slot
    require(not os.path.lexists(slot), "Slot já existe; use observar/retomar")
    base = git(root, "rev-parse", "--verify", args.base + "^{commit}")
    branch = "task/" + args.tarefa
    slot.mkdir(mode=0o700)
    for name in ("estado", "memory", "artifacts", "target", "tmp"):
        (slot / name).mkdir()
    # Falha parcial preserva o slot para diagnóstico; nunca remove WIP.
    git(root, "worktree", "add", "-b", branch, str(slot / "worktree"), base)
    state = {"schema": "pinker.task/1", "sequence": 0, "task_id": args.tarefa,
             "slot": args.slot, "branch": branch, "base_commit": base,
             "issue": args.issue, "executor": args.executor, "generation": 1,
             "status": "ACTIVE", "checkpoint": None}
    return write_revision(slot, state, "START")
# @pinker-nav:end tasks.start


# @pinker-nav:start tasks.cli
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True, help="checkout principal (contém .git/)")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("iniciar")
    a.add_argument("--slot", required=True)
    a.add_argument("--tarefa", required=True)
    a.add_argument("--issue", required=True)
    a.add_argument("--executor", required=True)
    a.add_argument("--base", default="HEAD")
    for name in ("observar", "retomar", "eventos", "checkpoint", "transferir"):
        a = sub.add_parser(name)
        a.add_argument("--slot", required=True)
        if name in ("checkpoint", "transferir"):
            a.add_argument("--executor", required=True, help="responsável atual registrado")
            a.add_argument("--geracao", required=True, type=int)
        if name == "checkpoint":
            a.add_argument("--arquivo", required=True)
        if name == "transferir":
            a.add_argument("--para", required=True)
            a.add_argument("--motivo", required=True)
            a.add_argument("--confirmar-exclusividade", action="store_true",
                           help="atesta cessação das mutações anteriores; não detecta nem mata processos")
    args = p.parse_args()
    root = root_of(args.repo)
    with locked(root):
        if args.command == "iniciar":
            state = start(root, args)
            slot = slot_path(root, args.slot)
        else:
            slot = slot_path(root, args.slot)
            records = history(slot)
            state = records[-1]
            observation = observed(root, slot, state)
            if args.command == "eventos":
                for item in records:
                    print(json.dumps(item, ensure_ascii=False, sort_keys=True))
                return
            if args.command in ("checkpoint", "transferir"):
                guard(state, args)
            if args.command == "checkpoint":
                payload = object_json(Path(args.arquivo))
                check_payload(payload)
                state["checkpoint"] = {"payload": payload, "observed": observation,
                                       "executor": state["executor"], "generation": state["generation"],
                                       "checks_authority": "EXECUTOR_REPORTED"}
                state = write_revision(slot, state, "CHECKPOINT")
            elif args.command == "transferir":
                identifier(args.para)
                require(args.para != state["executor"], "Executor já é responsável")
                require(args.confirmar_exclusividade and args.motivo.strip(), "Exclusividade e motivo requeridos")
                state["generation"] += 1
                state["executor"] = args.para
                state["transfer"] = {"reason": args.motivo, "previous_executor": args.executor,
                                     "exclusive_access": "OPERATOR_ATTESTED", "observed": observation}
                state = write_revision(slot, state, "TRANSFER")
        result = {"state": state, "current": observed(root, slot, state),
                  "notes": ["Checkpoint não salva cópia do WIP: preserve a worktree inteira.",
                            "Resultados dos checks são declarados; consulte a evidência.",
                            "Geração protege esta CLI, não bloqueia editores/processos externos."]}
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
# @pinker-nav:end tasks.cli
