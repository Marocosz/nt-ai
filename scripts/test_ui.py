import streamlit as st
import requests
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="New Tracking Intent AI - Teste",
    page_icon="🤖"
)

st.title("🤖 Interface de Teste - New Tracking Intent AI")
st.header("Análise de Intenção de Busca")
st.caption("Esta UI usa o endpoint de debug para mostrar os passos da IA.")

# --- MUDANÇA AQUI: Apontar para o novo endpoint de debug ---
MICROSERVICE_URL = "http://127.0.0.1:5001/debug-query"

# --- Interface do Usuário ---

query = st.text_input(
    "Digite sua consulta em linguagem natural:", 
    placeholder="Ex: notas do cliente acme transp veloz ordene por valor"
)

if st.button("Analisar com IA"):
    if not query:
        st.warning("Por favor, digite uma consulta antes de analisar.")
    else:
        with st.spinner('Analisando sua pergunta com a IA...'):
            try:
                payload = {"query": query}
                response = requests.post(MICROSERVICE_URL, json=payload)
                
                if response.status_code == 200:
                    st.success("Análise concluída com sucesso!")
                    
                    # --- MUDANÇA AQUI: Extrair e exibir os dois resultados ---
                    result_data = response.json()
                    
                    enhanced_query = result_data.get("enhanced_query", "Não foi possível gerar a query otimizada.")
                    parsed_json = result_data.get("parsed_json", {})

                    st.subheader("1. Query Otimizada (Enhanced Query):")
                    st.info(enhanced_query)
                    
                    st.subheader("2. Filtros JSON Extraídos:")
                    st.json(parsed_json)
                else:
                    error_details = response.json().get('detail', 'Erro desconhecido.')
                    st.error(f"Erro ao chamar o microsserviço (Status {response.status_code}): {error_details}")

            except requests.exceptions.RequestException as e:
                st.error(f"Não foi possível conectar ao microsserviço. Verifique se ele está rodando. Detalhes: {e}")