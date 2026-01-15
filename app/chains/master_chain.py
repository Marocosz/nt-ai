# =================================================================================================
# =================================================================================================
#
#                               MÓDULO DE ORQUESTRAÇÃO DA CADEIA DE INTERPRETAÇÃO
#
# Visão Geral da Arquitetura Lógica (ATUALIZADO - MODO UNIFICADO/TURBO):
#
# Este arquivo constrói e orquestra a cadeia de LangChain responsável por interpretar
# a linguagem natural do usuário.
#
# MUDANÇA ARQUITETURAL:
# Originalmente, o sistema operava em dois estágios (Normalização -> Parsing).
# Para reduzir a latência e custos, migramos para um estágio único UNIFICADO.
#
# 1. A Cadeia Unificada (`json_parser_chain`):
#    - Atua como "Tradutor" e "Extrator" simultaneamente.
#    - Responsabilidade: Recebe a pergunta bruta (`original_query`), aplica as regras de
#      normalização internamente (mentalmente) e extrai o JSON final em uma única chamada.
#    - Ação: Input do Usuário -> Prompt Unificado -> LLM -> JSON.
#
# 2. Resiliência:
#    - Mantemos a estrutura preparada para `OutputFixingParser`, mas atualmente usamos
#      `JsonOutputParser` direto para maximizar a velocidade.
#
# =================================================================================================
# =================================================================================================

import time 
import logging
import calendar
import re 
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda 
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from app.core.llm import get_llm_google, get_llm_groq, get_llm_openai
from app.prompts.filter_prompts import QUERY_ENHANCER_PROMPT, JSON_PARSER_PROMPT
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger(__name__)


# --- Configuração do Timezone (Hardcoded) ---
HARDCODED_TIMEZONE_STR = "America/Sao_Paulo"
try:
    APP_TZ = ZoneInfo(HARDCODED_TIMEZONE_STR)
    logger.info(f"Usando timezone (hardcoded): {HARDCODED_TIMEZONE_STR}")
except ZoneInfoNotFoundError:
    # Fallback muito improvável com string hardcoded válida, mas seguro ter.
    logger.error(f"Timezone hardcoded '{HARDCODED_TIMEZONE_STR}' é inválido! Usando UTC como fallback.")
    APP_TZ = ZoneInfo("UTC")
# --- Fim da Configuração do Timezone ---


def _get_current_dates(data_passthrough):
    """
    Calcula todas as datas dinâmicas no momento da execução da cadeia.
    Esta função será chamada para CADA requisição, garantindo que valores
    como 'today', 'week_start', etc., estejam sempre atualizados.
    O argumento `data_passthrough` recebe os dados que já estão no fluxo da cadeia,
    mas não é utilizado aqui; está presente para compatibilidade com o `.assign()`.
    """
    today = datetime.now(APP_TZ)
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
# --- Fim do Bloco de Funções Auxiliares (CoT Desativado) ---


def log_llm_call_time(step_name: str, start_time: float, result: any):
    """
    Calcula a duração, loga o tempo da chamada LLM e retorna o resultado original.
    """
    duration = time.time() - start_time
    logger.info(f"TIMING: Chamada LLM '{step_name}' levou {duration:.2f} segundos.")
    return result # Retorna o resultado da chamada LLM para continuar a cadeia


