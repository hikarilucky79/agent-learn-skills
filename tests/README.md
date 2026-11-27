# Test Suite & Verification Outputs

This directory contains automated unit/integration tests and manual activation evals for `agent-learn-skills`.

---

## 1. Test Files

| File | Coverage |
|---|---|
| [`test_validate_skills.py`](test_validate_skills.py) | YAML frontmatter parsing, `kebab-case` naming, 6 required sections, `DO NOT activate` boundary enforcement, and relative Markdown link checks. |
| [`test_validate_anki_csv.py`](test_validate_anki_csv.py) | Anki CSV/TXT export validation (`#separator:`, UTF-8 BOM, Q&A rows, Cloze `{{c1::...}}` syntax, and error cases). |
| [`test_installers.py`](test_installers.py) | Cross-platform installer and uninstaller behavior for `scripts/install.sh` and `scripts/install.ps1` (global/project scopes, flags, symlink/junction safety). |
| [`test_new_skill.py`](test_new_skill.py) | `scripts/new_skill.py` scaffolding CLI, template parsing, comment stripping, and path-traversal/invalid-name rejection. |
| [`test_activation_prompts.py`](test_activation_prompts.py) | Verifies every catalog skill has a positive activation prompt and reciprocal `Must Not Activate` boundaries in [`activation_prompts.md`](activation_prompts.md). |
| [`activation_prompts.md`](activation_prompts.md) | Human-readable eval matrix for testing real agent routing without trigger overlap. |

---

## 2. How to Run

```bash
# Structural, frontmatter, and link validation
python scripts/validate_skills.py

# Full unit & integration test suite
python -m unittest discover -s tests -v
```

---

## 3. Observed Test Outputs

### 3.1. `python scripts/validate_skills.py`

```text
OK: 9 skills, template e links validados sem erros.
```

### 3.2. `python -m unittest discover -s tests -v`

