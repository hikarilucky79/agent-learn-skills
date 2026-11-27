# Prompts de Teste de Ativação (Evals Manuais)

Use estes prompts para validar que o agente seleciona a skill correta sem conflito de gatilho entre as `description` do catálogo.

| Prompt de Teste | Skill Esperada | Não Deve Ativar | Critério de Sucesso |
|---|---|---|---|
| *"Me faça um quiz de 5 questões sobre Event Loop em JS, nível Júnior."* | `quiz-master` | `flashcards-srs`, `feynman-tutor` | Gera questões com distratores plausíveis e **oculta o gabarito**. |
| *"Transforme este resumo de índices SQL em 6 flashcards com Cloze e CSV para Anki."* | `flashcards-srs` | `quiz-master` | Gera cartas atômicas (1 conceito/carta) com `{{c1::...}}` e bloco CSV válido. |
| *"Quero testar se entendi Idempotência em REST usando Feynman; minha explicação é..."* | `feynman-tutor` | `quiz-master`, `code-mentor` | Aponta lacunas/jargões e faz perguntas socráticas antes da síntese final. |
| *"Minha função Python retorna `None` em vez da soma; me ajude a encontrar o erro sem reescrever tudo."* | `code-mentor` | `feynman-tutor`, `quiz-master` | Inicia no **Nível 1** (aponta região/conceito sem entregar a resposta pronta). |
| *"Tenho 6h/semana por 4 semanas para estudar SQL para entrevistas; monte um plano."* | `study-roadmap` | `quiz-master`, `flashcards-srs` | Entrega fases progressivas com mini-projeto e critérios objetivos de conclusão. |
| *"Me dê a resposta pronta deste exercício de SQL sem explicar nada."* | *(Nenhuma skill de estudo / recusa pedagógica)* | `quiz-master`, `code-mentor` | Não deve disparar fluxo de mentoria passiva ou gabarito sem tentativa quando o usuário busca estudo ativo. |
