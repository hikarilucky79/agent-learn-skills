# Changelog

All notable changes to `agent-learn-skills` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Shared offline interactive study page template (`templates/STUDY_PAGE_TEMPLATE.html`) with inline CSS/Vanilla JS (Active-Reveal Concept Cards, 4–8 Flip Flashcards, Diagnostic Quiz hidden until **Check Answers**, Light/Dark toggle, progress bar, and Reset button).
- Automatic `.html` study page generation integrated across all 9 catalog skills (`skills/*/SKILL.md`) and `templates/SKILL_TEMPLATE.md`, with portable inline instructions for isolated installs and automated validation (`tests/test_study_page_template.py`).
- README badges (CI status, MIT license, PRs welcome) and a "Before vs. After" showcase table.

### Fixed
- Resolved leftover merge conflict markers in the `tests/` repository tree inside `README.md`.

## [0.1.0] - 2026-11-27

### Added
- **MVP Skills:** `quiz-master`, `flashcards-srs`, `feynman-tutor`, `code-mentor`, and `study-roadmap`.
- **Templates & Governance:** `templates/SKILL_TEMPLATE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `AGENTS.md`, and `.github/` PR & Issue templates.
- **Tooling & Installers:** `scripts/install.sh`, `scripts/install.ps1`, `scripts/new_skill.py`, `scripts/validate_skills.py`, and `skills/flashcards-srs/scripts/validate_anki_csv.py`.
- **CI & Tests:** GitHub Actions validation workflow (`.github/workflows/validate.yml`), unit tests, and `tests/activation_prompts.md`.
