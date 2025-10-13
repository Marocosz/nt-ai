import requests
import json
import time
import sys
from colorama import Fore, Style, init

# Inicializa o colorama para funcionar no Windows
init(autoreset=True)

# --- CONFIGURAÇÕES ---
MICROSERVICE_URL = "http://127.0.0.1:5001/debug-query"
DELAY_BETWEEN_REQUESTS = 1  # segundos

def run_tests(queries):
    """
    Executa a suíte de testes, chamando o microsserviço para cada query.
    """
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================")
    print(f"{Style.BRIGHT}{Fore.MAGENTA} INICIANDO ROTEIRO DE TESTES - NEW TRACKING AI")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================\n")

    total_queries = len(queries)
    for i, query in enumerate(queries):
        print(f"{Style.BRIGHT}{Fore.CYAN}--- TESTE #{i+1}/{total_queries} ---")
        print(f"{Fore.WHITE}Query Original: {query}\n")

        payload = {"query": query}

        try:
            # Faz a chamada POST para o endpoint de debug
            response = requests.post(MICROSERVICE_URL, json=payload, timeout=60)

            # Verifica se a chamada foi bem-sucedida
            if response.status_code == 200:
                result_data = response.json()
                
                enhanced_query = result_data.get("enhanced_query", "ERRO: Não foi possível gerar a query otimizada.")
                parsed_json = result_data.get("parsed_json", {})

                print(f"{Fore.YELLOW}1. Query Otimizada (pela IA):")
                print(f"{Style.NORMAL}{Fore.YELLOW}{enhanced_query}\n")
                
                print(f"{Fore.GREEN}2. JSON de Filtros Gerado:")
                # Usa json.dumps para formatar o JSON de forma legível
                print(f"{Style.NORMAL}{Fore.GREEN}{json.dumps(parsed_json, indent=2, ensure_ascii=False)}")
            
            else:
                # Mostra uma mensagem de erro se a API falhar
                error_details = response.json().get('detail', 'Erro desconhecido.')
                print(f"{Fore.RED}ERRO na API (Status {response.status_code}): {error_details}")

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}FALHA CRÍTICA: Não foi possível conectar ao microsserviço.")
            print(f"{Fore.RED}Verifique se ele está rodando em {MICROSERVICE_URL}.")
            print(f"{Fore.RED}Detalhes do erro: {e}")
            # Se não conseguir conectar, para a execução dos testes
            break
        
        print(f"{Style.BRIGHT}{Fore.CYAN}---------------------\n")
        
        # Espera um tempo para não sobrecarregar o serviço de IA
        if i < total_queries - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}         ROTEIRO DE TESTES FINALIZADO")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=============================================\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Erro: Por favor, especifique o caminho para o arquivo de testes.")
        print(f"{Fore.YELLOW}Exemplo de uso: python debug_runner.py test_prompts.txt")
        sys.exit(1)
        
    test_file_path = sys.argv[1]
    
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            # Lê todas as linhas, remove espaços em branco e ignora linhas vazias ou comentários (#)
            queries_to_run = [
                line.strip() for line in f.readlines() 
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('=')
            ]
        
        if not queries_to_run:
            print(f"{Fore.YELLOW}Nenhuma query de teste encontrada em '{test_file_path}'.")
        else:
            run_tests(queries_to_run)

    except FileNotFoundError:
        print(f"{Fore.RED}Erro: O arquivo de teste '{test_file_path}' não foi encontrado.")