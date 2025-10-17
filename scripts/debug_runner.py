# =================================================================================================
# =================================================================================================
#
#                    SCRIPT DE TESTE DE INTEGRAÇÃO (DEBUG RUNNER)
#
# Visão Geral do Módulo:
#
# Este arquivo é uma ferramenta de linha de comando para realizar testes de integração
# no microsserviço 'nt-ai'. Ele não é parte da aplicação principal, mas sim um
# script utilitário para desenvolvedores, projetado para validar o comportamento
# de ponta a ponta da cadeia de IA.
#
# Arquitetura e Fluxo de Trabalho:
#
# 1. Leitura do Arquivo de Testes:
#    - O script é executado a partir do terminal, recebendo como argumento o caminho
#      para um arquivo de texto (ex: `testes_otimizados.txt`).
#    - Ele lê este arquivo linha por linha, ignorando linhas vazias ou aquelas que
#      começam com '#' ou '=', permitindo a criação de arquivos de teste comentados.
#
# 2. Execução em Loop:
#    - Itera sobre cada query lida do arquivo de teste.
#
# 3. Chamada à API de Debug:
#    - Para cada query, envia uma requisição HTTP POST para o endpoint `/debug-query`
#      do microsserviço. Este endpoint é específico para testes e retorna os
#      resultados intermediários da cadeia de IA.
#
# 4. Processamento e Exibição da Resposta:
#    - Verifica se a resposta da API foi bem-sucedida (status 200).
#    - Se sim, formata e exibe no console a "Query Otimizada" e o "JSON de Filtros Gerado",
#      usando cores para facilitar a leitura.
#    - Se ocorrer um erro na API (ex: 500) ou uma falha de conexão, exibe uma mensagem
#      de erro clara e detalhada.
#
# 5. Controle de Taxa (Rate Limiting):
#    - Pausa por um segundo (`time.sleep`) entre cada requisição para evitar sobrecarregar
#      a API do microsserviço ou atingir limites de taxa da API do LLM.
#
# Como Usar:
#
# Execute o script a partir do diretório raiz do projeto, passando o nome do arquivo de
# teste como argumento. Exemplo:
# > python scripts/debug_runner.py testes.txt
#
# =================================================================================================
# =================================================================================================

import requests
import json
import time
import sys
# Importa as bibliotecas para adicionar cor e estilo à saída do terminal, melhorando a legibilidade.
from colorama import Fore, Style, init

# Inicializa o colorama. `autoreset=True` garante que cada print volte ao estilo padrão.
init(autoreset=True)

# --- Bloco de Configurações ---
# Define as constantes usadas pelo script para facilitar a manutenção.

# URL do endpoint de debug do microsserviço.
MICROSERVICE_URL = "http://127.0.0.1:5001/debug-query"
# Intervalo em segundos para pausar entre as requisições, para evitar rate limiting.
DELAY_BETWEEN_REQUESTS = 10  # segundos

def run_tests(queries):
    """
    Função principal que executa a suíte de testes.
    Ela recebe uma lista de strings (queries) e itera sobre elas,
    chamando o microsserviço para cada uma.
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

        # O bloco try/except lida com possíveis falhas de conexão ou timeouts.
        try:
            # Faz a chamada POST para o endpoint de debug, com um timeout de 60 segundos.
            response = requests.post(MICROSERVICE_URL, json=payload, timeout=60)

            # Verifica se a chamada foi bem-sucedida (status code 200 OK).
            if response.status_code == 200:
                # Extrai os dados da resposta JSON.
                result_data = response.json()
                
                # Usa o método .get() para acessar as chaves de forma segura,
                # fornecendo uma mensagem de erro padrão caso a chave não exista.
                enhanced_query = result_data.get("enhanced_query", "ERRO: Não foi possível gerar a query otimizada.")
                parsed_json = result_data.get("parsed_json", {})

                # Exibe os resultados formatados no console.
                print(f"{Fore.YELLOW}1. Query Otimizada (pela IA):")
                print(f"{Style.NORMAL}{Fore.YELLOW}{enhanced_query}\n")
                
                print(f"{Fore.GREEN}2. JSON de Filtros Gerado:")
                # Usa json.dumps para formatar o JSON de forma legível (pretty-printing).
                # `ensure_ascii=False` garante a exibição correta de caracteres acentuados.
                print(f"{Style.NORMAL}{Fore.GREEN}{json.dumps(parsed_json, indent=2, ensure_ascii=False)}")
            
            else:
                # Se a API retornar um erro (ex: 400, 500), exibe os detalhes.
                error_details = response.json().get('detail', 'Erro desconhecido.')
                print(f"{Fore.RED}ERRO na API (Status {response.status_code}): {error_details}")

        except requests.exceptions.RequestException as e:
            # Captura falhas críticas, como a API estar offline ou a rede indisponível.
            print(f"{Fore.RED}FALHA CRÍTICA: Não foi possível conectar ao microsserviço.")
            print(f"{Fore.RED}Verifique se ele está rodando em {MICROSERVICE_URL}.")
            print(f"{Fore.RED}Detalhes do erro: {e}")
            # Interrompe a execução dos testes, pois não faz sentido continuar se a API está offline.
            break
        
        print(f"{Style.BRIGHT}{Fore.CYAN}---------------------\n")
        
        # Pausa a execução para não sobrecarregar o serviço de IA.
        if i < total_queries - 1:
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