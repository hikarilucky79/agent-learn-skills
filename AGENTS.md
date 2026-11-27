# AGENTS.md

Instruções para agentes de IA que editam ou mantêm este repositório (`agent-learn-skills`).

## Visão Geral
- Catálogo open-source de Agent Skills no padrão `SKILL.md` focado em **aprendizagem ativa** (*Active Recall*, SRS, Técnica Feynman, mentoria de código e roadmaps).
- Idioma padrão: **Português do Brasil (PT-BR)**, mantendo termos técnicos consolidados em inglês quando natural.

## Regras ao Criar ou Editar Skills
1. **Base obrigatória:** copie [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) para `skills/<nome-em-kebab-case>/SKILL.md` e remova todos os comentários HTML (`<!-- ... -->`).
2. **Frontmatter YAML:** o campo `name` deve ser idêntico ao nome da pasta em `kebab-case`. A `description` deve explicitar **quando usar** e **quando não usar** para evitar conflito de gatilho com outras skills.
3. **Estrutura:** mantenha as 6 seções obrigatórias do template de forma enxuta (sem inflar a janela de contexto).
4. **Documentação:** ao adicionar ou remover uma skill, script ou regra de CI, atualize o [`README.md`](README.md), o [`CONTRIBUTING.md`](CONTRIBUTING.md) e o [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) conforme a evolução do projeto.
5. **Portabilidade:** não dependa de comandos, MCPs ou ferramentas exclusivas de uma única CLI ou IDE nas instruções das skills.

## Validação Obrigatória
Antes de finalizar qualquer alteração ou abrir PR, execute:

```bash
python scripts/validate_skills.py
```

O script verifica estrutura, frontmatter, seções obrigatórias, ausência de comentários residuais e integridade dos links relativos (também executado automaticamente no CI em `.github/workflows/validate.yml`).

## Commits
- Use **Conventional Commits** (`feat(nome-da-skill): ...`, `docs: ...`, `ci: ...`, `fix: ...`).
