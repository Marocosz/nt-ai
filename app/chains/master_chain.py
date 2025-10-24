# =================================================================================================
# =================================================================================================
#
#                               MÓDULO DE ORQUESTRAÇÃO DA CADEIA DE INTERPRETAÇÃO
#
# Visão Geral da Arquitetura Lógica:
#
# Este arquivo constrói e orquestra as cadeias de LangChain responsáveis por interpretar
# a linguagem natural do usuário e traduzi-la para um objeto JSON estruturado.
# A arquitetura segue o princípio de "Separação de Responsabilidades", operando como uma
# linha de montagem em dois estágios principais:
#
# 1. A Cadeia de Normalização (`query_enhancer_chain`):
#    - Atua como um "Tradutor" de linguagem.
#    - Responsabilidade: Receber a pergunta bruta do usuário e normalizá-la de forma
#      segura e previsível, sem alterar a intenção original.
#    - Ação: Expande abreviações (ex: "nf" -> "nota fiscal") e mapeia sinônimos de
#      negócio (ex: "rodando" -> "em trânsito").
#
# 2. A Cadeia de Parsing (`json_parser_chain`):
#    - Atua como um "Especialista em Extração".
#    - Responsabilidade: Receber a pergunta já normalizada e convertê-la em um
#      objeto JSON preciso, com base em um conjunto de regras e exemplos.
#    - Ação: Extrai todas as entidades relevantes (datas, status, locais, ordenação)
#      diretamente para o formato JSON.
#    - (NOTA: A técnica Chain of Thought foi desativada por questões de performance/rate limit).
#
# 3. Resiliência (`OutputFixingParser`):
#    - A cadeia de parsing é equipada com um parser de auto-correção. Se o LLM gerar
#      um JSON com erro de sintaxe, esta ferramenta automaticamente solicita ao LLM
#      que corrija seu próprio erro, aumentando a confiabilidade do serviço.
#
# =================================================================================================
# =================================================================================================

import calendar
import re # [!] ATENÇÃO: Importado para a função _extract_json_from_output (CoT), atualmente desativada.
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda # [!] RunnableLambda importado para CoT, atualmente desativado.
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from app.core.llm import get_llm_groq, get_llm_google
from app.prompts.filter_prompts import QUERY_ENHANCER_PROMPT, JSON_PARSER_PROMPT
from datetime import datetime, timedelta

def _get_current_dates(data_passthrough):
    """
    Calcula todas as datas dinâmicas no momento da execução da cadeia.
    Esta função será chamada para CADA requisição, garantindo que valores
    como 'today', 'week_start', etc., estejam sempre atualizados.
    O argumento `data_passthrough` recebe os dados que já estão no fluxo da cadeia,
    mas não é utilizado aqui; está presente para compatibilidade com o `.assign()`.
    """
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    start_of_month = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    end_of_month = today.replace(day=days_in_month)
    if today.month <= 6:
        start_of_semester = today.replace(month=1, day=1)
        end_of_semester = today.replace(month=6, day=30)
    else:
        start_of_semester = today.replace(month=7, day=1)
        end_of_semester = today.replace(month=12, day=31)

    # `start_of_week` é esta segunda-feira (ou o dia atual se for segunda).
    # Subtrai 1 dia para obter o domingo passado (fim da última semana).
    end_of_last_week = start_of_week - timedelta(days=1)
    # Subtrai 6 dias do domingo passado para obter a segunda-feira passada (início da última semana).
    start_of_last_week = end_of_last_week - timedelta(days=6)

    # Retorna um dicionário com todas as datas formatadas como string.
    return {
        "today": today.strftime('%Y-%m-%d'),
        "yesterday": (today - timedelta(days=1)).strftime('%Y-%m-%d'),
        
        # "last_week_start" agora se refere ao início da semana de calendário passada.
        "last_week_start": start_of_last_week.strftime('%Y-%m-%d'),
        "last_week_end": end_of_last_week.strftime('%Y-%m-%d'),

        "week_start": start_of_week.strftime('%Y-%m-%d'),
        "week_end": end_of_week.strftime('%Y-%m-%d'),
        "month_start": start_of_month.strftime('%Y-%m-%d'),
        "month_end": end_of_month.strftime('%Y-%m-%d'),
        "semester_start": start_of_semester.strftime('%Y-%m-%d'),
        "semester_end": end_of_semester.strftime('%Y-%m-%d')
    }

