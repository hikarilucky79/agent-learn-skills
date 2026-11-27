#!/usr/bin/env python3
"""Tests for templates/STUDY_PAGE_TEMPLATE.html and skill integration across all catalog skills."""

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
TEMPLATE_HTML = REPO_ROOT / "templates" / "STUDY_PAGE_TEMPLATE.html"

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
    """Lightweight HTML5 parser checking tag balance and collecting external asset refs."""

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


class TestStudyPageTemplate(unittest.TestCase):
    """Validate shared offline HTML template and automatic integration across all catalog skills."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.template_text = TEMPLATE_HTML.read_text(encoding="utf-8")
        cls.skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))

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

        front_entries = re.findall(r'\{\s*front:\s*"', self.template_text)
        self.assertGreaterEqual(len(front_entries), 4)
        self.assertLessEqual(len(front_entries), 8)

    def test_every_catalog_skill_requires_automatic_study_page_generation(self) -> None:
        self.assertGreaterEqual(len(self.skill_files), 9)
        required_markers = (
            "templates/STUDY_PAGE_TEMPLATE.html",
            "Think first, then reveal",
            "4–8",
            "Check Answers",
            "Light/Dark",
            "Reset",
        )
        for skill_md in self.skill_files:
            text = skill_md.read_text(encoding="utf-8")
            with self.subTest(skill=skill_md.parent.name):
                self.assertNotIn("interactive-study-page", text)
                self.assertIn(".html", text)
                for marker in required_markers:
                    self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
