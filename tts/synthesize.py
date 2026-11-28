#!/usr/bin/env python3
"""Synthesize per-scene narration MP3s via edge-tts, compute durations, and emit manifest.json + subtitles.srt."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_VOICES: dict[str, str] = {
    "pt-BR": "pt-BR-AntonioNeural",
    "en-US": "en-US-AndrewNeural",
}

DEFAULT_FPS = 30
SCENE_BREATH_PAD_FRAMES = 12  # ~0.4s natural pause after speech
ACTIVE_PAUSE_REVEAL_FRAMES = 90  # 3.0s answer reveal when answer is present


def format_srt_timestamp(seconds: float) -> str:
    """Format seconds as an SRT timestamp (HH:MM:SS,mmm)."""
    total_ms = max(0, round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def split_caption_chunks(text: str, max_chars: int = 84) -> list[str]:
    """Split spoken narration into readable subtitle chunks."""
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: list[str] = []
    for sentence in sentences:
        if len(sentence) <= max_chars:
            chunks.append(sentence)
            continue
        words = sentence.split(" ")
        current: list[str] = []
        current_len = 0
        for word in words:
            projected = current_len + len(word) + (1 if current else 0)
            if projected > max_chars and current:
                chunks.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len = projected
        if current:
            chunks.append(" ".join(current))
    return chunks


def measure_audio_duration(audio_path: Path) -> float:
    """Measure real MP3 duration in seconds using mutagen, with ffprobe fallback."""
    try:
        from mutagen.mp3 import MP3  # type: ignore

        info = MP3(str(audio_path)).info
        duration = float(info.length)
        if duration > 0:
            return duration
    except Exception:
        pass

    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        result = subprocess.run(
            [
                ffprobe_bin,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())

    raise RuntimeError(f"Could not determine MP3 duration for {audio_path}. Ensure mutagen is installed.")


async def _synthesize_audio(text: str, voice: str, out_path: Path) -> None:
    import edge_tts  # type: ignore

    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(out_path))


def resolve_voice(meta: dict[str, Any]) -> str:
    """Resolve the neural voice from meta.voice or language default."""
    explicit = meta.get("voice")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    language = meta.get("language", "en-US")
    return DEFAULT_VOICES.get(language, DEFAULT_VOICES["en-US"])


def build_subtitles_srt(scene_entries: list[dict[str, Any]], fps: int = DEFAULT_FPS) -> str:
    """Generate an SRT subtitle string synchronized to the cumulative scene timeline."""
    blocks: list[str] = []
    cue_index = 1
    cursor_sec = 0.0

    for scene in scene_entries:
        narration = str(scene.get("narration", "")).strip()
        speech_sec = float(scene["durationSec"])
        total_scene_sec = float(scene["totalFrames"]) / fps

        chunks = split_caption_chunks(narration)
        if chunks and speech_sec > 0:
            total_chars = sum(len(chunk) for chunk in chunks) or 1
            local_cursor = cursor_sec
            for idx, chunk in enumerate(chunks):
                if idx == len(chunks) - 1:
                    chunk_end = cursor_sec + speech_sec
                else:
                    proportion = len(chunk) / total_chars
                    chunk_end = local_cursor + max(0.6, speech_sec * proportion)
                    chunk_end = min(chunk_end, cursor_sec + speech_sec)
                blocks.append(
                    f"{cue_index}\n"
                    f"{format_srt_timestamp(local_cursor)} --> {format_srt_timestamp(chunk_end)}\n"
                    f"{chunk}\n"
                )
                cue_index += 1
                local_cursor = chunk_end

        cursor_sec += total_scene_sec

    return "\n".join(blocks).strip() + ("\n" if blocks else "")


async def synthesize_lesson_async(
    lesson: dict[str, Any],
    out_dir: Path,
    *,
    fps: int = DEFAULT_FPS,
    audio_url_prefix: str = "",
) -> tuple[dict[str, Any], Path, Path]:
    """Synthesize all scene MP3 files and write manifest.json and subtitles.srt."""
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = dict(lesson["meta"])
    voice = resolve_voice(meta)
    meta["voice"] = voice
    meta.setdefault("aspectRatio", "16:9")

    prefix = audio_url_prefix.strip("/")
    manifest_scenes: list[dict[str, Any]] = []

    for index, scene in enumerate(lesson["scenes"]):
        filename = f"scene-{index:02d}.mp3"
        mp3_path = out_dir / filename
        await _synthesize_audio(scene["narration"], voice, mp3_path)

        duration_sec = round(measure_audio_duration(mp3_path), 3)
        duration_frames = max(fps, math.ceil(duration_sec * fps) + SCENE_BREATH_PAD_FRAMES)

        pause_seconds = float(scene.get("pauseSeconds", 0) or 0)
        pause_frames = round(pause_seconds * fps) if scene.get("type") == "active_pause" else 0
        reveal_frames = (
            ACTIVE_PAUSE_REVEAL_FRAMES
            if scene.get("type") == "active_pause" and str(scene.get("answer", "")).strip()
            else 0
        )
        total_frames = duration_frames + pause_frames + reveal_frames

        audio_ref = f"{prefix}/{filename}" if prefix else filename
        scene_entry = dict(scene)
        scene_entry.update(
            {
                "index": index,
                "audioPath": audio_ref,
                "durationSec": duration_sec,
                "durationFrames": duration_frames,
                "pauseFrames": pause_frames,
                "revealFrames": reveal_frames,
                "totalFrames": total_frames,
            }
        )
        manifest_scenes.append(scene_entry)

    total_frames_all = sum(int(item["totalFrames"]) for item in manifest_scenes)
    manifest: dict[str, Any] = {
        "fps": fps,
        "totalFrames": total_frames_all,
        "totalDurationSec": round(total_frames_all / fps, 3),
        "meta": meta,
        "scenes": manifest_scenes,
    }

    manifest_path = out_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    srt_content = build_subtitles_srt(manifest_scenes, fps=fps)
    srt_path = out_dir / "subtitles.srt"
    srt_path.write_text(srt_content, encoding="utf-8")

    return manifest, manifest_path, srt_path


def synthesize_lesson(
    lesson: dict[str, Any],
    out_dir: Path,
    *,
    fps: int = DEFAULT_FPS,
    audio_url_prefix: str = "",
) -> tuple[dict[str, Any], Path, Path]:
    """Synchronous wrapper around synthesize_lesson_async."""
    return asyncio.run(
        synthesize_lesson_async(
            lesson,
            out_dir,
            fps=fps,
            audio_url_prefix=audio_url_prefix,
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize TTS audio and subtitles for a lesson.json script.")
    parser.add_argument("lesson_json", type=Path, help="Path to lesson.json")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory for MP3s, manifest.json, and SRT")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Target video FPS (default: 30)")
    parser.add_argument(
        "--audio-url-prefix",
        type=str,
        default="",
        help="Relative prefix for audioPath in manifest.json (e.g. _build/run-1)",
    )
    args = parser.parse_args(argv)

    with args.lesson_json.open("r", encoding="utf-8") as fh:
        lesson = json.load(fh)

    manifest, manifest_path, srt_path = synthesize_lesson(
        lesson,
        args.out_dir,
        fps=args.fps,
        audio_url_prefix=args.audio_url_prefix,
    )
    print(
        f"Synthesized {len(manifest['scenes'])} scenes "
        f"({manifest['totalDurationSec']}s) -> {manifest_path} & {srt_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
