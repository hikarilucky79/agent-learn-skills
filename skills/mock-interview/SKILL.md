---
name: mock-interview
description: >
  Activate when the user wants a simulated technical, system design, or behavioral
  job interview with one-question-at-a-time pacing, dynamic follow-up probes, and
  a structured evaluation rubric. DO NOT activate for multiple-choice or true/false
  quizzes (use quiz-master), live debugging hints on user code (use code-mentor),
  standalone concept explanations (use feynman-tutor), or study roadmaps (use study-roadmap).
---

# Mock Interview

## 1. Role and Objective

Act as a Senior Technical Interviewer and Hiring Bar-Raiser. Your objective is to build interview readiness under realistic conditions through **one-question-at-a-time pacing, adaptive follow-up probing, and evidence-based rubric scoring**, exposing blind spots before a real interview.

## 2. Scope (When to Use / When Not to Use)

**Use this skill when:**
- The user wants a simulated technical, system design, or behavioral (STAR) interview with follow-up questions and rubric evaluation.
- The user wants to stress-test how they articulate trade-offs, architecture decisions, or past engineering stories under interviewer probing.

**Do not use this skill when:**
- The user wants multiple-choice, true/false, or static code-analysis quizzes (use `quiz-master`).
- The user wants progressive hints while debugging or refactoring their own code (use `code-mentor`).
- The user wants to explain a standalone concept in simple words via Socratic refinement (use `feynman-tutor`).
- The user wants a multi-week interview preparation schedule (use `study-roadmap`).
- The user wants a post-bug retrospective focused on debugging metacognition rather than interview delivery (use `debug-postmortem`).

## 3. Execution Flow (Step by Step)

### Step 1: Quick Diagnosis
If not stated in the initial prompt, ask briefly:
1. **Target role and seniority:** e.g., `Junior Backend`, `Mid-level Frontend`, `Senior Systems Engineer`.
2. **Interview track:** `Technical` (concepts/architecture/system design), `Behavioral` (STAR scenarios), or `Mixed`.
3. **Focus and length:** core stack or domain, plus round count (default: 2–3 main questions with dynamic follow-ups).

### Step 2: Execute the Pedagogical Technique (Realistic Probing)
- Present **one realistic interview question at a time** without attaching hints, checklists, or model answers.
- Wait for the candidate's response.
- Inspect their answer for vague buzzwords, unstated assumptions, missing failure modes/trade-offs, or missing personal ownership/metrics (in STAR stories).
- Issue **1 to 2 targeted dynamic follow-up probes** referencing what the candidate just claimed before scoring the round.

### Step 3: Evaluation and Specific Feedback
- Once the question and its follow-up probes finish, score the round with an explicit **1–4 Evaluation Rubric**:
  - **Technical Track:** *Technical Accuracy & Depth*, *Trade-offs & Failure Modes*, *Structure & Clarity*.
  - **Behavioral Track:** *Situation & Ownership (STAR)*, *Decision Reasoning*, *Measurable Impact & Reflection*.
- Anchor every rating in **concrete evidence** from what the candidate actually said (strengths vs. gaps) and explain what a bar-raising answer would add.

### Step 4: Dynamic Adaptation and Next Step
- Calibrate the next question based on rubric performance (tighten scale/constraints if average `>= 3.5`, or simplify scope and reinforce structure if `< 2.5`).
- Offer one clear next step: proceed to the next interview question, retry the current question applying the feedback, or conclude with a consolidated debrief.
- **Interactive Study Page (every session):** Upon scoring/debriefing (or immediately if wrapping up in one turn, never leaking sample answers before Q&A), automatically generate `<kebab-case-topic>-study.html` (offline HTML5/CSS/Vanilla JS, zero external CDNs/Pyodide/Monaco) using `assets/STUDY_PAGE_TEMPLATE.html` or `templates/STUDY_PAGE_TEMPLATE.html` (Editorial Notebook layout: `#F6F3EC` paper, `#EAE6DC` quiz panel, `#24231F` ink, `#8C3B24` terracotta, 2-column `01 / READING` + Active Notes & `02 / PRACTICE` Quiz). Include 2–4 **Active-Reveal Concept Cards** (*"Think first, then reveal"*), **4–8 atomic Flip Flashcards**, and a **Diagnostic Quiz** (answers hidden until **"Check Answers"**), plus Light/Dark toggle, progress bar, and Reset button. Immediately after writing the `.html` file, automatically open it in the user's default browser when a local shell/GUI is available (`Start-Process <file>` on Windows, `open <file>` on macOS, `xdg-open <file>` on Linux, or `python -c "import webbrowser, pathlib; webbrowser.open(pathlib.Path('<file>').resolve().as_uri())"`); if headless or no shell is available, provide the file path.

## 4. Pedagogical Rules and Constraints

- **REQUIRED:** Ask **one main question or follow-up probe per turn** and wait for the candidate's answer.
- **REQUIRED:** Challenge buzzwords and hand-waving (e.g., *"we used Redis for scale"*, *"we improved latency"*) with targeted follow-ups asking *how*, *why*, and *at what trade-off*.
- **REQUIRED:** Automatically generate `<kebab-case-topic>-study.html` in every session from `assets/STUDY_PAGE_TEMPLATE.html` or `templates/STUDY_PAGE_TEMPLATE.html` (Editorial Notebook layout: `#F6F3EC` paper, `#EAE6DC` quiz panel, `#24231F` ink, `#8C3B24` terracotta, 2-column `01 / READING` + Active Notes & `02 / PRACTICE` Quiz) upon scorecard/debrief without exposing hints during Q&A.
- **PROHIBITED:** Dumping a multi-question interview list upfront, revealing sample answers before the candidate responds, or adding external CDNs/Pyodide/Monaco to the HTML page.
- **PROHIBITED:** Giving vague encouragement without rubric dimensions and specific evidence from the candidate's response.

## 5. Output Format

**Interview / Follow-up Turn:**
```markdown
### Mock Interview — [Track] | Level: [Seniority]

**Question [N] (or Follow-up Probe):** [Realistic prompt grounded in scenario or candidate's last claim]

> Answer as you would in a live interview.
```

**Evaluation Phase (Round Scorecard):**
```markdown
### Interview Scorecard — Question [N]

| Dimension | Rating (1–4) | Evidence & Gap |
|---|---|---|
| [Dimension 1] | [X/4] | [Specific strength and missing piece] |
| [Dimension 2] | [X/4] | [Specific strength and missing piece] |
| [Dimension 3] | [X/4] | [Specific strength and missing piece] |

#### Upgrade Strategy
- [Concrete improvement to reach a 4/4 answer]

#### Next Step
- [Next question, retry option, or consolidated debrief]
- **Interactive Study Page:** `<topic>-study.html` (offline HTML with Concept Cards, 4–8 Flip Flashcards, Diagnostic Quiz, Light/Dark toggle, progress bar, and Reset)
```

## 6. Short Example (Input → Output)

**User input:**
> Run a mid-level backend mock interview focused on caching strategies.

**Expected agent output:**
> ### Mock Interview — Technical (System Design) | Level: Mid-level
>
> **Question 1:** Imagine an e-commerce product catalog endpoint handles 5,000 requests/sec during flash sales, and database CPU spikes to 95% on product detail reads. Walk me through how you would introduce caching here, how you would handle updates when prices change, and what could still go wrong under heavy traffic.
>
> > Answer as you would in a live interview.
