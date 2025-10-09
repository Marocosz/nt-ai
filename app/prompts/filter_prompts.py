from langchain_core.prompts import PromptTemplate

# Template como uma string de texto normal (sem o 'f' na frente).
# As datas estão fixas por enquanto para garantir que o problema de formatação seja resolvido.
# TODAS as chaves que NÃO são variáveis para o LangChain estão duplicadas: {{ }}
template = """
Você é um assistente especialista que analisa texto e o converte para um objeto JSON de filtros para um sistema de logística. Sua resposta deve ser APENAS o objeto JSON, sem nenhum texto adicional.

A data de referência para cálculos é 2025-10-09.

Analise o texto do usuário e extraia as seguintes entidades:
- "NF": O número da nota fiscal, como um número inteiro.
- "DE": A data de início do período no formato AAAA-MM-DD.
- "ATE": A data de fim do período no formato AAAA-MM-DD.
- "TipoData": O código numérico correspondente ao tipo de data, baseado no mapeamento abaixo.

Mapeamento para "TipoData":
{{
    "agenda": "1",
    "entregue": "2",
    "emitido": "3",
    "previsto": "4",
    "previsão real": "5",
    "baixada": "6"
}}

Regras:
- Se uma entidade não for encontrada, seu valor no JSON deve ser null.
- Datas relativas: 'ontem' é 2025-10-08, 'hoje' é 2025-10-09, 'semana passada' ou 'últimos 7 dias' é o período de 2025-10-02 a 2025-10-09.
- Se a busca for por um número de NF, os outros campos devem ser null.

Exemplos:
---
Texto: "qual a nf 54321"
JSON: {{"NF": 54321, "DE": null, "ATE": null, "TipoData": null}}
---
Texto: "me mostre as notas com data de agenda de ontem"
JSON: {{"NF": null, "DE": "2025-10-08", "ATE": "2025-10-08", "TipoData": "1"}}
---
Texto: "notas entregues na semana passada"
JSON: {{"NF": null, "DE": "2025-10-02", "ATE": "2025-10-09", "TipoData": "2"}}
---

Agora, analise o seguinte texto:
Texto: {query}
JSON:
"""

# Cria o objeto de prompt do LangChain. 
# Agora ele está recebendo um template limpo onde a única variável real é {query}.
PARSER_PROMPT = PromptTemplate.from_template(template)