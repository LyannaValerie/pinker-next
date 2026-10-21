#!/usr/bin/env python3
"""Localização literal de regiões explícitas; saída JSONL, sem catálogo persistente."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tokenize


# @pinker-nav:start navigation.regions
def regions(root):
    seen = set()
    for dirname in ("src", "runtime", "scripts"):
        folder = root / dirname
        if not folder.exists():
            continue
        if folder.is_symlink():
            raise ValueError(f"Raiz simbólica não aceita: {folder}")
        for path in sorted(folder.rglob("*")):
            if path.suffix not in (".py", ".rs", ".c", ".h") or not path.is_file():
                continue
            if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root):
                raise ValueError(f"Fonte simbólica não aceita: {path}")
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines(keepends=True)
            # Python: somente comentários reais. Rust/C: marcador de linha literal
            # reservado; não é um lexer dessas linguagens nem resolve símbolos.
            python_comments = None
            if path.suffix == ".py":
                python_comments = {t.start[0]: t.string for t in
                                   tokenize.generate_tokens(io.StringIO(text).readline)
                                   if t.type == tokenize.COMMENT}
            opened = None
            for n, line in enumerate(lines, 1):
                candidate = python_comments.get(n, "") if python_comments is not None else line.strip()
                m = re.fullmatch(r"(?:#|//) @pinker-nav:(start|end) ([a-z0-9][a-z0-9_.-]*)", candidate)
                if not m:
                    continue
                action, key = m.groups()
                if action == "start":
                    if opened or key in seen:
                        raise ValueError(f"Região duplicada/aninhada: {key}")
                    opened = (key, n)
                    seen.add(key)
                else:
                    if not opened or opened[0] != key:
                        raise ValueError(f"Fim sem início correspondente: {path}:{n}")
                    body = "".join(lines[opened[1]:n - 1])
                    yield {"schema": "pinker.region/1", "key": key,
                           "path": str(path.relative_to(root)), "start": opened[1] + 1,
                           "end": n - 1, "sha256": hashlib.sha256(body.encode()).hexdigest(),
                           "text": body}
                    opened = None
            if opened:
                raise ValueError(f"Região não encerrada: {opened[0]}")
# @pinker-nav:end navigation.regions


# @pinker-nav:start navigation.cli
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    p.add_argument("command", choices=("mapa", "localizar", "mostrar"))
    p.add_argument("query", nargs="?")
    args = p.parse_args()
    if args.command != "mapa" and not args.query:
        p.error("localizar/mostrar exigem consulta")
    records = list(regions(Path(args.repo).resolve()))
    if args.command == "mostrar":
        records = [r for r in records if r["key"] == args.query]
    elif args.command == "localizar":
        q = args.query.casefold()
        records = [r for r in records if q in (r["key"] + " " + r["path"]).casefold()]
    for record in records:
        if args.command != "mostrar":
            record.pop("text")
        print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return 0 if records else 4


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, tokenize.TokenError, SyntaxError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
# @pinker-nav:end navigation.cli
