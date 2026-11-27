#!/usr/bin/env python3
"""Tests for skills/interactive-study-page/SKILL.md and assets/template.html."""

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "interactive-study-page"
SKILL_MD = SKILL_DIR / "SKILL.md"
TEMPLATE_HTML = SKILL_DIR / "assets" / "template.html"

VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class TagBalanceParser(HTMLParser):
    """Lightweight HTML5 parser checking tag balance and collecting tags/assets."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.tags: list[str] = []
        self.external_attrs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        for attr, val in attrs:
            if attr in {"src", "href"} and val:
                self.external_attrs.append((tag, val))
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        for attr, val in attrs:
            if attr in {"src", "href"} and val:
                self.external_attrs.append((tag, val))

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if not self.stack or self.stack[-1] != tag:
            expected = self.stack[-1] if self.stack else "<empty>"
            self.errors.append(f"Mismatched closing </{tag}> (expected </{expected}>)")
            return
        self.stack.pop()


class TestInteractiveStudyPageSkill(unittest.TestCase):
    """Validate skill structure, conciseness, and offline HTML template compliance."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL_MD.read_text(encoding="utf-8")
        cls.template_text = TEMPLATE_HTML.read_text(encoding="utf-8")

    def test_skill_markdown_is_lean_and_references_template(self) -> None:
        line_count = len(self.skill_text.splitlines())
        self.assertLessEqual(line_count, 105, f"SKILL.md too long ({line_count} lines)")
        self.assertIn("assets/template.html", self.skill_text)
        self.assertNotIn("<!--", self.skill_text)
        for marker in (
            "Think first, then reveal",
            "Check Answers",
            "4–8",
            "Light/Dark",
            "Reset",
        ):
            self.assertIn(marker, self.skill_text)

    def test_template_is_valid_self_contained_html5(self) -> None:
        self.assertTrue(self.template_text.lstrip().startswith("<!DOCTYPE html>"))

        parser = TagBalanceParser()
        parser.feed(self.template_text)
        parser.close()

        self.assertEqual(parser.errors, [])
        self.assertEqual(parser.stack, [], f"Unclosed tags remain: {parser.stack}")
        self.assertEqual(parser.external_attrs, [])

        for forbidden in ("http://", "https://", "@import", "pyodide", "monaco"):
            self.assertNotIn(
                forbidden,
                self.template_text.lower(),
                f"Template must remain 100% offline without '{forbidden}'",
            )

        self.assertIn("<style>", self.template_text)
        self.assertIn("<script>", self.template_text)

    def test_template_includes_required_modules_and_ux_controls(self) -> None:
        required_tokens = [
            "STUDY_DATA",
            "Think first, then reveal",
            "Check Answers",
            'id="theme-toggle"',
            'id="reset-btn"',
            'id="progress-bar"',
            'id="concepts-list"',
            'id="flashcards-grid"',
            'id="quiz-list"',
            'id="quiz-score"',
            "flashcard-front",
            "flashcard-back",
        ]
        for token in required_tokens:
            self.assertIn(token, self.template_text)

        # Verify placeholder deck already models 4-8 atomic flashcards
        front_entries = re.findall(r'\{\s*front:\s*"', self.template_text)
        self.assertGreaterEqual(len(front_entries), 4)
        self.assertLessEqual(len(front_entries), 8)


if __name__ == "__main__":
    unittest.main()
