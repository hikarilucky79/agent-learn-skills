#!/usr/bin/env python3
"""Unit tests for lesson validation, TTS timing helpers, and skill metadata."""

from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_lesson import validate_lesson, validate_lesson_file
from tts.synthesize import format_srt_timestamp, split_caption_chunks


class TestValidateLesson(unittest.TestCase):
    def setUp(self) -> None:
        sample_path = REPO_ROOT / "examples" / "sample-lesson.json"
        with sample_path.open("r", encoding="utf-8") as fh:
            self.valid_lesson = json.load(fh)

    def test_sample_lesson_file_is_valid(self) -> None:
        errors = validate_lesson_file(REPO_ROOT / "examples" / "sample-lesson.json")
        self.assertEqual(errors, [])

    def test_invalid_kebab_case_id_is_rejected(self) -> None:
        bad = copy.deepcopy(self.valid_lesson)
        bad["meta"]["id"] = "EventLoop_NodeJS"
        errors = validate_lesson(bad)
        self.assertTrue(any("meta.id" in err for err in errors), errors)

    def test_invalid_scene_type_is_rejected(self) -> None:
        bad = copy.deepcopy(self.valid_lesson)
        bad["scenes"][0]["type"] = "animation_3d"
        errors = validate_lesson(bad)
        self.assertTrue(any("scenes[0].type" in err or "enum" in err for err in errors), errors)

    def test_active_pause_requires_pause_seconds(self) -> None:
        bad = copy.deepcopy(self.valid_lesson)
        pause_scene = next(s for s in bad["scenes"] if s["type"] == "active_pause")
        del pause_scene["pauseSeconds"]
        errors = validate_lesson(bad)
        self.assertTrue(any("pauseSeconds" in err for err in errors), errors)

    def test_active_pause_rejects_out_of_range_seconds(self) -> None:
        bad = copy.deepcopy(self.valid_lesson)
        pause_scene = next(s for s in bad["scenes"] if s["type"] == "active_pause")
        pause_scene["pauseSeconds"] = 15
        errors = validate_lesson(bad)
        self.assertTrue(any("pauseSeconds" in err for err in errors), errors)

    def test_quiz_recap_rejects_out_of_range_correct_index(self) -> None:
        bad = copy.deepcopy(self.valid_lesson)
        quiz_scene = next(s for s in bad["scenes"] if s["type"] == "quiz_recap")
        quiz_scene["correctIndex"] = len(quiz_scene["options"])
        errors = validate_lesson(bad)
        self.assertTrue(any("correctIndex" in err for err in errors), errors)

    def test_code_trace_requires_code(self) -> None:
        bad = copy.deepcopy(self.valid_lesson)
        code_scene = next(s for s in bad["scenes"] if s["type"] == "code_trace")
        code_scene["code"] = "   "
        errors = validate_lesson(bad)
        self.assertTrue(any("code" in err for err in errors), errors)

    def test_raw_markdown_in_narration_is_rejected(self) -> None:
        bad = copy.deepcopy(self.valid_lesson)
        bad["scenes"][0]["narration"] = "Veja ```const x = 1;``` no codigo."
        errors = validate_lesson(bad)
        self.assertTrue(any("narration" in err for err in errors), errors)


class TestTtsHelpers(unittest.TestCase):
    def test_format_srt_timestamp(self) -> None:
        self.assertEqual(format_srt_timestamp(0.0), "00:00:00,000")
        self.assertEqual(format_srt_timestamp(65.432), "00:01:05,432")
        self.assertEqual(format_srt_timestamp(3661.5), "01:01:01,500")

    def test_split_caption_chunks_respects_max_chars(self) -> None:
        text = (
            "First sentence is short. Second sentence is deliberately much longer so that "
            "it must be wrapped cleanly across multiple subtitle cues without cutting words."
        )
        chunks = split_caption_chunks(text, max_chars=60)
        self.assertGreaterEqual(len(chunks), 3)
        self.assertTrue(all(len(c) <= 60 for c in chunks))


class TestSkillMetadata(unittest.TestCase):
    def test_lesson_skill_frontmatter_and_boundaries(self) -> None:
        skill_path = REPO_ROOT / "skills" / "lesson" / "SKILL.md"
        self.assertTrue(skill_path.exists())
        content = skill_path.read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^name:\s*lesson\s*$")
        self.assertIn("DO NOT activate", content)
        self.assertNotIn("<!--", content)


if __name__ == "__main__":
    unittest.main()
