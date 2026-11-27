# Activation Test Prompts (Manual Evals)

Use these prompts to verify that the agent selects the right skill without trigger overlap across catalog `description` fields.

| Test Prompt | Expected Skill | Must Not Activate | Success Criteria |
|---|---|---|---|
| *"Give me a 5-question quiz on JS Event Loop, Junior level."* | `quiz-master` | `flashcards-srs`, `feynman-tutor` | Generates questions with plausible distractors, **hides the answer key** in chat, and generates an offline `<topic>-study.html` companion page. |
| *"Turn this SQL indexes summary into 6 flashcards with Cloze and Anki CSV."* | `flashcards-srs` | `quiz-master` | Generates atomic cards (1 concept/card) with `{{c1::...}}`, valid CSV output, and an offline `<topic>-study.html` companion page. |
| *"I want to test if I understand REST Idempotency using Feynman; here is my explanation..."* | `feynman-tutor` | `quiz-master`, `code-mentor` | Identifies gaps/jargon, asks Socratic questions first, and generates an offline `<topic>-study.html` page upon synthesis. |
| *"My Python function returns `None` instead of the sum; help me find the bug without rewriting everything."* | `code-mentor` | `feynman-tutor`, `quiz-master` | Starts at **Level 1** without giving away the fix and generates an offline `<topic>-study.html` page after the debugging/review cycle. |
| *"I have 6h/week for 4 weeks to study SQL for interviews; build me a roadmap."* | `study-roadmap` | `quiz-master`, `flashcards-srs` | Delivers progressive phases with mini-projects, completion criteria, and an offline Phase 1 `<topic>-study.html` study page. |
| *"Run a mid-level backend mock interview on caching strategies."* | `mock-interview` | `quiz-master`, `code-mentor`, `study-roadmap` | Presents **one realistic question at a time**, probes claims dynamically, scores via rubric, and generates an offline `<topic>-study.html` page upon debrief. |
| *"Let's practice B1 English via reverse translation for daily engineering standups (Portuguese to English)."* | `idiom-coach` | `flashcards-srs`, `quiz-master`, `feynman-tutor` | Gives reference-language prompts hiding target phrasing, provides surgical inline corrections, and generates an offline `<topic>-study.html` study page. |
| *"Help me actively read this `stale-while-revalidate` HTTP spec excerpt before summarizing it: [excerpt]."* | `docs-deconstructor` | `feynman-tutor`, `flashcards-srs`, `quiz-master` | Withholds upfront summary behind prediction/invariant checkpoints and generates an offline `<topic>-study.html` page upon unlocking synthesis. |
| *"I just fixed a duplicate-job bug with `FOR UPDATE SKIP LOCKED` after wrongly blaming Redis drops; help me run a postmortem."* | `debug-postmortem` | `code-mentor`, `mock-interview`, `feynman-tutor` | Probes false hypothesis, root cause, and automated prevention before locking the postmortem and generating an offline `<topic>-study.html` page. |
| *"Just give me the ready answer to this SQL exercise without explaining anything."* | *(No study skill / pedagogical refusal)* | `quiz-master`, `code-mentor` | Must not trigger passive tutoring or hand out answers without an attempt when active study is expected. |
