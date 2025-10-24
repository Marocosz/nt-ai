from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def get_llm_groq():
    """
    Cria e retorna uma instância do LLM da Groq configurado para respostas rápidas.
    """
    # Cria a instância do ChatGroq
    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.1-8b-instant",
        # model_name="openai/gpt-oss-120b",
        # model_name="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
    return llm


def get_llm_google():
    """
    Retorna uma instância configurada do modelo Google Gemini via Google AI Studio.
    """
    # Cria a instância do ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,                  
        google_api_key=os.getenv("GOOGLE_API_KEY")  
    )

    # Imprime no console qual LLM está sendo carregado (útil para debug)
    print(f"INFO: Usando LLM: Google Gemini ({llm.model})")

    # Retorna a instância configurada do LLM
    return llm