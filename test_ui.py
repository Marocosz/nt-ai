import streamlit as st
import requests
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="New Tracking AI - Teste",
    page_icon="🤖"
)

st.title("Interface Teste")

# URL do seu microsserviço rodando localmente
MICROSERVICE_URL = "http://127.0.0.1:5001/parse-query"

# --- Interface do Usuário ---

# Cria a caixa de texto para o usuário digitar a pergunta
query = st.text_input(
    "Digite sua consulta em linguagem natural:", 
    placeholder="Ex: notas entregues na semana passada para o cliente ACME"
)

# Cria o botão para enviar a consulta
if st.button("Analisar com IA"):
    if not query:
        st.warning("Por favor, digite uma consulta antes de analisar.")
    else:
        # Mostra um "spinner" de carregamento enquanto a requisição está em andamento
        with st.spinner('Analisando sua pergunta com a IA...'):
            try:
                # Monta o corpo da requisição JSON
                payload = {"query": query}
                
                # Faz a chamada POST para o microsserviço
                response = requests.post(MICROSERVICE_URL, json=payload)
                
                # Verifica se a chamada foi bem-sucedida
                if response.status_code == 200:
                    st.success("Análise concluída com sucesso!")
                    
                    # Pega o resultado JSON e exibe de forma formatada
                    result_json = response.json()
                    st.subheader("Filtros JSON Extraídos:")
                    st.json(result_json)
                else:
                    # Mostra uma mensagem de erro se a API falhar
                    error_details = response.json().get('detail', 'Erro desconhecido.')
                    st.error(f"Erro ao chamar o microsserviço (Status {response.status_code}): {error_details}")

            except requests.exceptions.RequestException as e:
                st.error(f"Não foi possível conectar ao microsserviço. Verifique se ele está rodando. Detalhes: {e}")