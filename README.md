# 🤖 New Tracking - Intent AI

> New Tracking - Intent AI é um microsserviço especializado em traduzir linguagem natural para filtros estruturados. Construído com Python, FastAPI e LangChain, este sistema atua como o "cérebro da interpretação" para a plataforma New Tracking. Ele recebe perguntas de usuários em português, as normaliza e converte em um objeto JSON preciso, que é então consumido pelo NT API backend para consultar uma procedure no banco de dados (SP_TK_NOTAS_AI_HOM). Com uma arquitetura de duas cadeias de IA, o serviço lida com sinônimos, ambiguidades e lógicas de data complexas, permitindo uma interação conversacional poderosa com os dados logísticos.

# 🗂️ Índice
- [🤖 New Tracking - Intent AI](#-new-tracking---intent-ai)
- [🗂️ Índice](#️-índice)
- [🛠️ Tecnologias Usadas](#️-tecnologias-usadas)
  - [**Geral**](#geral)
  - [**Interface de Teste e Demonstração (Streamlit)**](#interface-de-teste-e-demonstração-streamlit)
- [🌳 Estrutura do Projeto](#-estrutura-do-projeto)
- [🔄 Updates](#-updates)
  - [Próximas Implementações](#próximas-implementações)
- [🧠 Funcionamento](#-funcionamento)
  - [`app/main.py`](#appmainpy)
  - [`app/chains/master_chain.py`](#appchainsmaster_chainpy)
  - [`app/prompts/filter_prompts.py`](#apppromptsfilter_promptspy)
- [Outros Módulos e Ferramentas de Suporte](#outros-módulos-e-ferramentas-de-suporte)
- [Endpoints](#endpoints)
  - [**1. Endpoint de Produção**](#1-endpoint-de-produção)
    - [**Endpoint:** `POST /parse-query`](#endpoint-post-parse-query)
    - [**Endpoint:** `POST /debug-query`](#endpoint-post-debug-query)

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

# 🔄 Updates

> [!NOTE]
> Versão 1

| Versão | Data       | Mudanças principais               |
|--------|------------|-----------------------------------|
| 1.0    | 25/09/2025 | MVP funcional

## Próximas Implementações
- [ ] 
- [ ] 

---

# 🧠 Funcionamento

Nesta seção, apresentamos uma visão detalhada de como cada parte do New Tracking - Intent AI opera. Aqui você encontrará uma explicação clara de como os módulos interagem entre si, como os dados fluem da pergunta do usuário até a geração do JSON final, e como a inteligência artificial é utilizada para normalizar e extrair informações complexas.

O objetivo é fornecer ao leitor uma compreensão completa do funcionamento interno do sistema, permitindo não apenas integrá-lo, mas também entender, manter e expandir seu código com facilidade.

> [!TIP]
> **Explore o código-fonte!** Cada arquivo de código mencionado abaixo foi documentado com um cabeçalho descritivo que detalha sua arquitetura, o fluxo de dados (entradas e saídas) e a responsabilidade de cada função. É um excelente complemento a esta documentação de alto nível.

---

## [`app/main.py`](./app/main.py)

> Este arquivo é responsável por configurar e expor os endpoints da API.

1. **Inicialização:** Carrega as variáveis de ambiente e, através dos eventos de ciclo de vida (startup/shutdown), gerencia o carregamento e o encerramento da aplicação.

2. **Logging:** Implementa um sistema de log robusto que escreve para o console e para um arquivo com rotação (logs/nt_ai_service.log), garantindo a observabilidade do serviço.

3. **Carregamento Otimizado:** Invoca a criação das cadeias de IA uma única vez durante o evento de startup, uma otimização de performance crucial que evita recarregar os modelos a cada requisição.

4. **Endpoints Assíncronos:** Define os endpoints /parse-query (produção) e /debug-query (testes) de forma assíncrona (async def), permitindo que o servidor lide com múltiplas requisições concorrentes de forma eficiente.

---

## [`app/chains/master_chain.py`](./app/chains/master_chain.py)

> Este módulo é o coração da lógica de IA, responsável por montar e conectar as diferentes etapas do processo de interpretação.

**Arquitetura e Princípio de Design:**

A arquitetura segue o princípio de "Separação de Responsabilidades", operando como uma linha de montagem com as seguintes etapas:

1. **Cálculo de Datas em Tempo de Execução:**

    - **Responsabilidade:** Garantir que a IA sempre trabalhe com o contexto de tempo correto.

    - **Ação:** A cada requisição, a função _get_current_dates calcula dinamicamente todos os períodos relevantes (hoje, ontem, semana de calendário, mês de calendário, etc.) e os injeta no fluxo de dados.

2. **O Tradutor (query_enhancer_chain):**

    **- Responsabilidade:** Normalizar a pergunta do usuário de forma segura.

    **- Ação:** Recebe a pergunta bruta e a traduz para os termos de negócio, expandindo abreviações (ex: "nf" -> "nota fiscal") sem alterar a intenção original.

3. **O Especialista em Extração (json_parser_chain):**

    - **Responsabilidade:** Converter a pergunta já normalizada em um objeto JSON estruturado.

    - **Ação:** Recebe a pergunta clara e os dados de tempo e, com base em regras e exemplos, extrai todas as entidades (status, locais, ordenação) para o formato JSON final.

4. **Resiliência com OutputFixingParser:**

    - **esponsabilidade:** Garantir que a saída seja sempre um JSON sintaticamente válido.

    - **Ação:** Se o LLM gerar um JSON com erro de sintaxe, esta ferramenta automaticamente solicita ao LLM que corrija seu próprio erro antes de retornar o resultado


## [`app/prompts/filter_prompts.py`](.app/prompts/filter_prompts.py)

> Este arquivo centraliza todas as instruções que definem o comportamento da IA. É aqui que a "personalidade" e as "habilidades" do sistema são moldadas.

**Componentes Principais:**

1. **QUERY_ENHANCER_PROMPT (O Tradutor):**

    - Contém as "Regras de Ouro" que proíbem a IA de adicionar ou remover informações, garantindo a preservação da intenção do usuário.

    - Define um dicionário de mapeamento de sinônimos (ex: "rodando", "viajando" -> "em trânsito") e abreviações.

2. **JSON_PARSER_PROMPT (O Especialista em Extração):**

    - Define o "schema" do JSON de saída, listando todas as entidades que a IA deve extrair.

    - Contém seções de regras detalhadas para lidar com ambiguidades (entregue com data vs. entregue como status), precisão de datas (períodos relativos vs. de calendário) e hierarquias (prioridade de filtros).

    - Utiliza uma extensa lista de exemplos (Few-Shot Learning) para ensinar à IA o comportamento esperado em cenários complexos, como filtros combinados com ordenação.


# Outros Módulos e Ferramentas de Suporte

> Além dos arquivos centrais que definem a lógica da IA, o projeto conta com outros módulos de suporte e ferramentas de desenvolvimento. Cada um desses arquivos possui sua própria documentação interna detalhada para explicar seu funcionamento.

- `app/core/llm.py:` Este arquivo atua como uma "fábrica" que centraliza a criação e configuração do modelo de linguagem (ChatGroq). Isso facilita a manutenção e a troca do modelo em um único local.

- `scripts/debug_runner.py:` Uma ferramenta de linha de comando para executar o roteiro de testes (ex: testes_completos.txt) de forma automatizada, exibindo os resultados de cada query diretamente no terminal. É essencial para a validação em lote.

- `scripts/test_ui.py:` Lança uma interface web local com Streamlit, ideal para testes individuais, prototipação rápida de novas regras de prompt e demonstrações visuais do fluxo da IA.

- `sql/:` Esta pasta organiza todo o código SQL relevante para o projeto, incluindo a procedure principal SP_TK_NOTAS_AI_HOM e os scripts usados para validação no banco de dados.

- `tests_case/:` Armazena os arquivos .txt que contêm as frases em linguagem natural usadas como entrada para os testes de integração, servindo como a "fonte da verdade" para validar o comportamento da IA.


# Endpoints

> Esta seção detalha os endpoints que sua API expõe, o que é crucial para a equipe que irá consumir seu microsserviço.

## **1. Endpoint de Produção**

### **Endpoint:** `POST /parse-query`

**Descrição:** Recebe uma query em linguagem natural e retorna apenas o objeto JSON final com os filtros extraídos. Este é o endpoint que deve ser consumido pela aplicação principal.
  
- **Request Body:**
  ```json
  {
    "query": "notas entregues hoje para o cliente BEXX"
  }
- **Success Response (200 OK)**
    ```
    {
    "NF":NULL
    "DE":"2025-10-17"
    "ATE":"2025-10-17"
    "TipoData":"2"
    "Cliente":"BEXX"
    "Transportadora":NULL
    "UFDestino":NULL
    "CidadeDestino":NULL
    "Operacao":NULL
    "SituacaoNF":NULL
    "StatusAnaliseData":NULL
    "CNPJRaizTransp":NULL
    "SortColumn":NULL
    "SortDirection":NULL
    }
    ```
### **Endpoint:** `POST /debug-query`

**Descrição:** Endpoint para desenvolvimento e diagnóstico. Retorna um objeto JSON contendo os resultados de cada etapa da cadeia de IA.
  
- **Request Body:**
  ```json
  {
    "query": "notas entregues hoje para o cliente BEXX"
  }
- **Success Response (200 OK)**
    ```
    {
    "query": "notas entregues hoje para o cliente BEXX",
    "dates": {
        "today": "2025-10-17",
        "yesterday": "2025-10-16",
        "last_week_start": "2025-10-10",
        "week_start": "2025-10-13",
        "week_end": "2025-10-19",
        "month_start": "2025-10-01",
        "month_end": "2025-10-31",
        "semester_start": "2025-07-01",
        "semester_end": "2025-12-31"
    },
    "enhanced_query": "Quais notas fiscais foram entregues hoje para o cliente BEXX?",
    "parsed_json": {
        "NF": null,
        "DE": "2025-10-17",
        "ATE": "2025-10-17",
        "TipoData": "2",
        "Cliente": "BEXX",
        "Transportadora": null,
        "UFDestino": null,
        "CidadeDestino": null,
        "Operacao": null,
        "SituacaoNF": null,
        "StatusAnaliseData": null,
        "CNPJRaizTransp": null,
        "SortColumn": null,
        "SortDirection": null
    }
    }
    ```