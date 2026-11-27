# Changelog

All notable changes to `agent-learn-skills` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- README badges (CI status, MIT license, PRs welcome) and a "Before vs. After" showcase table.

## [0.1.0] - 2026-11-27

### Added
- **MVP Skills:** `quiz-master`, `flashcards-srs`, `feynman-tutor`, `code-mentor`, and `study-roadmap`.
- **Templates & Governance:** `templates/SKILL_TEMPLATE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `AGENTS.md`, and `.github/` PR & Issue templates.
- **Tooling & Installers:** `scripts/install.sh`, `scripts/install.ps1`, `scripts/new_skill.py`, `scripts/validate_skills.py`, and `skills/flashcards-srs/scripts/validate_anki_csv.py`.
- **CI & Tests:** GitHub Actions validation workflow (`.github/workflows/validate.yml`), unit tests, and `tests/activation_prompts.md`.
