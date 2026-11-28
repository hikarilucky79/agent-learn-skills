#!/usr/bin/env python3
"""Validate a lesson.json script against schema/lesson.schema.json and semantic rules."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schema" / "lesson.schema.json"

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_LANGUAGES = {"pt-BR", "en-US"}
VALID_ASPECT_RATIOS = {"16:9", "9:16"}
VALID_SCENE_TYPES = {"intro", "concept", "code_trace", "active_pause", "quiz_recap"}

RAW_MARKDOWN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"```"), "triple backtick code fence"),
    (re.compile(r"(?m)^#{1,6}\s+"), "Markdown heading"),
    (re.compile(r"\[[^\]]+\]\([^)]+\)"), "Markdown link"),
]


def _load_schema(schema_path: Path = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    with schema_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _validate_with_jsonschema(data: Any, schema_path: Path) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []

    schema = _load_schema(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(part) for part in err.absolute_path) or "<root>"
        errors.append(f"Schema error at {path}: {err.message}")
    return errors


def validate_lesson(data: Any, schema_path: Path = DEFAULT_SCHEMA_PATH) -> list[str]:
    """Return a list of human-readable validation errors for a parsed lesson payload."""
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Root JSON value must be an object."]

    errors.extend(_validate_with_jsonschema(data, schema_path))

    meta = data.get("meta")
    if not isinstance(meta, dict):
        errors.append("Missing or invalid 'meta' object.")
    else:
        lesson_id = meta.get("id")
        if not isinstance(lesson_id, str) or not KEBAB_CASE_RE.match(lesson_id):
            errors.append("meta.id must be a non-empty kebab-case string (e.g. 'event-loop-nodejs').")

        for field in ("title", "discipline"):
            val = meta.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"meta.{field} must be a non-empty string.")

        language = meta.get("language")
        if language not in VALID_LANGUAGES:
            errors.append(f"meta.language must be one of {sorted(VALID_LANGUAGES)}.")

        aspect_ratio = meta.get("aspectRatio", "16:9")
        if aspect_ratio not in VALID_ASPECT_RATIOS:
            errors.append(f"meta.aspectRatio must be one of {sorted(VALID_ASPECT_RATIOS)}.")

        voice = meta.get("voice")
        if voice is not None and (not isinstance(voice, str) or not voice.strip()):
            errors.append("meta.voice, when provided, must be a non-empty string.")

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or len(scenes) == 0:
        errors.append("'scenes' must be a non-empty array.")
        return errors

    for idx, scene in enumerate(scenes):
        prefix = f"scenes[{idx}]"
        if not isinstance(scene, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        scene_type = scene.get("type")
        if scene_type not in VALID_SCENE_TYPES:
            errors.append(f"{prefix}.type must be one of {sorted(VALID_SCENE_TYPES)}.")

        heading = scene.get("heading")
        if not isinstance(heading, str) or not heading.strip():
            errors.append(f"{prefix}.heading must be a non-empty string.")

        narration = scene.get("narration")
        if not isinstance(narration, str) or len(narration.strip()) < 5:
            errors.append(f"{prefix}.narration must be a spoken string with at least 5 characters.")
        else:
            for pattern, label in RAW_MARKDOWN_PATTERNS:
                if pattern.search(narration):
                    errors.append(
                        f"{prefix}.narration contains raw Markdown ({label}); use natural spoken text only."
                    )

        if scene_type == "active_pause":
            pause_sec = scene.get("pauseSeconds")
            if (
                isinstance(pause_sec, bool)
                or not isinstance(pause_sec, (int, float))
                or pause_sec < 3
                or pause_sec > 8
            ):
                errors.append(f"{prefix}.pauseSeconds is required for active_pause and must be between 3 and 8.")

        elif scene_type == "code_trace":
            code = scene.get("code")
            if not isinstance(code, str) or not code.strip():
                errors.append(f"{prefix}.code is required for code_trace and must be a non-empty string.")

        elif scene_type == "quiz_recap":
            question = scene.get("question")
            if not isinstance(question, str) or not question.strip():
                errors.append(f"{prefix}.question is required for quiz_recap.")

            options = scene.get("options")
            if not isinstance(options, list) or not (2 <= len(options) <= 6) or any(
                not isinstance(opt, str) or not opt.strip() for opt in options
            ):
                errors.append(f"{prefix}.options must be an array of 2 to 6 non-empty strings.")

            correct_idx = scene.get("correctIndex")
            if isinstance(correct_idx, bool) or not isinstance(correct_idx, int):
                errors.append(f"{prefix}.correctIndex must be an integer.")
            elif isinstance(options, list) and not (0 <= correct_idx < len(options)):
                errors.append(
                    f"{prefix}.correctIndex ({correct_idx}) is out of range for {len(options)} options."
                )

            explanation = scene.get("explanation")
            if not isinstance(explanation, str) or not explanation.strip():
                errors.append(f"{prefix}.explanation is required for quiz_recap.")

    # Deduplicate while preserving order
    return list(dict.fromkeys(errors))


def validate_lesson_file(path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH) -> list[str]:
    """Load and validate a lesson JSON file from disk."""
    if not path.exists():
        return [f"File not found: {path}"]
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON in {path}: {exc}"]
    return validate_lesson(data, schema_path=schema_path)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1 or args[0] in {"-h", "--help"}:
        print("Usage: python scripts/validate_lesson.py <lesson.json>")
        return 0 if args and args[0] in {"-h", "--help"} else 1

    lesson_path = Path(args[0])
    errors = validate_lesson_file(lesson_path)
    if errors:
        print(f"Validation failed for {lesson_path} ({len(errors)} error(s)):", file=sys.stderr)
        for idx, err in enumerate(errors, start=1):
            print(f"  {idx}. {err}", file=sys.stderr)
        return 1

    print(f"OK: {lesson_path} is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
