# =================================================================================================
# =================================================================================================
#
#               INTERFACE DE TESTE E DEMONSTRAÇÃO (STREAMLIT UI)
#
# Visão Geral do Módulo:
#
# Este arquivo cria uma interface web local usando a biblioteca Streamlit. Ele serve como
# uma ferramenta de desenvolvimento e depuração ("playground") para o microsserviço 'nt-ai',
# permitindo que os desenvolvedores testem a cadeia de IA de forma interativa sem
# a necessidade de usar clientes de API como Postman ou cURL.
#
# Arquitetura e Fluxo de Trabalho:
#
# 1. Interface do Usuário (UI):
#    - Renderiza um título, uma descrição e um campo de texto onde o desenvolvedor
#      pode inserir uma pergunta em linguagem natural.
#
# 2. Ação do Usuário:
#    - Ao clicar no botão "Analisar com IA", o script é acionado.
#
# 3. Comunicação com a API:
#    - O script envia a pergunta do usuário em uma requisição HTTP POST para o endpoint
#      `/debug-query` do microsserviço FastAPI, que deve estar rodando localmente.
#
# 4. Processamento da Resposta:
#    - Aguarda a resposta do endpoint de debug, que contém os resultados intermediários
#      do processamento da IA.
#
# 5. Exibição dos Resultados:
#    - Se a requisição for bem-sucedida, a interface exibe de forma clara e separada:
#      a) A "Query Otimizada" (saída da primeira cadeia, o Enhancer).
#      b) O "JSON de Filtros Extraído" (saída da segunda cadeia, o Parser).
#
# 6. Tratamento de Erros:
#    - Exibe mensagens de erro amigáveis na interface caso o microsserviço esteja
#      offline ou retorne um erro.
#
# Como Usar:
#
# 1. Certifique-se de que o microsserviço FastAPI esteja rodando (uvicorn app.main:app).
# 2. Execute este script a partir do diretório raiz do projeto com o comando:
#    > streamlit run scripts/test_ui.py
#
# =================================================================================================
# =================================================================================================

import streamlit as st
import requests
import json

# --- Configuração da Página ---
# Define o título e o ícone que aparecerão na aba do navegador.
st.set_page_config(
    page_title="New Tracking Intent AI - Teste",
    page_icon="🤖"
)

# --- Renderização do Cabeçalho da UI ---
# Exibe os textos principais da interface.
st.title("🤖 Interface de Teste - New Tracking Intent AI")
st.header("Análise de Intenção de Busca")
st.caption("Esta UI usa o endpoint de debug para mostrar os passos da IA.")

# Define a URL do endpoint de debug do microsserviço FastAPI.
MICROSERVICE_URL = "http://127.0.0.1:5001/debug-query"

# --- Interface Interativa ---

# Cria o campo de texto para a entrada do usuário.
query = st.text_input(
    "Digite sua consulta em linguagem natural:", 
    placeholder="Ex: notas do cliente acme transp veloz ordene por valor"
)

# Cria o botão que dispara a análise. O código dentro deste 'if' só é
# executado quando o botão é clicado.
if st.button("Analisar com IA"):
    # Validação de entrada: verifica se o usuário digitou algo.
    if not query:
        st.warning("Por favor, digite uma consulta antes de analisar.")
    else:
        # Exibe uma mensagem de "carregando" enquanto a requisição está em andamento.
        # O bloco `with` garante que a mensagem desapareça ao final.
        with st.spinner('Analisando sua pergunta com a IA...'):
            try:
                # Prepara o payload JSON para a requisição POST.
                payload = {"query": query}
                # Envia a requisição para a API do microsserviço.
                response = requests.post(MICROSERVICE_URL, json=payload)
                
                # Caminho de sucesso: a API respondeu corretamente.
                if response.status_code == 200:
                    st.success("Análise concluída com sucesso!")
                    
                    # Extrai os dados da resposta JSON.
                    result_data = response.json()
                    
                    # Usa o método .get() para acessar as chaves de forma segura,
                    # evitando erros caso uma chave não esteja presente na resposta.
                    enhanced_query = result_data.get("enhanced_query", "Não foi possível gerar a query otimizada.")
                    parsed_json = result_data.get("parsed_json", {})

                    # Exibe os resultados formatados na interface.
                    st.subheader("1. Query Otimizada (Enhanced Query):")
                    st.info(enhanced_query)
                    
                    st.subheader("2. Filtros JSON Extraídos:")
                    # st.json() é um componente do Streamlit que renderiza
                    # dicionários/JSON de forma interativa e legível.
                    st.json(parsed_json)
                
                # Trata o caso em que a API retornou um código de erro (ex: 400, 500).
                else:
                    error_details = response.json().get('detail', 'Erro desconhecido.')
                    st.error(f"Erro ao chamar o microsserviço (Status {response.status_code}): {error_details}")

            # Trata o caso em que não foi possível conectar ao microsserviço (ex: está offline).
            except requests.exceptions.RequestException as e:
                st.error(f"Não foi possível conectar ao microsserviço. Verifique se ele está rodando. Detalhes: {e}")