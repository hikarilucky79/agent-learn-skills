#!/usr/bin/env python3
"""Tests verifying catalog coverage and boundary alignment in tests/activation_prompts.md."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
PROMPTS_FILE = REPO_ROOT / "tests" / "activation_prompts.md"

BACKTICK_CODE_RE = re.compile(r"`([a-z0-9-]+)`")
DO_NOT_ACTIVATE_RE = re.compile(r"\bDO NOT activate\b(.*?)\n---", re.DOTALL)
DO_NOT_USE_SECTION_RE = re.compile(
    r"\*\*Do not use this skill when:\*\*(.*?)(?:\n## |\Z)",
    re.DOTALL,
)


def parse_activation_table(markdown: str) -> list[dict[str, str]]:
    """Extract data rows from the Markdown table in tests/activation_prompts.md."""
    rows: list[dict[str, str]] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] == "Test Prompt" or all(set(cell) <= {"-"} for cell in cells):
            continue
        rows.append(
            {
                "prompt": cells[0],
                "expected": cells[1],
                "must_not": cells[2],
                "criteria": cells[3],
            }
        )
    return rows


def extract_negative_boundary_text(skill_markdown: str) -> str:
    """Return combined text from frontmatter DO NOT activate and Scope exclusion clauses."""
    parts: list[str] = []
    fm_match = DO_NOT_ACTIVATE_RE.search(skill_markdown)
    if fm_match:
        parts.append(fm_match.group(1))
    scope_match = DO_NOT_USE_SECTION_RE.search(skill_markdown)
    if scope_match:
        parts.append(scope_match.group(1))
    return "\n".join(parts)


class TestActivationPrompts(unittest.TestCase):
    """Ensure activation prompt evals stay synchronized with catalog skills and boundaries."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_texts = {
            path.parent.name: path.read_text(encoding="utf-8")
            for path in sorted(SKILLS_DIR.glob("*/SKILL.md"))
        }
        cls.skill_names = set(cls.skill_texts.keys())
        cls.rows = parse_activation_table(PROMPTS_FILE.read_text(encoding="utf-8"))

    def test_table_has_entries_without_duplicate_prompts(self) -> None:
        self.assertGreater(len(self.rows), 0)
        prompts = [row["prompt"] for row in self.rows]
        self.assertEqual(len(prompts), len(set(prompts)))
        for row in self.rows:
            self.assertTrue(row["criteria"], f"Missing criteria for {row['prompt']}")

    def test_every_catalog_skill_has_a_positive_activation_prompt(self) -> None:
        covered_skills: set[str] = set()
        for row in self.rows:
            match = BACKTICK_CODE_RE.fullmatch(row["expected"])
            if match:
                covered_skills.add(match.group(1))
        self.assertEqual(
            covered_skills,
            self.skill_names,
            f"Missing activation prompts for: {sorted(self.skill_names - covered_skills)}",
        )

    def test_must_not_activate_boundaries_exist_and_are_reciprocal(self) -> None:
        negative_texts = {
            name: extract_negative_boundary_text(text)
            for name, text in self.skill_texts.items()
        }

        for row in self.rows:
            expected_match = BACKTICK_CODE_RE.fullmatch(row["expected"])
            must_not_skills = BACKTICK_CODE_RE.findall(row["must_not"])
            self.assertTrue(
                must_not_skills,
                f"Expected at least one Must Not Activate skill in row: {row['prompt']}",
            )

            for excluded in must_not_skills:
                self.assertIn(
                    excluded,
                    self.skill_names,
                    f"Unknown skill '{excluded}' in Must Not Activate",
                )

            if not expected_match:
                continue

            expected_skill = expected_match.group(1)
            self.assertIn(expected_skill, self.skill_names)
            self.assertNotIn(expected_skill, must_not_skills)

            for excluded in must_not_skills:
                self.assertIn(
                    excluded,
                    negative_texts[expected_skill],
                    f"{expected_skill}/SKILL.md should exclude '{excluded}' in DO NOT activate or Scope",
                )
                self.assertIn(
                    expected_skill,
                    negative_texts[excluded],
                    f"{excluded}/SKILL.md should reciprocally exclude '{expected_skill}' in DO NOT activate or Scope",
                )


if __name__ == "__main__":
    unittest.main()
