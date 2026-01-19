# =================================================================================================
# =================================================================================================
#
#                               SCRIPT DE TESTE DE INTEGRAÇÃO ROBUSTO (DEBUG RUNNER v3 - AUDITOR)
#
# Visão Geral do Módulo:
#
# Este script é uma ferramenta de linha de comando resiliente para realizar testes de
# integração no microsserviço 'nt-ai'. Ele é projetado para rodar de forma autônoma
# e lidar com falhas de rede, timeouts e limites de taxa (rate limiting) da API.
#
# ATUALIZAÇÃO v3 (AUDITOR):
# Agora valida automaticamente o JSON de resposta contra um resultado esperado definido
# no arquivo de texto (separado por '||').
#
# Arquitetura e Fluxo de Trabalho:
#
# 1. Leitura do Arquivo de Testes:
#    - Lê um arquivo de texto linha por linha, ignorando comentários.
#    - Faz o parse da linha para separar a PERGUNTA do JSON ESPERADO.
#
# 2. Execução em Loop com Retentativas (A Lógica Principal):
#    - Itera sobre cada query. Para cada query, ele entra em um loop de "tentativa infinita".
#    - Ele SÓ passará para a próxima query (ex: Teste #2) após o teste atual
#      (ex: Teste #1) ser concluído com um `status_code == 200` OU receber um erro 4xx (cliente).
#    - Ele TENTARÁ NOVAMENTE apenas em caso de erros 5xx (servidor) ou falhas de conexão/timeout.
#
# 3. Tratamento de Erros de Conexão e Timeout:
#    - Se o script não conseguir conectar ao microsserviço ou se a requisição estourar
#      o `timeout` (uma `RequestException`), ele imprimirá o erro, aguardará o
#      `RETRY_DELAY` (ex: 60 segundos) e tentará a *mesma query* novamente.
#
# 4. Tratamento de Erros de API (Rate Limiting, Erros 4xx vs 5xx):
#    - Se a API retornar um erro 4xx (ex: 400 Bad Request por query vaga), o script
#      registrará o erro como resultado final e passará para o próximo teste.
#    - Se a API retornar um erro 5xx (ex: 500 Internal Server Error),
#      o script imprimirá o erro, aguardará o `RETRY_DELAY` e
#      tentará a *mesma query* novamente.
#
# 5. Controle de Taxa Preventivo:
#    - Roda em lotes de 10. Após cada lote, faz uma pausa longa de 5 minutos
#    - para evitar o banimento da API por "uso abusivo".
#
# Como Usar:
# > python scripts/debug_runner.py testes.txt
#
# =================================================================================================
# =================================================================================================

import requests
import json
import time
import sys
import datetime
from datetime import timedelta
from colorama import Fore, Style, init

# Inicializa o colorama. `autoreset=True` garante que cada print volte ao estilo padrão.
init(autoreset=True)

# --- Bloco de Configurações ---
# Define as constantes usadas pelo script para facilitar a manutenção.

# URL do endpoint de debug do microsserviço.
# ATUALIZADO: Apontando para a rota principal de produção
MICROSERVICE_URL = "http://127.0.0.1:5001/parse-query"

# Delay "amigável" entre requisições BEM-SUCEDIDAS para EVITAR o rate limit.
# [TURBO MODE]: Reduzido drasticamente pois a API é paga.
DELAY_BETWEEN_REQUESTS = 0.2 

# Delay "de penalidade" quando um erro (timeout, erro 5xx) ocorre, para AGUARDAR o reset da API.
RETRY_DELAY = 5 # 5 segundos para retry de conexão

# Configurações para o "throttling em lote" para evitar banimento
# (DESATIVADAS NO MODO TURBO, mantidas apenas para referência estrutural)
REQUESTS_PER_BATCH = 9999 
LONG_PAUSE_MINUTES = 0   

