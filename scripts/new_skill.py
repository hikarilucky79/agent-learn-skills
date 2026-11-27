#!/usr/bin/env python3
"""Gerador de scaffolding para novas skills do repositório agent-learn-skills."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence

if "validate_skills" in sys.modules:
    _validate_skills = sys.modules["validate_skills"]
else:
    _script_dir = str(Path(__file__).resolve().parent)
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)
    import validate_skills as _validate_skills

ROOT = Path(__file__).resolve().parent.parent
KEBAB_CASE_RE = _validate_skills.KEBAB_CASE_RE
FRONTMATTER_RE = _validate_skills.FRONTMATTER_RE
FRONTMATTER_NAME_RE = re.compile(r"^(name:[ \t]*)\S+([ \t]*)$", re.MULTILINE)
TITLE_PLACEHOLDER_RE = re.compile(
    r"^# \[Human-Readable Skill Name\][ \t]*$", re.MULTILINE
)
HTML_COMMENT_RE = re.compile(r"[ \t]*<!--.*?-->[ \t]*\r?\n?", re.DOTALL)
EXCESS_NEWLINES_RE = re.compile(r"\n{3,}")


def default_skill_title(name: str) -> str:
    """Converte um nome em kebab-case para título legível em Title Case."""
    return " ".join(part.capitalize() for part in name.split("-"))


def render_skill_from_template(
    template_text: str,
    name: str,
    title: str | None = None,
    strip_comments: bool = False,
) -> str:
    """Preenche frontmatter e título de um template SKILL_TEMPLATE.md."""
    normalized = template_text.replace("\r\n", "\n")
    fm_match = FRONTMATTER_RE.match(normalized)
    if not fm_match:
        raise ValueError("Template inválido: frontmatter YAML ausente ou malformado.")

    fm_body = fm_match.group(1)
    updated_fm, name_subs = FRONTMATTER_NAME_RE.subn(
        lambda m: f"{m.group(1)}{name}{m.group(2)}", fm_body, count=1
    )
    if name_subs != 1:
        raise ValueError("Template inválido: campo 'name' ausente no frontmatter.")

    rendered = (
        normalized[: fm_match.start(1)]
        + updated_fm
        + normalized[fm_match.end(1) :]
    )

    heading = title.strip() if title is not None else default_skill_title(name)
    rendered = TITLE_PLACEHOLDER_RE.sub(f"# {heading}", rendered, count=1)

    if strip_comments:
        rendered = HTML_COMMENT_RE.sub("", rendered)
        rendered = EXCESS_NEWLINES_RE.sub("\n\n", rendered)

    if not rendered.endswith("\n"):
        rendered += "\n"
    return rendered


def create_skill(
    name: str,
    root: Path | None = None,
    title: str | None = None,
    force: bool = False,
    strip_comments: bool = False,
) -> Path:
    """Cria `skills/<name>/SKILL.md` a partir de `templates/SKILL_TEMPLATE.md`."""
    if not KEBAB_CASE_RE.match(name):
        raise ValueError(
            f"Nome de skill inválido '{name}'. Use kebab-case (ex: mock-interview)."
        )

    if title is not None:
        clean_title = title.strip()
        if not clean_title or "\n" in clean_title or "\r" in clean_title:
            raise ValueError("O título informado em --title deve ser uma linha não vazia.")
        title = clean_title

    base_root = ROOT if root is None else root
    template_path = base_root / "templates" / "SKILL_TEMPLATE.md"
    if not template_path.is_file():
        raise FileNotFoundError(
            f"Template não encontrado: {template_path}"
        )

    skills_root = (base_root / "skills").resolve()
    target_dir = (skills_root / name).resolve()
    if target_dir.parent != skills_root:
        raise ValueError(f"Caminho de destino inválido para a skill '{name}'.")

    target_file = target_dir / "SKILL.md"
    if target_file.exists() and not force:
        raise FileExistsError(
            f"A skill '{name}' já existe em {target_file} (use --force para sobrescrever)."
        )

    template_text = template_path.read_text(encoding="utf-8")
    rendered = render_skill_from_template(
        template_text=template_text,
        name=name,
        title=title,
        strip_comments=strip_comments,
    )

    target_dir.mkdir(parents=True, exist_ok=True)
    target_file.write_text(rendered, encoding="utf-8", newline="\n")
    return target_file


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser de linha de comando para new_skill.py."""
    parser = argparse.ArgumentParser(
        description=(
            "Cria skills/<nome>/SKILL.md a partir de templates/SKILL_TEMPLATE.md "
            "com o campo name preenchido."
        )
    )
    parser.add_argument(
        "name",
        help="Nome da nova skill em kebab-case (ex: mock-interview).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Título legível para o cabeçalho '# ...' (padrão: derivado de name).",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Sobrescreve skills/<nome>/SKILL.md caso já exista.",
    )
    parser.add_argument(
        "--strip-comments",
        action="store_true",
        help="Remove os comentários HTML instrucionais (<!-- ... -->) do arquivo gerado.",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    root: Path | None = None,
) -> int:
    """Ponto de entrada CLI do scaffolding de skills."""
    parser = build_parser()
    args = parser.parse_args(argv)
    base_root = ROOT if root is None else root

    try:
        created = create_skill(
            name=args.name,
            root=base_root,
            title=args.title,
            force=args.force,
            strip_comments=args.strip_comments,
        )
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    try:
        rel_created = created.relative_to(base_root.resolve()).as_posix()
    except ValueError:
        rel_created = created.as_posix()

    print(f"OK: skill '{args.name}' criada em {rel_created}")
    print("Próximos passos:")
    if args.strip_comments:
        print(f"  1. Preencha as seções de {rel_created}.")
    else:
        print(
            f"  1. Preencha as seções de {rel_created} e remova os comentários <!-- ... -->."
        )
    print("  2. Adicione a skill ao catálogo em README.md.")
    print("  3. Valide com: python scripts/validate_skills.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
