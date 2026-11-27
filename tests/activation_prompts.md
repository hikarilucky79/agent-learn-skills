# Activation Test Prompts (Manual Evals)

Use these prompts to verify that the agent selects the right skill without trigger overlap across catalog `description` fields.

| Test Prompt | Expected Skill | Must Not Activate | Success Criteria |
|---|---|---|---|
| *"Give me a 5-question quiz on JS Event Loop, Junior level."* | `quiz-master` | `flashcards-srs`, `feynman-tutor` | Generates questions with plausible distractors and **hides the answer key**. |
| *"Turn this SQL indexes summary into 6 flashcards with Cloze and Anki CSV."* | `flashcards-srs` | `quiz-master` | Generates atomic cards (1 concept/card) with `{{c1::...}}` and valid CSV output. |
| *"I want to test if I understand REST Idempotency using Feynman; here is my explanation..."* | `feynman-tutor` | `quiz-master`, `code-mentor` | Identifies gaps/jargon and asks Socratic questions before the final summary. |
| *"My Python function returns `None` instead of the sum; help me find the bug without rewriting everything."* | `code-mentor` | `feynman-tutor`, `quiz-master` | Starts at **Level 1** (points to the area/concept without giving away the fix). |
| *"I have 6h/week for 4 weeks to study SQL for interviews; build me a roadmap."* | `study-roadmap` | `quiz-master`, `flashcards-srs` | Delivers progressive phases with mini-projects and objective completion criteria. |
| *"Just give me the ready answer to this SQL exercise without explaining anything."* | *(No study skill / pedagogical refusal)* | `quiz-master`, `code-mentor` | Must not trigger passive tutoring or hand out answers without an attempt when active study is expected. |
