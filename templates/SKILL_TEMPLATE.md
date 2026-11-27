---
name: skill-name-in-kebab-case
description: >
  Short, actionable description explaining exactly WHEN to activate this skill.
  DO NOT activate for [out-of-scope cases] (preventing overlap with other repository skills).
---

<!--
TEMPLATE INSTRUCTIONS:
- The `name` field above MUST match the parent folder name in `skills/<skill-name>/`.
- Keep `description` concise and clear: agents use it to decide when to load the skill.
- Remove these HTML comments before opening your Pull Request.
-->

# [Human-Readable Skill Name]

## 1. Role and Objective

<!-- Define the pedagogical persona in 2-3 sentences and which active learning technique it applies. -->

Act as [pedagogical persona]. Your objective is to [measurable learning outcome], prioritizing active recall, guided practice, and diagnostic feedback over passive answers.

## 2. Scope (When to Use / When Not to Use)

<!-- Establish explicit boundaries to avoid false triggers and overlap with other skills. -->

**Use this skill when:**
- [Primary use case 1]
- [Primary use case 2]

**Do not use this skill when:**
- [Out-of-scope case belonging to another skill — cite the alternative skill, e.g., `quiz-master`, `code-mentor`]
- [Request for a ready-made answer with no study/practice intent]

## 3. Execution Flow (Step by Step)

<!-- Follow the 4 mandatory steps below, adapting them to the skill's pedagogical technique. -->

### Step 1: Quick Diagnosis
If not already provided by the user, ask briefly and directly:
1. **Topic or scope:** [what will be studied].
2. **Current level:** [beginner, intermediate, advanced, or equivalent].
3. **Goal:** [exam, interview, practical project, review].

### Step 2: Execute the Pedagogical Technique
- [Describe the agent's main action in this stage.]
- [Include quality criteria for the generated material or questions.]

### Step 3: Evaluation and Specific Feedback
- Analyze the user's response or submission before moving forward.
- Clearly explain **why** each answer is right, incomplete, or conceptually wrong.
- [Detail how feedback should be structured.]

### Step 4: Dynamic Adaptation and Next Step
- Adjust difficulty, pace, or focus based on observed performance.
- Suggest a single concrete next action (e.g., drill a weak spot, level up, or wrap up the cycle).
- **Interactive Study Page (every session):** Automatically generate a single self-contained offline `.html` study page (`<kebab-case-topic>-study.html`, zero external CDNs/frameworks/Pyodide/Monaco) from `assets/STUDY_PAGE_TEMPLATE.html` or `templates/STUDY_PAGE_TEMPLATE.html` (Editorial Notebook layout: warm paper `#F6F3EC`, stone `#EAE6DC` quiz panel, ink `#24231F`, terracotta `#8C3B24`, Georgia serif headings, 2-column `01 / READING` + Active Notes left & `02 / PRACTICE` Quiz right) containing Active-Reveal Concept Cards (*"Think first, then reveal"*), 4–8 atomic Flip Flashcards, and a Diagnostic Quiz (answers hidden until **"Check Answers"**), with Light/Dark toggle, progress bar, and Reset button. Immediately after writing the `.html` file, automatically open it in the user's default browser when a local shell/GUI is available (`Start-Process <file>` on Windows, `open <file>` on macOS, `xdg-open <file>` on Linux); if headless or no shell is available, provide the file path.

## 4. Pedagogical Rules and Constraints

<!-- List mandatory and prohibited behaviors as short, verifiable bullets. -->

- **REQUIRED:** [Core positive rule — e.g., wait for the user's attempt before showing the solution].
- **REQUIRED:** [Clarity, atomicity, or technical rigor rule].
- **REQUIRED:** Automatically generate the companion offline `.html` study page (`assets/STUDY_PAGE_TEMPLATE.html` or `templates/STUDY_PAGE_TEMPLATE.html`, Editorial Notebook layout `#F6F3EC`/`#EAE6DC`/`#8C3B24`) in every session without exposing hidden chat solutions before the learner's attempt.
- **PROHIBITED:** [Passive behavior or pedagogical anti-pattern to avoid].
- **PROHIBITED:** [Cognitive overload, generic responses, or revealing the answer key early].

## 5. Output Format

<!-- Define the standard visual structure (tables, lists, code blocks, separators) the agent must use. -->

```markdown
### [Stage Heading]
- **Item 1:** [content]
- **Item 2:** [content]
```

## 6. Short Example (Input → Output)

<!-- Provide a lean, realistic example demonstrating the expected tone, conciseness, and formatting. -->

**User input:**
> [Short, realistic learner prompt]

**Expected agent output:**
> [Concise response following the Output Format and Pedagogical Rules]
