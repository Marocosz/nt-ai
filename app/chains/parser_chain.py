from langchain_core.runnables import Runnable
from langchain_core.output_parsers import JsonOutputParser
from app.core.llm import get_llm
from app.prompts.filter_prompts import PARSER_PROMPT

def create_parser_chain() -> Runnable:
    """
    Cria a cadeia de LangChain que:
    1. Recebe a query do usuário.
    2. Insere a query no prompt.
    3. Envia o prompt para o LLM.
    4. Converte a resposta em texto para um JSON limpo e validado.
    """
    llm = get_llm()
    parser = JsonOutputParser()

    # A cadeia agora é mais simples: o prompt só espera a 'query'.
    chain = PARSER_PROMPT | llm | parser

    return chain