#!/usr/bin/env python3
"""Validador de arquivos CSV/TXT para importação no Anki (P&R e Cloze Deletion)."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

CLOZE_TAG_RE = re.compile(r"\{\{c([1-9]\d*)::([^:}]+?)(?:::([^}]+?))?\}\}")
ANY_BRACES_RE = re.compile(r"\{\{|\}\}")

SEPARATOR_MAP = {
    "semicolon": ";",
    "tab": "\t",
    "comma": ",",
    "pipe": "|",
}


def validate_cloze(front: str, line_no: int, errors: list[str]) -> bool:
    """Valida sintaxe Cloze {{c1::termo}} e retorna True se houver ao menos um Cloze."""
    matches = list(CLOZE_TAG_RE.finditer(front))
    stripped = CLOZE_TAG_RE.sub("", front)

    if ANY_BRACES_RE.search(stripped):
        errors.append(
            f"Linha {line_no}: sintaxe Cloze malformada ou chaves desbalanceadas em '{front}'."
        )
        return True

    for match in matches:
        term = match.group(2).strip()
        if not term:
            errors.append(f"Linha {line_no}: Cloze vazio encontrado em '{front}'.")

    return len(matches) > 0


def validate_anki_file(path: Path) -> tuple[int, list[str]]:
    """Valida um arquivo CSV/TXT do Anki e retorna (total_cartas, lista_de_erros)."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    separator = ";"
    data_lines: list[tuple[int, str]] = []

    for idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if stripped.lower().startswith("#separator:"):
                sep_name = stripped.split(":", 1)[1].strip().lower()
                if sep_name in SEPARATOR_MAP:
                    separator = SEPARATOR_MAP[sep_name]
                elif len(sep_name) == 1:
                    separator = sep_name
                else:
                    return 0, [f"Linha {idx}: separador desconhecido '{sep_name}'."]
            continue
        data_lines.append((idx, raw_line))

    if not data_lines:
        return 0, ["Nenhuma carta encontrada no arquivo."]

    errors: list[str] = []
    for line_no, raw_line in data_lines:
        row = next(csv.reader([raw_line], delimiter=separator))
        if len(row) < 2 or len(row) > 3:
            errors.append(
                f"Linha {line_no}: esperado 2 ou 3 colunas (Frente, Verso[, Tags]), encontrado {len(row)}."
            )
            continue

        front = row[0].strip()
        back = row[1].strip()

        if not front:
            errors.append(f"Linha {line_no}: campo 'Frente' está vazio.")
            continue

        has_cloze = validate_cloze(front, line_no, errors)
        if not has_cloze and not back:
            errors.append(
                f"Linha {line_no}: carta P&R sem 'Verso' preenchido e sem Cloze na 'Frente'."
            )

    return len(data_lines), errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida exportações CSV/TXT do Anki geradas pela skill flashcards-srs."
    )
    parser.add_argument("file", type=Path, help="Caminho para o arquivo .csv ou .txt")
    args = parser.parse_args()

    if not args.file.is_file():
        print(f"ERRO: arquivo não encontrado: {args.file}", file=sys.stderr)
        return 1

    total, errors = validate_anki_file(args.file)
    if errors:
        print("FALHA NA VALIDAÇÃO ANKI CSV:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK: {total} carta(s) válida(s) para importação no Anki.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
