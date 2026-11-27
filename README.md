# agent-learn-skills

An open-source repository of **Agent Skills for active learning** built on the `SKILL.md` standard. Designed to turn AI agents (CLIs and IDEs) into rigorous tutors that prioritize **guided practice, active recall, and diagnostic feedback** instead of passive answers.

---

## Value Proposition

- **Active learning first:** the agent requires an attempt, explanation, or debugging step before revealing ready-made answers.
- **Modularity:** each skill executes a single pedagogical method with clear boundaries and zero trigger overlap.
- **Lean context:** concise, actionable instructions that save model context window.
- **Portability:** compatible with modern `SKILL.md`-based agents (Claude Code, Codex CLI, Cursor, OpenCode, Antigravity, and others).

---

## Skills Catalog (MVP)

| Skill | Pedagogical Technique | When to Use | Example Prompt |
|---|---|---|---|
| [`quiz-master`](skills/quiz-master/SKILL.md) | Active Recall with realistic distractors | Mock exams, quizzes, certifications, and code analysis | *"Give me a 5-question quiz on JS Event Loop, Junior level."* |
| [`flashcards-srs`](skills/flashcards-srs/SKILL.md) | Atomicity and Spaced Repetition (Anki/SRS) | Building Q&A or Cloze Deletion decks with CSV export | *"Create 8 atomic flashcards on SQL indexes and export as CSV."* |
| [`feynman-tutor`](skills/feynman-tutor/SKILL.md) | Feynman Technique and Socratic questioning | Validating deep understanding by explaining in your own words | *"I want to study REST Idempotency using Feynman; here is my explanation..."* |
| [`code-mentor`](skills/code-mentor/SKILL.md) | Pair programming and 3-level progressive hints | Guided debugging, refactoring, and educational code review | *"My Python function returns None instead of the sum; give me hints without rewriting everything."* |
| [`study-roadmap`](skills/study-roadmap/SKILL.md) | Project-oriented instructional design | Planning study tracks with deadlines, milestones, and checkpoints | *"Build a 4-week SQL roadmap (6h/week, beginner level)."* |

---

## Installation & Usage

### Quick Install (Recommended)

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
```

**Windows PowerShell ([`scripts/install.ps1`](scripts/install.ps1)):**
```powershell
git clone https://github.com/hikarilucky79/agent-learn-skills.git
cd agent-learn-skills

# Install all skills by copy (default: -Agent claude -Scope global)
.\scripts\install.ps1 -Agent claude -Scope global

# Install specific skills in the current project
.\scripts\install.ps1 -Agent cursor -Scope project -Skill quiz-master,code-mentor
```

> **Tip:** use `--copy` (`install.sh`) or `-Symlink` (`install.ps1`) to invert the default mode, and `--force` / `-Force` to overwrite existing skills.

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

1. Copy the official template [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) to `skills/<kebab-case-name>/SKILL.md`.
2. Ensure the `name:` field in the YAML frontmatter matches the folder name exactly.
3. Define clear boundaries in `description` (when to activate and an explicit `DO NOT activate` clause) to avoid conflicting with existing skills.
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
│   └── validate_skills.py
├── templates/
│   └── SKILL_TEMPLATE.md
├── tests/
│   ├── activation_prompts.md
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
    └── study-roadmap/
        └── SKILL.md
```

---

## License

Distributed under the [MIT](LICENSE) License.