def _create_chains():
    """
    Função "fábrica" auxiliar para construir e configurar os componentes base das cadeias.
    Esta função é chamada uma vez na inicialização para criar os objetos reutilizáveis.
    """
    llm = get_llm_google()
    # llm = get_llm_groq()
    # llm = get_llm_openai()

    # --- Definição da Cadeia de Normalização (Enhancer) ---
    # [ATUALIZAÇÃO TURBO]: O Enhancer foi incorporado ao Parser Unificado.
    # Não instanciamos mais o query_enhancer_chain separado para economizar tempo.
    
    # --- Definição da Cadeia de Parsing Unificada com Timing ---
    
    # output_fixing_parser = OutputFixingParser.from_llm(parser=JsonOutputParser(), llm=llm)
    # Parser simples (substitui o output fixing parser para velocidade máxima)
    json_parser = JsonOutputParser()

    # Passo 1 (Parser Unificado): Prepara o prompt e o LLM principal
    parser_prompt_llm = JSON_PARSER_PROMPT | llm

    json_parser_chain = (
        # Passo A: Captura o tempo inicial ANTES da chamada LLM principal
        RunnablePassthrough.assign(start_time=lambda x: time.time())
        # Passo B: Executa a chamada LLM principal (Prompt + LLM). O resultado é AIMessage.
        .assign(llm_output=lambda x: parser_prompt_llm.invoke(x))
        # Passo C: Loga o tempo usando o start_time e o llm_output
        | RunnableLambda(lambda x: log_llm_call_time("UnifiedParser", x['start_time'], x['llm_output']))
        # Passo D: Aplica o StrOutputParser DEPOIS do log
        | StrOutputParser()
        # [CoT DESATIVADO] - A linha abaixo seria necessária se CoT estivesse ativo
        # | RunnableLambda(_extract_json_from_output)
        # Passo E: Parser final para JSON
        # | output_fixing_parser # Substituído por json_parser para testes sem auto-correção
        | json_parser
    )

    # Retornamos apenas o parser chain agora (o enhancer é None ou ignorado)
    return None, json_parser_chain



def create_master_chain() -> Runnable:
    """
    Cria a cadeia principal de PRODUÇÃO.
    Esta cadeia orquestra o fluxo completo (UNIFICADO), injetando as datas atuais,
    passando a query original para o prompt unificado e retornando o JSON.
    """
    _, json_parser_chain = _create_chains()

    # A linha de montagem simplificada (Modo Turbo):
    # 1. RunnablePassthrough.assign(dates=...): Calcula as datas atuais.
    # 2. Renomeia a entrada 'query' para 'original_query' (esperado pelo novo prompt).
    # 3. | json_parser_chain: Executa a extração direta.
    master_chain = (
        RunnablePassthrough.assign(dates=_get_current_dates)
        .assign(original_query=lambda x: x["query"])
        | (lambda x: {**x["dates"], "original_query": x["original_query"]})
        | json_parser_chain
    )
    return master_chain

def create_debug_chain() -> Runnable:
    """
    Cria a cadeia de DEBUG.
    Funciona de forma idêntica à master_chain na nova arquitetura unificada.
    """
    _, json_parser_chain = _create_chains()

    # Prepara o passo de transformação de dados para o parser
    debug_parser_input = (lambda x: {**x["dates"], "original_query": x["original_query"]})

    # A linha de montagem de debug:
    debug_chain = (
        RunnablePassthrough.assign(dates=_get_current_dates)
        .assign(original_query=lambda x: x["query"])
        .assign(
            parsed_json = debug_parser_input | json_parser_chain
        )
    )
    return debug_chain

# =================================================================================================
# Análise de Fluxo e Dados das Cadeias (Chains) - ATUALIZADO
# =================================================================================================
#
# 1. json_parser_chain (UNIFICADO)
# Propósito: Receber a pergunta bruta e converter DIRETAMENTE em JSON estruturado.
# Fluxo Detalhado:
#   1. Recebe o dicionário com 'original_query' e todas as datas.
#   2. O JSON_PARSER_PROMPT (Unificado) aplica as regras de tradução mentalmente.
#   3. (Timing Inicia) Envia para o LLM. (Timing Termina)
#   4. O StrOutputParser captura a string de saída.
#   5. O JsonOutputParser converte a string para objeto Python.
# Exemplo de Entrada:
#   {
#     "today": "2025-10-27", ...
#     "original_query": "notas rodando ordenadas pelo mais caro"
#   }
# Exemplo de Saída:
#   {
#     "SituacaoNF": "TRÂNSITO",
#     "SortColumn": "valor_nf",
#     "SortDirection": "DESC",
#     ...
#   }
#
# =================================================================================================