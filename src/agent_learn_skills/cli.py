#!/usr/bin/env python3
"""Cross-platform CLI for installing agent-learn-skills via pip/pipx."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VALID_AGENTS = ("claude", "cursor", "codex", "opencode", "antigravity")
VALID_SCOPES = ("global", "project")


def _resolve_data_root() -> Path:
    packaged = Path(__file__).resolve().parent / "data"
    if (packaged / "skills").is_dir():
        return packaged
    repo_root = Path(__file__).resolve().parents[2]
    if (repo_root / "skills").is_dir():
        return repo_root
    raise FileNotFoundError("Could not locate 'skills/' directory in package or repository.")


def _resolve_target(agent: str, scope: str, target: str) -> Path:
    if target.strip():
        return Path(target).expanduser().resolve()
    home = Path.home()
    base = home if scope == "global" else Path.cwd()
    if agent == "claude":
        return base / ".claude" / "skills"
    if agent == "cursor":
        return base / ".cursor" / "skills"
    if agent in ("codex", "opencode"):
        return base / ".agents" / "skills"
    if agent == "antigravity":
        return (home / ".gemini" / "antigravity" / "skills") if scope == "global" else (base / ".agent" / "skills")
    raise ValueError(f"Unknown agent: {agent}")


def _available_skills(skills_src: Path) -> list[str]:
    return sorted(
        d.name for d in skills_src.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent-learn-skills",
        description="Install or uninstall agent-learn-skills for AI coding agents.",
    )
    parser.add_argument("-a", "--agent", choices=VALID_AGENTS, default="claude")
    parser.add_argument("-s", "--scope", choices=VALID_SCOPES, default="global")
    parser.add_argument("-t", "--target", default="", help="Custom destination directory")
    parser.add_argument(
        "-k",
        "--skill",
        action="append",
        default=[],
        help="Skill name to install/uninstall (repeatable or comma-separated)",
    )
    parser.add_argument("-l", "--list", action="store_true", help="List available skills")
    parser.add_argument("--symlink", action="store_true", help="Create symlinks instead of copying")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing skills")
    parser.add_argument("--uninstall", action="store_true", help="Remove installed repository skills")

    args = parser.parse_args(argv)
    data_root = _resolve_data_root()
    skills_src = data_root / "skills"
    study_template = data_root / "templates" / "STUDY_PAGE_TEMPLATE.html"

    available = _available_skills(skills_src)
    if args.list:
        print("Available skills:")
        for s in available:
            print(f"  - {s}")
        return 0

    selected: list[str] = []
    for raw in args.skill:
        for item in raw.split(","):
            if item.strip():
                selected.append(item.strip())
    if not selected:
        selected = available

    for name in selected:
        if not SKILL_NAME_RE.match(name) or not (skills_src / name / "SKILL.md").is_file():
            print(f"ERROR: invalid or missing skill '{name}'.", file=sys.stderr)
            return 1

    dest_dir = _resolve_target(args.agent, args.scope, args.target)

    if args.uninstall:
        removed = 0
        skipped = 0
        for name in selected:
            dst = dest_dir / name
            if not dst.exists() and not dst.is_symlink():
                skipped += 1
                continue
            if dst.is_symlink() and not args.force:
                if dst.resolve() != (skills_src / name).resolve():
                    print(f"SKIPPED: {name} (external symlink at {dst}; use --force to remove)")
                    skipped += 1
                    continue
            if dst.is_symlink():
                dst.unlink()
            else:
                shutil.rmtree(dst)
            print(f"REMOVED: {name} <- {dst}")
            removed += 1
        print(f"Done: {removed} removed, {skipped} skipped in {dest_dir}")
        return 0

    dest_dir.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped = 0

    for name in selected:
        src = skills_src / name
        dst = dest_dir / name
        if dst.exists() or dst.is_symlink():
            if args.force:
                if dst.is_symlink():
                    dst.unlink()
                else:
                    shutil.rmtree(dst)
            else:
                print(f"SKIPPED: {name} (already exists at {dst}; use --force to replace)")
                skipped += 1
                continue

        if args.symlink:
            os.symlink(src, dst, target_is_directory=True)
        else:
            shutil.copytree(src, dst)
            if study_template.is_file():
                assets_dir = dst / "assets"
                assets_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(study_template, assets_dir / "STUDY_PAGE_TEMPLATE.html")

        mode = "symlink" if args.symlink else "copy"
        print(f"INSTALLED ({mode}): {name} -> {dst}")
        installed += 1

    print(f"Done: {installed} installed, {skipped} skipped in {dest_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
