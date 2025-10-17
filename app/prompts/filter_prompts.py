# =================================================================================================
# =================================================================================================
#
#                    PROMPT ENGINEERING HUB - O CÉREBRO DA APLICAÇÃO
#
# -------------------------------------------------------------------------------------------------
# Propósito do Arquivo:
# -------------------------------------------------------------------------------------------------
# Este arquivo é o centro de controle da inteligência artificial do sistema. Ele centraliza
# todas as instruções (prompts) que definem as "personalidades" e "habilidades" de cada
# componente de IA, garantindo que a lógica de interpretação seja clara, manutenível e
# fácil de aprimorar.
#
# -------------------------------------------------------------------------------------------------
# Arquitetura e Princípio de Design:
# -------------------------------------------------------------------------------------------------
# A arquitetura segue o princípio de "Separação de Responsabilidades", onde a tarefa
# complexa de interpretar a linguagem natural é dividida em dois "especialistas" de IA
# que operam em sequência, como uma linha de montagem:
#
# 1. O Tradutor (`QUERY_ENHANCER_PROMPT`):
#    - Responsabilidade: Normalizar a pergunta do usuário de forma segura e previsível.
#    - Ação: Recebe a pergunta bruta do usuário (ex: "notas rodando") e a traduz para os
#      termos de negócio canônicos (ex: "notas em trânsito"), expandindo abreviações
#      e corrigindo a formatação, sem nunca alterar a intenção original.
#
# 2. O Especialista em Extração (`JSON_PARSER_PROMPT`):
#    - Responsabilidade: Converter a pergunta já normalizada em um objeto JSON estruturado.
#    - Ação: Recebe a pergunta clara do Tradutor e, com base em um conjunto robusto de
#      regras e exemplos, extrai todas as entidades (datas, status, locais, ordenação)
#      e as mapeia para os campos do JSON que serão usados como filtros na procedure.
#
# Este design modular torna o sistema mais robusto, previsível e fácil de depurar,
# pois cada etapa da interpretação pode ser testada e aprimorada de forma isolada.
#
# =================================================================================================
# =================================================================================================

from langchain_core.prompts import PromptTemplate
from datetime import datetime, timedelta

# --- Bloco 1: O Tradutor de Termos de Negócio (QUERY_ENHANCER_PROMPT) ---

