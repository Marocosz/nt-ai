from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.chains.parser_chain import create_parser_chain

# Carrega as variáveis de ambiente do .env
load_dotenv()

app = FastAPI(
    title="Microsserviço de IA para Análise de Intenção",
    description="Traduz texto em linguagem natural para filtros JSON para o sistema New Tracking.",
    version="1.0.0"
)

# Define o modelo de dados para a requisição
class QueryRequest(BaseModel):
    query: str

# Cria a cadeia de IA
parser_chain = create_parser_chain()

@app.post("/parse-query")
def parse_query(request: QueryRequest):
    """
    Recebe uma query em texto e retorna os filtros estruturados em JSON.
    """
    try:
        user_query = request.query
        if not user_query:
            raise HTTPException(status_code=400, detail="A 'query' não pode ser vazia.")
            
        # Invoca a cadeia de LangChain com a query do usuário
        result = parser_chain.invoke({"query": user_query})
        
        return result
        
    except Exception as e:
        print(f"Erro na execução da cadeia: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a query com a IA.")

# Comando para rodar: uvicorn app.main:app --reload --port 5001