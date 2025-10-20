# =================================================================================================
# =================================================================================================
#
#                               SCRIPT DE TESTE DE INTEGRAÇÃO ROBUSTO (DEBUG RUNNER v2)
#
# Visão Geral do Módulo:
#
# Este script é uma ferramenta de linha de comando resiliente para realizar testes de
# integração no microsserviço 'nt-ai'. Ele é projetado para rodar de forma autônoma
# e lidar com falhas de rede, timeouts e limites de taxa (rate limiting) da API.
#
# Arquitetura e Fluxo de Trabalho:
#
# 1. Leitura do Arquivo de Testes:
#    - Lê um arquivo de texto linha por linha, ignorando comentários.
#
# 2. Execução em Loop com Retentativas (A Lógica Principal):
#    - Itera sobre cada query. Para cada query, ele entra em um loop de "tentativa infinita".
#    - Ele SÓ passará para a próxima query (ex: Teste #2) após o teste atual
#      (ex: Teste #1) ser concluído com um `status_code == 200`.
#
# 3. Tratamento de Erros de Conexão e Timeout:
#    - Se o script não conseguir conectar ao microsserviço ou se a requisição estourar
#      o `timeout` (uma `RequestException`), ele imprimirá o erro, aguardará o
#      `RETRY_DELAY` (ex: 60 segundos) e tentará a *mesma query* novamente.
#
# 4. Tratamento de Erros de API (Rate Limiting, etc.):
#    - Se a API retornar um erro (ex: 429 "Too Many Requests", 413 "Tokens Exceeded", 500 "Server Error"),
#      o script imprimirá o erro, aguardará o `RETRY_DELAY` (ex: 60 segundos) e
#      tentará a *mesma query* novamente.
#
# 5. Controle de Taxa Preventivo:
#    - Após uma query ser BEM-SUCEDIDA, o script pausa por `DELAY_BETWEEN_REQUESTS` (ex: 10 segundos)
#    - antes de iniciar a próxima, como uma medida "amigável" para evitar o rate limiting.
#
# Como Usar:
# > python scripts/debug_runner.py testes_finais_cobertura_total.txt
#
# =================================================================================================
# =================================================================================================

import requests
import json
import time
import sys
import datetime # <-- ADICIONADO PARA O TIMER
from colorama import Fore, Style, init

# Inicializa o colorama. `autoreset=True` garante que cada print volte ao estilo padrão.
init(autoreset=True)

# --- Bloco de Configurações ---
# Define as constantes usadas pelo script para facilitar a manutenção.

# URL do endpoint de debug do microsserviço.
MICROSERVICE_URL = "http://127.0.0.1:5001/debug-query"

# Delay "amigável" entre requisições BEM-SUCEDIDAS para EVITAR o rate limit.
DELAY_BETWEEN_REQUESTS = 5 # segundos

# Delay "de penalidade" quando um erro (timeout, rate limit) ocorre, para AGUARDAR o reset da API.
# Ajuste este valor se a API exigir uma espera mais longa (ex: 300 para 5 minutos).
RETRY_DELAY = 60 # 60 segundos

