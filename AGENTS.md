# AGENTS.md

Instructions for AI agents editing or maintaining this repository (`agent-learn-skills`).

## Overview
- Open-source catalog of `SKILL.md` Agent Skills focused on **active learning** (Active Recall, SRS, Feynman Technique, code mentoring, and study roadmaps).
- Standard language for all `.md` files: **English**.

## Rules When Creating or Editing Skills
1. **Mandatory base:** copy [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) to `skills/<kebab-case-name>/SKILL.md` and remove all HTML comments (`<!-- ... -->`).
2. **YAML frontmatter:** `name` must match the folder name in `kebab-case`. `description` must state **when to use** and include an explicit `DO NOT activate` boundary to prevent trigger overlap with other skills.
3. **Structure:** keep all 6 required sections from the template lean and concise (avoid bloating the context window).
4. **Documentation:** when adding or removing a skill, script, or CI rule, update [`README.md`](README.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), and [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) to stay aligned with repository evolution.
5. **Portability:** do not rely on commands, MCPs, or tools exclusive to a single CLI or IDE inside skill instructions.

## Mandatory Validation
Before finishing any change or opening a PR, run:

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

This suite verifies repository structure, frontmatter (including the explicit `DO NOT activate` boundary), required sections, absence of leftover HTML comments, relative link integrity, and the validator unit tests (also enforced in CI by `.github/workflows/validate.yml`).

## Commits
- Use **Conventional Commits** (`feat(skill-name): ...`, `docs: ...`, `ci: ...`, `fix: ...`).
