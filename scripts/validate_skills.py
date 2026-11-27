#!/usr/bin/env python3
"""Validador estrutural de skills e documentação do repositório agent-learn-skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NEGATIVE_BOUNDARY_RE = re.compile(r"\bDO NOT activate\b")

REQUIRED_ROOT_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "templates/SKILL_TEMPLATE.md",
)

REQUIRED_SECTIONS = (
    "## 1. Role and Objective",
    "## 2. Scope",
    "## 3. Execution Flow",
    "## 4. Pedagogical Rules",
    "## 5. Output Format",
    "## 6. Short Example",
)


def _format_rel_path(path: Path, root: Path) -> str:
    """Retorna caminho relativo POSIX ao diretório raiz, ou caminho POSIX absoluto como fallback."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def parse_frontmatter(text: str, rel_path: str, errors: list[str]) -> dict[str, str]:
    """Extrai e valida campos obrigatórios do frontmatter YAML."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        errors.append(f"{rel_path}: frontmatter YAML ausente ou malformado.")
        return {}

    fm_text = match.group(1)
    name_match = re.search(r"^name:[ \t]*(\S+)[ \t]*\r?$", fm_text, re.MULTILINE)
    desc_match = re.search(
        r"^description:[ \t]*(?:"
        r"[>|][+-]?[ \t]*\r?\n((?:[ \t]+[^\r\n]+\r?\n?|\r?\n(?=[ \t]+\S))+)"
        r"|"
        r"([^\r\n]*)"
        r")\r?$",
        fm_text,
        re.MULTILINE,
    )

    fields: dict[str, str] = {}
    if not name_match:
        errors.append(f"{rel_path}: campo 'name' ausente no frontmatter.")
    else:
        fields["name"] = name_match.group(1)

    raw_desc = ""
    if desc_match:
        if desc_match.group(1) is not None:
            raw_desc = desc_match.group(1)
        else:
            inline_desc = (desc_match.group(2) or "").strip()
            if not re.fullmatch(r"[>|][+-]?", inline_desc):
                raw_desc = inline_desc

    if not raw_desc.strip():
        errors.append(f"{rel_path}: campo 'description' ausente ou vazio no frontmatter.")
    else:
        fields["description"] = " ".join(
            line.strip() for line in raw_desc.splitlines() if line.strip()
        )

    return fields


def validate_skill_file(
    path: Path,
    is_template: bool,
    errors: list[str],
    root: Path | None = None,
) -> str | None:
    """Valida um arquivo SKILL.md (ou template) e retorna o nome da skill."""
    base_root = ROOT if root is None else root
    rel_path = _format_rel_path(path, base_root)
    text = path.read_text(encoding="utf-8")
    fields = parse_frontmatter(text, rel_path, errors)

    name = fields.get("name")
    if name:
        if not KEBAB_CASE_RE.match(name):
            errors.append(f"{rel_path}: 'name' ({name}) deve estar em kebab-case.")
        if not is_template and name != path.parent.name:
            errors.append(
                f"{rel_path}: 'name' ({name}) deve ser idêntico à pasta ({path.parent.name})."
            )

    description = fields.get("description")
    if description and not NEGATIVE_BOUNDARY_RE.search(description):
        errors.append(
            f"{rel_path}: campo 'description' deve conter fronteira negativa explícita ('DO NOT activate')."
        )

    if not is_template and "<!--" in text:
        errors.append(f"{rel_path}: contém comentário HTML residual ('<!--').")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"{rel_path}: seção obrigatória ausente: '{section}'.")

    return name


def validate_markdown_links(
    doc_path: Path,
    errors: list[str],
    root: Path | None = None,
) -> set[Path]:
    """Verifica se todos os links relativos em um arquivo Markdown existem."""
    base_root = ROOT if root is None else root
    rel_doc = _format_rel_path(doc_path, base_root)
    content = doc_path.read_text(encoding="utf-8")
    resolved_targets: set[Path] = set()

    for link in LINK_RE.findall(content):
        if link.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean_link = link.split("#", 1)[0]
        if not clean_link:
            continue
        target = (doc_path.parent / clean_link).resolve()
        if not target.exists():
            errors.append(f"{rel_doc}: link relativo quebrado -> '{link}'.")
        else:
            resolved_targets.add(target)

    return resolved_targets


def main(root: Path | None = None) -> int:
    """Executa a validação completa do repositório e retorna o código de saída."""
    base_root = ROOT if root is None else root
    errors: list[str] = []

    for rel_file in REQUIRED_ROOT_FILES:
        if not (base_root / rel_file).is_file():
            errors.append(f"Arquivo obrigatório ausente: {rel_file}")

    template_path = base_root / "templates" / "SKILL_TEMPLATE.md"
    if template_path.is_file():
        validate_skill_file(template_path, is_template=True, errors=errors, root=base_root)

    skills_dir = base_root / "skills"
    if not skills_dir.is_dir():
        errors.append("Diretório 'skills/' ausente.")
        skill_dirs: list[Path] = []
    else:
        skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())

    if not skill_dirs:
        errors.append("Nenhuma skill encontrada em 'skills/'.")

    seen_names: dict[str, str] = {}
    skill_files: list[Path] = []

    for sdir in skill_dirs:
        if not KEBAB_CASE_RE.match(sdir.name):
            errors.append(f"skills/{sdir.name}: nome da pasta deve estar em kebab-case.")
        skill_md = sdir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"skills/{sdir.name}: arquivo 'SKILL.md' ausente.")
            continue
        skill_files.append(skill_md)
        name = validate_skill_file(skill_md, is_template=False, errors=errors, root=base_root)
        if name:
            if name in seen_names:
                errors.append(
                    f"Nome duplicado '{name}' em skills/{sdir.name} e {seen_names[name]}."
                )
            seen_names[name] = f"skills/{sdir.name}"

    readme_path = base_root / "README.md"
    if readme_path.is_file():
        readme_targets = validate_markdown_links(readme_path, errors, root=base_root)
        for skill_md in skill_files:
            if skill_md.resolve() not in readme_targets:
                rel = _format_rel_path(skill_md, base_root)
                errors.append(f"README.md: skill '{rel}' não está linkada no catálogo.")

    contributing_path = base_root / "CONTRIBUTING.md"
    if contributing_path.is_file():
        validate_markdown_links(contributing_path, errors, root=base_root)

    if errors:
        print("FALHA NA VALIDAÇÃO:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(skill_files)} skills, template e links validados sem erros."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