# --- Helpers de Data (CORRIGIDO PARA ISO - SEGUNDA A DOMINGO) ---
def get_dates():
    t = datetime.datetime.now().date()
    y = t - timedelta(days=1)
    
    # Lógica ISO (Semana começa na Segunda = 0, termina Domingo = 6)
    idx_dia_semana = t.weekday() 
    
    # Início desta semana (Segunda-feira)
    start_current_week = t - timedelta(days=idx_dia_semana)
    # Fim desta semana (Domingo)
    end_current_week = start_current_week + timedelta(days=6)
    
    # Semana passada
    start_last_week = start_current_week - timedelta(days=7)
    end_last_week = start_current_week - timedelta(days=1)
    
    # Mês
    start_month = t.replace(day=1)
    # Gambiarra segura para fim do mês
    next_month = t.replace(day=28) + timedelta(days=4)
    end_month = next_month - timedelta(days=next_month.day)

    return {
        "{today}": t.strftime("%Y-%m-%d"),
        "{yesterday}": y.strftime("%Y-%m-%d"),
        "{last_week_start}": start_last_week.strftime("%Y-%m-%d"),
        "{last_week_end}": end_last_week.strftime("%Y-%m-%d"),
        "{week_start}": start_current_week.strftime("%Y-%m-%d"),
        "{week_end}": end_current_week.strftime("%Y-%m-%d"),
        "{month_start}": start_month.strftime("%Y-%m-%d"),
        "{month_end": end_month.strftime("%Y-%m-%d")
    }

DYNAMIC_DATES = get_dates()

def parse_line(line):
    """Separa a pergunta do JSON esperado"""
    if "||" in line:
        parts = line.split("||")
        query = parts[0].strip()
        expected_str = parts[1].strip()
        
        # Substitui variáveis de data
        for k, v in DYNAMIC_DATES.items():
            expected_str = expected_str.replace(k, v)
            
        try:
            expected_json = json.loads(expected_str)
            return query, expected_json
        except json.JSONDecodeError:
            return query, None
    return line.strip(), None

def validate_response(api_json, expected_json):
    """Compara o JSON recebido com o esperado (apenas chaves presentes no esperado)"""
    if not expected_json:
        return True, [] # Sem expectativa, passa direto
    
    errors = []
    # Tratamento caso o backend retorne lista ou dict
    data = api_json[0] if isinstance(api_json, list) and len(api_json) > 0 else api_json
    
    # Se retornou vazio mas esperávamos algo
    if (not data or (isinstance(api_json, list) and len(api_json) == 0)) and expected_json:
         return False, ["API retornou vazio/null, mas havia expectativa de dados."]

    for key, val in expected_json.items():
        # Normaliza valores para string para comparação segura (ignora int vs str)
        api_val = data.get(key)
        
        str_api = str(api_val).lower().strip() if api_val is not None else "null"
        str_exp = str(val).lower().strip() if val is not None else "null"
        
        if str_api != str_exp:
            errors.append(f"Campo '{key}': Esperado [{val}] vs Recebido [{api_val}]")
            
    return len(errors) == 0, errors

