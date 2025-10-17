# 🤖 New Tracking - Intent AI

> New Tracking - Intent AI é um microsserviço especializado em traduzir linguagem natural para filtros estruturados. Construído com Python, FastAPI e LangChain, este sistema atua como o "cérebro da interpretação" para a plataforma New Tracking. Ele recebe perguntas de usuários em português, as normaliza e converte em um objeto JSON preciso, que é então consumido pelo NT API backend para consultar uma procedure no banco de dados (SP_TK_NOTAS_AI_HOM). Com uma arquitetura de duas cadeias de IA, o serviço lida com sinônimos, ambiguidades e lógicas de data complexas, permitindo uma interação conversacional poderosa com os dados logísticos.

# 🗂️ Índice
- [🤖 New Tracking - Intent AI](#-new-tracking---intent-ai)
- [🗂️ Índice](#️-índice)
- [🛠️ Tecnologias Usadas](#️-tecnologias-usadas)
  - [**Geral**](#geral)
  - [**Interface de Teste e Demonstração (Streamlit)**](#interface-de-teste-e-demonstração-streamlit)
- [🌳 Estrutura do Projeto](#-estrutura-do-projeto)

---

# 🛠️ Tecnologias Usadas

## **Geral**
- [Python](https://www.python.org/) (**3.12**)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [Git](https://git-scm.com/)
- [Modelo LLM - llama-3.1-8b-instant (GROQ)](https://groq.com/)

---

## **Interface de Teste e Demonstração (Streamlit)**

> [!IMPORTANT]
> Este projeto é um microsserviço de backend, projetado para ser consumido por outra API. Como tal, não inclui uma interface de frontend para o usuário final.

Para fins de desenvolvimento, depuração e demonstração, o repositório contém uma interface de teste interativa (`test_ui.py`) desenvolvida com **Streamlit**. Esta ferramenta é essencial para entender o comportamento da IA e permite ao desenvolvedor:

-   **Testar Queries Individuais:** Enviar perguntas em linguagem natural de forma rápida, sem a necessidade de usar um cliente de API como o Postman.
-   **Visualizar o Fluxo de IA:** Observar em tempo real a transformação dos dados em cada etapa da cadeia:
    1.  A query original do usuário.
    2.  A versão normalizada pela cadeia `Enhancer`.
    3.  O objeto JSON final extraído pela cadeia `Parser`.
-   **Depurar e Validar:** Validar instantaneamente o resultado das alterações nos prompts, tornando o processo de "prompt engineering" muito mais eficiente.

> [!NOTE]
> Esta interface é uma ferramenta exclusiva para desenvolvimento e não faz parte do serviço principal (`main.py`) exposto pelo Uvicorn/FastAPI.

---

# 🌳 Estrutura do Projeto

```
├── 📁 app/
│   ├── 📁 chains/
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 master_chain.py
│   ├── 📁 core/
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 llm.py
│   ├── 📁 prompts/
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 filter_prompts.py
│   ├── 🐍 __init__.py
│   └── 🐍 main.py
├── 📁 logs/
├── 📁 scripts/
│   ├── 🐍 debug_runner.py
│   └── 🐍 test_ui.py
├── 📁 sql/
│   ├── 🗄️ PROCEDURE_TESTE.sql
│   ├── 🗄️ SCRIPT_TESTE_AI_HOM.sql
│   └── 🗄️ SP_TK_NOTAS_AI_HOM.sql
├── 📁 tests_case/
│   ├── 📄 testes.txt
│   └── 📄 testes_otimizado.txt
├── 📁 venvntai/
├── 🔒 .env 
├── 📖 README.md
└── 📄 requirements.txt
```