# Contribuindo para o `learn-skills`

Obrigado pelo interesse em expandir este catálogo de Agent Skills para aprendizagem ativa. Este guia define os padrões técnicos e pedagógicos para manter o repositório consistente, enxuto e portátil.

---

## 1. Padrões de Nomenclatura e Estrutura

- **Nome da pasta e da skill:** use obrigatoriamente `kebab-case` (apenas letras minúsculas, números e hífens), por exemplo: `skills/socratic-debugger/SKILL.md`.
- **Correspondência exata:** o campo `name:` no frontmatter YAML deve ser **idêntico** ao nome do diretório pai.
- **Idioma:** Português do Brasil (PT-BR), mantendo termos técnicos consolidados em inglês quando natural (ex.: *Active Recall*, *Cloze Deletion*, *Symlink*, *Event Loop*).
- **Base obrigatória:** toda nova skill deve partir de [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) e conter todas as 6 seções obrigatórias.

---

## 2. Diretrizes de Design Instrucional

1. **Uma skill, um método:** cada skill deve resolver uma única técnica pedagógica com excelência (ex.: quizzes, flashcards, Feynman, mentoria de código, roadmap). Evite skills "faz-tudo".
2. **Sem sobreposição de gatilhos:** antes de propor uma skill, verifique as `description` das skills existentes em `skills/`. Deixe explícito no campo `description` e na seção **Escopo** quando *usar* e quando *não usar* (apontando a skill vizinha correta).
3. **Contexto enxuto:** escreva instruções diretas e acionáveis. Evite introduções longas, repetições ou exemplos extensos que desperdicem a janela de contexto do modelo.
4. **Aprendizagem ativa acima de tudo:** a skill deve sempre exigir esforço cognitivo do estudante (tentativa, explicação, depuração, escolha) antes de entregar respostas prontas ou gabaritos.
5. **Portabilidade:** não dependa de ferramentas, comandos ou APIs exclusivas de uma única CLI ou IDE. As instruções devem funcionar em qualquer agente compatível com `SKILL.md`.

---

## 3. Fluxo de Contribuição

1. Faça um fork do repositório e crie uma branch descritiva:
   ```bash
   git checkout -b feat/skill-nome-da-skill
   ```
2. Copie o template oficial:
   ```bash
   mkdir -p skills/nome-da-skill
   cp templates/SKILL_TEMPLATE.md skills/nome-da-skill/SKILL.md
   ```
3. Preencha o `SKILL.md` removendo todos os comentários HTML de instrução.
4. Atualize a tabela de catálogo no `README.md` mantendo a ordem e os links relativos válidos.
5. Execute o validador automático e confira o checklist abaixo antes de abrir o Pull Request:
   ```bash
   python scripts/validate_skills.py
   ```

---

## 4. Checklist de Qualidade para Pull Requests

- [ ] `python scripts/validate_skills.py` executado sem erros.
- [ ] A pasta está em `skills/<nome-em-kebab-case>/SKILL.md`.
- [ ] O frontmatter YAML é válido e `name` coincide exatamente com o nome da pasta.
- [ ] A `description` define claramente **quando ativar** e **quando não ativar**, sem conflitar com outras skills.
- [ ] Todas as 6 seções obrigatórias do template estão presentes e preenchidas sem comentários residuais.
- [ ] O fluxo inclui diagnóstico rápido, prática ativa, feedback explicativo e adaptação dinâmica.
- [ ] Há um exemplo curto (`Input → Output`) fiel ao formato de saída especificado.
- [ ] O `README.md` foi atualizado com a nova skill e todos os links relativos funcionam.
- [ ] O texto está em PT-BR claro, técnico e sem preenchimento genérico.

---

## 5. Código de Conduta

Ao participar deste projeto, você concorda em seguir o [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Para agentes de IA que operam neste repositório, consulte também [`AGENTS.md`](AGENTS.md).
