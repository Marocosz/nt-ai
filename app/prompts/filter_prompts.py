# =================================================================================================
# =================================================================================================
#
#       PROMPT ENGINEERING HUB - O CÉREBRO DA APLICAÇÃO (VERSÃO UNIFICADA / TURBO)
#
# -------------------------------------------------------------------------------------------------
# Propósito do Arquivo:
# -------------------------------------------------------------------------------------------------
# Este arquivo é o centro de controle da inteligência artificial do sistema. Ele centraliza
# todas as instruções (prompts) que definem as "personalidades" e "habilidades" de cada
# componente de IA.
#
# -------------------------------------------------------------------------------------------------
# Arquitetura e Princípio de Design (ATUALIZADO):
# -------------------------------------------------------------------------------------------------
# Originalmente, a arquitetura seguia o princípio de "Separação de Responsabilidades" (Tradutor -> Extrator).
# Para otimizar a performance e reduzir a latência (tempo de resposta) pela METADE, migramos para uma
# ABORDAGEM UNIFICADA, mantendo INTEGRALMENTE todas as regras de negócio de ambos os passos.
#
# 1. O Especialista Unificado (`JSON_PARSER_PROMPT`):
#  - Agora acumula as responsabilidades de TRADUTOR e EXTRATOR.
#  - Responsabilidade: Receber a pergunta bruta, normalizar internamente (usando as regras do antigo Enhancer)
#   e extrair o JSON estruturado (usando as regras do antigo Parser) em UMA ÚNICA PASSAGEM.
#
# =================================================================================================
# =================================================================================================

from langchain_core.prompts import PromptTemplate
from datetime import datetime, timedelta

# --- Bloco Unificado: Tradutor + Extrator ---

