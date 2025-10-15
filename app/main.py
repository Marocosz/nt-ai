import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.chains.master_chain import create_master_chain, create_debug_chain

# --- 1. Configuração Avançada do Logging ---

# Define o nome do arquivo e os parâmetros de rotação
LOG_FILE = "nt_ai_service.log"
MAX_LOG_SIZE_MB = 5  # Tamanho máximo de 5 MB por arquivo
LOG_BACKUP_COUNT = 3 # Manter até 3 arquivos de backup (ex: .log, .log.1, .log.2)

# Cria o logger principal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Define o nível mínimo de log a ser capturado

# Cria um formatador para definir como cada linha do log será escrita
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Cria o handler de rotação de arquivo
# Ele vai escrever no arquivo LOG_FILE, com um tamanho máximo e número de backups
file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024, # Converte MB para bytes
    backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter) # Aplica o formatador ao handler

# Cria um handler para o console (para continuar vendo os logs no terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Adiciona AMBOS os handlers ao logger
# Assim, os logs aparecerão no console E serão salvos no arquivo
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --- Fim da Configuração do Logging ---


# Carrega as variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="New Tracking AI - Microsserviço de Análise de Intenção",
    description="Traduz texto em linguagem natural para filtros JSON para o sistema New Tracking.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str

# Cria as cadeias
master_chain = create_master_chain()
debug_chain = create_debug_chain()

@app.post("/parse-query")
async def parse_query(request: QueryRequest):
    try:
        logger.info(f"Recebida nova requisição em /parse-query para a query: '{request.query[:50]}...'")
        result = await master_chain.ainvoke({"query": request.query})
        return result
    except Exception as e:
        logger.error(f"Erro no endpoint /parse-query para a query: '{request.query}'", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/debug-query")
async def debug_query(request: QueryRequest):
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="A 'query' não pode ser vazia.")
        
        logger.info(f"Recebida nova requisição em /debug-query para a query: '{request.query[:50]}...'")
        result = await debug_chain.ainvoke({"query": request.query})
        
        return result
    except Exception as e:
        logger.error(f"Erro na execução da cadeia de debug para a query: '{request.query}'", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a query com a IA: {str(e)}")

# Comando para rodar: uvicorn app.main:app --reload --port 5001