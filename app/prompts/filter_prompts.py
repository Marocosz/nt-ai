from langchain_core.prompts import PromptTemplate
from datetime import datetime, timedelta

# --- 1. O Otimizador de Query (inalterado, mas essencial para a etapa seguinte) ---
enhancer_template = """
Sua tarefa é reescrever a pergunta do usuário para ser mais clara, completa e explícita, corrigindo erros de digitação e expandindo abreviações. Responda APENAS com a frase reescrita.

Exemplos:
---
Pergunta Original: "nf entregues ontem sp"
Pergunta Reescrita: "Me mostre as notas fiscais que foram entregues ontem para o estado de São Paulo"
---
Pergunta Original: "o q foi emitido na sem passada"
Pergunta Reescrita: "O que foi emitido na semana passada"
---
Pergunta Original: "notas do cliente acme transp veloz ordene por valor"
Pergunta Reescrita: "Me mostre as notas do cliente ACME da transportadora Veloz, ordenado pelo maior valor da nota fiscal"
---

Pergunta Original: {query}
Pergunta Reescrita:
"""
QUERY_ENHANCER_PROMPT = PromptTemplate.from_template(enhancer_template)


# --- 2. O Parser de JSON (Versão 4.2 - com Lógica de Ambiguidade e Hierarquia) ---
parser_template = """
Você é um assistente especialista que analisa um texto claro e o converte para um objeto JSON de filtros. Sua resposta deve ser APENAS o objeto JSON.

A data de referência para cálculos é {today}.

Analise o texto do usuário e extraia as seguintes entidades:
- "NF", "DE", "ATE", "TipoData", "Cliente", "Transportadora", "UFDestino", "CidadeDestino", "Operacao", "SituacaoNF", "StatusAnaliseData", "CNPJRaizTransp", "SortColumn", "SortDirection".

Mapeamento para "TipoData" (eventos com data, ex: "entregues ontem"):
{{
    "agenda": "1", "entregue": "2", "emitido": "3",
    "previsto": "4", "previsão real": "5", "baixada": "6"
}}

Mapeamento para "Operacao" (propósito do transporte):
Valores possíveis: "InBound-IPO", "InBound-MAO", "InBound-UDI", "OutBound-BAR", "OutBound-BAR-MAT.PRIMA", "OutBound-IPO", "OutBound-MAO", "OutBound-RIO", "OutBound-SPO", "OutBound-UDI".

Mapeamento para "SituacaoNF" (estado logístico ATUAL da nota):
Valores possíveis: "ENTREGUE", "RETIDA", "TRÂNSITO".
- Mapeie sinônimos: "em trânsito", "rodando", "viajando" -> "TRÂNSITO". "retidas" -> "RETIDA".

Mapeamento para "StatusAnaliseData" (status de PERFORMANCE em relação ao prazo):
Valores possíveis: "ATRASO", "DIA SEGUINTE", "DO DIA", "ENTREGUE", "FUTURO", "PREVISTO PARA 2 DIAS".
- Mapeie sinônimos: "atrasado", "com atraso" -> "ATRASO". "previsto para amanhã" -> "DIA SEGUINTE". "previsto para hoje" -> "DO DIA".

Mapeamento para "UFDestino" (estado):
Valores possíveis: "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO".

--- NOVAS REGRAS DE INTELIGÊNCIA ---
Regras de Ambiguidade (TipoData vs. SituacaoNF):
- Se uma palavra como "entregue", "emitido" ou "baixada" for usada JUNTO com um período de tempo (ex: "ontem", "hoje", "na semana passada", "em setembro"), priorize o preenchimento de "TipoData".
- Se uma palavra que descreve um estado (ex: "em trânsito", "retida") for usada sem um período de tempo claro, priorize o preenchimento de "SituacaoNF".
- Se um termo como "entregue" for usado sem um período de tempo, priorize o preenchimento de "SituacaoNF" com o valor 'ENTREGUE'.

Regras de Localização:
- Se o usuário mencionar uma sigla de 2 letras da lista de "UFDestino", preencha o campo "UFDestino".
- Se um nome pode ser tanto cidade quanto estado (ex: "São Paulo"), priorize o preenchimento de "UFDestino" com a sigla correspondente (ex: "SP"), a menos que o usuário especifique "cidade de".
- Extraia o nome da cidade para "CidadeDestino" sempre que possível.
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
- Se o usuário pedir uma ordenação que não corresponde às opções acima, "SortColumn" deve ser null.

Regras Gerais:
- Se uma entidade não for encontrada, seu valor no JSON deve ser null.
- Datas relativas: 'ontem' é {yesterday}, 'hoje' é {today}, 'semana passada' é o período de {last_week_start} a {today}.
- Se a busca for por um número de NF, todos os outros campos devem ser null.

Exemplos:
---
Texto: "Mostre todas as notas com situação 'RETIDA' para o cliente BEXX"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": "BEXX", "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": "RETIDA", "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": "ASC"}}
---
Texto: "Quais notas de operação OutBound-SPO estão com análise de performance 'ATRASO'?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": "OutBound-SPO", "SituacaoNF": null, "StatusAnaliseData": "ATRASO", "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": "ASC"}}
---
Texto: "notas entregues ontem ordenadas pelo maior valor"
JSON: {{"NF": null, "DE": "{yesterday}", "ATE": "{yesterday}", "TipoData": "2", "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": "valor_nf", "SortDirection": "DESC"}}
---
Texto: "quais notas foram para a cidade de Uberlândia em Minas Gerais?"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": "MG", "CidadeDestino": "Uberlândia", "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": "ASC"}}
---

Agora, analise o seguinte texto:
Texto: {enhanced_query}
JSON:
"""
JSON_PARSER_PROMPT = PromptTemplate.from_template(parser_template)