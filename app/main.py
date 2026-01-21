# =================================================================================================
# =================================================================================================
#
#                               PONTO DE ENTRADA DO MICROSSERVIÇO DE IA (API)
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
#      resultado final (o JSON de filtros). Valida o JSON e retorna erro 400 se for nulo.
#    - `/debug-query` (POST): O endpoint de desenvolvimento e diagnóstico, que retorna
#      os resultados de cada etapa intermediária. Valida o JSON interno e retorna erro 400 se for nulo.
#
# 5. Validação de Entrada (Pydantic):
#    - Utiliza o modelo `QueryRequest` para garantir que todas as requisições recebidas
#      tenham um corpo (body) JSON válido e com os campos esperados.
#
# =================================================================================================
# =================================================================================================

import time
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ValidationError # <-- Adicionado ValidationError
from dotenv import load_dotenv
from app.chains.master_chain import create_master_chain, create_debug_chain
from app.core.schemas import ParsedFilters
from pathlib import Path

# --- Configuração Avançada do Logging ---

# --- DEFINIÇÃO DE CAMINHO ABSOLUTO PARA O LOG ---
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "nt_ai_service.log"
MAX_LOG_SIZE_MB = 5
LOG_BACKUP_COUNT = 5

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024,
    backupCount=LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
# --- Fim da Configuração do Logging ---


# Carrega as variáveis de ambiente do arquivo .env (API Keys, CA_BUNDLE_PATH)
load_dotenv()


# Cria a instância principal da aplicação FastAPI com metadados para a documentação.
app = FastAPI(
    title="New Tracking Intent AI - Microsserviço de Análise de Intenção",
    description="Traduz texto em linguagem natural para filtros JSON para o sistema New Tracking.",
    version="1.0.0"
)


# Define os objetos das cadeias como globais (iniciados como None).
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
class QueryRequest(BaseModel):
    query: str


def is_all_null(data):
    """
    Função auxiliar para verificar se todos os valores em um dicionário são None (null).
    Retorna True se todos forem None, False caso contrário.
    """
    if not isinstance(data, dict):
        return False
    if not data:
        return True
    return all(value is None for value in data.values())


@app.post("/parse-query")
async def parse_query(request: QueryRequest):
    """
    Endpoint de produção. Recebe uma query, processa na cadeia principal,
    valida o JSON semanticamente e retorna o resultado, OU um erro 400/500.
    """
    start_request_time = time.time()
    try:
        # Validação de entrada básica
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A 'query' não pode ser vazia.")

        logger.info(f"Recebida nova requisição em /parse-query para a query: '{request.query[:50]}...'")
        # 1. Obter o resultado bruto da cadeia (já deve ser um dict após OutputFixingParser)
        raw_result_dict = await master_chain.ainvoke({"query": request.query})

        try:
            # 2. Tentar validar/parsear o dicionário usando o modelo Pydantic
            validated_result = ParsedFilters(**raw_result_dict)
            # Se chegou aqui, a estrutura, tipos e valores (Literals) estão corretos.
            # Usaremos o dicionário gerado pelo Pydantic para garantir consistência e remover campos extras se houver.
            result_dict_to_return = validated_result.model_dump(exclude_unset=True) # Exclui campos que não foram definidos (permanecem None)

        except ValidationError as e:
            # 3. Se a validação Pydantic falhar (tipo errado, valor inválido, etc.)
            logger.error(f"Falha na validação Pydantic para query '{request.query}': {e.errors()}", exc_info=False)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # 500 indica falha interna (IA gerou JSON inválido)
                detail="Erro interno: A IA gerou uma estrutura JSON com dados inválidos após a análise."
            )

        # 4. Checar se o JSON VALIDADO é totalmente nulo
        if is_all_null(result_dict_to_return):
            logger.warning(f"Consulta vaga/irrelevante detectada para query: '{request.query}'. Retornando erro 400.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A consulta fornecida é muito vaga, irrelevante ou não pôde ser interpretada. Por favor, seja mais específico."
            )

        duration_request = time.time() - start_request_time
        logger.info(f"TIMING: Requisição /parse-query completa levou {duration_request:.2f} segundos.")

        # 5. Retornar o dicionário validado e não-nulo
        return result_dict_to_return

    except HTTPException as http_exc:
        # Re-levanta exceções HTTP (como a nossa 400 ou a 500 da validação)
        raise http_exc
    except Exception as e:
        logger.error(f"Erro inesperado no endpoint /parse-query para a query: '{request.query}'", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {str(e)}")


@app.post("/debug-query")
async def debug_query(request: QueryRequest):
    """
    Endpoint de desenvolvimento. Retorna resultados intermediários,
    valida o JSON interno semanticamente, OU retorna um erro 400/500.
    """
    start_request_time = time.time()
    try:
        if not request.query or not request.query.strip():
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A 'query' não pode ser vazia.")

        logger.info(f"Recebida nova requisição em /debug-query para a query: '{request.query[:50]}...'")
        # 1. Obter o resultado bruto completo da cadeia de debug
        raw_debug_result = await debug_chain.ainvoke({"query": request.query})

        # 2. Extrair o dicionário JSON que precisa ser validado
        parsed_json_dict = raw_debug_result.get("parsed_json")

        validated_parsed_json_dict = None # Inicializa
        if isinstance(parsed_json_dict, dict): # Só valida se for um dicionário
            try:
                # 3. Tentar validar/parsear o dicionário JSON interno
                validated_result = ParsedFilters(**parsed_json_dict)
                # Guarda o dicionário validado para substituir no resultado final
                validated_parsed_json_dict = validated_result.model_dump(exclude_unset=True)

            except ValidationError as e:
                # 4. Se a validação Pydantic falhar
                logger.error(f"Falha na validação Pydantic (debug) para query '{request.query}': {e.errors()}", exc_info=False)
                # Mesmo no debug, é um erro interno da IA gerar JSON inválido
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro interno: A IA gerou uma estrutura JSON interna com dados inválidos. Erros: {e.errors()}"
                )
        else:
             # Se o parsed_json não for um dict (ex: erro no OutputFixingParser retornou string ou None)
             logger.error(f"Resultado 'parsed_json' não é um dicionário para query '{request.query}'. Valor: {parsed_json_dict}")
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno: Falha ao obter o JSON interno para validação."
             )

        # 5. Checar se o JSON VALIDADO é totalmente nulo
        if is_all_null(validated_parsed_json_dict):
            logger.warning(f"Consulta vaga/irrelevante detectada (debug) para query: '{request.query}'. Retornando erro 400.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A consulta fornecida é muito vaga, irrelevante ou não pôde ser interpretada (JSON final seria nulo)."
            )

        duration_request = time.time() - start_request_time
        logger.info(f"TIMING: Requisição /debug-query completa levou {duration_request:.2f} segundos.")

        # 6. Substitui o 'parsed_json' original pelo validado no resultado de debug ANTES de retornar
        raw_debug_result["parsed_json"] = validated_parsed_json_dict
        return raw_debug_result # Retorna a estrutura completa do debug com o JSON validado

    except HTTPException as http_exc:
        # Re-levanta exceções HTTP (como a 400 ou 500)
        raise http_exc
    except Exception as e:
        logger.error(f"Erro inesperado na execução da cadeia de debug para a query: '{request.query}'", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno ao processar a query com a IA: {str(e)}")

# Comando para rodar a aplicação: uvicorn app.main:app --reload --port 5001 --reload-dir app
