import calendar
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from app.core.llm import get_llm
from app.prompts.filter_prompts import QUERY_ENHANCER_PROMPT, JSON_PARSER_PROMPT
from datetime import datetime, timedelta

def _create_chains():
    """Função auxiliar para não repetir a criação das cadeias."""
    llm = get_llm()
    query_enhancer_chain = QUERY_ENHANCER_PROMPT | llm | StrOutputParser()

    # --- LÓGICA DE CÁLCULO DE DATAS ---
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

    prompt_with_dates = JSON_PARSER_PROMPT.partial(
        today=today.strftime('%Y-%m-%d'),
        yesterday=(today - timedelta(days=1)).strftime('%Y-%m-%d'),
        last_week_start=(today - timedelta(days=7)).strftime('%Y-%m-%d'),
        week_start=start_of_week.strftime('%Y-%m-%d'),
        week_end=end_of_week.strftime('%Y-%m-%d'),
        month_start=start_of_month.strftime('%Y-%m-%d'),
        month_end=end_of_month.strftime('%Y-%m-%d'),
        semester_start=start_of_semester.strftime('%Y-%m-%d'),
        semester_end=end_of_semester.strftime('%Y-%m-%d')
    )
    
    output_fixing_parser = OutputFixingParser.from_llm(parser=JsonOutputParser(), llm=llm)
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