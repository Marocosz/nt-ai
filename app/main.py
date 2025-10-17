# =================================================================================================
# =================================================================================================
#
#                       PONTO DE ENTRADA DO MICROSSERVIÇO DE IA (API)
#
# Visão Geral do Módulo:
#
# Este arquivo é o ponto de entrada principal para o microsserviço FastAPI 'nt-ai'.
# Suas responsabilidades incluem:
#
# 1. Configuração de Logging Robusto:
#    - Implementa um sistema de log que escreve tanto para o console (para desenvolvimento)
#      quanto para um arquivo físico (`nt_ai_service.log`).
#    - Utiliza um `RotatingFileHandler` para gerenciar o tamanho dos arquivos de log,
#      evitando que um único arquivo cresça indefinidamente em produção.
#
# 2. Inicialização da Aplicação FastAPI:
#    - Cria e configura a instância principal da aplicação, incluindo metadados como
#      título e descrição, que são usados para a documentação automática (Swagger/OpenAPI).
#
# 3. Carregamento das Cadeias de IA na Inicialização:
#    - Invoca as funções `create_master_chain()` and `create_debug_chain()` uma única vez
#      quando o servidor é iniciado, através do evento "startup". Esta é uma otimização de 
#      performance crucial para evitar o custo de recarregar os modelos de IA a cada nova requisição.
#
# 4. Definição de Endpoints (Rotas) Assíncronos:
#    - `/parse-query` (POST): O endpoint de produção, otimizado para retornar apenas o
#      resultado final (o JSON de filtros).
#    - `/debug-query` (POST): O endpoint de desenvolvimento e diagnóstico, que retorna
#      os resultados de cada etapa intermediária do processamento da IA.
#
# 5. Validação de Entrada (Pydantic):
#    - Utiliza o modelo `QueryRequest` para garantir que todas as requisições recebidas
#      tenham um corpo (body) JSON válido e com os campos esperados.
#
# =================================================================================================
# =================================================================================================

import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.chains.master_chain import create_master_chain, create_debug_chain
from pathlib import Path

# --- Configuração Avançada do Logging ---

# --- DEFINIÇÃO DE CAMINHO ABSOLUTO PARA O LOG ---
# Pega o caminho absoluto para o diretório raiz do projeto (a pasta que contém a pasta 'app').
# Path(__file__) -> caminho para este arquivo (main.py)
# .parent -> sobe para a pasta 'app'
# .parent -> sobe para a pasta raiz do projeto 'nt-ai'
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LOG_DIR = PROJECT_ROOT / "logs"  # Define o caminho para a pasta de logs.

# Cria o diretório de logs se ele não existir.
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define as constantes para a configuração dos logs, facilitando a manutenção.
LOG_FILE = LOG_DIR / "nt_ai_service.log"
MAX_LOG_SIZE_MB = 5  # Tamanho máximo de 5 MB por arquivo de log.
LOG_BACKUP_COUNT = 5 # Número de arquivos de backup a serem mantidos (ex: .log, .log.1, .log.2...).

# Cria o logger principal para a aplicação. Usar __name__ é uma convenção padrão.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Define o nível mínimo de severidade para as mensagens a serem processadas.

# Cria um formatador para padronizar a aparência de todas as linhas de log.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Cria o handler responsável por escrever os logs em um arquivo com rotação automática.
# Quando o arquivo atinge `maxBytes`, ele é renomeado e um novo é criado.
file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024, # Converte o tamanho de MB para bytes.
    backupCount=LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setFormatter(formatter) # Aplica o formatador a este handler.

# Cria o handler para exibir os logs no console (terminal). Essencial para debug em tempo real.
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Adiciona ambos os handlers ao logger. A partir daqui, qualquer chamada a `logger.info`, `logger.error`,
# etc., será enviada tanto para o arquivo quanto para o console.
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --- Fim da Configuração do Logging ---


# Carrega as variáveis de ambiente do arquivo .env (ex: GROQ_API_KEY).
load_dotenv()

# Cria a instância principal da aplicação FastAPI com metadados para a documentação.
app = FastAPI(
    title="New Tracking Intent AI - Microsserviço de Análise de Intenção",
    description="Traduz texto em linguagem natural para filtros JSON para o sistema New Tracking.",
    version="1.0.0"
)


# Define os objetos das cadeias como globais (iniciados como None).
# Eles serão populados pela função de startup para garantir que sejam carregados apenas uma vez.
master_chain = None
debug_chain = None

@app.on_event("startup")
async def startup_event():
    """
    Função executada uma vez quando a aplicação inicia.
    """
    global master_chain, debug_chain
    logger.info("=============================================")
    logger.info("===     INICIANDO APLICAÇÃO NT-AI         ===")
    logger.info("=============================================")
    logger.info("Carregando as cadeias de LangChain na inicialização...")
    
    # Carrega as cadeias de IA aqui, dentro do evento de startup.
    # Esta é a prática recomendada pelo FastAPI.
    master_chain = create_master_chain()
    debug_chain = create_debug_chain()
    
    logger.info("Cadeias de LangChain carregadas com sucesso.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Função executada uma vez quando a aplicação é encerrada.
    """
    logger.info("=============================================")
    logger.info("===     ENCERRANDO APLICAÇÃO NT-AI        ===")
    logger.info("=============================================")


# Define o formato esperado para o corpo (body) da requisição, usando Pydantic.
# Garante que qualquer requisição para os endpoints tenha uma chave "query" do tipo string.
class QueryRequest(BaseModel):
    query: str

@app.post("/parse-query")
async def parse_query(request: QueryRequest):
    """
    Endpoint de produção. Recebe uma query, processa na cadeia principal
    e retorna o JSON de filtros final.
    """
    try:
        # Loga a chegada da requisição, truncando a query para evitar logs muito longos.
        logger.info(f"Recebida nova requisição em /parse-query para a query: '{request.query[:50]}...'")
        # Invoca a cadeia de forma assíncrona, passando a query do usuário.
        result = await master_chain.ainvoke({"query": request.query})
        return result
    except Exception as e:
        # Em caso de erro, loga o traceback completo (`exc_info=True`) e retorna um erro 500.
        logger.error(f"Erro no endpoint /parse-query para a query: '{request.query}'", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/debug-query")
async def debug_query(request: QueryRequest):
    """
    Endpoint de desenvolvimento. Recebe uma query, processa na cadeia de debug
    e retorna um dicionário com os resultados intermediários (query otimizada e JSON).
    """
    try:
        # Validação de entrada para garantir que a query não seja vazia.
        if not request.query:
            raise HTTPException(status_code=400, detail="A 'query' não pode ser vazia.")
        
        logger.info(f"Recebida nova requisição em /debug-query para a query: '{request.query[:50]}...'")
        # Invoca a cadeia de debug de forma assíncrona.
        result = await debug_chain.ainvoke({"query": request.query})
        
        return result
    except Exception as e:
        logger.error(f"Erro na execução da cadeia de debug para a query: '{request.query}'", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a query com a IA: {str(e)}")

# Comando para rodar a aplicação: uvicorn app.main:app --reload --port 5001