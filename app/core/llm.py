from langchain_groq import ChatGroq
import os

def get_llm():
    """
    Cria e retorna uma instância do LLM da Groq configurado para respostas rápidas.
    """
    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.1-8b-instant",
        # model_name="openai/gpt-oss-120b",
        # model_name="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
    return llm