# Contributing to `agent-learn-skills`

Thank you for helping expand this catalog of Agent Skills for active learning. This guide defines the technical and pedagogical standards to keep the repository consistent, lean, and portable.

---

## 1. Naming and Structure Standards

- **Folder and skill name:** strictly use `kebab-case` (lowercase letters, numbers, and hyphens only), e.g., `skills/socratic-debugger/SKILL.md`.
- **Exact match:** the `name:` field in the YAML frontmatter must be **identical** to the parent directory name.
- **Language:** English across all `.md` documentation and skill definitions.
- **Mandatory base:** every new skill must start from [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) and include all 6 required sections.

---

## 2. Instructional Design Guidelines

1. **One skill, one method:** each skill must execute a single pedagogical technique with excellence (e.g., quizzes, flashcards, Feynman, code mentoring, roadmap). Avoid "do-everything" skills.
2. **No trigger overlap:** before proposing a skill, review the `description` fields of existing skills under `skills/`. State explicitly in `description` (using `DO NOT activate`) and in the **Scope** section when *to use* and when *not to use* (pointing to the right sibling skill).
3. **Lean context:** write direct, actionable instructions. Avoid long introductions, repetition, or bloated examples that waste the model's context window.
4. **Active learning above all:** the skill must always require cognitive effort from the learner (attempt, explanation, debugging, choice) before providing ready-made answers or solutions.
5. **Portability:** do not depend on tools, commands, or APIs exclusive to a single CLI or IDE. Instructions must work on any `SKILL.md`-compatible agent.

---

## 3. Contribution Workflow

1. To propose a new skill or report trigger conflicts, use the templates in `.github/ISSUE_TEMPLATE/`.
2. Fork the repository and create a descriptive branch using Conventional Commits:
   ```bash
   git checkout -b feat/skill-name
   ```
3. If adding a skill, scaffold it from the official template with [`scripts/new_skill.py`](scripts/new_skill.py) (or copy [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) manually):
   ```bash
   python scripts/new_skill.py skill-name
   ```
4. Fill out `SKILL.md` and remove all instructional HTML comments.
5. Update the catalog table and repository structure in `README.md`, keeping valid relative links.
6. Run the automated validator and unit tests (and test install/`--uninstall` flows in `scripts/` if you modified `scripts/` or `skills/` structure) before opening a Pull Request:
   ```bash
   python scripts/validate_skills.py
   python -m unittest discover -s tests -v
   ```
7. Use `.github/PULL_REQUEST_TEMPLATE.md` and check off verified items (`[x]`). The `main` branch requires the `Validate SKILL.md structure and links` CI check to pass.

---

## 4. Pull Request Quality Checklist

- [ ] `python scripts/validate_skills.py` and `python -m unittest discover -s tests -v` executed locally with zero errors.
- [ ] `Validate SKILL.md structure and links` CI check passed on the PR.
- [ ] Commits follow **Conventional Commits** (`feat(...)`, `docs(...)`, `ci(...)`, `fix(...)`).
- [ ] Folder path is `skills/<kebab-case-name>/SKILL.md` (for new skills).
- [ ] YAML frontmatter is valid and `name` matches the folder name exactly.
- [ ] `description` clearly defines **when to activate** and includes an explicit `DO NOT activate` boundary, without conflicting with other skills.
- [ ] All 6 required sections from the template are present and free of leftover HTML comments.
- [ ] Flow includes quick diagnosis, active practice, diagnostic feedback, and dynamic adaptation.
- [ ] Includes a short example (`Input → Output`) matching the specified output format.
- [ ] `README.md` is updated with the new skill/change and all relative links resolve.
- [ ] Installers (`scripts/install.sh` / `scripts/install.ps1`) tested when applicable.
- [ ] Writing is clear, technical, concise English without generic filler.

---

## 5. Code of Conduct

By participating in this project, you agree to follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). For AI agents operating on this repository, also see [`AGENTS.md`](AGENTS.md).