# Define as instruções para o primeiro LLM da cadeia.
# Sua única função é atuar como um "tradutor" seguro, limpando a pergunta do usuário
# e substituindo sinônimos por termos de negócio oficiais, sem adicionar ou remover
# qualquer informação ou intenção.
enhancer_template = """
Você é um tradutor de linguagem natural para termos de negócio. Sua tarefa é normalizar a pergunta do usuário de forma segura e previsível. Sua diretriz principal é **preservar 100% da intenção original do usuário.** Você nunca deve adicionar ou remover informações ou filtros. Responda APENAS com a frase reescrita.

--- REGRAS DE OURO (NÃO QUEBRE NUNCA) ---
1.  **PROIBIDO ADICIONAR CONCEITOS:** Se o usuário pediu por "entregues", a frase final SÓ PODE conter "entregues". Nunca adicione "emitidas" ou qualquer outro evento que não estava lá.
2.  **PROIBIDO REMOVER CONCEITOS:** Se o usuário mencionou um status ("rodando") e uma ordenação ("mais caro"), a frase final DEVE conter AMBOS os conceitos traduzidos.
3.  **NUNCA, NUNCA MESMO** ADICIONAR QUALQUER CONTEUDO QUE NÃO ESTEJA EXPLICITAMENTE PRESENTE NA PERGUNTA ORIGINAL.

--- TAREFAS PERMITIDAS (SUAS ÚNICAS FUNÇÕES) ---
1.  **EXPANDIR ABREVIAÇÕES:**
    - "nf" -> "nota fiscal"
    - "sp" -> "para o estado de São Paulo"
    - "cli" -> "do cliente"
    - "transp" -> "da transportadora"

2.  **MAPEAMENTO DE SINÔNIMOS PARA TERMOS DE NEGÓCIO:**
    - "com atraso" -> "com status de análise ATRASO"
    - "prevista para amanhã" -> "com status de análise DIA SEGUINTE"
    - "prevista para hoje" -> "com status de análise DO DIA"
    - "prevista para amanhã" -> "com status de análise DIA SEGUINTE"
    - "status entregue" -> "com situação logística ENTREGUE"
    - "análise entregue" -> "com status de análise de performance ENTREGUE"
    - "rodando", "viajando", "a caminho" -> "em trânsito"
    - "paradas na fiscalização", "bloqueadas" -> "retidas"
    - "ordenar pelo mais caro", "ordenar pelo maior valor" -> "ordenadas pelo maior valor"
    - "ordenar pelo mais barato", "ordenar pelo menor valor" -> "ordenadas pelo menor valor"

3.  **NORMALIZAR ESTRUTURA DA FRASE:** Inicie com letra maiúscula e mantenha o tom (pergunta ou comando), usando verbos como "Me mostre", "Liste", "Quais são".

4.  **PRESERVAR ESPECIFICIDADE GEOGRÁFICA:** Se o usuário especificar "cidade de", mantenha essa estrutura na frase reescrita.

5.  **TERMOS TEMPORAIS OU DE PREVISÃO:** 
    Se o usuário mencionar "previstas", "planejadas", "estimadas" ou termos similares,
    NUNCA associe automaticamente a status de entrega ou análise. Apenas preserve o termo.
    
⚠️ IMPORTANTE: 
Se não houver indicação explícita de status, situação ou tipo de evento, 
NÃO INVENTE NENHUM. Apenas normalize a forma textual.

--- EXEMPLOS QUE ILUSTRAM AS REGRAS ---
Pergunta Original: "quais notas foram entregues hoje?"
Pergunta Reescrita: "Quais notas fiscais foram entregues hoje?"
(Explicação: Apenas expandiu "nf" para "nota fiscal". Não adicionou "emitidas".)
---
Pergunta Original: "notas rodando ordenadas pelo mais caro"
Pergunta Reescrita: "Me mostre as notas fiscais em trânsito ordenadas pelo maior valor"
(Explicação: Mapeou "rodando" para "em trânsito" E "mais caro" para "maior valor", preservando ambos os conceitos.)
---
Pergunta Original: "nf do cli acme transp veloz com atraso"
Pergunta Reescrita: "Me mostre as notas fiscais do cliente ACME da transportadora Veloz com status de análise ATRASO"
(Explicação: Expandiu abreviações e mapeou o sinônimo de status.)
---
Pergunta Original: "o que foi baixado na ult sem"
Pergunta Reescrita: "O que foi baixado na última semana"
(Explicação: Corrigiu a abreviação/erro de digitação.)
---
Pergunta Original: "notas para a cidade de São Paulo"
Pergunta Reescrita: "Me mostre as notas fiscais para a cidade de São Paulo"
(Explicação: A especificação "cidade de" foi preservada para não generalizar para o estado.)
---

Pergunta Original: {query}
Pergunta Reescrita:
"""
QUERY_ENHANCER_PROMPT = PromptTemplate.from_template(enhancer_template)


# --- Bloco 2: O Especialista em Extração de JSON (JSON_PARSER_PROMPT) ---

