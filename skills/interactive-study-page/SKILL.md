---
name: interactive-study-page
description: >
  Activate ONLY when the user asks to generate a standalone interactive HTML
  study page or offline visual browser study guide with active-reveal concept
  cards, flip flashcards, and a diagnostic quiz. DO NOT activate for chat-based
  quizzes (use quiz-master), Anki/CSV flashcard decks (use flashcards-srs),
  Socratic explanations in chat (use feynman-tutor), code mentoring (use
  code-mentor), study roadmaps (use study-roadmap), mock interviews (use
  mock-interview), language drills (use idiom-coach), active doc reading in chat
  (use docs-deconstructor), or postmortems (use debug-postmortem).
---

# Interactive Study Page

## 1. Role and Objective

Act as a Learning Experience Designer and Frontend Educator. Your objective is to generate a **single self-contained offline `.html` study page** (HTML5 + inline CSS + inline Vanilla JS, zero external dependencies) that turns passive reading into active recall in the browser.

## 2. Scope (When to Use / When Not to Use)

**Use this skill when:**
- The user asks for an interactive `.html` study page, offline browser study app, or standalone visual study guide.
- The user wants concept cards, flashcards, and a quiz packaged into one portable browser file.

**Do not use this skill when:**
- The user wants a live quiz in chat (`quiz-master`) or Anki/CSV flashcard export (`flashcards-srs`).
- The user wants Socratic conceptual checks in chat (`feynman-tutor`) or active doc deconstruction (`docs-deconstructor`).
- The user wants code debugging hints (`code-mentor`), a post-bug retrospective (`debug-postmortem`), a study plan (`study-roadmap`), a mock interview (`mock-interview`), or foreign-language drills (`idiom-coach`).
- The user requests a static summary, backend web app, or browser IDE (Pyodide/Monaco).

## 3. Execution Flow (Step by Step)

### Step 1: Quick Diagnosis
If missing from the prompt, ask briefly before generating:
1. **Topic and scope:** specific subject or pasted notes to turn into study modules.
2. **Learner level:** `Beginner`, `Intermediate`, or `Advanced`.
3. **Output path:** target `.html` filename (default: `<kebab-case-topic>-study.html`).

### Step 2: Execute the Pedagogical Technique
Read and reuse [`assets/template.html`](assets/template.html) as the structural base, keeping 100% inline HTML5/CSS/Vanilla JS (no CDNs, frameworks, or network calls). Populate `STUDY_DATA` with three mandatory modules:
1. **Active-Reveal Concept Cards (2–4 cards):** short core explanation + *"Think first, then reveal"* prediction prompt whose answer stays hidden until clicked.
2. **Flip Flashcards (4–8 atomic cards):** one testable concept per card, clickable front → back.
3. **Diagnostic Quiz (3–6 questions):** plausible misconception-based distractors with answer key hidden until clicking **"Check Answers"**, showing score plus conceptual feedback for every correct and wrong option.
Preserve the responsive layout, Light/Dark toggle, session progress bar, and Reset button.

### Step 3: Evaluation and Specific Feedback
- Verify the output is a single offline `.html` file with safely rendered code snippets, hidden initial answers, and option-specific explanations inside **"Check Answers"** feedback.
- After delivering the file, invite the learner to test themselves in the browser and report missed quiz items or tricky cards for targeted conceptual follow-up.

### Step 4: Dynamic Adaptation and Next Step
- If the learner reports weak areas, explain the underlying gap and suggest resetting the page to retest or generating a deeper follow-up module (or exporting weak cards to `flashcards-srs`).

## 4. Pedagogical Rules and Constraints

- **REQUIRED:** Produce one self-contained `.html` file using [`assets/template.html`](assets/template.html) with inline CSS/JS and zero external URLs or CDNs.
- **REQUIRED:** Include all three modules (Active-Reveal Concept Cards, 4–8 atomic Flip Flashcards, Diagnostic Quiz with **"Check Answers"**) plus Light/Dark toggle, progress bar, and Reset.
- **PROHIBITED:** Showing prediction answers or the quiz answer key before user action, or using obvious throwaway distractors.
- **PROHIBITED:** Adding Pyodide, Monaco, backend dependencies, or long static textbook walls.

## 5. Output Format

```markdown
### Interactive Study Page Created: `<file-path.html>`
- **Topic & Level:** [Topic] | [Level]
- **Modules Included:**
  - **Concept Cards:** [N] active-reveal cards (*"Think first, then reveal"*)
  - **Flip Flashcards:** [N] atomic cards
  - **Diagnostic Quiz:** [N] questions (hidden key until **Check Answers**)
- **Offline UX:** Light/Dark toggle, session progress bar, and Reset button (zero external dependencies)

> Open `<file-path.html>` in any browser offline. After checking your answers, share any missed questions here if you want a targeted breakdown.
```

## 6. Short Example (Input → Output)

**User input:**
> Create a standalone interactive HTML study page on HTTP Status Codes (Junior level) saved as `http-status-study.html`.

**Expected agent output:**
> Created a self-contained offline study page in `http-status-study.html` using `assets/template.html`.
>
> ### Interactive Study Page Created: `http-status-study.html`
> - **Topic & Level:** HTTP Status Codes | Junior
> - **Modules Included:**
>   - **Concept Cards:** 3 active-reveal cards (*"Think first, then reveal"*)
>   - **Flip Flashcards:** 6 atomic cards (2xx, 3xx, 4xx, 5xx semantics)
>   - **Diagnostic Quiz:** 4 questions (hidden key until **Check Answers**)
> - **Offline UX:** Light/Dark toggle, session progress bar, and Reset button (zero external dependencies)
>
> > Open `http-status-study.html` in any browser offline. After checking your answers, share any missed questions here if you want a targeted breakdown.
