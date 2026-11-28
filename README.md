# agent-learn-skills

[![Validate Skills](https://github.com/hikarilucky79/agent-learn-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/hikarilucky79/agent-learn-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

An open-source repository of **Agent Skills for active learning** built on the `SKILL.md` standard. Designed to turn AI agents (CLIs and IDEs) into rigorous tutors that prioritize **guided practice, active recall, and diagnostic feedback** instead of passive answers.

---

## Value Proposition

- **Active learning first:** the agent requires an attempt, explanation, or debugging step before revealing ready-made answers.
- **Offline interactive study page in every skill:** every skill automatically generates a single-file offline `.html` study page (`templates/STUDY_PAGE_TEMPLATE.html`) with active-reveal concept cards (*"Think first, then reveal"*), 4–8 flip flashcards, and a diagnostic quiz (hidden key until **Check Answers**), plus Light/Dark toggle, progress bar, and Reset.
- **Modularity:** each skill executes a single pedagogical method with clear boundaries and zero trigger overlap.
- **Lean context:** concise, actionable instructions that save model context window.
- **Portability:** compatible with modern `SKILL.md`-based agents (Claude Code, Codex CLI, Cursor, OpenCode, Antigravity, and others).

---

## Before vs. After

| Scenario | Default AI Agent | With `agent-learn-skills` |
|---|---|---|
| *"Why does my Python function return `None`?"* | Rewrites the entire function immediately, robbing you of the debugging step. | **`code-mentor` (Hint Level 1):** points to the last line and asks what happens when you `print()` instead of `return`. |
| *"Quiz me on JS Event Loop"* | Dumps questions with the answer key right below them. | **`quiz-master`:** presents plausible distractors, **hides the key**, and diagnoses misconceptions after your attempt. |
| *"Help me understand REST Idempotency"* | Outputs a generic 5-paragraph summary. | **`feynman-tutor`:** asks you to explain it first, flags jargon/gaps, and guides refinement with Socratic questions. |

---

## Skills Catalog

| Skill | Pedagogical Technique | When to Use | Example Prompt |
|---|---|---|---|
| [`quiz-master`](skills/quiz-master/SKILL.md) | Active Recall with realistic distractors | Mock exams, quizzes, certifications, and code analysis | *"Give me a 5-question quiz on JS Event Loop, Junior level."* |
| [`flashcards-srs`](skills/flashcards-srs/SKILL.md) | Atomicity and Spaced Repetition (Anki/SRS) | Building Q&A or Cloze Deletion decks with CSV export | *"Create 8 atomic flashcards on SQL indexes and export as CSV."* |
| [`feynman-tutor`](skills/feynman-tutor/SKILL.md) | Feynman Technique and Socratic questioning | Validating deep understanding by explaining in your own words | *"I want to study REST Idempotency using Feynman; here is my explanation..."* |
| [`code-mentor`](skills/code-mentor/SKILL.md) | Pair programming and 3-level progressive hints | Guided debugging, refactoring, and educational code review | *"My Python function returns None instead of the sum; give me hints without rewriting everything."* |
| [`study-roadmap`](skills/study-roadmap/SKILL.md) | Project-oriented instructional design | Planning study tracks with deadlines, milestones, and checkpoints | *"Build a 4-week SQL roadmap (6h/week, beginner level)."* |
| [`mock-interview`](skills/mock-interview/SKILL.md) | Simulated interviewing with dynamic follow-ups & rubric | Practicing technical, system design, or behavioral (STAR) interviews | *"Run a mid-level backend mock interview on caching strategies."* |
| [`idiom-coach`](skills/idiom-coach/SKILL.md) | Reverse translation, roleplay, and surgical correction | Active foreign-language production with targeted feedback | *"Let's practice B1 English via reverse translation for daily standups."* |
| [`docs-deconstructor`](skills/docs-deconstructor/SKILL.md) | Active reading and invariant extraction pre-summary | Dissecting dense docs, RFCs, or technical articles before summarizing | *"Help me actively read this HTTP caching excerpt before summarizing it."* |
| [`debug-postmortem`](skills/debug-postmortem/SKILL.md) | Blameless post-bug metacognitive retrospective | Analyzing false hypotheses, root cause, and systemic prevention after a fix | *"I fixed a duplicate-job bug after blaming Redis; help me run a postmortem."* |
| [`lesson`](skills/lesson/SKILL.md) | Unified active lesson + narrated MP4 video (`edge-tts` + Remotion) | Generating a full bundle: `.mp4` + `.srt` + embedded Editorial Notebook `.html` + Anki `.csv` | *"/lesson Event Loop in Node.js (intermediate, pt-BR, 16:9)"* |

---

## Installation & Usage

### 1-Command Package Install (`npx` or `pip`)

**Via npm / `npx` (Node.js 18+):**
```bash
# Install all 10 skills globally for Claude Code (default)
npx agent-learn-skills

# Target Cursor, Codex, OpenCode, or Antigravity
npx agent-learn-skills --agent cursor --scope global --force
```

**Via PyPI / `pip` (Python 3.10+):**
```bash
pip install agent-learn-skills
agent-learn-skills --agent claude --scope global

# Optional: include /lesson MP4 video pipeline dependencies
pip install "agent-learn-skills[video]"
```

### Quick Install (Local Clone)

Clone the repository and run the installer for your agent (`claude`, `cursor`, `codex`, `opencode`, or `antigravity`):

**Linux / macOS ([`scripts/install.sh`](scripts/install.sh)):**
```bash
git clone https://github.com/hikarilucky79/agent-learn-skills.git
cd agent-learn-skills
chmod +x scripts/install.sh

# Install all skills via symlink (default: --agent claude --scope global)
./scripts/install.sh --agent claude --scope global

# Install specific skills in the current project
./scripts/install.sh --agent cursor --scope project --skill quiz-master --skill code-mentor

# Uninstall repository skills from the target agent
./scripts/install.sh --uninstall --agent claude --scope global
```

**Windows PowerShell ([`scripts/install.ps1`](scripts/install.ps1)):**
```powershell
git clone https://github.com/hikarilucky79/agent-learn-skills.git
cd agent-learn-skills

# Install all skills by copy (default: -Agent claude -Scope global)
.\scripts\install.ps1 -Agent claude -Scope global

# Install specific skills in the current project
.\scripts\install.ps1 -Agent cursor -Scope project -Skill quiz-master,code-mentor

# Uninstall repository skills from the target agent
.\scripts\install.ps1 -Uninstall -Agent claude -Scope global
```

> **Tip:** use `--copy` (`install.sh`) or `-Symlink` (`install.ps1`) to invert the default mode, `--force` / `-Force` to overwrite existing skills (or remove external symlinks when uninstalling), and `--uninstall` / `-Uninstall` to remove installed repository skills.

### Manual Installation (Alternative)

```bash
# Example: manual symlink for Claude Code
mkdir -p ~/.claude/skills
for skill in skills/*; do
  ln -s "$(pwd)/$skill" ~/.claude/skills/"$(basename "$skill")"
done
```

---

## Creating a New Skill

1. Scaffold the new skill using [`scripts/new_skill.py`](scripts/new_skill.py) (which creates `skills/<kebab-case-name>/SKILL.md` from [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) with `name:` pre-filled):
   ```bash
   python scripts/new_skill.py <kebab-case-name>
   ```
2. Complete all 6 sections, define clear boundaries in `description` (when to activate and an explicit `DO NOT activate` clause) to avoid conflicting with existing skills, and remove all HTML comments (`<!-- ... -->`).
3. Add the new skill to the catalog above and run `python scripts/validate_skills.py` and `python -m unittest discover -s tests -v`.
4. Follow all guidelines and the checklist in [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Repository Structure

```text
agent-learn-skills/
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── AGENTS.md
├── LICENSE
├── scripts/
│   ├── install.ps1
│   ├── install.sh
│   ├── new_skill.py
│   └── validate_skills.py
├── templates/
│   ├── SKILL_TEMPLATE.md
│   └── STUDY_PAGE_TEMPLATE.html
├── tests/
│   ├── README.md
│   ├── activation_prompts.md
│   ├── test_activation_prompts.py
│   ├── test_installers.py
│   ├── test_new_skill.py
│   ├── test_study_page_template.py
│   ├── test_validate_anki_csv.py
│   └── test_validate_skills.py
└── skills/
    ├── quiz-master/
    │   └── SKILL.md
    ├── flashcards-srs/
    │   ├── SKILL.md
    │   └── scripts/
    │       └── validate_anki_csv.py
    ├── feynman-tutor/
    │   └── SKILL.md
    ├── code-mentor/
    │   └── SKILL.md
    ├── study-roadmap/
    │   └── SKILL.md
    ├── mock-interview/
    │   └── SKILL.md
    ├── idiom-coach/
    │   └── SKILL.md
    ├── docs-deconstructor/
    │   └── SKILL.md
    ├── debug-postmortem/
    │   └── SKILL.md
    └── lesson/
        ├── SKILL.md
        └── assets/
            └── STUDY_PAGE_TEMPLATE.html
```

### Video Lesson Pipeline (`/lesson` Prerequisites)

To render `.mp4` videos with the `lesson` skill, install Python (`edge-tts`, `jsonschema`, `mutagen`) and Remotion dependencies:

```bash
pip install -r requirements.txt
cd video && npm install
```

Render any validated `lesson.json` directly:

```bash
python scripts/validate_lesson.py examples/sample-lesson.json
python scripts/build_video.py examples/sample-lesson.json --out out/sample/sample.mp4
```

---

## Publishing (Maintainers)

```bash
# npm (npx agent-learn-skills)
npm publish --access public

# PyPI (pip install agent-learn-skills)
python -m build
twine upload dist/*
```

---

## License

Distributed under the [MIT](LICENSE) License.