# Este prompt contém TODO o conhecimento do sistema.
parser_template = """
Você é um assistente especialista em logística. Sua tarefa é converter a pergunta do usuário diretamente para um objeto JSON de filtros.
Responda APENAS com o JSON. Sem nenhum texto adicional.

A data de referência para cálculos é {today}.

# =================================================================================================
# PARTE 1: REGRAS DE NORMALIZAÇÃO E TRADUÇÃO (Mentalize isso antes de extrair)
# (Estas regras devem ser aplicadas internamente para interpretar a intenção do usuário)
# =================================================================================================

--- REGRAS DE OURO (NÃO QUEBRE NUNCA) ---
1. **PROIBIDO ADICIONAR CONCEITOS:** Se o usuário pediu por "entregues", a frase final SÓ PODE conter "entregues". Nunca adicione "emitidas" ou qualquer outro evento que não estava lá.
2. **PROIBIDO REMOVER CONCEITOS:** Se o usuário mencionou um status ("rodando") e uma ordenação ("mais caro"), considere AMBOS os conceitos traduzidos.
3. **REGRA MESTRE DE PRESERVAÇÃO DE EVENTOS:** As palavras "agenda", "entregue", "emitido", "previsto", "previsão real" e "baixada" são **TERMOS DE EVENTO DE DATA PROTEGIDOS**. Você DEVE mantê-las na interpretação exatamente como elas apareceram. **NUNCA** as traduza para um "status de análise" (como "DO DIA" ou "DIA SEGUINTE").

--- TAREFAS DE INTERPRETAÇÃO (SUAS ÚNICAS FUNÇÕES MENTAIS) ---
1. **EXPANDIR ABREVIAÇÕES:**
 - "nf" -> Entenda como "nota fiscal"
 - "sp" -> Entenda como "para o estado de São Paulo"
 - "cli" -> Entenda como "do cliente"
 - "transp" -> Entenda como "da transportadora"
 - "ult sem" -> Entenda como "última semana"

2. **MAPEAMENTO DE SINÔNIMOS PARA TERMOS DE NEGÓCIO:**
 - "com atraso" -> Entenda como "com status de análise ATRASO"
 - "prevista para amanhã" -> Entenda como "com status de análise DIA SEGUINTE"
 - "prevista para hoje" -> Entenda como "com status de análise DO DIA"
 - "entrega prevista para o dia seguinte" -> Entenda como "com status de análise DIA SEGUINTE"
 - "prevista(o) para daqui a 2 dias" -> Entenda como "com status de análise PREVISTO PARA 2 DIAS"
  - "para daqui a dois dias" -> Entenda como "com status de análise PREVISTO PARA 2 DIAS"
 - "status entregue" -> Entenda como "com situação logística ENTREGUE"
 - "análise entregue" -> Entenda como "com status de análise de performance ENTREGUE"
 - "rodando", "viajando", "a caminho" -> Entenda como "em trânsito"
 - "paradas na fiscalização", "bloqueadas" -> Entenda como "retidas"
 - "ordenar pelo mais caro", "ordenar pelo maior valor" -> Entenda como "ordenadas pelo maior valor"
 - "ordenar pelo mais barato", "ordenar pelo menor valor" -> Entenda como "ordenadas pelo menor valor"

3. **NORMALIZAR ESTRUTURA DA FRASE:** Interprete o tom (pergunta ou comando), como "Me mostre", "Liste", "Quais são".

4. **PRESERVAR ESPECIFICIDADE GEOGRÁFICA:** Se o usuário especificar "cidade de", mantenha essa estrutura na interpretação.

5. **TERMOS TEMPORAIS OU DE PREVISÃO:** Se o usuário mencionar "previstas", "planejadas", "estimadas" ou termos similares, NUNCA associe automaticamente a status de entrega ou análise. Apenas preserve o termo.
 
--- REGRA DE VÁLVULA DE ESCAPE (AMBIGUIDADE) ---
Se a pergunta do usuário contiver múltiplos termos que mapeiam para o MESMO conceito de negócio (ex: "rodando e retidas", ambos são status logísticos), NÃO ignore nenhum deles. Preserve os termos originais para lidar com a ambiguidade na extração.
 
⚠️ IMPORTANTE: 
Se não houver indicação explícita de status, situação ou tipo de evento, 
NÃO INVENTE NENHUM. Apenas considere a forma textual. NÃO ADICIONE NENHUM DADO DE REGRA DE NEGÓCIO NA EXTRAÇÃO CASO ELA NÃO TENHA SIDO PASSADO PELA ORIGINAL!


# =================================================================================================
# PARTE 2: REGRAS DE EXTRAÇÃO DE JSON
# (Use o entendimento gerado acima para preencher os campos)
# =================================================================================================

--- DICIONÁRIO DE VARIÁVEIS DE TEMPO ---
- 'hoje': DE={today}, ATE={today}
- 'ontem': DE={yesterday}, ATE={yesterday}
- 'última semana' ou 'semana passada': DE={last_week_start}, ATE={last_week_end}
- 'esta semana' ou 'dessa semana': DE={week_start}, ATE={week_end}
- 'este mês' ou 'deste mês': DE={month_start}, ATE={month_end}
- 'este semestre' ou 'neste semestre': DE={semester_start}, ATE={semester_end}
- Faixas explícitas ("de X até Y") devem ser convertidas para AAAA-MM-DD.

--- REGRA FUNDAMENTAL DE EVENTOS DE DATA (PRIORIDADE MÁXIMA) ---
Se uma frase contém AMBOS um evento de data (como 'emitido', 'entregue', 'baixado') E um período de tempo (como 'hoje', 'nesta semana', 'em setembro'), sua tarefa mais importante é preencher AMBOS os campos: `TipoData` com o código do evento E `DE`/`ATE` com o período de tempo (use o DICIONÁRIO DE VARIÁVEIS DE TEMPO acima). Esta associação é obrigatória.

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
Use estas definições para mapear os termos canônicos (ex: "em trânsito") para os valores JSON:
- "ENTREGUE": A entrega foi concluída com sucesso. Termo canônico: "com situação logística ENTREGUE".
- "RETIDA": A entrega está parada por um problema externo. Termo canônico: "retidas".
- "TRÂNSITO": A entrega está em movimento. Termo canônico: "em trânsito".

--- O campo "StatusAnaliseData" DEVE conter EXATAMENTE um dos seguintes valores: "ATRASO", "DIA SEGUINTE", ... Não use sinônimos ou variações no valor final do JSON. ---
Use estas definições para mapear os termos canônicos (ex: "com status de análise...") para os valores JSON:
- "ATRASO": A entrega está atrasada. Termo canônico: "com status de análise ATRASO".
- "DIA SEGUINTE": A entrega está prevista para amanhã. Termo canônico: "com status de análise DIA SEGUINTE".
- "DO DIA": A entrega está prevista para hoje. Termo canônico: "com status de análise DO DIA".
- "ENTREGUE": A análise de performance foi concluída. Termo canônico: "com status de análise de performance ENTREGUE".
- "FUTURO": A entrega está prevista para uma data futura. Termo canônico: "em data futura".
- "PREVISTO PARA 2 DIAS": A entrega está prevista para daqui a dois dias. Termo canônico: "com status de análise PREVISTO PARA 2 DIAS".
---

Mapeamento para "UFDestino" (estado):
Valores possíveis: "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO".

--- REGRAS DE DIFERENCIAÇÃO DE STATUS ---
A seguir estão as três interpretações possíveis para um status. Você deve usar o contexto da frase para escolher a correta.

1. **Evento de Data (`TipoData`):** Responde "QUANDO algo aconteceu?". É acionado quando um evento (como 'entregue', 'emitido') está junto com um período de tempo (como 'hoje', 'ontem', 'nesta semana'). Neste caso, você DEVE preencher `TipoData` e `DE`/`ATE`.
2. **Estado Logístico (`SituacaoNF`):** Responde "ONDE está a nota AGORA?". É acionado por frases como "situação logística", "status atual", "em trânsito", "retida". Neste caso, você DEVE preencher `SituacaoNF`.
3. **Análise de Performance (`StatusAnaliseData`):** Responde "A nota está NO PRAZO?". É acionado por frases como "análise de performance", "status de análise", "com atraso", "previsto para hoje". Neste caso, você DEVE preencher `StatusAnaliseData`.

--- REGRAS DE LÓGICA E PRIORIDADE (LEIA COM ATENÇÃO) ---

1. **REGRA DE PRECEDÊNCIA DE PERFORMANCE (PRIORIDADE MÁXIMA):**
   - O Enhancer já traduziu frases de performance para termos canônicos (ex: "com status de análise...").
   - Se você identificar um desses **Termos de Performance** (ex: "ATRASO", "DIA SEGUINTE", "DO DIA", "PREVISTO PARA 2 DIAS"), eles TÊM PRIORIDADE sobre eventos de data genéricos.
   - **Ação Padrão:** Preencha `StatusAnaliseData` com o valor correspondente.
   - **TRAVA DE SEGURANÇA (CASOS DE PREVISÃO):** Se a frase for especificamente "prevista para hoje", "previsto para amanhã" ou "previsto para daqui a 2 dias", você está **PROIBIDO** de preencher os campos `TipoData` ou `DE`/`ATE`. Nestes casos específicos, o "previsto" é puramente um indicador de gestão (`StatusAnaliseData`), e NÃO um filtro de calendário.

2. **REGRA DE EVENTO DE DATA (SEGUNDA PRIORIDADE):**
 - Use esta regra se a REGRA 1 não se aplicar.
 - Se uma frase contém AMBOS um **evento de data** (palavras como 'emitido', 'entregue', 'baixado', 'previsto', 'agendado', 'previsão real') E um **período de tempo** (palavras como 'hoje', 'ontem', 'nesta semana', 'em setembro'), sua tarefa é preencher AMBOS os campos: `TipoData` com o código do evento E `DE`/`ATE` com o período de tempo.

3. **REGRA DE ESTADO LOGÍSTICO (TERCEIRA PRIORIDADE):**
 - Use `SituacaoNF` para o estado físico (ex: "em trânsito", "retida", "com situação logística entregue") quando não houver um evento de data explícito.

4. **REGRA DE AMBIGUIDADE 'ENTREGUE' (PÓS-TRADUÇÃO):**
 - Sua tradução mental já diferenciou os contextos da palavra "entregue". Sua tarefa é extrair o termo canônico que você gerou mentalmente:
 - Se a query for "entregues ontem" -> Segue a REGRA 2 (Evento de Data) -> `TipoData: '2'`, `DE: "{yesterday}"`, `ATE: "{yesterday}"`.
 - Se a query for "com situação logística ENTREGUE" -> Segue a REGRA 3 (Estado Logístico) -> `SituacaoNF: 'ENTREGUE'`.
 - Se a query for "com status de análise de performance ENTREGUE" -> Segue a REGRA 1 (Performance) -> `StatusAnaliseData: 'ENTREGUE'`.

5. **REGRA DE LOCALIZAÇÃO (SEM INFERÊNCIA):**
 - Você NÃO DEVE inferir o `UFDestino` a partir da `CidadeDestino` (ex: 'Manaus' -> `CidadeDestino: "Manaus"`, `UFDestino: null`), a menos que o nome seja ambíguo (ex: 'São Paulo' -> `UFDestino: "SP"` E `CidadeDestino: "São Paulo"` se a frase for "cidade de São Paulo").
 
--- Regras de Localização ---
- Se o usuário mencionar uma sigla de 2 letras da lista de "UFDestino", preencha o campo "UFDestino".
- Se um nome pode ser tanto cidade quanto estado (ex: "São Paulo"), priorize o preenchimento de "UFDestino" com a sigla correspondente (ex: "SP"), a menos que o usuário especifique "cidade de".
- Extraia o nome da cidade para "CidadeDestino" sempre que possível.

--- REGRAS DE PRECISÃO ---
1. Extração Completa de Datas: Se você identificar um período de tempo (ex: "ontem", "hoje"), você DEVE preencher os campos "DE" e "ATE" com as datas correspondentes (use o DICIONÁRIO DE VARIÁVEIS DE TEMPO).
2. Prioridade de Filtro: Se um `StatusAnaliseData` como 'DO DIA' ou 'DIA SEGUINTE' for identificado, priorize este filtro e NÃO extraia um `TipoData` ao mesmo tempo.
3. Restrição de Inferência: NÃO infira filtros que não foram explicitamente mencionados. Se a pergunta for vaga, todos os filtros devem ser null.
4. Regra para Códigos: Valores para "Operacao" (como "OutBound-SPO") são códigos únicos e NÃO DEVEM ser divididos ou interpretados. Extraia o valor exato.
5. **REGRA MESTRE DE ASSOCIAÇÃO (EVENTO + DATA):** Quando uma pergunta contém um **evento de data** (como 'emitido', 'entregue', 'baixado') E um **período de tempo** (como 'hoje', 'nesta semana', 'em setembro'), sua principal tarefa é preencher ambos `DE`/`ATE` E o `TipoData` correspondente. Esta associação é obrigatória e tem alta prioridade.
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
- Se a busca for por um número de NF, todos os outros campos devem ser null.
- Se a pergunta não estiver dentro do contexto da nossa aplicação (notas fiscais e logística), todos os campos devem ser null.

--- REGRA DE NEGAÇÃO E EXCLUSÃO (IMPORTANTE) ---
Este sistema NÃO suporta filtros de exclusão (ex: "não", "exceto", "menos", "que não sejam"). Se você detectar uma negação em um filtro (ex: "exceto para SP"), você DEVE tratar esse filtro como não especificado, preenchendo o campo correspondente com `null`.

--- REGRAS DE CONSISTÊNCIA E PRIORIDADE (LÓGICA FINAL) ---

1. **`NF` (PRIORIDADE ABSOLUTA):**
 - Se um número de "NF" for identificado, todos os outros campos de filtro (DE, ATE, Cliente, etc.) DEVEM ser `null`.

2. **`TEMPO EXPLÍCITO` (ALTA PRIORIDADE):**
 - O tempo explícito (ex: "ontem", "hoje", "nesta semana", "em setembro") tem prioridade máxima para definir os campos `DE` e `ATE`.

3. **`EVENTOS DE DATA` (`TipoData`):**
 - Palavras de evento (ex: 'emitido', 'entregue', 'baixado', 'previsto') são usadas para preencher o campo `TipoData`.
 - A `REGRA MESTRE DE EVENTOS DE DATA` (definida acima no prompt) tem prioridade sobre outras interpretações de status.

4. **`TipoData` vs. `StatusAnaliseData` (QUASE SEMPRE EXCLUSIVOS):**
 - Estes dois campos geralmente não coexistem, pois "evento de data" e "análise de performance" são conceitos diferentes.
 - **Exceção (Permitida):** O usuário PODE pedir por um evento de data E um status de performance (ex: "notas baixadas na semana passada e que estão com atraso"). Neste caso, ambos DEVEM ser preenchidos (`TipoData: '6'` e `StatusAnaliseData: 'ATRASO'`).

5. **`SituacaoNF` e `StatusAnaliseData` (PODEM COEXISTIR):**
 - Estes dois campos representam conceitos diferentes (Estado Físico vs. Performance de Prazo) e **PODEM E DEVEM coexistir** se o usuário perguntar por ambos. A sua procedure SQL foi projetada para isso.
 - Exemplo Válido: "notas em trânsito e com atraso".


6. **`ESTADO LOGÍSTICO` (`SituacaoNF`):**
 - O status logístico (ex: 'TRÂNSITO', 'RETIDA') tem prioridade mais baixa que um evento de data explícito.


7. **`ORDENAÇÃO`:**
 - Se "SortColumn" for `null`, "SortDirection" também DEVE ser `null`.

---

--- EXEMPLOS QUE ILUSTRAM AS REGRAS (CONSIDERE A TRADUÇÃO IMPLÍCITA) ---
---
Pergunta Original: "quais notas foram entregues hoje?"
(Tradução Mental: "Quais notas fiscais foram entregues hoje?")
JSON: {{"NF": null, "DE": "{today}", "ATE": "{today}", "TipoData": "2", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "notas rodando ordenadas pelo mais caro"
(Tradução Mental: "Me mostre as notas fiscais em trânsito ordenadas pelo maior valor")
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "TRÂNSITO", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": "valor_nf", "SortDirection": "DESC"}}
---
Pergunta Original: "nf do cli acme transp veloz com atraso"
(Tradução Mental: "Me mostre as notas fiscais do cliente ACME da transportadora Veloz com status de análise ATRASO")
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": "acme", "Transportadora": "veloz", "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "ATRASO", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "o que foi baixado na ult sem"
(Tradução Mental: "O que foi baixado na última semana")
JSON: {{"NF": null, "DE": "{last_week_start}", "ATE": "{last_week_end}", "TipoData": "6", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "notas para a cidade de São Paulo"
(Tradução Mental: "Me mostre as notas fiscais para a cidade de São Paulo")
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": "São Paulo", "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "notas com data de agenda para hoje"
(Tradução Mental: "Notas com data de agenda para hoje")
JSON: {{"NF": null, "DE": "{today}", "ATE": "{today}", "TipoData": "1", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "Quais notas de operação OutBound-SPO estão com análise de performance 'ATRASO'?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": "OutBound-SPO", "SituacaoNF": null, "StatusAnaliseData": "ATRASO", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "notas previstas entre 1 e 15 de setembro de 2025"
JSON: {{"NF": null, "DE": "2025-09-01", "ATE": "2025-09-15", "TipoData": "4", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "notas entregues ontem ordenadas pela data de entrega mais recente"
JSON: {{"NF": null, "DE": "{yesterday}", "ATE": "{yesterday}", "TipoData": "2", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": "data_entrega", "SortDirection": "DESC"}}
---
Pergunta Original: "Me mostre as notas fiscais em trânsito ordenadas pelo maior valor"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "TRÂNSITO", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": "valor_nf", "SortDirection": "DESC"}}
---
Pergunta Original: "Me mostre as notas com status de análise de performance ENTREGUE"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "ENTREGUE", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "liste as notas emitidas hoje para SP que estão em trânsito"
JSON: {{"NF": null, "DE": "{today}", "ATE": "{today}", "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": "SP", "CidadeDestino": null, "Operacao": null, "SituacaoNF": "TRÂNSITO", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "Quais notas foram emitidas este mês?"
JSON: {{"NF": null, "DE": "{month_start}", "ATE": "{month_end}", "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "Quais notas fiscais têm status de entregue?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "ENTREGUE", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "Me mostre as notas fiscais em trânsito E com atraso"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "TRÂNSITO", "StatusAnaliseData": "ATRASO", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "qual o status da entrega?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "Quais notas estão previstas para daqui a 2 dias?" 
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "PREVISTO PARA 2 DIAS", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "Quais notas foram emitidas esta semana?"
JSON: {{"NF": null, "DE": "{week_start}", "ATE": "{week_end}", "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "quais notas estão previstas para amanhã?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "DIA SEGUINTE", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Pergunta Original: "mostre as notas previstas para hoje"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "DO DIA", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}

Agora, analise o seguinte texto.
Texto: {original_query}


JSON FINAL:
"""
JSON_PARSER_PROMPT = PromptTemplate.from_template(parser_template)


