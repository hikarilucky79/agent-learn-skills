#!/usr/bin/env python3
"""Unit and integration tests for scripts/validate_skills.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_skills.py"


def _load_validate_skills():
    spec = importlib.util.spec_from_file_location("validate_skills", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_skills"] = module
    spec.loader.exec_module(module)
    return module


validate_skills = _load_validate_skills()

REQUIRED_SECTION_LINES = "\n\n".join(
    f"{heading}\n\nContent for {heading}."
    for heading in validate_skills.REQUIRED_SECTIONS
)


def build_skill_markdown(
    name: str = "sample-skill",
    description: str = (
        "Activate when the user asks for sample practice. "
        "DO NOT activate for quizzes (use quiz-master)."
    ),
    body_extra: str = "",
    multiline_desc: bool = False,
) -> str:
    """Build a valid SKILL.md document unless intentionally overridden."""
    if multiline_desc:
        indented = "\n".join(f"  {line}" for line in description.splitlines())
        desc_block = f"description: >\n{indented}"
    else:
        desc_block = f"description: {description}"

    extra = f"\n{body_extra}\n" if body_extra else "\n"
    return (
        f"---\n"
        f"name: {name}\n"
        f"{desc_block}\n"
        f"---\n\n"
        f"# Sample Skill\n"
        f"{extra}"
        f"{REQUIRED_SECTION_LINES}\n"
    )


def build_valid_repo(root: Path, skills: dict[str, str] | None = None) -> None:
    """Populate a minimal valid repository structure inside `root`."""
    skill_map = skills or {"sample-skill": build_skill_markdown()}

    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (root / "CONTRIBUTING.md").write_text(
        "# Contributing\n\nSee [README](README.md).\n", encoding="utf-8"
    )

    templates_dir = root / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    (templates_dir / "STUDY_PAGE_TEMPLATE.html").write_text(
        "<!DOCTYPE html><html><head><title>Template</title></head><body></body></html>\n",
        encoding="utf-8",
    )
    (templates_dir / "SKILL_TEMPLATE.md").write_text(
        build_skill_markdown(
            name="skill-name-in-kebab-case",
            description=(
                "Activate when appropriate.\n"
                "DO NOT activate for unrelated tasks."
            ),
            body_extra="<!-- template comment -->",
            multiline_desc=True,
        ),
        encoding="utf-8",
    )

    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    readme_links = []
    for folder_name, content in skill_map.items():
        sdir = skills_dir / folder_name
        sdir.mkdir(parents=True, exist_ok=True)
        (sdir / "SKILL.md").write_text(content, encoding="utf-8")
        readme_links.append(f"- [`{folder_name}`](skills/{folder_name}/SKILL.md)")

    (root / "README.md").write_text(
        "# Repo\n\n" + "\n".join(readme_links) + "\n",
        encoding="utf-8",
    )


class TestParseFrontmatter(unittest.TestCase):
    """Tests for YAML frontmatter extraction and validation."""

    def test_valid_inline_and_multiline_descriptions(self) -> None:
        inline_doc = build_skill_markdown(
            description="Activate for X. DO NOT activate for Y.",
            multiline_desc=False,
        )
        errors: list[str] = []
        fields = validate_skills.parse_frontmatter(inline_doc, "SKILL.md", errors)
        self.assertEqual(errors, [])
        self.assertEqual(fields["name"], "sample-skill")
        self.assertEqual(
            fields["description"], "Activate for X. DO NOT activate for Y."
        )

        multiline_doc = build_skill_markdown(
            description="Activate for X.\n\nDO NOT activate for Y.",
            multiline_desc=True,
        )
        errors = []
        fields = validate_skills.parse_frontmatter(multiline_doc, "SKILL.md", errors)
        self.assertEqual(errors, [])
        self.assertEqual(
            fields["description"], "Activate for X. DO NOT activate for Y."
        )

    def test_missing_frontmatter_and_fields(self) -> None:
        errors: list[str] = []
        fields = validate_skills.parse_frontmatter("# No Frontmatter\n", "a.md", errors)
        self.assertEqual(fields, {})
        self.assertEqual(len(errors), 1)
        self.assertIn("frontmatter YAML ausente", errors[0])

        missing_fields = "---\nauthor: dev\n---\n\n# Body\n"
        errors = []
        fields = validate_skills.parse_frontmatter(missing_fields, "b.md", errors)
        self.assertEqual(fields, {})
        self.assertTrue(any("campo 'name' ausente" in err for err in errors))
        self.assertTrue(any("campo 'description' ausente" in err for err in errors))

    def test_empty_block_scalar_description_is_rejected(self) -> None:
        cases = [
            "---\nname: sample-skill\ndescription: >\n---\n\n# Body\n",
            "---\nname: sample-skill\ndescription: |\nauthor: dev\n---\n\n# Body\n",
            "---\nname:\ndescription:\nauthor: dev\n---\n\n# Body\n",
        ]
        for idx, doc in enumerate(cases):
            with self.subTest(case=idx):
                errors: list[str] = []
                fields = validate_skills.parse_frontmatter(doc, "c.md", errors)
                self.assertNotIn("description", fields)
                self.assertTrue(
                    any("campo 'description' ausente ou vazio" in err for err in errors)
                )


class TestValidateSkillFile(unittest.TestCase):
    """Tests for individual SKILL.md and template validation rules."""

    def test_valid_skill_passes_with_negative_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_path = Path(tmp) / "skills" / "sample-skill" / "SKILL.md"
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text(
                build_skill_markdown(multiline_desc=True), encoding="utf-8"
            )
            errors: list[str] = []
            name = validate_skills.validate_skill_file(
                skill_path, is_template=False, errors=errors, root=Path(tmp)
            )
            self.assertEqual(name, "sample-skill")
            self.assertEqual(errors, [])

    def test_missing_negative_boundary_fails(self) -> None:
        cases = [
            "Activate when the user wants interactive quizzes.",
            "Activate for X and WHEN NOT to activate for Y.",
            "Activate for X. do not activate for Y.",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for idx, bad_desc in enumerate(cases):
                with self.subTest(case=idx, description=bad_desc):
                    skill_path = Path(tmp) / f"case-{idx}" / "sample-skill" / "SKILL.md"
                    skill_path.parent.mkdir(parents=True)
                    skill_path.write_text(
                        build_skill_markdown(description=bad_desc), encoding="utf-8"
                    )
                    errors: list[str] = []
                    validate_skills.validate_skill_file(
                        skill_path, is_template=False, errors=errors, root=Path(tmp)
                    )
                    self.assertTrue(
                        any("DO NOT activate" in err for err in errors),
                        f"Expected 'DO NOT activate' error, got {errors}",
                    )

    def test_template_requires_negative_boundary_but_allows_comments_and_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "templates" / "SKILL_TEMPLATE.md"
            template_path.parent.mkdir(parents=True)

            # Valid template with HTML comments and placeholder name
            template_path.write_text(
                build_skill_markdown(
                    name="skill-name-in-kebab-case",
                    description="Activate when X. DO NOT activate for Y.",
                    body_extra="<!-- keep instructional comment -->",
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_skills.validate_skill_file(
                template_path, is_template=True, errors=errors, root=Path(tmp)
            )
            self.assertEqual(errors, [])

            # Template without DO NOT activate must fail
            template_path.write_text(
                build_skill_markdown(
                    name="skill-name-in-kebab-case",
                    description="Activate when X and WHEN NOT to activate for Y.",
                    body_extra="<!-- keep instructional comment -->",
                ),
                encoding="utf-8",
            )
            errors = []
            validate_skills.validate_skill_file(
                template_path, is_template=True, errors=errors, root=Path(tmp)
            )
            self.assertTrue(any("DO NOT activate" in err for err in errors))

    def test_name_folder_comments_and_sections_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_path = Path(tmp) / "skills" / "my-skill" / "SKILL.md"
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text(
                "---\n"
                "name: Bad_Name\n"
                "description: Activate for X. DO NOT activate for Y.\n"
                "---\n\n"
                "<!-- leftover comment -->\n"
                "## 1. Role and Objective\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_skills.validate_skill_file(
                skill_path, is_template=False, errors=errors, root=Path(tmp)
            )
            self.assertTrue(any("kebab-case" in err for err in errors))
            self.assertTrue(any("idêntico à pasta" in err for err in errors))
            self.assertTrue(any("comentário HTML residual" in err for err in errors))
            self.assertTrue(any("## 2. Scope" in err for err in errors))
            self.assertTrue(any("## 6. Short Example" in err for err in errors))


class TestValidateMarkdownLinks(unittest.TestCase):
    """Tests for relative Markdown link verification."""

    def test_valid_external_and_broken_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "skills" / "demo" / "SKILL.md"
            target.parent.mkdir(parents=True)
            target.write_text("# Demo\n", encoding="utf-8")

            readme = root / "README.md"
            readme.write_text(
                "\n".join(
                    [
                        "[Skill](skills/demo/SKILL.md#section)",
                        "[Web](https://example.com)",
                        "[Http](http://example.com)",
                        "[Mail](mailto:test@example.com)",
                        "[Anchor](#local)",
                        "[Broken](skills/missing/SKILL.md)",
                    ]
                ),
                encoding="utf-8",
            )

            errors: list[str] = []
            resolved = validate_skills.validate_markdown_links(
                readme, errors, root=root
            )
            self.assertEqual(resolved, {target.resolve()})
            self.assertEqual(len(errors), 1)
            self.assertIn("skills/missing/SKILL.md", errors[0])


class TestRepositoryValidation(unittest.TestCase):
    """End-to-end tests for full repository validation."""

    def _run_main(self, root: Path) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = validate_skills.main(root=root)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_valid_isolated_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_valid_repo(root)
            code, out, err = self._run_main(root)
            self.assertEqual(code, 0, msg=err)
            self.assertIn("OK: 1 skills", out)
            self.assertEqual(err, "")

    def test_missing_root_file_or_unlinked_skill_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_valid_repo(root)
            (root / "LICENSE").unlink()
            (root / "README.md").write_text("# Repo\n", encoding="utf-8")

            code, _, err = self._run_main(root)
            self.assertEqual(code, 1)
            self.assertIn("Arquivo obrigatório ausente: LICENSE", err)
            self.assertIn("não está linkada no catálogo", err)

    def test_duplicate_skill_name_and_missing_skill_md_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared_doc = build_skill_markdown(name="alpha-skill")
            build_valid_repo(
                root,
                skills={
                    "alpha-skill": shared_doc,
                    "beta-skill": shared_doc,
                },
            )
            (root / "skills" / "gamma-skill").mkdir()

            code, _, err = self._run_main(root)
            self.assertEqual(code, 1)
            self.assertIn("Nome duplicado 'alpha-skill'", err)
            self.assertIn("skills/gamma-skill: arquivo 'SKILL.md' ausente.", err)

    def test_empty_skills_dir_and_bad_folder_name_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_valid_repo(root)
            (root / "skills" / "sample-skill" / "SKILL.md").unlink()
            (root / "skills" / "sample-skill").rmdir()

            code, _, err = self._run_main(root)
            self.assertEqual(code, 1)
            self.assertIn("Nenhuma skill encontrada", err)

            bad_dir = root / "skills" / "BadFolder"
            bad_dir.mkdir()
            (bad_dir / "SKILL.md").write_text(
                build_skill_markdown(name="bad-folder"), encoding="utf-8"
            )
            code, _, err = self._run_main(root)
            self.assertEqual(code, 1)
            self.assertIn("nome da pasta deve estar em kebab-case", err)

    def test_actual_repository_passes_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("OK:", result.stdout)


if __name__ == "__main__":
    unittest.main()
