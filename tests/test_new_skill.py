#!/usr/bin/env python3
"""Unit and CLI tests for scripts/new_skill.py."""

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
SCRIPT_PATH = REPO_ROOT / "scripts" / "new_skill.py"
REAL_TEMPLATE = (REPO_ROOT / "templates" / "SKILL_TEMPLATE.md").read_text(
    encoding="utf-8"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validate_skills = _load_module(
    "validate_skills", REPO_ROOT / "scripts" / "validate_skills.py"
)
new_skill = _load_module("new_skill", SCRIPT_PATH)


def _setup_temp_repo(root: Path, template_content: str = REAL_TEMPLATE) -> None:
    templates_dir = root / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    (templates_dir / "SKILL_TEMPLATE.md").write_text(
        template_content, encoding="utf-8", newline="\n"
    )
    (root / "skills").mkdir(parents=True, exist_ok=True)


class TestNewSkillScaffolding(unittest.TestCase):
    """Tests for skill scaffolding generation and validation."""

    def _run_main(self, argv: list[str], root: Path) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = new_skill.main(argv=argv, root=root)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_creates_skill_with_prefilled_name_and_default_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_temp_repo(root)

            code, out, err = self._run_main(["mock-interview"], root)
            self.assertEqual(code, 0, msg=err)
            self.assertIn("OK: skill 'mock-interview' criada", out)

            target = root / "skills" / "mock-interview" / "SKILL.md"
            self.assertTrue(target.is_file())

            raw_bytes = target.read_bytes()
            self.assertNotIn(b"\r\n", raw_bytes)

            content = raw_bytes.decode("utf-8")
            self.assertIn("name: mock-interview\n", content)
            self.assertIn("# Mock Interview\n", content)
            self.assertIn("<!--", content)
            self.assertNotIn("skill-name-in-kebab-case", content)
            self.assertNotIn("[Human-Readable Skill Name]", content)

            parse_errors: list[str] = []
            fields = validate_skills.parse_frontmatter(
                content, "skills/mock-interview/SKILL.md", parse_errors
            )
            self.assertEqual(parse_errors, [])
            self.assertEqual(fields["name"], "mock-interview")
            self.assertIn("DO NOT activate", fields["description"])

    def test_custom_title_and_strip_comments_passes_skill_validator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_temp_repo(root)

            code, _, err = self._run_main(
                ["sql-trainer", "--title", "SQL Trainer", "--strip-comments"],
                root,
            )
            self.assertEqual(code, 0, msg=err)

            target = root / "skills" / "sql-trainer" / "SKILL.md"
            content = target.read_text(encoding="utf-8")
            self.assertIn("# SQL Trainer\n", content)
            self.assertNotIn("<!--", content)
            self.assertNotIn("-->", content)

            val_errors: list[str] = []
            name = validate_skills.validate_skill_file(
                target, is_template=False, errors=val_errors, root=root
            )
            self.assertEqual(name, "sql-trainer")
            self.assertEqual(val_errors, [])

    def test_rejects_invalid_names_and_path_traversal(self) -> None:
        invalid_names = [
            "",
            "BadName",
            "snake_case",
            "with spaces",
            "-leading-hyphen",
            "trailing-hyphen-",
            "double--hyphen",
            "../outside",
            "nested/skill",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_temp_repo(root)

            for bad_name in invalid_names:
                with self.subTest(name=bad_name):
                    argv = ["--", bad_name] if bad_name.startswith("-") else [bad_name]
                    code, _, err = self._run_main(argv, root)
                    self.assertEqual(code, 1)
                    self.assertIn("ERRO:", err)
                    with self.assertRaises(ValueError):
                        new_skill.create_skill(bad_name, root=root)

            self.assertEqual(list((root / "skills").iterdir()), [])

    def test_existing_skill_requires_force_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_temp_repo(root)

            skill_dir = root / "skills" / "existing-skill"
            skill_dir.mkdir(parents=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("existing custom content\n", encoding="utf-8")

            code, _, err = self._run_main(["existing-skill"], root)
            self.assertEqual(code, 1)
            self.assertIn("já existe", err)
            self.assertEqual(
                skill_file.read_text(encoding="utf-8"), "existing custom content\n"
            )

            code, out, err = self._run_main(["existing-skill", "--force"], root)
            self.assertEqual(code, 0, msg=err)
            self.assertIn("OK:", out)
            self.assertIn("name: existing-skill\n", skill_file.read_text(encoding="utf-8"))

    def test_rejects_invalid_title_and_missing_or_malformed_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Missing template
            code, _, err = self._run_main(["valid-name"], root)
            self.assertEqual(code, 1)
            self.assertIn("Template não encontrado", err)

            # Invalid title
            _setup_temp_repo(root)
            for bad_title in ["   ", "Line 1\nLine 2"]:
                with self.subTest(title=bad_title):
                    code, _, err = self._run_main(
                        ["valid-name", "--title", bad_title], root
                    )
                    self.assertEqual(code, 1)
                    self.assertIn("ERRO:", err)

            # Malformed template without frontmatter
            _setup_temp_repo(root, template_content="# Missing frontmatter\n")
            code, _, err = self._run_main(["valid-name"], root)
            self.assertEqual(code, 1)
            self.assertIn("frontmatter YAML ausente", err)

    def test_cli_help_executes_successfully(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--strip-comments", result.stdout)
        self.assertIn("--force", result.stdout)


if __name__ == "__main__":
    unittest.main()