def run_tests(queries):
    """
    Função principal que executa a suíte de testes de forma resiliente.
    Ela recebe uma lista de queries e só passa para a próxima após o
    sucesso da query atual.
    """
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================")
    print(f"{Style.BRIGHT}{Fore.MAGENTA} INICIANDO ROTEIRO DE TESTES - New Tracking Intent AI")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================\n")

    total_queries = len(queries)
    for i, query in enumerate(queries):
        print(f"{Style.BRIGHT}{Fore.CYAN}--- TESTE #{i+1}/{total_queries} ---")
        print(f"{Fore.WHITE}Query Original: {query}\n")

        # Prepara o payload JSON para a requisição POST.
        payload = {"query": query}
        
        # --- INÍCIO DA LÓGICA DE RETENTATIVA ---
        success = False
        while not success:
            try:
                # ==================================================================
                # --- INÍCIO DA ALTERAÇÃO (TIMER) ---
                # ==================================================================
                # Captura o tempo exato de início da tentativa
                start_time_epoch = time.time()
                start_time_str = datetime.datetime.now().strftime('%H:%M:%S')
                print(f"{Style.DIM}{Fore.WHITE}Iniciando requisição às {start_time_str}...{Style.RESET_ALL}")
                # ==================================================================
                # --- FIM DA ALTERAÇÃO ---
                # ==================================================================

                # Faz a chamada POST para o endpoint de debug, com um timeout de 120 segundos.
                response = requests.post(MICROSERVICE_URL, json=payload, timeout=120)

                # Verifica se a chamada foi bem-sucedida (status code 200 OK).
                if response.status_code == 200:
                    # ==================================================================
                    # --- INÍCIO DA ALTERAÇÃO (TIMER) ---
                    # ==================================================================
                    # Captura o tempo exato de fim e calcula a duração
                    end_time_epoch = time.time()
                    end_time_str = datetime.datetime.now().strftime('%H:%M:%S')
                    duration = end_time_epoch - start_time_epoch
                    # ==================================================================
                    # --- FIM DA ALTERAÇÃO ---
                    # ==================================================================

                    # Extrai os dados da resposta JSON.
                    result_data = response.json()
                    
                    enhanced_query = result_data.get("enhanced_query", "ERRO: Não foi possível gerar a query otimizada.")
                    parsed_json = result_data.get("parsed_json", {})

                    # Exibe os resultados formatados no console.
                    print(f"{Fore.YELLOW}1. Query Otimizada (pela IA):")
                    print(f"{Style.NORMAL}{Fore.YELLOW}{enhanced_query}\n")
                    
                    print(f"{Fore.GREEN}2. JSON de Filtros Gerado:")
                    print(f"{Style.NORMAL}{Fore.GREEN}{json.dumps(parsed_json, indent=2, ensure_ascii=False)}\n") # Adicionado \n
                    
                    # ==================================================================
                    # --- INÍCIO DA ALTERAÇÃO (TIMER) ---
                    # ==================================================================
                    # Exibe o log de performance da requisição
                    print(f"{Style.BRIGHT}{Fore.BLUE}Tempo de Resposta: {duration:.2f} segundos (Início: {start_time_str} | Fim: {end_time_str}){Style.RESET_ALL}")
                    # ==================================================================
                    # --- FIM DA ALTERAÇÃO ---
                    # ==================================================================
                    
                    # SINALIZA SUCESSO: Quebra o loop 'while' e passa para a próxima query.
                    success = True
                
                else:
                    # Erro da API (ex: 429, 413, 500). A API está online, mas retornou um erro.
                    error_details = "Erro desconhecido."
                    try:
                        # Tenta extrair a mensagem de erro detalhada do JSON da API.
                        error_details = response.json().get('detail', response.text)
                    except json.JSONDecodeError:
                        error_details = response.text
                        
                    print(f"{Fore.YELLOW}ERRO na API (Status {response.status_code}): {error_details}")
                    print(f"{Fore.YELLOW}Aguardando {RETRY_DELAY} segundos para tentar novamente a MESMA query...")
                    time.sleep(RETRY_DELAY)
                    # 'success' continua False, então o loop 'while' repetirá a query.

            except requests.exceptions.RequestException as e:
                # Erro de Rede: Captura falhas críticas (Timeout, Conexão Recusada, DNS, etc.).
                print(f"{Fore.RED}FALHA DE CONEXÃO/TIMEOUT: {e}")
                print(f"{Fore.RED}Verifique se o microsserviço está rodando em {MICROSERVICE_URL}.")
                print(f"{Fore.YELLOW}Aguardando {RETRY_DELAY} segundos para tentar novamente a MESMA query...")
                time.sleep(RETRY_DELAY)
                # 'success' continua False, então o loop 'while' repetirá a query.
        
        # --- FIM DA LÓGICA DE RETENTATIVA ---

        print(f"{Style.BRIGHT}{Fore.CYAN}---------------------\n")
        
        # Pausa "amigável" entre os testes BEM-SUCEDIDOS para evitar o rate limit.
        if i < total_queries - 1:
            print(f"{Style.BRIGHT}{Fore.MAGENTA}Aguardando {DELAY_BETWEEN_REQUESTS} segundos antes do próximo teste...{Style.RESET_ALL}")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}        ROTEIRO DE TESTES FINALIZADO")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================\n")


# Este bloco é o ponto de entrada do script quando executado diretamente pelo Python.
if __name__ == "__main__":
    # Verifica se o usuário passou o nome do arquivo de teste como argumento na linha de comando.
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Erro: Por favor, especifique o nome do arquivo de testes.")
        print(f"{Fore.YELLOW}Exemplo de uso: python scripts/debug_runner.py testes_completos.txt")
        sys.exit(1)
        
    test_file_name = sys.argv[1]
    # Constrói o caminho completo para o arquivo de teste, assumindo a nova estrutura de pastas.
    test_file_path = f"tests_cases/{test_file_name}"
    
    try:
        # Abre o arquivo de teste com codificação utf-8 para ler caracteres especiais.
        with open(test_file_path, 'r', encoding='utf-8') as f:
            # Usa uma list comprehension para ler todas as linhas e filtrá-las:
            # 1. line.strip(): Remove espaços em branco do início e do fim.
            # 2. if line.strip(): Ignora linhas que ficaram vazias após o strip.
            # 3. and not line.strip().startswith(...): Ignora linhas de comentário.
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