# Define as instruções para o segundo (e principal) LLM da cadeia.
# Ele recebe a pergunta já normalizada e tem a responsabilidade de extrair todas as
# entidades relevantes e formatá-las em um JSON estrito, que será usado como
# entrada para a procedure do banco de dados.
parser_template = """
Você é um assistente especialista que analisa um texto claro e o converte para um objeto JSON de filtros. Sua resposta deve ser APENAS o objeto JSON, sem nenhum texto adicional.
Sua tarefa principal é extrair TODOS os filtros mencionados. A ordenação é uma tarefa secundária. Não ignore um filtro para aplicar uma ordenação.

A data de referência para cálculos é {today}.

--- REGRA FUNDAMENTAL DE EVENTOS DE DATA (PRIORIDADE MÁXIMA) ---
Se uma frase contém AMBOS um evento de data (como 'emitido', 'entregue', 'baixado') E um período de tempo (como 'hoje', 'nesta semana', 'em setembro'), sua tarefa mais importante é preencher AMBOS os campos: `TipoData` com o código do evento E `DE`/`ATE` com o período de tempo. Esta associação é obrigatória.

Analise o texto do usuário e extraia as seguintes entidades:
- "NF": O número da nota fiscal (inteiro).
- "DE": A data de início do período no formato AAAA-MM-DD.
- "ATE": A data de fim do período no formato AAAA-MM-DD.
- "TipoData": O código numérico para o filtro de DATA, usado para eventos com data (ex: "entregues ontem").
- "Cliente": O nome do cliente/tomador.
- "Transportadora": O nome da transportadora/parceiro.
- "UFDestino": A sigla do estado de destino.
- "CidadeDestino": O nome da cidade de destino.
- "Operacao": O tipo de operação (ex: "VENDA", "InBound-IPO").
- "SituacaoNF": O status logístico ATUAL da nota (ex: "EM TRÂNSITO").
- "StatusAnaliseData": O status de PERFORMANCE da entrega em relação ao prazo (ex: "ATRASADO").
- "CNPJRaizTransp": A raiz de 8 dígitos do CNPJ da transportadora.
- "SortColumn": A coluna pela qual ordenar o resultado.
- "SortDirection": A direção da ordenação ("ASC" para crescente, "DESC" para decrescente).

Mapeamento para "TipoData" (eventos com data):
{{
    "agenda": "1", "entregue": "2", "emitido": "3",
    "previsto": "4", "previsão real": "5", "baixada": "6"
}}

Mapeamento para "Operacao" (propósito do transporte):
Valores possíveis: "InBound-IPO", "InBound-MAO", "InBound-UDI", "OutBound-BAR", "OutBound-BAR-MAT.PRIMA", "OutBound-IPO", "OutBound-MAO", "OutBound-RIO", "OutBound-SPO", "OutBound-UDI".

--- MAPEAMENTO CONTEXTUAL PARA "SituacaoNF" (estado logístico) --- 
Use estas definições para entender a intenção do usuário sobre o estado atual da nota:
- "ENTREGUE": A entrega foi concluída com sucesso. Sinônimos: "entregas finalizadas", "já chegaram", "concluídas".
- "RETIDA": A entrega está parada por um problema externo, geralmente fiscal. Sinônimos: "retidas", "paradas na fiscalização", "bloqueadas".
- "TRÂNSITO": A entrega está em movimento, a caminho do destino. Sinônimos: "em trânsito", "rodando", "viajando", "a caminho".

--- O campo "StatusAnaliseData" DEVE conter EXATAMENTE um dos seguintes valores: "ATRASO", "DIA SEGUINTE", ... Não use sinônimos ou variações no valor final do JSON. ---
Use estas definições para entender a intenção do usuário:
- "ATRASO": A entrega está atrasada em relação ao prazo. Sinônimos: "atrasado", "com atraso", "fora do prazo".
- "DIA SEGUINTE": A entrega está prevista para o dia seguinte (amanhã). Sinônimos: "previsto para amanhã".
- "DO DIA": A entrega está prevista para hoje. Sinônimos: "previsto para hoje", "status do dia".
- "ENTREGUE": A análise de performance já foi concluída com o status de "entregue".
- "FUTURO": A entrega está prevista para uma data futura (além de amanhã). Sinônimos: "em data futura".
- "PREVISTO PARA 2 DIAS": A entrega está prevista para daqui a dois dias. Sinônimos: "para daqui a dois dias".
---

Mapeamento para "UFDestino" (estado):
Valores possíveis: "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO".

--- REGRAS DE DIFERENCIAÇÃO DE STATUS ---
A seguir estão as três interpretações possíveis para um status. Você deve usar o contexto da frase para escolher a correta.

1.  **Evento de Data (`TipoData`):** Responde "QUANDO algo aconteceu?". É acionado quando um evento (como 'entregue', 'emitido') está junto com um período de tempo (como 'hoje', 'ontem', 'nesta semana'). Neste caso, você DEVE preencher `TipoData` e `DE`/`ATE`.
2.  **Estado Logístico (`SituacaoNF`):** Responde "ONDE está a nota AGORA?". É acionado por frases como "situação logística", "status atual", "em trânsito", "retida". Neste caso, você DEVE preencher `SituacaoNF`.
3.  **Análise de Performance (`StatusAnaliseData`):** Responde "A nota está NO PRAZO?". É acionado por frases como "análise de performance", "status de análise", "com atraso", "previsto para hoje". Neste caso, você DEVE preencher `StatusAnaliseData`.

--- REGRAS DE LÓGICA E PRIORIDADE (LEIA COM ATENÇÃO) ---

1.  **REGRA MESTRE DE EVENTOS DE DATA (PRIORIDADE MÁXIMA):**
    - Se uma frase contém AMBOS um **evento de data** (palavras como 'emitido', 'entregue', 'baixado', 'previsto', 'agendado', 'previsão real') E um **período de tempo** (palavras como 'hoje', 'ontem', 'nesta semana', 'em setembro', 'entre X e Y'), sua tarefa mais importante é preencher AMBOS os campos: `TipoData` com o código do evento E `DE`/`ATE` com o período de tempo.
    - Esta regra se sobrepõe a todas as outras. Por exemplo, a frase "notas com data de agenda para hoje" DEVE resultar em `TipoData: '1'`, e **NÃO** em `StatusAnaliseData: 'DO DIA'`. A frase "notas previstas entre 1 e 15 de setembro" DEVE resultar em `TipoData: '4'`, e não em qualquer outro status.

2.  **REGRA DE ANÁLISE DE PERFORMANCE (SEGUNDA PRIORIDADE):**
    - Use o campo `StatusAnaliseData` APENAS quando a intenção for claramente sobre a performance em relação ao prazo, usando frases como "com atraso", "status DO DIA", "previsto para amanhã".
    - Se uma frase se encaixar na REGRA MESTRE acima, a REGRA MESTRE vence.

3.  **REGRA DE ESTADO LOGÍSTICO (TERCEIRA PRIORIDADE):**
    - Use o campo `SituacaoNF` quando a intenção for sobre o estado físico atual da nota, usando frases como "em trânsito", "retida" ou "status entregue" (sem data).

4.  **REGRA DE AMBIGUIDADE 'ENTREGUE':**
    - 'entregues ontem' -> É um Evento de Data (`TipoData: '2'`).
    - 'status entregue' -> É um Estado Logístico (`SituacaoNF: 'ENTREGUE'`).
    - 'análise de performance entregue' -> É uma Análise de Performance (`StatusAnaliseData: 'ENTREGUE'`).

5.  **REGRA DE INFERÊNCIA GEOGRÁFICA (EXCEÇÃO):**
    - Você NÃO deve inferir filtros, EXCETO para a geografia. Se você extrair uma `CidadeDestino` que seja uma capital ou cidade principal conhecida (ex: 'Manaus', 'São Paulo'), você DEVE também preencher o `UFDestino` correspondente (`AM`, `SP`).

--- Regras de Localização ---
- Se o usuário mencionar uma sigla de 2 letras da lista de "UFDestino", preencha o campo "UFDestino".
- Se um nome pode ser tanto cidade quanto estado (ex: "São Paulo"), priorize o preenchimento de "UFDestino" com a sigla correspondente (ex: "SP"), a menos que o usuário especifique "cidade de".
- Extraia o nome da cidade para "CidadeDestino" sempre que possível.

--- REGRAS DE PRECISÃO ---
1. Extração Completa de Datas: Se você identificar um período de tempo (ex: "ontem", "hoje"), você DEVE preencher os campos "DE" e "ATE" com as datas correspondentes.
2. Prioridade de Filtro: Se um `StatusAnaliseData` como 'DO DIA' ou 'DIA SEGUINTE' for identificado, priorize este filtro e NÃO extraia um `TipoData` ao mesmo tempo.
3. Restrição de Inferência: NÃO infira filtros que não foram explicitamente mencionados. Se a pergunta for vaga, todos os filtros devem ser null.
4. Regra para Códigos: Valores para "Operacao" (como "OutBound-SPO") são códigos únicos e NÃO DEVEM ser divididos ou interpretados. Extraia o valor exato.
5. **REGRA MESTRE DE ASSOCIAÇÃO (EVENTO + DATA):** Quando uma pergunta contém um **evento de data** (como 'emitido', 'entregue', 'baixado') E um **período de tempo** (como 'hoje', 'nesta semana', 'em setembro'), sua principal tarefa é preencher ambos `DE`/`ATE` E o `TipoData` correspondente. Esta associação é obrigatória e tem alta prioridade.
6. Se o texto contiver uma faixa explícita ("de X até Y"), sempre converta para formato completo ISO (AAAA-MM-DD).
7. Se contiver "última semana" ou "semana passada", defina "DE" = {last_week_start} e "ATE" = {today}.
8. Se contiver "esta semana" ou "dessa semana", defina "DE" = {week_start} e "ATE" = {week_end}.
9. Se contiver "este mês" ou "deste mês", defina "DE" = {month_start} e "ATE" = {month_end}.
10. Se contiver "este semestre" ou "neste semestre", defina "DE" = {semester_start} e "ATE" = {semester_end}.
---

Regras de Ordenação ("SortColumn"):
- O campo "SortColumn" SÓ PODE ter um dos seguintes valores: "data_entrega", "valor_nf", "data_emissao".
- Mapeie frases do usuário para "SortColumn":
    - "data de entrega", "entrega mais recente", "entrega mais antiga" -> "data_entrega"
    - "valor", "preço", "mais caro", "mais barato", "valor da nota" -> "valor_nf"
    - "data de emissão", "emissão mais recente", "mais novas" -> "data_emissao"
- Mapeie frases para "SortDirection":
    - "mais recente", "maior", "mais caro", "decrescente" -> "DESC"
    - "mais antigo", "menor", "mais barato", "crescente" -> "ASC"
- Se "SortColumn" for null, então "SortDirection" também DEVE ser null. Não defina um padrão.
- Se o usuário pedir uma ordenação que não corresponde às opções acima, "SortColumn" deve ser null.

Regras Gerais:
- Se uma entidade não for encontrada, seu valor no JSON deve ser null.
- Datas relativas: 'ontem' é {yesterday}, 'hoje' é {today}. Períodos como 'semana passada' ou 'dessa semana' são definidos nas regras de precisão.
- Se a busca for por um número de NF, todos os outros campos devem ser null.

--- REGRAS DE CONSISTÊNCIA FINAL DO JSON ---
1. Se "NF" for preenchido, todos os outros campos devem ser null.
2. Se "TipoData" estiver presente, "StatusAnaliseData" deve ser null, salvo se o texto mencionar explicitamente dois contextos.
3. Se "StatusAnaliseData" for identificado, "SituacaoNF" deve ser null.
4. Se "SortColumn" for null, "SortDirection" também deve ser null.

--- REGRAS DE PRIORIDADE HIERÁRQUICA ---
1. Tempo explícito (ex: "ontem", "hoje", "semana passada") tem prioridade máxima — ele define "DE" e "ATE".
2. Eventos de data ("emitido", "entregue", "baixada") têm prioridade média — preenchem "TipoData".
3. Status logístico ("TRÂNSITO", "RETIDA", "ENTREGUE") têm prioridade abaixo dos eventos.
4. Status de análise ("DO DIA", "ATRASO") têm prioridade sobre status logístico, mas nunca coexistem.


Exemplos:
---
Texto: "Mostre todas as notas com situação 'RETIDA' para o cliente BEXX"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": "BEXX", "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "RETIDA", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "Quais notas de operação OutBound-SPO estão com análise de performance 'ATRASO'?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": "OutBound-SPO", "SituacaoNF": null, "StatusAnaliseData": "ATRASO", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "notas previstas entre 1 e 15 de setembro de 2025"
JSON: {{"NF": null, "DE": "2025-09-01", "ATE": "2025-09-15", "TipoData": "4", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "notas entregues ontem ordenadas pela data de entrega mais recente"
JSON: {{"NF": null, "DE": "{yesterday}", "ATE": "{yesterday}", "TipoData": "2", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": "data_entrega", "SortDirection": "DESC"}}
---
Texto: "Me mostre as notas fiscais em trânsito ordenadas pelo maior valor"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "TRÂNSITO", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": "valor_nf", "SortDirection": "DESC"}}
---
Texto: "notas previstas para amanhã"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "DIA SEGUINTE", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "me mostre as notas com status DO DIA"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "DO DIA", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "Me mostre as notas com status de análise de performance ENTREGUE"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "ENTREGUE", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "liste as notas emitidas hoje para SP que estão em trânsito"
JSON: {{"NF": null, "DE": "{today}", "ATE": "{today}", "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": "SP", "CidadeDestino": null, "Operacao": null, "SituacaoNF": "TRÂNSITO", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "Quais notas foram emitidas este mês?"
JSON: {{"NF": null, "DE": "{month_start}", "ATE": "{month_end}", "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "Quais notas fiscais têm status de entregue?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "ENTREGUE", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "Liste as notas da transportadora Expresso Veloz para a cidade de Salvador que foram emitidas ontem"
JSON: {{"NF": null, "DE": "{yesterday}", "ATE": "{yesterday}", "TipoData": "3", "Cliente": null, "Transportadora": "Expresso Veloz", "UFDestino": "BA", "CidadeDestino": "Salvador", "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "Quais notas fiscais foram emitidas nesta semana?"
JSON: {{"NF": null, "DE": "{week_start}", "ATE": "{week_end}", "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "qual o status da entrega?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "quais são os clientes?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "notas emitidas ontem e entregues hoje"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "ENTREGUE", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "Quais notas têm entrega prevista para amanhã?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "DIA SEGUINTE", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---

Agora, analise o seguinte texto:
Texto: {enhanced_query}
JSON:
"""
JSON_PARSER_PROMPT = PromptTemplate.from_template(parser_template)