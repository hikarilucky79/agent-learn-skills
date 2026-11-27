## Resumo
<!-- Descreva brevemente o que este PR adiciona, altera ou corrige. -->

## Tipo de Alteração
- [ ] Nova skill (`skills/<nome-em-kebab-case>/SKILL.md`)
- [ ] Melhoria em skill existente
- [ ] Documentação (`README.md`, `CONTRIBUTING.md`, `AGENTS.md`)
- [ ] CI / Ferramentas (`scripts/`, `.github/`)

## Checklist de Qualidade
- [ ] Li e segui as diretrizes de [`CONTRIBUTING.md`](../CONTRIBUTING.md) e [`AGENTS.md`](../AGENTS.md)
- [ ] A skill partiu de [`templates/SKILL_TEMPLATE.md`](../templates/SKILL_TEMPLATE.md) e não possui comentários HTML residuais
- [ ] O campo `name` no frontmatter é idêntico ao nome da pasta em `kebab-case`
- [ ] A `description` define claramente **quando usar** e **quando não usar**, sem conflito de gatilho
- [ ] O [`README.md`](../README.md) foi atualizado (se aplicável)
- [ ] Instaladores ([`scripts/install.sh`](../scripts/install.sh) / [`scripts/install.ps1`](../scripts/install.ps1)) testados (se aplicável)
- [ ] Commits seguem Conventional Commits
- [ ] Executei `python scripts/validate_skills.py` localmente e passou sem erros
