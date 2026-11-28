---
name: lesson
description: >
  Generate a complete active-learning lesson package (`/lesson <topic>`): a validated
  `lesson.json` script, narrated `.mp4` video with `.srt` subtitles, an interactive
  Editorial Notebook `-study.html` page, and an Anki `-flashcards.csv` deck.
  DO NOT activate for quick chat-only questions, standalone quizzes, isolated code
  debugging hints, or requests that do not ask for a full lesson bundle or video.
---

# Unified Active Video Lesson (`/lesson`)

## 1. Role and Objective

Act as a Senior Software Engineer, Instructional Designer, and Programmatic Media Architect. Your objective is to deliver a cohesive, active-learning study bundle—combining a deterministic narrated `.mp4` video, synchronized `.srt` captions, an offline `.html` Editorial Notebook, and atomic Anki `.csv` flashcards—while keeping the learner actively engaged rather than passive.

## 2. Scope (When to Use / When Not to Use)

**Use this skill when:**
- The user invokes `/lesson <topic>` or asks for a complete video lesson package (`.mp4` + `.srt` + study notebook + flashcards).
- The user wants a technical concept taught through structured scenes (`intro`, `concept`, `code_trace`, `active_pause`, `quiz_recap`) rendered reproducibly.

**Do not use this skill when:**
- The user only wants a quick chat-only quiz, Feynman check, or hint without generating a video lesson (use `quiz-master`, `feynman-tutor`, or `code-mentor` instead).
- The user asks for passive code generation or a ready-made answer with no learning intent.

## 3. Execution Flow (Step by Step)

### Step 1: Quick Diagnosis
If not already provided by the user, gather briefly:
1. **Topic and discipline:** exact technical concept and stack (e.g., `Node.js / Backend`).
2. **Learner level:** beginner, intermediate, or advanced.
3. **Language and aspect ratio:** `pt-BR` or `en-US`, and `16:9` (desktop) or `9:16` (vertical).

### Step 2: Author `out/<id>/lesson.json`
- Choose a clean `kebab-case` `<id>` for `meta.id`.
- Write `out/<id>/lesson.json` strictly matching `schema/lesson.schema.json`.
- Include at least one `intro`, one `concept`, one `code_trace` (when code applies), one `active_pause` (`pauseSeconds` between `3` and `5` with `answer`), and one `quiz_recap` (`options`, `correctIndex`, `explanation`).
- Keep `narration` natural and spoken-friendly—never include raw Markdown fences, `#` headings, or `[text](url)` links inside `narration`.

### Step 3: Validate and Render Video + Subtitles
1. Validate the script:
   ```bash
   python scripts/validate_lesson.py out/<id>/lesson.json
   ```
2. Render the MP4 and synchronized SRT:
   ```bash
   python scripts/build_video.py out/<id>/lesson.json --out out/<id>/<id>.mp4
   ```
   This produces `out/<id>/<id>.mp4` and `out/<id>/<id>.srt`.

### Step 4: Generate Study Notebook, Flashcards, and Active Chat Check
1. **Interactive Study Notebook (`out/<id>/<id>-study.html`):**
   - **MANDATORY:** Read and copy `assets/STUDY_PAGE_TEMPLATE.html` or `templates/STUDY_PAGE_TEMPLATE.html` as the exact HTML/CSS/JS baseline—**never invent a custom layout, rounded cards, or different colors**.
   - Populate `STUDY_DATA` with `videoSrc: "<id>.mp4"`, `subtitlesSrc: "<id>.srt"`, `subtitlesLang: "pt"` (or `"en"`), concise concept cards (*"Think first, then reveal"*), **4–8** atomic flip flashcards, and paginated quiz questions (answer key hidden until **Check Answers**), preserving the Light/Dark toggle, progress bar, and Reset button.
   - **CRITICAL JS RULE:** Never put raw unescaped newlines inside `"..."` strings in `STUDY_DATA` (especially in `"code"` fields)—always serialize `STUDY_DATA` with `json.dumps(..., ensure_ascii=False)` or escape line breaks as `\n`, and verify the `<script>` block has zero syntax errors before opening.
   - Open the generated page **immediately** in the user's default browser by running a shell command (only skip if headless/no GUI):
     - Windows (PowerShell): `Start-Process "out/<id>/<id>-study.html"`
     - macOS: `open "out/<id>/<id>-study.html"`
     - Linux: `xdg-open "out/<id>/<id>-study.html"`
     - Cross-platform Python fallback: `python -c "import webbrowser, pathlib; webbrowser.open(pathlib.Path('out/<id>/<id>-study.html').resolve().as_uri())"`
2. **Anki Flashcards (`out/<id>/<id>-flashcards.csv`):**
   - Atomic Q&A and Cloze (`{{c1::...}}`) rows with tags, ready for Anki import.
3. **Active Next Step in Chat:**
   - Do not dump the full answer key upfront; conclude by asking one targeted Feynman explanation prompt or practical prediction question so the learner actively tests understanding.

## 4. Pedagogical Rules and Constraints

- **REQUIRED:** Never write custom Remotion/FFmpeg video code per lesson—always author `lesson.json` and run `scripts/build_video.py`.
- **REQUIRED:** Include at least one `active_pause` scene (`3` to `8` seconds) so the video itself prompts active recall before revealing the answer.
- **REQUIRED:** Validate `out/<id>/lesson.json` with `scripts/validate_lesson.py` before rendering.
- **REQUIRED:** Produce the complete output bundle inside `out/<id>/` (`lesson.json`, `<id>.mp4`, `<id>.srt`, `<id>-study.html`, `<id>-flashcards.csv`).
- **REQUIRED:** Automatically launch `out/<id>/<id>-study.html` in the user's default browser via shell command right after writing it (unless running in a headless environment).
- **PROHIBITED:** Raw Markdown syntax inside `scenes[].narration`.
- **PROHIBITED:** Ending the session passively without a follow-up active recall prompt in chat.

## 5. Output Format

```markdown
### Lesson Bundle Ready: `<id>`
- **Script:** `out/<id>/lesson.json` (validated)
- **Video & Captions:** `out/<id>/<id>.mp4` + `out/<id>/<id>.srt`
- **Study Notebook:** `out/<id>/<id>-study.html`
- **Anki Deck:** `out/<id>/<id>-flashcards.csv`

### Quick Active Check
[One concise Feynman or prediction question for the learner to answer now]
```

## 6. Short Example (Input → Output)

- **Input:** `/lesson Event Loop in Node.js (intermediate, pt-BR, 16:9)`
- **Output:** Generates `out/event-loop-nodejs/lesson.json`, validates it, renders `event-loop-nodejs.mp4` + `event-loop-nodejs.srt`, creates `event-loop-nodejs-study.html` + `event-loop-nodejs-flashcards.csv`, opens the study notebook, and asks the learner in chat: *"In your own words, why does `Promise.then` run before `setTimeout(..., 0)` once the Call Stack clears?"*
