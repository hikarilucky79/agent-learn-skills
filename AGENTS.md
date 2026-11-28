# AGENTS.md

Instructions for AI agents editing or maintaining this repository (`agent-learn-skills`).

## Overview
- Open-source catalog of `SKILL.md` Agent Skills focused on **active learning** (Active Recall quizzes, SRS flashcards, Feynman Technique, code mentoring, study roadmaps, mock interviews, active language coaching, active doc deconstruction, and post-bug postmortems), where every skill automatically generates a self-contained offline `.html` interactive study page via [`templates/STUDY_PAGE_TEMPLATE.html`](templates/STUDY_PAGE_TEMPLATE.html).
- Standard language for all `.md` files: **English**.

## Rules When Creating or Editing Skills
1. **Mandatory base:** scaffold new skills with [`scripts/new_skill.py`](scripts/new_skill.py) (`python scripts/new_skill.py <kebab-case-name>`) or copy [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) to `skills/<kebab-case-name>/SKILL.md`, and remove all HTML comments (`<!-- ... -->`).
2. **YAML frontmatter:** `name` must match the folder name in `kebab-case`. `description` must state **when to use** and include an explicit `DO NOT activate` boundary to prevent trigger overlap with other skills.
3. **Structure:** keep all 6 required sections from the template lean and concise (avoid bloating the context window).
4. **Offline study page output:** every skill must automatically generate a single-file offline `.html` companion (`<kebab-case-topic>-study.html`, using `templates/STUDY_PAGE_TEMPLATE.html` or a portable inline HTML5/CSS/Vanilla JS equivalent when installed outside the repo) with Active-Reveal Concept Cards (*"Think first, then reveal"*), 4–8 Flip Flashcards, and a Diagnostic Quiz (answers hidden until **"Check Answers"**), without spoiling chat turns prematurely.
5. **Mathematical & derived formulas (`.tex`):** whenever a lesson, quiz, flashcard, explanation, or study page requires mathematical, physical, chemical, or derived formulas, format them using **LaTeX (`.tex`) notation** (`$...$` inline and `$$...$$` display; in `STUDY_DATA`, double-escape backslashes inside JSON strings like `\\frac{a}{b}`, and keep `narration` in `lesson.json` spoken in plain words).
5. **Documentation:** when adding or removing a skill, script, or CI rule, update [`README.md`](README.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), and [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) to stay aligned with repository evolution.
6. **Portability:** do not rely on commands, MCPs, or tools exclusive to a single CLI or IDE inside skill instructions.

## Mandatory Validation
Before finishing any change or opening a PR, run:

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

This suite verifies repository structure, frontmatter (including the explicit `DO NOT activate` boundary), required sections, absence of leftover HTML comments, relative link integrity, activation prompt boundary alignment, and the validator unit tests (also enforced in CI by `.github/workflows/validate.yml`).

## Commits
- Use **Conventional Commits** (`feat(skill-name): ...`, `docs: ...`, `ci: ...`, `fix: ...`).
