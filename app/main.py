from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
# Importamos as duas funções de criação de cadeia
from app.chains.master_chain import create_master_chain, create_debug_chain

# Carrega as variáveis de ambiente (GROQ_API_KEY)
load_dotenv()

app = FastAPI(
    title="New Tracking AI - Microsserviço de Análise de Intenção",
    description="Traduz texto em linguagem natural para filtros JSON para o sistema New Tracking.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str

# Cria as duas cadeias na inicialização
master_chain = create_master_chain()
debug_chain = create_debug_chain() # Nova cadeia para debug

# --- Endpoint de Produção (inalterado) ---
@app.post("/parse-query")
def parse_query(request: QueryRequest):
    try:
        result = master_chain.invoke({"query": request.query})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# --- NOVO ENDPOINT DE DEBUG ---
@app.post("/debug-query")
def debug_query(request: QueryRequest):
    """
    Endpoint de teste que retorna os passos intermediários da análise da IA.
    """
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="A 'query' não pode ser vazia.")
        
        # Invoca a cadeia de debug
        result = debug_chain.invoke({"query": request.query})
        
        # O resultado agora contém 'enhanced_query' e 'parsed_json'
        return result
        
    except Exception as e:
        print(f"Erro na execução da cadeia de debug: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a query com a IA: {str(e)}")

# Comando para rodar: uvicorn app.main:app --reload --port 5001