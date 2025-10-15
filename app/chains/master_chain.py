# app/chains/master_chain.py

from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from app.core.llm import get_llm
from app.prompts.filter_prompts import QUERY_ENHANCER_PROMPT, JSON_PARSER_PROMPT
from datetime import datetime, timedelta

def _create_chains():
    """Função auxiliar para não repetir a criação das cadeias."""
    llm = get_llm()

    # --- Cadeia 1: Otimizador de Query (inalterada) ---
    query_enhancer_chain = QUERY_ENHANCER_PROMPT | llm | StrOutputParser()

    # --- Cadeia 2: Parser de JSON (AGORA COM CORREÇÃO AUTOMÁTICA) ---
    today = datetime.now()
    prompt_with_dates = JSON_PARSER_PROMPT.partial(
        today=today.strftime('%Y-%m-%d'),
        yesterday=(today - timedelta(days=1)).strftime('%Y-%m-%d'),
        last_week_start=(today - timedelta(days=7)).strftime('%Y-%m-%d')
    )
    
    # --- 2. Criamos o parser de correção ---
    # Ele usa o JsonOutputParser como parser base e o próprio llm para fazer as correções
    output_fixing_parser = OutputFixingParser.from_llm(
        parser=JsonOutputParser(), 
        llm=llm
    )

    # --- 3. A cadeia de parsing agora usa o OutputFixingParser ---
    # A lógica é a mesma, apenas trocamos o parser final.
    json_parser_chain = prompt_with_dates | llm | output_fixing_parser
    
    return query_enhancer_chain, json_parser_chain

def create_master_chain() -> Runnable:
    """
    Cria a cadeia principal de PRODUÇÃO.
    Retorna apenas o JSON final.
    """
    query_enhancer_chain, json_parser_chain = _create_chains()
    
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

    debug_chain = (
        RunnablePassthrough.assign(
            enhanced_query=query_enhancer_chain
        ).assign(
            parsed_json=json_parser_chain
        )
    )
    return debug_chain