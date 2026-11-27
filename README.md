# learn-skills

Repositório open-source de **Agent Skills para aprendizagem ativa** no padrão `SKILL.md`. Projetado para transformar agentes de IA (CLIs e IDEs) em tutores rigorosos que priorizam **prática guiada, recuperação ativa (*Active Recall*) e feedback diagnóstico** em vez de respostas passivas.

---

## Proposta de Valor

- **Aprendizagem ativa primeiro:** o agente exige tentativa, explicação ou depuração antes de revelar respostas prontas.
- **Modularidade:** cada skill executa um único método pedagógico com fronteiras claras e sem sobreposição de gatilhos.
- **Contexto enxuto:** instruções diretas que economizam janela de contexto do modelo.
- **Portabilidade:** compatível com agentes modernos baseados em `SKILL.md` (Claude Code, Codex CLI, Cursor, OpenCode, Antigravity, entre outros).

---

## Catálogo de Skills (MVP)

| Skill | Técnica Pedagógica | Quando Usar | Exemplo de Prompt |
|---|---|---|---|
| [`quiz-master`](skills/quiz-master/SKILL.md) | *Active Recall* com distratores realistas | Simulados, provas, certificações e análise de código | *"Aplique um quiz de 5 questões sobre Event Loop em JS, nível Júnior."* |
| [`flashcards-srs`](skills/flashcards-srs/SKILL.md) | Atomicidade e Repetição Espaçada (Anki/SRS) | Criar baralhos P&R ou *Cloze Deletion* com exportação CSV | *"Crie 8 flashcards atômicos sobre índices em SQL e exporte em CSV."* |
| [`feynman-tutor`](skills/feynman-tutor/SKILL.md) | Técnica Feynman e questionamento socrático | Validar compreensão profunda explicando com suas palavras | *"Quero estudar Idempotência em REST usando Feynman; aqui vai minha explicação..."* |
| [`code-mentor`](skills/code-mentor/SKILL.md) | *Pair programming* e dicas em 3 níveis | Debugging guiado, refatoração e *code review* educativo | *"Minha função Python retorna None em vez da soma; me dê dicas sem reescrever tudo."* |
| [`study-roadmap`](skills/study-roadmap/SKILL.md) | Design instrucional orientado a projetos | Planejar trilhas de estudo com prazo, metas e checkpoints | *"Monte um roadmap de 4 semanas para SQL (6h/semana, nível iniciante)."* |

---

## Instalação e Uso

Clone o repositório e copie ou crie um *symlink* das pastas desejadas para o diretório de skills do seu agente.

### Linux / macOS (Symlink recomendado)

```bash
git clone https://github.com/<seu-usuario>/learn-skills.git

# Exemplo: instalar todas as skills globalmente (ajuste o destino para seu agente)
# Claude Code: ~/.claude/skills/ | Cursor: ~/.cursor/skills/ | Codex/OpenCode: ~/.agents/skills/
mkdir -p ~/.claude/skills
for skill in learn-skills/skills/*; do
  ln -s "$(pwd)/$skill" ~/.claude/skills/"$(basename "$skill")"
done
```

### Windows (PowerShell)

```powershell
git clone https://github.com/<seu-usuario>/learn-skills.git

# Copiar uma skill específica para o projeto atual ou diretório global do agente
Copy-Item -Recurse .\learn-skills\skills\quiz-master .\.agents\skills\quiz-master
```

> **Dica:** Para usar apenas em um projeto específico, copie ou faça *symlink* das pastas dentro do diretório de skills do próprio repositório (ex.: `.claude/skills/` ou `.cursor/skills/`).

---

## Como Criar uma Nova Skill

1. Copie o modelo oficial [`templates/SKILL_TEMPLATE.md`](templates/SKILL_TEMPLATE.md) para `skills/<nome-em-kebab-case>/SKILL.md`.
2. Garanta que o campo `name:` no frontmatter YAML seja idêntico ao nome da pasta.
3. Defina fronteiras claras na `description` (quando ativar e quando **não** ativar) para evitar conflito com as skills existentes.
4. Siga todas as diretrizes e o checklist em [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Estrutura do Repositório

```text
learn-skills/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── templates/
│   └── SKILL_TEMPLATE.md
└── skills/
    ├── quiz-master/
    │   └── SKILL.md
    ├── flashcards-srs/
    │   └── SKILL.md
    ├── feynman-tutor/
    │   └── SKILL.md
    ├── code-mentor/
    │   └── SKILL.md
    └── study-roadmap/
        └── SKILL.md
```

---

## Licença

Distribuído sob a licença [MIT](LICENSE).
