from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from app.core.llm import get_llm
from app.prompts.filter_prompts import QUERY_ENHANCER_PROMPT, JSON_PARSER_PROMPT
from datetime import datetime, timedelta

def _create_chains():
    """Função auxiliar para não repetir a criação das cadeias."""
    llm = get_llm()

    # --- Cadeia 1: Otimizador de Query ---
    query_enhancer_chain = QUERY_ENHANCER_PROMPT | llm | StrOutputParser()

    # --- Cadeia 2: Parser de JSON ---
    today = datetime.now()
    prompt_with_dates = JSON_PARSER_PROMPT.partial(
        today=today.strftime('%Y-%m-%d'),
        yesterday=(today - timedelta(days=1)).strftime('%Y-%m-%d'),
        last_week_start=(today - timedelta(days=7)).strftime('%Y-%m-%d')
    )
    json_parser_chain = prompt_with_dates | llm | JsonOutputParser()
    
    return query_enhancer_chain, json_parser_chain

def create_master_chain() -> Runnable:
    """
    Cria a cadeia principal de PRODUÇÃO.
    Retorna apenas o JSON final.
    """
    query_enhancer_chain, json_parser_chain = _create_chains()
    
    # A linha de montagem: otimiza e depois parseia.
    master_chain = (
        RunnablePassthrough.assign(
            enhanced_query=query_enhancer_chain
        )
        | json_parser_chain
    )
    return master_chain

def create_debug_chain() -> Runnable:
    """
    Cria a cadeia de DEBUG.
    Retorna um dicionário com os passos intermediários.
    """
    query_enhancer_chain, json_parser_chain = _create_chains()

    # A linha de montagem de debug:
    debug_chain = (
        RunnablePassthrough.assign(
            enhanced_query=query_enhancer_chain # Passo 1: Otimiza e guarda em 'enhanced_query'
        ).assign(
            parsed_json=json_parser_chain     # Passo 2: Parseia e guarda em 'parsed_json'
        )
    )
    return debug_chain