# --- Bloco de Funções Auxiliares para o Parser (CoT) ---
# [!] ESTA FUNÇÃO E O CHAIN OF THOUGHT ESTÃO ATUALMENTE DESATIVADOS [!]
def _extract_json_from_output(llm_output: str) -> str:
    """
    (Atualmente Inativa) Encontra e extrai o bloco JSON da saída do LLM
    quando a técnica Chain of Thought está ativa.
    Procura o marcador "JSON FINAL" e extrai o JSON que vem depois.
    """
    # Divide a saída pelo marcador "JSON FINAL", ignorando maiúsculas/minúsculas e espaços
    parts = re.split(r'JSON FINAL\s*:?', llm_output, flags=re.IGNORECASE)
    
    json_part_to_parse = llm_output # Por padrão, tenta parsear a saída inteira

    if len(parts) > 1:
        # Se o marcador foi encontrado, pega a última parte, que deve ser o JSON
        json_part_to_parse = parts[-1]
    
    # Tenta encontrar o primeiro JSON válido (iniciando com { e terminando com })
    match = re.search(r'\{.*\}', json_part_to_parse, re.DOTALL)
    
    if match:
        # Retorna o JSON encontrado
        return match.group(0)
    
    # Se nenhum JSON for encontrado (ex: erro do LLM ou formato inesperado),
    # retorna um JSON vazio para o OutputFixingParser tentar corrigir.
    return "{}"
# --- Fim do Bloco de Funções Auxiliares (Desativado) ---


def _create_chains():
    """
    Função "fábrica" auxiliar para construir e configurar os componentes base das cadeias.
    Esta função é chamada uma vez na inicialização para criar os objetos reutilizáveis.
    """
    llm = get_llm_google()
    # llm = get_llm_groq()
    
    # --- Definição da Cadeia de Normalização (Enhancer) ---
    query_enhancer_chain = QUERY_ENHANCER_PROMPT | llm | StrOutputParser()
    
    # --- Definição da Cadeia de Parsing com Auto-Correção ---
    # O OutputFixingParser é usado para tentar corrigir/validar a saída do LLM como JSON.
    output_fixing_parser = OutputFixingParser.from_llm(parser=JsonOutputParser(), llm=llm)
    
    # ==================================================================
    # --- CONFIGURAÇÃO DA CADEIA DE PARSING ---
    # ==================================================================
    #
    # Fluxo Atual (CoT Desativado):
    # 1. `JSON_PARSER_PROMPT | llm`: O prompt é enviado ao LLM.
    # 2. `| StrOutputParser()`: A saída (esperada como string JSON) é capturada.
    # 3. `| output_fixing_parser`: O parser tenta corrigir e validar o JSON.
    #
    # Fluxo Anterior (CoT Ativado - linha comentada abaixo):
    # O CoT gerava "Pensamento + JSON FINAL:", exigindo um passo extra (`RunnableLambda`)
    # para extrair o JSON antes de passar ao `output_fixing_parser`.
    # Foi desativado devido a performance/rate limits (ver função _extract_json_from_output).
    #
    json_parser_chain = (
        JSON_PARSER_PROMPT
        | llm
        | StrOutputParser() # Captura a saída do LLM como string
        # | RunnableLambda(_extract_json_from_output)  # [CoT DESATIVADO] Extrairia o JSON do "Pensamento"
        | output_fixing_parser # Tenta parsear/corrigir o JSON
    )
    # ==================================================================
    # --- FIM DA CONFIGURAÇÃO ---
    # ==================================================================
    
    return query_enhancer_chain, json_parser_chain


