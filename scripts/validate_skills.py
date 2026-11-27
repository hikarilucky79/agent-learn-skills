#!/usr/bin/env python3
"""Validador estrutural de skills e documentação do repositório agent-learn-skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

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


def parse_frontmatter(text: str, rel_path: str, errors: list[str]) -> dict[str, str]:
    """Extrai e valida campos obrigatórios do frontmatter YAML."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        errors.append(f"{rel_path}: frontmatter YAML ausente ou malformado.")
        return {}

    fm_text = match.group(1)
    name_match = re.search(r"^name:\s*(\S+)\s*$", fm_text, re.MULTILINE)
    desc_match = re.search(
        r"^description:\s*(?:>\s*\r?\n((?:\s+.+\r?\n?)+)|(.+))$",
        fm_text,
        re.MULTILINE,
    )

    fields: dict[str, str] = {}
    if not name_match:
        errors.append(f"{rel_path}: campo 'name' ausente no frontmatter.")
    else:
        fields["name"] = name_match.group(1)

    if not desc_match or not (desc_match.group(1) or desc_match.group(2) or "").strip():
        errors.append(f"{rel_path}: campo 'description' ausente ou vazio no frontmatter.")
    else:
        raw_desc = desc_match.group(1) or desc_match.group(2) or ""
        fields["description"] = " ".join(line.strip() for line in raw_desc.splitlines())

    return fields


def validate_skill_file(path: Path, is_template: bool, errors: list[str]) -> str | None:
    """Valida um arquivo SKILL.md (ou template) e retorna o nome da skill."""
    rel_path = path.relative_to(ROOT).as_posix()
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

    if not is_template and "<!--" in text:
        errors.append(f"{rel_path}: contém comentário HTML residual ('<!--').")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"{rel_path}: seção obrigatória ausente: '{section}'.")

    return name


def validate_markdown_links(doc_path: Path, errors: list[str]) -> set[Path]:
    """Verifica se todos os links relativos em um arquivo Markdown existem."""
    rel_doc = doc_path.relative_to(ROOT).as_posix()
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


def main() -> int:
    errors: list[str] = []

    for rel_file in REQUIRED_ROOT_FILES:
        if not (ROOT / rel_file).is_file():
            errors.append(f"Arquivo obrigatório ausente: {rel_file}")

    template_path = ROOT / "templates" / "SKILL_TEMPLATE.md"
    if template_path.is_file():
        validate_skill_file(template_path, is_template=True, errors=errors)

    skills_dir = ROOT / "skills"
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
        name = validate_skill_file(skill_md, is_template=False, errors=errors)
        if name:
            if name in seen_names:
                errors.append(
                    f"Nome duplicado '{name}' em skills/{sdir.name} e {seen_names[name]}."
                )
            seen_names[name] = f"skills/{sdir.name}"

    readme_path = ROOT / "README.md"
    if readme_path.is_file():
        readme_targets = validate_markdown_links(readme_path, errors)
        for skill_md in skill_files:
            if skill_md.resolve() not in readme_targets:
                rel = skill_md.relative_to(ROOT).as_posix()
                errors.append(f"README.md: skill '{rel}' não está linkada no catálogo.")

    contributing_path = ROOT / "CONTRIBUTING.md"
    if contributing_path.is_file():
        validate_markdown_links(contributing_path, errors)

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
