from langchain_core.prompts import PromptTemplate

# --- 1. O Otimizador de Query (Versão 2.0) ---
# Atualizado com exemplos mais complexos para lidar com as novas capacidades de filtro e ordenação.
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


# --- 2. O Parser de JSON (Versão 2.0 - Robusta) ---
# Responsável por traduzir a pergunta JÁ OTIMIZADA em um JSON de filtros completo.
parser_template = """
Você é um assistente especialista que analisa um texto claro e o converte para um objeto JSON de filtros. Sua resposta deve ser APENAS o objeto JSON, sem nenhum texto adicional.

A data de referência para cálculos é {today}.

Analise o texto do usuário e extraia as seguintes entidades:
- "NF": O número da nota fiscal (inteiro).
- "DE": A data de início do período no formato AAAA-MM-DD.
- "ATE": A data de fim do período no formato AAAA-MM-DD.
- "TipoData": O código numérico correspondente ao tipo de data.
- "Cliente": O nome do cliente/tomador.
- "Transportadora": O nome da transportadora/parceiro.
- "UFDestino": A sigla do estado de destino (ex: "SP", "RJ").
- "CidadeDestino": O nome da cidade de destino.
- "Operacao": O tipo de operação (ex: "VENDA").
- "SituacaoNF": O status da nota (ex: "EM TRÂNSITO").
- "StatusAnaliseData": O status da análise de performance (ex: "ATRASADO").
- "CNPJRaizTransp": A raiz de 8 dígitos do CNPJ da transportadora.
- "SortColumn": A coluna pela qual ordenar o resultado.
- "SortDirection": A direção da ordenação ("ASC" para crescente, "DESC" para decrescente).

Mapeamento para "TipoData":
{{
    "agenda": "1",
    "entregue": "2",
    "emitido": "3",
    "previsto": "4",
    "previsão real": "5",
    "baixada": "6"
}}

Mapeamento para Ordenação ("SortColumn"):
- Se o usuário pedir para ordenar por valor da nota, use "valor_nf".
- Se pedir por data de entrega, use "data_entrega".
- Se pedir por data de emissão, use "data_emissao".

Regras:
- Se uma entidade não for encontrada, seu valor no JSON deve ser null.
- Datas relativas: 'ontem' é {yesterday}, 'hoje' é {today}, 'semana passada' é o período de {last_week_start} a {today}.
- Para ordenação, se o usuário pedir "maior valor" ou "mais recente", use "DESC". Se pedir "menor valor" ou "mais antigo", use "ASC". Se não especificar, o padrão é "ASC".
- Se a busca for por um número de NF, todos os outros campos devem ser null.

Exemplos:
---
Texto: "Me mostre as notas fiscais que foram entregues ontem para o estado de São Paulo"
JSON: {{"NF": null, "DE": "{yesterday}", "ATE": "{yesterday}", "TipoData": "2", "Cliente": null, "Transportadora": null, "UFDestino": "SP", "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": "ASC"}}
---
Texto: "qual a nf 12345"
JSON: {{"NF": 12345, "DE": null, "ATE": null, "TipoData": null, "Cliente": null, "Transportadora": null, "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": null, "CNPJRaizTransp": null, "SortColumn": null, "SortDirection": "ASC"}}
---
Texto: "Mostre as notas com status de análise 'ATRASADO' da transportadora 'Veloz' para o cliente 'ACME', ordenado pelo maior valor da nota fiscal"
JSON: {{"NF": null, "DE": null, "ATE": null, "TipoData": null, "Cliente": "ACME", "Transportadora": "Veloz", "UFDestino": null, "CidadeDestino": null, "Operacao": null, "SituacaoNF": null, "StatusAnaliseData": "ATRASADO", "CNPJRaizTransp": null, "SortColumn": "valor_nf", "SortDirection": "DESC"}}
---

Agora, analise o seguinte texto:
Texto: {enhanced_query}
JSON:
"""
JSON_PARSER_PROMPT = PromptTemplate.from_template(parser_template)