def create_master_chain() -> Runnable:
    """
    Cria a cadeia principal de PRODUÇÃO.
    Esta cadeia orquestra o fluxo completo, injetando as datas atuais a cada
    execução, passando pela normalização e pelo parsing, e retornando o JSON final.
    """
    query_enhancer_chain, json_parser_chain = _create_chains()
    
    # A linha de montagem:
    # 1. RunnablePassthrough.assign(dates=...): Calcula as datas atuais e adiciona ao fluxo.
    # 2. .assign(enhanced_query=...): Passa o fluxo (query + datas) para o Enhancer
    #    e adiciona o resultado como 'enhanced_query'.
    # 3. | (lambda...): Reorganiza o dicionário para preparar a entrada do Parser,
    #    colocando 'dates' e 'enhanced_query' no nível raiz.
    # 4. | json_parser_chain: Passa o dicionário preparado para a cadeia de parsing,
    #    que gera o JSON final.
    master_chain = (
        RunnablePassthrough.assign(dates=_get_current_dates)
        .assign(
            enhanced_query=query_enhancer_chain
        )
        | (lambda x: {**x["dates"], "enhanced_query": x["enhanced_query"]})
        | json_parser_chain
    )
    return master_chain

def create_debug_chain() -> Runnable:
    """
    Cria a cadeia de DEBUG.
    Funciona de forma idêntica à master_chain, mas retorna os resultados de cada
    passo intermediário ('dates', 'enhanced_query', 'parsed_json') para facilitar a depuração.
    """
    query_enhancer_chain, json_parser_chain = _create_chains()
    
    # Prepara o passo de transformação de dados para o parser (idêntico ao master_chain)
    debug_parser_input = (lambda x: {**x["dates"], "enhanced_query": x["enhanced_query"]})
    
    # A linha de montagem de debug:
    # Executa os mesmos passos do master_chain, mas usa .assign() extra
    # para preservar os resultados intermediários ('dates', 'enhanced_query')
    # e adicionar o resultado final do parser sob a chave 'parsed_json'.
    debug_chain = (
        RunnablePassthrough.assign(dates=_get_current_dates) # Passo 1: Calcula datas
        .assign(
            enhanced_query=query_enhancer_chain # Passo 2: Roda o Enhancer
        ).assign( # Passo 3 & 4 combinados: Prepara input, Roda Parser e guarda resultado
            parsed_json = debug_parser_input | json_parser_chain
        )
    )
    return debug_chain

# =================================================================================================
# Análise de Fluxo e Dados das Cadeias (Chains)
# =================================================================================================
#
# 1. query_enhancer_chain
# Propósito: Normalizar a pergunta do usuário de forma segura, traduzindo sinônimos.
# Fluxo Detalhado:
#   1. Recebe a pergunta do usuário (ex: "notas rodando").
#   2. Monta o QUERY_ENHANCER_PROMPT com a pergunta.
#   3. Envia para o LLM, que traduz para os termos de negócio (ex: "notas em trânsito").
#   4. O StrOutputParser garante que a saída seja uma string de texto limpa.
# Exemplo de Entrada:
#   { "query": "notas rodando ordenadas pelo mais caro", "dates": { ... } }
# Exemplo de Saída (string):
#   "Me mostre as notas fiscais em trânsito ordenadas pelo maior valor"
#
# -------------------------------------------------------------------------------------------------
#
# 2. json_parser_chain
# Propósito: Converter a pergunta normalizada em um objeto JSON estruturado.
# Fluxo Detalhado (CoT Desativado):
#   1. Recebe o dicionário completo com a pergunta normalizada ('enhanced_query') e todas as datas.
#   2. O JSON_PARSER_PROMPT usa as chaves do dicionário para preencher todas as suas
#      variáveis (ex: {today}, {week_start}, {enhanced_query}).
#   3. Envia para o LLM, que gera uma string (idealmente formatada como JSON).
#   4. O StrOutputParser captura essa string de saída.
#   5. O OutputFixingParser tenta parsear a string como JSON. Se falhar, ele pede ao LLM
#      para corrigir a sintaxe e tenta parsear novamente.
# Exemplo de Entrada:
#   {
#     "today": "2025-10-22", "last_week_start": "2025-10-13", ...
#     "enhanced_query": "Me mostre as notas fiscais em trânsito ordenadas pelo maior valor"
#   }
# Exemplo de Saída (objeto Python após parsing):
#   {
#     "SituacaoNF": "TRÂNSITO",
#     "SortColumn": "valor_nf",
#     "SortDirection": "DESC",
#     ... (outros campos nulos)
#   }
#
# =================================================================================================