def run_tests(raw_lines):
    """
    Função principal que executa a suíte de testes de forma resiliente e autidata.
    """
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================")
    print(f"{Style.BRIGHT}{Fore.MAGENTA} INICIANDO ROTEIRO DE TESTES - New Tracking Intent AI")
    print(f"{Style.BRIGHT}{Fore.MAGENTA} (Modo TURBO: Sem pausas longas, API Paga)")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================\n")

    total_queries = len(raw_lines)
    passed_count = 0
    failed_count = 0

    for i, line in enumerate(raw_lines):
        query, expected_json = parse_line(line)
        
        print(f"{Style.BRIGHT}{Fore.CYAN}--- TESTE #{i+1}/{total_queries} ---")
        print(f"{Fore.WHITE}Query: {query}")
        if expected_json:
            print(f"{Fore.LIGHTBLACK_EX}Expectativa: {json.dumps(expected_json, ensure_ascii=False)}")

        # Prepara o payload JSON para a requisição POST.
        payload = {"query": query}

        # --- INÍCIO DA LÓGICA DE RETENTATIVA ---
        success = False # Indica que o teste foi concluído (seja sucesso 200 ou erro 4xx)
        
        while not success:
            try:
                # Captura o tempo exato de início da tentativa
                start_time_epoch = time.time()
                # start_time_str = datetime.datetime.now().strftime('%H:%M:%S')
                # print(f"{Style.DIM}{Fore.WHITE}Iniciando requisição às {start_time_str}...{Style.RESET_ALL}")

                # Faz a chamada POST para o endpoint de debug, com um timeout de 120 segundos.
                response = requests.post(MICROSERVICE_URL, json=payload, timeout=120)

                # Processa a resposta baseada no status code
                if response.status_code == 200:
                    # SUCESSO DE CONEXÃO (200 OK)
                    end_time_epoch = time.time()
                    duration = end_time_epoch - start_time_epoch

                    # Extrai os dados da resposta JSON.
                    result_data = response.json()
                    
                    # --- VALIDAÇÃO DE CONTEÚDO (AUDITORIA) ---
                    is_valid, validation_errors = validate_response(result_data, expected_json)

                    if is_valid:
                        print(f"{Style.BRIGHT}{Fore.GREEN}[APROVADO] ✅ OK ({duration:.2f}s)")
                        # [TURBO] Exibindo o JSON completo na aprovação
                        print(f"{Style.DIM}{Fore.GREEN}{json.dumps(result_data, indent=2, ensure_ascii=False)}")
                        passed_count += 1
                    else:
                        print(f"{Style.BRIGHT}{Fore.RED}[REPROVADO] ❌ Divergência encontrada! ({duration:.2f}s)")
                        for err in validation_errors:
                            print(f"  └─ {err}")
                        print(f"{Fore.LIGHTRED_EX}JSON Recebido: {json.dumps(result_data, ensure_ascii=False)}")
                        failed_count += 1

                    success = True # Sai do loop while

                elif 400 <= response.status_code < 500:
                    # ERRO DO CLIENTE (4xx) - Validar se era esperado?
                    end_time_epoch = time.time()
                    
                    error_details = response.text
                    try: error_details = response.json().get('detail', response.text)
                    except: pass

                    print(f"{Fore.RED}ERRO HTTP {response.status_code}: {error_details}")
                    
                    # Se esperávamos null/erro, talvez isso seja um sucesso? 
                    # Por enquanto, contamos como falha se não for 200
                    failed_count += 1
                    success = True 

                else: 
                    # ERRO DO SERVIDOR (5xx) - [MODIFICAÇÃO TURBO]
                    # Não tenta infinitamente. Mostra o erro e avança.
                    error_details = response.text
                    try: error_details = response.json().get('detail', response.text)
                    except: pass

                    print(f"{Style.BRIGHT}{Fore.RED}[FALHA CRÍTICA API] Status {response.status_code}")
                    print(f"{Fore.RED}DETALHE: {error_details}")
                    
                    failed_count += 1
                    success = True # Sai do loop (considera falha e vai pro próximo)

            except requests.exceptions.RequestException as e:
                # ERRO DE REDE/TIMEOUT - AQUI AINDA TENTA DE NOVO (Pode ser servidor down)
                print(f"{Fore.RED}FALHA DE CONEXÃO: {e}")
                print(f"{Fore.YELLOW}Tentando reconectar em {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)

        # --- FIM DA LÓGICA DE RETENTATIVA ---

        print(f"{Style.BRIGHT}{Fore.CYAN}---------------------\n")

        # Pausa "amigável" [MODO TURBO]
        if i < total_queries - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)

            # Lógica da pausa longa REMOVIDA na prática (configurada para não pausar)
            if REQUESTS_PER_BATCH < 1000 and (i + 1) % REQUESTS_PER_BATCH == 0:
                print(f"{Style.BRIGHT}{Fore.RED} PAUSA DE LOTE...")
                time.sleep(LONG_PAUSE_MINUTES * 60)

    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}        RELATÓRIO FINAL")
    print(f"{Fore.GREEN} Aprovados: {passed_count}")
    print(f"{Fore.RED} Reprovados: {failed_count}")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================\n")


# Este bloco é o ponto de entrada do script quando executado diretamente pelo Python.
if __name__ == "__main__":
    # Verifica se o usuário passou o nome do arquivo de teste como argumento na linha de comando.
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Erro: Por favor, especifique o nome do arquivo de testes.")
        print(f"{Fore.YELLOW}Exemplo de uso: python scripts/debug_runner.py testes.txt")
        sys.exit(1)

    test_file_name = sys.argv[1]
    # Constrói o caminho completo para o arquivo de teste, assumindo a nova estrutura de pastas.
    test_file_path = f"tests_cases/{test_file_name}" # Ajuste se o nome da pasta for diferente

    try:
        # Abre o arquivo de teste com codificação utf-8 para ler caracteres especiais.
        with open(test_file_path, 'r', encoding='utf-8') as f:
            queries_to_run = [
                line.strip() for line in f.readlines()
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('=')
            ]

        if not queries_to_run:
            print(f"{Fore.YELLOW}Nenhuma query de teste encontrada em '{test_file_path}'.")
        else:
            # Inicia a execução dos testes com a lista de queries limpa.
            run_tests(queries_to_run)

    except FileNotFoundError:
        # Trata o erro caso o nome do arquivo de teste esteja incorreto.
        print(f"{Fore.RED}Erro: O arquivo de teste '{test_file_path}' não foi encontrado.")