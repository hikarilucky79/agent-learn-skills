#!/usr/bin/env python3
"""Unit and CLI tests for skills/flashcards-srs/scripts/validate_anki_csv.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = (
    REPO_ROOT / "skills" / "flashcards-srs" / "scripts" / "validate_anki_csv.py"
)


def _load_validate_anki_csv():
    spec = importlib.util.spec_from_file_location("validate_anki_csv", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_anki_csv"] = module
    spec.loader.exec_module(module)
    return module


validate_anki_csv = _load_validate_anki_csv()


class TestValidateCloze(unittest.TestCase):
    """Tests for Anki Cloze syntax validation."""

    def test_valid_single_hint_and_multiple_clozes(self) -> None:
        valid_fronts = [
            "The default SQL index structure is {{c1::B-Tree}}.",
            "HTTP runs over {{c1::TLS::encryption protocol}}.",
            "{{c1::HTTPS}} relies on {{c2::TLS}} for transport security.",
        ]
        for front in valid_fronts:
            with self.subTest(front=front):
                errors: list[str] = []
                has_cloze = validate_anki_csv.validate_cloze(front, 1, errors)
                self.assertTrue(has_cloze)
                self.assertEqual(errors, [])

    def test_plain_qa_front_returns_false_without_errors(self) -> None:
        errors: list[str] = []
        has_cloze = validate_anki_csv.validate_cloze(
            "What is the time complexity of binary search?", 1, errors
        )
        self.assertFalse(has_cloze)
        self.assertEqual(errors, [])

    def test_malformed_and_invalid_cloze_cases(self) -> None:
        invalid_fronts = [
            ("The {{c1::unclosed protocol", "malformada"),
            ("Trailing braces }} in front", "malformada"),
            ("Invalid index {{c0::term}} here", "malformada"),
            ("Empty braces {{c1::}} here", "malformada"),
            ("Whitespace term {{c1::   }} here", "Cloze vazio"),
            ("Whitespace with hint {{c1::  ::hint}} here", "Cloze vazio"),
        ]
        for front, expected_fragment in invalid_fronts:
            with self.subTest(front=front):
                errors: list[str] = []
                has_cloze = validate_anki_csv.validate_cloze(front, 4, errors)
                self.assertTrue(has_cloze)
                self.assertEqual(len(errors), 1)
                self.assertIn("Linha 4:", errors[0])
                self.assertIn(expected_fragment, errors[0])


class TestValidateAnkiFile(unittest.TestCase):
    """Tests for CSV/TXT file parsing and card validation."""

    def _validate_content(
        self, content: str, encoding: str = "utf-8", suffix: str = ".csv"
    ) -> tuple[int, list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"deck{suffix}"
            path.write_text(content, encoding=encoding)
            return validate_anki_csv.validate_anki_file(path)

    def test_valid_mixed_semicolon_deck_with_headers_and_blank_lines(self) -> None:
        deck = (
            "#separator:semicolon\n"
            "#html:false\n"
            "\n"
            "What is an index?;Speeds up reads.;sql\n"
            "What is the trade-off?;Slower writes.\n"
            "Default index is {{c1::B-Tree}}.;;sql\n"
            "Use {{c1::EXPLAIN}} to inspect plans.;\n"
        )
        total, errors = self._validate_content(deck)
        self.assertEqual(total, 4)
        self.assertEqual(errors, [])

    def test_supported_separators_and_utf8_bom(self) -> None:
        cases = [
            ("#separator:tab\nFront\tBack\ttag\n", "utf-8"),
            ('#separator:comma\n"Front, with comma",Back,tag\n', "utf-8"),
            ("#separator:pipe\nFront|Back|tag\n", "utf-8"),
            ("#separator::\nFront:Back:tag\n", "utf-8"),
            ("#separator:semicolon\nBOM {{c1::card}};;tag\n", "utf-8-sig"),
        ]
        for content, encoding in cases:
            with self.subTest(content=content, encoding=encoding):
                total, errors = self._validate_content(content, encoding=encoding)
                self.assertEqual(total, 1)
                self.assertEqual(errors, [])

    def test_unknown_separator_and_empty_deck_fail(self) -> None:
        total, errors = self._validate_content("#separator:space\nA B C\n")
        self.assertEqual(total, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("separador desconhecido 'space'", errors[0])

        for empty_content in ["", "\n   \n#separator:semicolon\n#html:false\n"]:
            with self.subTest(empty_content=empty_content):
                total, errors = self._validate_content(empty_content)
                self.assertEqual(total, 0)
                self.assertEqual(errors, ["Nenhuma carta encontrada no arquivo."])

    def test_row_and_card_validation_errors(self) -> None:
        deck = (
            "#separator:semicolon\n"
            "Only one column\n"
            "A;B;C;D\n"
            ";Missing front;tag\n"
            "Question without back;;tag\n"
            "Broken {{c1::cloze;;tag\n"
            "Valid question;Valid answer;tag\n"
        )
        total, errors = self._validate_content(deck)
        self.assertEqual(total, 6)
        self.assertEqual(len(errors), 5)
        self.assertIn("Linha 2: esperado 2 ou 3 colunas", errors[0])
        self.assertIn("Linha 3: esperado 2 ou 3 colunas", errors[1])
        self.assertIn("Linha 4: campo 'Frente' está vazio.", errors[2])
        self.assertIn("Linha 5: carta P&R sem 'Verso' preenchido", errors[3])
        self.assertIn("Linha 6: sintaxe Cloze malformada", errors[4])


class TestValidateAnkiCli(unittest.TestCase):
    """Tests for CLI entry point and subprocess execution."""

    def test_main_missing_file_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does_not_exist.csv"
            stderr = io.StringIO()
            with (
                patch.object(sys, "argv", ["validate_anki_csv.py", str(missing)]),
                contextlib.redirect_stderr(stderr),
            ):
                code = validate_anki_csv.main()
            self.assertEqual(code, 1)
            self.assertIn("arquivo não encontrado", stderr.getvalue())

    def test_subprocess_valid_and_invalid_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            valid_file = Path(tmp) / "valid.csv"
            valid_file.write_text(
                "#separator:semicolon\nQ1;A1;tag\n{{c1::Cloze}};;tag\n",
                encoding="utf-8",
            )
            ok_res = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(valid_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(ok_res.returncode, 0, msg=ok_res.stderr)
            self.assertIn("OK: 2 carta(s) válida(s)", ok_res.stdout)

            invalid_file = Path(tmp) / "invalid.csv"
            invalid_file.write_text("Question only\n", encoding="utf-8")
            bad_res = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(invalid_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(bad_res.returncode, 1)
            self.assertIn("FALHA NA VALIDAÇÃO ANKI CSV:", bad_res.stderr)


if __name__ == "__main__":
    unittest.main()