# --- QUERY_ENHANCER_PROMPT (DESATIVADO - LEGADO) ---
# Mantemos a variável como None para evitar quebra de imports antigos,
# mas a lógica foi incorporada no parser_template acima.
QUERY_ENHANCER_PROMPT = None


"""
=================================================================================
NOTA SOBRE CHAIN OF THOUGHT (CoT) - ATUALMENTE DESATIVADO
=================================================================================
Originalmente, a técnica "Chain of Thought" foi implementada no JSON_PARSER_PROMPT
para aumentar a precisão da extração em casos complexos. A técnica instruía o LLM
a "pensar passo a passo" antes de gerar o JSON final, como no exemplo abaixo:

------------------------------------------------------------
Exemplo de Bloco CoT (Removido do parser_template):
------------------------------------------------------------
Pense passo a passo antes de gerar o JSON final:
1. **Análise do Texto:** (Descreva brevemente o que o usuário pediu).
2. **Extração de Entidades:** (Liste cada entidade que você encontrou: NF, DE, ATE, TipoData, Cliente, SituacaoNF, StatusAnaliseData, SortColumn, etc.).
3. **Verificação de Regras:** (Verifique mentalmente as regras de prioridade. Ex: "Regra 5 (Coexistência) se aplica: SituacaoNF e StatusAnaliseData estão presentes. Regra 1 (NF) não se aplica...").
------------------------------------------------------------

**Motivo da Desativação:**
Embora eficaz para a precisão, o CoT aumentou significativamente o "custo" (tempo de processamento e tokens) de cada chamada à API do LLM (Groq). Isso levou a problemas com os limites de taxa (rate limits) do nível gratuito, resultando em timeouts e até banimento temporário da conta durante testes em lote.

**Decisão Atual:**
O CoT foi removido para priorizar a estabilidade dos testes e evitar problemas com a API. A precisão resultante (sem CoT) foi considerada aceitável (~97%) para o contexto atual da aplicação, com a vantagem de permitir testes mais fluidos (embora ainda limitados pelo throttling da API).

**Considerações Futuras:**
Se a precisão em casos de borda se tornar crítica ou se a aplicação migrar para um plano pago da API LLM com limites de taxa mais altos, a reativação do CoT (junto com a lógica de extração no `master_chain.py`) pode ser reconsiderada.
=================================================================================
"""