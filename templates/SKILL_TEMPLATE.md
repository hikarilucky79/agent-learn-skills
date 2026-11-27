---
name: nome-da-skill-em-kebab-case
description: >
  Descrição curta e acionável explicando exatamente QUANDO ativar esta skill
  e QUANDO NÃO ativar (evitando conflito com outras skills do repositório).
---

<!--
INSTRUÇÕES DE PREENCHIMENTO:
- O campo `name` acima DEVE ser idêntico ao nome da pasta em `skills/<nome-da-skill>/`.
- Mantenha a `description` objetiva: agentes usam esse texto para decidir quando carregar a skill.
- Remova estes comentários HTML antes de abrir seu Pull Request.
-->

# [Nome Legível da Skill]

## 1. Papel e Objetivo

<!-- Defina em 2–3 frases a persona pedagógica do agente e qual técnica de aprendizagem ativa ele aplica. -->

Atue como [persona pedagógica]. Seu objetivo é [objetivo mensurável de aprendizagem], priorizando recuperação ativa, prática guiada e feedback diagnóstico em vez de respostas passivas.

## 2. Escopo (Quando Usar / Quando Não Usar)

<!-- Estabeleça fronteiras explícitas para evitar disparos indevidos e sobreposição com outras skills. -->

**Use esta skill quando:**
- [Caso de uso principal 1]
- [Caso de uso principal 2]

**Não use esta skill quando:**
- [Caso fora de escopo que pertence a outra skill — cite a skill alternativa, ex.: `quiz-master`, `code-mentor`]
- [Pedido de resposta pronta sem intenção de estudo/prática]

## 3. Fluxo de Execução (Passo a Passo)

<!-- Siga os 4 passos obrigatórios abaixo adaptando-os à técnica pedagógica da skill. -->

### Passo 1: Diagnóstico Rápido
Se o usuário não tiver informado, pergunte de forma breve e direta:
1. **Tema ou escopo:** [o que será estudado].
2. **Nível atual:** [iniciante, intermediário, avançado ou equivalente].
3. **Objetivo:** [prova, entrevista, projeto prático, revisão].

### Passo 2: Execução da Técnica Pedagógica
- [Descreva a ação principal do agente nesta etapa.]
- [Inclua critérios de qualidade do material gerado ou das perguntas feitas.]

### Passo 3: Avaliação e Feedback Específico
- Analise a resposta ou entrega do usuário antes de avançar.
- Explique claramente o **porquê** de cada acerto, lacuna ou erro conceitual.
- [Detalhe como o feedback deve ser estruturado.]

### Passo 4: Adaptação Dinâmica e Próximo Passo
- Ajuste a dificuldade, o ritmo ou o foco com base no desempenho observado.
- Sugira uma única próxima ação concreta (ex.: aprofundar ponto fraco, aumentar nível ou encerrar ciclo).

## 4. Regras Pedagógicas e Restrições

<!-- Liste comportamentos obrigatórios e proibidos em formato de bullets curtos e verificáveis. -->

- **OBRIGATÓRIO:** [Regra positiva essencial — ex.: aguardar a tentativa do usuário antes de mostrar a solução].
- **OBRIGATÓRIO:** [Regra de clareza, atomicidade ou rigor técnico].
- **PROIBIDO:** [Comportamento passivo ou anti-padrão pedagógico a evitar].
- **PROIBIDO:** [Sobrecarga cognitiva, respostas genéricas ou entrega antecipada de gabarito].

## 5. Formato de Saída

<!-- Defina a estrutura visual padrão (tabelas, listas, blocos de código, separadores) que o agente deve usar. -->

```markdown
### [Cabeçalho da Etapa]
- **Item 1:** [conteúdo]
- **Item 2:** [conteúdo]
```

## 6. Exemplo Curto (Input → Output)

<!-- Forneça um exemplo enxuto e realista demonstrando o tom, a concisão e a formatação esperados. -->

**Input do usuário:**
> [Prompt curto e realista do estudante]

**Output esperado do agente:**
> [Resposta curta seguindo exatamente o Formato de Saída e as Regras Pedagógicas]
