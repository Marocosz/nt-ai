from langchain_core.prompts import PromptTemplate
from datetime import datetime, timedelta

# --- 1. O Otimizador de Query ---
enhancer_template = """
Sua tarefa é reescrever a pergunta do usuário para ser mais clara, completa e explícita. Corrija erros de digitação e expanda abreviações, mas seguindo regras estritas de preservação. Responda APENAS com a frase reescrita.

--- REGRAS DE PRESERVAÇÃO DE TERMOS DE NEGÓCIO (REGRA MAIS IMPORTANTE) ---
As seguintes palavras são termos técnicos do sistema e NÃO DEVEM ser alteradas, traduzidas ou substituídas por sinônimos genéricos. Apenas corrija a gramática ao redor delas.
- Termos de Evento de Data: "agenda", "entregue", "emitido", "previsto", "previsão real", "baixada".
- Termos de Status Logístico: "ENTREGUE", "RETIDA", "TRÂNSITO".
- Termos de Análise de Performance: "ATRASO", "DIA SEGUINTE", "DO DIA", "FUTURO", "PREVISTO PARA 2 DIAS".
- Códigos de Operação: Qualquer termo que comece com "InBound-" ou "OutBound-" (ex: "InBound-IPO", "OutBound-SPO").

--- REGRAS GERAIS DE REESCRITA ---
1. Expanda abreviações comuns: "nf" -> "nota fiscal", "sp" -> "estado de São Paulo", "transp" -> "transportadora", "cli" -> "cliente".
2. Normalize termos de status (apenas se não for um termo preservado): Se o usuário mencionar "com atraso", reescreva usando a frase "com status de análise ATRASO".
3. Expanda códigos de operação ambíguos:
    - Se o usuário digitar apenas "IPO", reescreva como "operação InBound-IPO ou OutBound-IPO".
    - Se o usuário digitar apenas "MAO", reescreva como "operação InBound-MAO ou OutBound-MAO".

--- REGRAS DE PRIORIZAÇÃO DE CONTEXTO ---
1. Se a pergunta mencionar tempo ("ontem", "hoje", "semana passada") junto com um evento de data ("entregue", "emitido", "baixada"), mantenha ambos, mas priorize a clareza temporal (ex: "notas entregues ontem").
2. Se a pergunta mencionar tempo e performance simultaneamente ("ontem com atraso"), preserve ambos os conceitos.
3. Se a pergunta for genérica (sem tempo, status ou operação), apenas normalize o texto, sem adicionar contexto.
4. Utilize expressões variadas de ação, escolhendo naturalmente entre:
   - "Me mostre", "Mostre", "Liste", ou "Quais são", conforme o tipo da frase original.
5. Se houver dois eventos de data diferentes ("emitidas ontem e entregues hoje"), preserve ambos, mas mantenha a sequência cronológica natural. 
6. Sempre inicie a frase reescrita com letra maiúscula, mantendo o formato interrogativo ou declarativo original. 
7. Nunca adicione contexto, filtro ou status que o usuário não mencionou explicitamente.

Exemplos:
---
Pergunta Original: "nf entregues ontem sp"
Pergunta Reescrita: "Me mostre as notas fiscais que foram entregues ontem para o estado de São Paulo"
---
Pergunta Original: "notas do cli acme transp veloz com atraso"
Pergunta Reescrita: "Me mostre as notas do cliente ACME da transportadora Veloz com status de análise ATRASO"
---
Pergunta Original: "o que foi baixado na ult sem"
Pergunta Reescrita: "O que foi baixado na última semana"
---
Pergunta Original: "notas para IPO"
Pergunta Reescrita: "Me mostre as notas fiscais para operação InBound-IPO ou OutBound-IPO"
---

Pergunta Original: {query}
Pergunta Reescrita:
"""
QUERY_ENHANCER_PROMPT = PromptTemplate.from_template(enhancer_template)


# --- 2. O Parser de JSON ---
parser_template = """
Você é um assistente especialista que analisa um texto claro e o converte para um objeto JSON de filtros. Sua resposta deve ser APENAS o objeto JSON, sem nenhum texto adicional.

A data de referência para cálculos é {today}.

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
---

--- MAPEAMENTO CONTEXTUAL PARA "StatusAnaliseData" (performance em relação ao prazo) ---
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

--- REGRAS DE INTELIGÊNCIA ---
Regras de Ambiguidade (TipoData vs. SituacaoNF):
- Se uma palavra como "entregue", "emitido" ou "baixada" for usada JUNTO com um período de tempo (ex: "ontem", "hoje", "na semana passada", "em setembro"), priorize o preenchimento de "TipoData".
- Se uma palavra que descreve um estado (ex: "em trânsito", "retida") for usada sem um período de tempo claro, priorize o preenchimento de "SituacaoNF".
- Se um termo como "entregue" for usado sem um período de tempo, priorize o preenchimento de "SituacaoNF" com o valor 'ENTREGUE'.

Regras de Localização:
- Se o usuário mencionar uma sigla de 2 letras da lista de "UFDestino", preencha o campo "UFDestino".
- Se um nome pode ser tanto cidade quanto estado (ex: "São Paulo"), priorize o preenchimento de "UFDestino" com a sigla correspondente (ex: "SP"), a menos que o usuário especifique "cidade de".
- Extraia o nome da cidade para "CidadeDestino" sempre que possível.

--- REGRAS DE PRECISÃO ---
1. Extração Completa de Datas: Se você identificar um período de tempo (ex: "ontem", "hoje"), você DEVE preencher os campos "DE" e "ATE" com as datas correspondentes.
2. Prioridade de Filtro: Se um `StatusAnaliseData` como 'DO DIA' ou 'DIA SEGUINTE' for identificado, priorize este filtro e NÃO extraia um `TipoData` ao mesmo tempo.
3. Restrição de Inferência: NÃO infira filtros que não foram explicitamente mencionados. Se a pergunta for vaga, todos os filtros devem ser null.
4. Regra para Códigos: Valores para "Operacao" (como "OutBound-SPO") são códigos únicos e NÃO DEVEM ser divididos ou interpretados. Extraia o valor exato.
5. Associação de Data e Tipo: Se um filtro de data (`DE`/`ATE`) for preenchido com base em um evento (como 'entregue' ou 'emitido'), o `TipoData` correspondente DEVE ser preenchido.
6. Se o texto contiver uma faixa explícita ("de X até Y"), sempre converta para formato completo ISO (AAAA-MM-DD).
7. Se contiver "última semana" ou "semana passada", defina "DE" = {last_week_start} e "ATE" = {today}.
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
- Datas relativas: 'ontem' é {yesterday}, 'hoje' é {today}, 'semana passada' é o período de {last_week_start} a {today}.
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
Texto: "notas previstas para amanhã"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "DIA SEGUINTE", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "me mostre as notas com status DO DIA"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "DO DIA", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "liste as notas emitidas hoje para SP que estão em trânsito"
JSON: {{"NF": null, "DE": "{today}", "ATE": "{today}", "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": "SP", "CidadeDestino": null, "Operacao": null, "SituacaoNF": "TRÂNSITO", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "qual o status da entrega?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "quais são os clientes?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}}
---
Texto: "notas emitidas ontem e entregues hoje"
JSON: {"NF": null, "DE": null, "ATE": null, "TipoData": "3", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "ENTREGUE", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": null}
---

Agora, analise o seguinte texto:
Texto: {enhanced_query}
JSON:
"""
JSON_PARSER_PROMPT = PromptTemplate.from_template(parser_template)