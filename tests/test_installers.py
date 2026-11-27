#!/usr/bin/env python3
"""Integration tests for install and --uninstall / -Uninstall in install.sh and install.ps1."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = REPO_ROOT / "scripts" / "install.sh"
INSTALL_PS1 = REPO_ROOT / "scripts" / "install.ps1"


def _find_bash() -> str | None:
    if sys.platform == "win32":
        git_path = shutil.which("git")
        candidates = [
            Path(r"C:\Program Files\Git\bin\bash.exe"),
            Path(r"C:\Program Files (x86)\Git\bin\bash.exe"),
        ]
        if git_path:
            git_root = Path(git_path).resolve().parent.parent
            candidates.insert(0, git_root / "bin" / "bash.exe")
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        return None
    return shutil.which("bash")


def _find_powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


class TestInstallSh(unittest.TestCase):
    """Tests for scripts/install.sh including --uninstall."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.bash = _find_bash()
        if cls.bash is None:
            raise unittest.SkipTest("bash executable not available in this environment")

    def _run_sh(
        self,
        args: list[str],
        cwd: Path | None = None,
        env_overrides: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        assert self.bash is not None
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            [self.bash, INSTALL_SH.as_posix(), *args],
            cwd=cwd or REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help_and_conflicting_flags(self) -> None:
        help_res = self._run_sh(["--help"])
        self.assertEqual(help_res.returncode, 0, msg=help_res.stderr)
        self.assertIn("--uninstall", help_res.stdout)

        conflict_res = self._run_sh(["--uninstall", "--copy"])
        self.assertEqual(conflict_res.returncode, 1)
        self.assertIn("não pode ser combinado", conflict_res.stderr)

    def test_invalid_skill_name_rejected_before_uninstall(self) -> None:
        for bad_skill in ["../evil", "unknown-skill", "BadName"]:
            with self.subTest(skill=bad_skill):
                with tempfile.TemporaryDirectory() as tmp:
                    res = self._run_sh(
                        ["--uninstall", "--target", Path(tmp).as_posix(), "--skill", bad_skill]
                    )
                    self.assertEqual(res.returncode, 1)
                    self.assertIn("ERRO:", res.stderr)

    def test_copy_install_and_selective_or_full_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "custom-skills"

            # Uninstalling when target directory does not exist should succeed without creating it
            missing_res = self._run_sh(["--uninstall", "--target", dest.as_posix()])
            self.assertEqual(missing_res.returncode, 0, msg=missing_res.stderr)
            self.assertFalse(dest.exists())
            self.assertIn("0 removida(s)", missing_res.stdout)

            # Install two selected skills using --copy
            inst_res = self._run_sh(
                [
                    "--copy",
                    "--target",
                    dest.as_posix(),
                    "--skill",
                    "quiz-master",
                    "--skill",
                    "code-mentor",
                ]
            )
            self.assertEqual(inst_res.returncode, 0, msg=inst_res.stderr)
            self.assertTrue((dest / "quiz-master" / "SKILL.md").is_file())
            self.assertTrue((dest / "code-mentor" / "SKILL.md").is_file())

            # Place an unrelated third-party skill that must never be deleted
            third_party = dest / "third-party-skill"
            third_party.mkdir()
            (third_party / "SKILL.md").write_text("# Keep\n", encoding="utf-8")

            # Uninstall only quiz-master
            uninst_one = self._run_sh(
                [
                    "--uninstall",
                    "--target",
                    dest.as_posix(),
                    "--skill",
                    "quiz-master",
                ]
            )
            self.assertEqual(uninst_one.returncode, 0, msg=uninst_one.stderr)
            self.assertFalse((dest / "quiz-master").exists())
            self.assertTrue((dest / "code-mentor").is_dir())
            self.assertTrue(third_party.is_dir())
            self.assertIn("1 removida(s)", uninst_one.stdout)

            # Uninstall all repo skills (should remove code-mentor, skip absent ones, keep third-party)
            uninst_all = self._run_sh(["--uninstall", "--target", dest.as_posix()])
            self.assertEqual(uninst_all.returncode, 0, msg=uninst_all.stderr)
            self.assertFalse((dest / "code-mentor").exists())
            self.assertTrue((third_party / "SKILL.md").is_file())
            self.assertIn("1 removida(s)", uninst_all.stdout)

    def test_project_scope_install_and_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            inst_res = self._run_sh(
                [
                    "--copy",
                    "--agent",
                    "antigravity",
                    "--scope",
                    "project",
                    "--skill",
                    "feynman-tutor",
                ],
                cwd=project_dir,
            )
            self.assertEqual(inst_res.returncode, 0, msg=inst_res.stderr)
            expected = project_dir / ".agent" / "skills" / "feynman-tutor" / "SKILL.md"
            self.assertTrue(expected.is_file())

            uninst_res = self._run_sh(
                [
                    "--uninstall",
                    "--agent",
                    "antigravity",
                    "--scope",
                    "project",
                    "--skill",
                    "feynman-tutor",
                ],
                cwd=project_dir,
            )
            self.assertEqual(uninst_res.returncode, 0, msg=uninst_res.stderr)
            self.assertFalse((project_dir / ".agent" / "skills" / "feynman-tutor").exists())

    def test_symlink_uninstall_and_external_symlink_protection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dest = tmp_path / "skills-dest"
            external_src = tmp_path / "external-skill"
            external_src.mkdir()
            sentinel = external_src / "keep.txt"
            sentinel.write_text("do not delete\n", encoding="utf-8")

            inst_res = self._run_sh(
                ["--target", dest.as_posix(), "--skill", "quiz-master"]
            )
            self.assertEqual(inst_res.returncode, 0, msg=inst_res.stderr)
            installed_entry = dest / "quiz-master"
            if not installed_entry.is_symlink():
                self.skipTest("Platform/shell ln -s created a copy instead of symlink")

            # Uninstall repo symlink without --force
            uninst_res = self._run_sh(
                ["--uninstall", "--target", dest.as_posix(), "--skill", "quiz-master"]
            )
            self.assertEqual(uninst_res.returncode, 0, msg=uninst_res.stderr)
            self.assertFalse(installed_entry.exists() or installed_entry.is_symlink())
            self.assertTrue((REPO_ROOT / "skills" / "quiz-master" / "SKILL.md").is_file())

            # External symlink must be skipped without --force, and unlinked with --force
            ext_link = dest / "code-mentor"
            os.symlink(external_src, ext_link, target_is_directory=True)

            skip_res = self._run_sh(
                ["--uninstall", "--target", dest.as_posix(), "--skill", "code-mentor"]
            )
            self.assertEqual(skip_res.returncode, 0, msg=skip_res.stderr)
            self.assertTrue(ext_link.is_symlink())
            self.assertIn("PULADA: code-mentor", skip_res.stdout)

            force_res = self._run_sh(
                [
                    "--uninstall",
                    "--force",
                    "--target",
                    dest.as_posix(),
                    "--skill",
                    "code-mentor",
                ]
            )
            self.assertEqual(force_res.returncode, 0, msg=force_res.stderr)
            self.assertFalse(ext_link.exists() or ext_link.is_symlink())
            self.assertTrue(sentinel.is_file())


class TestInstallPs1(unittest.TestCase):
    """Tests for scripts/install.ps1 including -Uninstall."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pwsh = _find_powershell()
        if cls.pwsh is None:
            raise unittest.SkipTest("PowerShell executable not available")

    def _run_ps1(
        self,
        args: list[str],
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        assert self.pwsh is not None
        return subprocess.run(
            [
                self.pwsh,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(INSTALL_PS1),
                *args,
            ],
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_conflicting_flags_and_invalid_skill_rejected(self) -> None:
        conflict = self._run_ps1(["-Uninstall", "-Symlink"])
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("Não é possível combinar", conflict.stderr + conflict.stdout)

        for bad_skill in ["../evil", "unknown-skill", "BadName"]:
            with self.subTest(skill=bad_skill):
                with tempfile.TemporaryDirectory() as tmp:
                    res = self._run_ps1(["-Uninstall", "-Target", tmp, "-Skill", bad_skill])
                    self.assertNotEqual(res.returncode, 0)

    def test_copy_install_and_selective_or_full_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "custom-skills"

            # Non-existent destination directory should not be created
            missing_res = self._run_ps1(["-Uninstall", "-Target", str(dest)])
            self.assertEqual(missing_res.returncode, 0, msg=missing_res.stderr)
            self.assertFalse(dest.exists())
            self.assertIn("0 removida(s)", missing_res.stdout)

            # Install two skills (comma-separated string as used in PowerShell CLI)
            inst_res = self._run_ps1(
                ["-Target", str(dest), "-Skill", "quiz-master,code-mentor"]
            )
            self.assertEqual(inst_res.returncode, 0, msg=inst_res.stderr)
            self.assertTrue((dest / "quiz-master" / "SKILL.md").is_file())
            self.assertTrue((dest / "code-mentor" / "SKILL.md").is_file())

            third_party = dest / "third-party-skill"
            third_party.mkdir()
            (third_party / "SKILL.md").write_text("# Keep\n", encoding="utf-8")

            # Uninstall only quiz-master
            uninst_one = self._run_ps1(
                ["-Uninstall", "-Target", str(dest), "-Skill", "quiz-master"]
            )
            self.assertEqual(uninst_one.returncode, 0, msg=uninst_one.stderr)
            self.assertFalse((dest / "quiz-master").exists())
            self.assertTrue((dest / "code-mentor").is_dir())
            self.assertTrue(third_party.is_dir())

            # Uninstall remaining repo skills
            uninst_all = self._run_ps1(["-Uninstall", "-Target", str(dest)])
            self.assertEqual(uninst_all.returncode, 0, msg=uninst_all.stderr)
            self.assertFalse((dest / "code-mentor").exists())
            self.assertTrue((third_party / "SKILL.md").is_file())
            self.assertIn("1 removida(s)", uninst_all.stdout)

    def test_project_scope_install_and_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            inst_res = self._run_ps1(
                ["-Agent", "antigravity", "-Scope", "project", "-Skill", "study-roadmap"],
                cwd=project_dir,
            )
            self.assertEqual(inst_res.returncode, 0, msg=inst_res.stderr)
            self.assertTrue(
                (project_dir / ".agent" / "skills" / "study-roadmap" / "SKILL.md").is_file()
            )

            uninst_res = self._run_ps1(
                [
                    "-Uninstall",
                    "-Agent",
                    "antigravity",
                    "-Scope",
                    "project",
                    "-Skill",
                    "study-roadmap",
                ],
                cwd=project_dir,
            )
            self.assertEqual(uninst_res.returncode, 0, msg=uninst_res.stderr)
            self.assertFalse(
                (project_dir / ".agent" / "skills" / "study-roadmap").exists()
            )

    @unittest.skipUnless(
        sys.platform == "win32", "Windows Junction reparse-point check"
    )
    def test_reparse_point_junction_uninstall_safety(self) -> None:
        assert self.pwsh is not None
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dest = tmp_path / "dest"
            dest.mkdir()
            external_dir = tmp_path / "external"
            external_dir.mkdir()
            external_sentinel = external_dir / "keep.txt"
            external_sentinel.write_text("preserve me\n", encoding="utf-8")

            missing_target = tmp_path / "deleted-target"
            missing_target.mkdir()

            repo_quiz = REPO_ROOT / "skills" / "quiz-master"
            setup_cmd = (
                f"New-Item -ItemType Junction -Path '{dest / 'quiz-master'}' -Target '{repo_quiz}' | Out-Null; "
                f"New-Item -ItemType Junction -Path '{dest / 'code-mentor'}' -Target '{external_dir}' | Out-Null; "
                f"New-Item -ItemType Junction -Path '{dest / 'feynman-tutor'}' -Target '{missing_target}' | Out-Null"
            )
            setup_res = subprocess.run(
                [self.pwsh, "-NoProfile", "-Command", setup_cmd],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(setup_res.returncode, 0, msg=setup_res.stderr)
            missing_target.rmdir()

            # Without -Force: repo junction removed, external and broken junctions skipped
            res = self._run_ps1(
                [
                    "-Uninstall",
                    "-Target",
                    str(dest),
                    "-Skill",
                    "quiz-master,code-mentor,feynman-tutor",
                ]
            )
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            self.assertFalse(os.path.lexists(dest / "quiz-master"))
            self.assertTrue((repo_quiz / "SKILL.md").is_file())
            self.assertTrue(os.path.lexists(dest / "code-mentor"))
            self.assertTrue(os.path.lexists(dest / "feynman-tutor"))
            self.assertIn("PULADA: code-mentor", res.stdout)
            self.assertIn("PULADA: feynman-tutor", res.stdout)

            # With -Force: external and broken junctions removed without touching external files
            res_force = self._run_ps1(
                [
                    "-Uninstall",
                    "-Force",
                    "-Target",
                    str(dest),
                    "-Skill",
                    "code-mentor,feynman-tutor",
                ]
            )
            self.assertEqual(res_force.returncode, 0, msg=res_force.stderr)
            self.assertFalse(os.path.lexists(dest / "code-mentor"))
            self.assertFalse(os.path.lexists(dest / "feynman-tutor"))
            self.assertTrue(external_sentinel.is_file())


if __name__ == "__main__":
    unittest.main()
