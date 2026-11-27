## Summary
<!-- Briefly describe what this PR adds, changes, or fixes. -->

## Change Type
- [ ] New skill (`skills/<kebab-case-name>/SKILL.md`)
- [ ] Improvement to an existing skill
- [ ] Documentation (`README.md`, `CONTRIBUTING.md`, `AGENTS.md`)
- [ ] CI / Tooling (`scripts/`, `.github/`)

## Quality Checklist
- [ ] I have read and followed [`CONTRIBUTING.md`](../CONTRIBUTING.md) and [`AGENTS.md`](../AGENTS.md)
- [ ] The skill started from [`templates/SKILL_TEMPLATE.md`](../templates/SKILL_TEMPLATE.md) and has no leftover HTML comments
- [ ] The `name` field in frontmatter matches the `kebab-case` folder name
- [ ] `description` clearly defines **when to use** and **when not to use**, with no trigger conflicts
- [ ] [`README.md`](../README.md) has been updated (if applicable)
- [ ] Installers ([`scripts/install.sh`](../scripts/install.sh) / [`scripts/install.ps1`](../scripts/install.ps1)) tested (if applicable)
- [ ] Commits follow Conventional Commits
- [ ] Ran `python scripts/validate_skills.py` locally with zero errors