```text
test_every_catalog_skill_has_a_positive_activation_prompt (test_activation_prompts.TestActivationPrompts.test_every_catalog_skill_has_a_positive_activation_prompt) ... ok
test_must_not_activate_boundaries_exist_and_are_reciprocal (test_activation_prompts.TestActivationPrompts.test_must_not_activate_boundaries_exist_and_are_reciprocal) ... ok
test_table_has_entries_without_duplicate_prompts (test_activation_prompts.TestActivationPrompts.test_table_has_entries_without_duplicate_prompts) ... ok
test_conflicting_flags_and_invalid_skill_rejected (test_installers.TestInstallPs1.test_conflicting_flags_and_invalid_skill_rejected) ... ok
test_copy_install_and_selective_or_full_uninstall (test_installers.TestInstallPs1.test_copy_install_and_selective_or_full_uninstall) ... ok
test_project_scope_install_and_uninstall (test_installers.TestInstallPs1.test_project_scope_install_and_uninstall) ... ok
test_reparse_point_junction_uninstall_safety (test_installers.TestInstallPs1.test_reparse_point_junction_uninstall_safety) ... ok
test_copy_install_and_selective_or_full_uninstall (test_installers.TestInstallSh.test_copy_install_and_selective_or_full_uninstall) ... ok
test_help_and_conflicting_flags (test_installers.TestInstallSh.test_help_and_conflicting_flags) ... ok
test_invalid_skill_name_rejected_before_uninstall (test_installers.TestInstallSh.test_invalid_skill_name_rejected_before_uninstall) ... ok
test_project_scope_install_and_uninstall (test_installers.TestInstallSh.test_project_scope_install_and_uninstall) ... ok
test_symlink_uninstall_and_external_symlink_protection (test_installers.TestInstallSh.test_symlink_uninstall_and_external_symlink_protection) ... skipped 'Platform/shell ln -s created a copy instead of symlink'
test_cli_help_executes_successfully (test_new_skill.TestNewSkillScaffolding.test_cli_help_executes_successfully) ... ok
test_creates_skill_with_prefilled_name_and_default_title (test_new_skill.TestNewSkillScaffolding.test_creates_skill_with_prefilled_name_and_default_title) ... ok
test_custom_title_and_strip_comments_passes_skill_validator (test_new_skill.TestNewSkillScaffolding.test_custom_title_and_strip_comments_passes_skill_validator) ... ok
test_existing_skill_requires_force_to_overwrite (test_new_skill.TestNewSkillScaffolding.test_existing_skill_requires_force_to_overwrite) ... ok
test_rejects_invalid_names_and_path_traversal (test_new_skill.TestNewSkillScaffolding.test_rejects_invalid_names_and_path_traversal) ... ok
test_rejects_invalid_title_and_missing_or_malformed_template (test_new_skill.TestNewSkillScaffolding.test_rejects_invalid_title_and_missing_or_malformed_template) ... ok
test_main_missing_file_returns_one (test_validate_anki_csv.TestValidateAnkiCli.test_main_missing_file_returns_one) ... ok
test_subprocess_valid_and_invalid_files (test_validate_anki_csv.TestValidateAnkiCli.test_subprocess_valid_and_invalid_files) ... ok
test_row_and_card_validation_errors (test_validate_anki_csv.TestValidateAnkiFile.test_row_and_card_validation_errors) ... ok
test_supported_separators_and_utf8_bom (test_validate_anki_csv.TestValidateAnkiFile.test_supported_separators_and_utf8_bom) ... ok
test_unknown_separator_and_empty_deck_fail (test_validate_anki_csv.TestValidateAnkiFile.test_unknown_separator_and_empty_deck_fail) ... ok
test_valid_mixed_semicolon_deck_with_headers_and_blank_lines (test_validate_anki_csv.TestValidateAnkiFile.test_valid_mixed_semicolon_deck_with_headers_and_blank_lines) ... ok
test_malformed_and_invalid_cloze_cases (test_validate_anki_csv.TestValidateCloze.test_malformed_and_invalid_cloze_cases) ... ok
test_plain_qa_front_returns_false_without_errors (test_validate_anki_csv.TestValidateCloze.test_plain_qa_front_returns_false_without_errors) ... ok
test_valid_single_hint_and_multiple_clozes (test_validate_anki_csv.TestValidateCloze.test_valid_single_hint_and_multiple_clozes) ... ok
test_empty_block_scalar_description_is_rejected (test_validate_skills.TestParseFrontmatter.test_empty_block_scalar_description_is_rejected) ... ok
test_missing_frontmatter_and_fields (test_validate_skills.TestParseFrontmatter.test_missing_frontmatter_and_fields) ... ok
test_valid_inline_and_multiline_descriptions (test_validate_skills.TestParseFrontmatter.test_valid_inline_and_multiline_descriptions) ... ok
test_actual_repository_passes_cli (test_validate_skills.TestRepositoryValidation.test_actual_repository_passes_cli) ... ok
test_duplicate_skill_name_and_missing_skill_md_fail (test_validate_skills.TestRepositoryValidation.test_duplicate_skill_name_and_missing_skill_md_fail) ... ok
test_empty_skills_dir_and_bad_folder_name_fail (test_validate_skills.TestRepositoryValidation.test_empty_skills_dir_and_bad_folder_name_fail) ... ok
test_missing_root_file_or_unlinked_skill_fails (test_validate_skills.TestRepositoryValidation.test_missing_root_file_or_unlinked_skill_fails) ... ok
test_valid_isolated_repository_passes (test_validate_skills.TestRepositoryValidation.test_valid_isolated_repository_passes) ... ok
test_valid_external_and_broken_links (test_validate_skills.TestValidateMarkdownLinks.test_valid_external_and_broken_links) ... ok
test_missing_negative_boundary_fails (test_validate_skills.TestValidateSkillFile.test_missing_negative_boundary_fails) ... ok
test_name_folder_comments_and_sections_validation (test_validate_skills.TestValidateSkillFile.test_name_folder_comments_and_sections_validation) ... ok
test_template_requires_negative_boundary_but_allows_comments_and_name (test_validate_skills.TestValidateSkillFile.test_template_requires_negative_boundary_but_allows_comments_and_name) ... ok
test_valid_skill_passes_with_negative_boundary (test_validate_skills.TestValidateSkillFile.test_valid_skill_passes_with_negative_boundary) ... ok

----------------------------------------------------------------------
Ran 40 tests in 5.788s

OK (skipped=1)
```

> **Note:** On Windows Git Bash, `test_symlink_uninstall_and_external_symlink_protection` is skipped when `ln -s` falls back to copying rather than creating a native symlink. On Linux/macOS CI (`ubuntu-latest`), all 40 tests execute.

---

## 4. End-to-End Agent Behavioral Verification (Multi-Turn Client-Tutor)

All 9 skills + 1 negative boundary scenario were tested in 2-turn conversations with independent Tutor agents (without naming skills in the user prompt):

| Scenario | Target Skill | Result | Verified Behavior |
|---|---|---|---|
| 1 | `quiz-master` | PASS | Generates questions with plausible distractors and hides the answer key until submission. |
| 2 | `flashcards-srs` | PASS | Enforces atomicity (1 concept/card) with valid Cloze `{{c1::...}}` and Anki CSV export. |
| 3 | `feynman-tutor` | PASS | Flags unexplained jargon/gaps and asks Socratic questions before the final synthesis. |
| 4 | `code-mentor` | PASS | Progresses from Hint Level 1 → Level 2 without rewriting the whole file. |
| 5 | `study-roadmap` | PASS | Structures phases with prerequisites, mini-projects, and objective completion criteria. |
| 6 | `mock-interview` | PASS | Challenges superficial buzzwords with dynamic follow-up probes and rubric scoring. |
| 7 | `idiom-coach` | PASS | Applies surgical inline corrections in short layers without long grammar lectures. |
| 8 | `docs-deconstructor` | PASS | Requires active prediction/invariant extraction and corrects misconceptions before summarizing. |
| 9 | `debug-postmortem` | PASS | Rejects vague root causes (*"I forgot"* / *"be more careful"*) and enforces systemic prevention. |
| 10 | *(Negative boundary)* | PASS | Direct-answer requests with no study/mentoring intent trigger **zero** `SKILL.md` reads. |
