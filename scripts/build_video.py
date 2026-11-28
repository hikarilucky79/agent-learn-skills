#!/usr/bin/env python3
"""End-to-end CLI to validate a lesson.json, synthesize TTS audio, and render MP4 + SRT via Remotion."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_lesson import validate_lesson_file
from tts.synthesize import DEFAULT_FPS, synthesize_lesson


def _resolve_npx() -> str:
    npx_bin = shutil.which("npx")
    if npx_bin:
        return npx_bin
    if os.name == "nt":
        npx_cmd = shutil.which("npx.cmd")
        if npx_cmd:
            return npx_cmd
    raise FileNotFoundError("Could not find 'npx' on PATH. Install Node.js 20+ and npm.")


def _find_ffmpeg(video_dir: Path) -> str | None:
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path

    exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    node_modules = video_dir / "node_modules" / "@remotion"
    if node_modules.exists():
        for match in node_modules.rglob(exe_name):
            if match.is_file():
                return str(match)
    return None


def _embed_soft_subtitles(mp4_path: Path, srt_path: Path, ffmpeg_bin: str) -> None:
    temp_out = mp4_path.with_name(f"{mp4_path.stem}.subbed{mp4_path.suffix}")
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(mp4_path),
        "-i",
        str(srt_path),
        "-c",
        "copy",
        "-c:s",
        "mov_text",
        str(temp_out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        if temp_out.exists():
            temp_out.unlink()
        raise RuntimeError(f"FFmpeg subtitle muxing failed:\n{result.stderr}")
    temp_out.replace(mp4_path)


def build_video(
    lesson_path: Path,
    out_mp4: Path,
    *,
    fps: int = DEFAULT_FPS,
    embed_subs: bool = False,
    keep_temp: bool = False,
) -> tuple[Path, Path]:
    """Validate lesson.json, synthesize audio + SRT, and render the final MP4."""
    lesson_abs = lesson_path.resolve()
    out_abs = out_mp4.resolve()

    errors = validate_lesson_file(lesson_abs)
    if errors:
        formatted = "\n".join(f"  - {err}" for err in errors)
        raise ValueError(f"Lesson validation failed for {lesson_abs}:\n{formatted}")

    with lesson_abs.open("r", encoding="utf-8") as fh:
        lesson = json.load(fh)

    video_dir = REPO_ROOT / "video"
    if not (video_dir / "node_modules").exists():
        raise FileNotFoundError(
            f"Remotion dependencies are not installed in {video_dir}. Run 'cd video && npm install'."
        )

    build_id = f"{lesson['meta']['id']}-{uuid.uuid4().hex[:8]}"
    staging_dir = video_dir / "public" / "_build" / build_id
    out_abs.parent.mkdir(parents=True, exist_ok=True)

    try:
        manifest, _manifest_path, srt_src = synthesize_lesson(
            lesson,
            staging_dir,
            fps=fps,
            audio_url_prefix=f"_build/{build_id}",
        )

        # Save <out_stem>.srt and subtitles.srt alongside the rendered MP4
        out_srt = out_abs.with_suffix(".srt")
        shutil.copy2(srt_src, out_srt)
        companion_srt = out_abs.parent / "subtitles.srt"
        if companion_srt != out_srt:
            shutil.copy2(srt_src, companion_srt)

        props_path = staging_dir / "props.json"
        with props_path.open("w", encoding="utf-8") as fh:
            json.dump({"manifest": manifest}, fh, ensure_ascii=False, indent=2)

        npx_bin = _resolve_npx()
        render_cmd = [
            npx_bin,
            "remotion",
            "render",
            "src/index.ts",
            "LessonVideo",
            str(out_abs),
            "--props",
            str(props_path),
        ]
        result = subprocess.run(render_cmd, cwd=str(video_dir), check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Remotion render failed with exit code {result.returncode}.")

        if embed_subs:
            ffmpeg_bin = _find_ffmpeg(video_dir)
            if not ffmpeg_bin:
                raise RuntimeError("Cannot embed subtitles: 'ffmpeg' was not found on PATH or in Remotion.")
            _embed_soft_subtitles(out_abs, out_srt, ffmpeg_bin)

        return out_abs, out_srt
    finally:
        if not keep_temp and staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build an Editorial Notebook MP4 video lesson and SRT subtitles from lesson.json."
    )
    parser.add_argument("lesson_json", type=Path, help="Path to lesson.json")
    parser.add_argument("--out", type=Path, required=True, help="Output MP4 path (e.g. out/lesson/lesson.mp4)")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Video frame rate (default: 30)")
    parser.add_argument(
        "--embed-subs",
        action="store_true",
        help="Mux soft subtitles (mov_text) into the MP4 container using ffmpeg",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary audio and manifest staging files under video/public/_build/",
    )
    args = parser.parse_args(argv)

    try:
        out_mp4, out_srt = build_video(
            args.lesson_json,
            args.out,
            fps=args.fps,
            embed_subs=args.embed_subs,
            keep_temp=args.keep_temp,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Success: rendered video -> {out_mp4}")
    print(f"Success: subtitles      -> {out_srt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
