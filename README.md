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
  - [Nota sobre Chain of Thought (CoT) - Desativado](#nota-sobre-chain-of-thought-cot---desativado)
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
- [💾 Componente de Banco de Dados](#-componente-de-banco-de-dados)
  - [Stored Procedure: `SP_TK_NOTAS_AI_HOM`](#stored-procedure-sp_tk_notas_ai_hom)
- [🚀 Instalação e Configuração Local](#-instalação-e-configuração-local)
  - [Pré-requisitos](#pré-requisitos)
  - [Passos de Instalação](#passos-de-instalação)
  - [Executando a Aplicação](#executando-a-aplicação)
  - [Executando a Aplicação](#executando-a-aplicação-1)
  - [Ferramentas de Teste e Desenvolvimento](#ferramentas-de-teste-e-desenvolvimento)

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
├── 📁 app
│   ├── 📁 chains
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 master_chain.py
│   ├── 📁 core
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 llm.py
│   ├── 📁 prompts
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 filter_prompts.py
│   ├── 🐍 __init__.py
│   └── 🐍 main.py
├── 📁 scripts
│   ├── 🐍 debug_runner.py
│   └── 🐍 test_ui.py
├── 📁 sql
│   ├── 📄 SCRIPT_TESTE_AI_HOM.sql
│   ├── 📄 SP_DOC.txt
│   └── 📄 SP_TK_NOTAS_AI_HOM.sql
├── 📁 tests_cases
│   ├── 📄 testes.txt
│   └── 📄 testes_pontuais.txt
├── 📁 venvntia
├── 🔒 .env
├── 🔒 .env.example
├── 📝 README.md
└── 📄 requirements.txt
```


# 🔄 Updates

> [!NOTE]
> Versão 1

| Versão | Data       | Mudanças principais               |
|--------|------------|-----------------------------------|
| 1.0    | 22/10/2025 | MVP funcional


## Nota sobre Chain of Thought (CoT) - Desativado 

Durante o desenvolvimento e otimização da precisão da IA (especialmente na Cadeia de Parsing), a técnica de **Chain of Thought (CoT)** foi implementada e testada.

**O que é CoT?**

Chain of Thought é uma técnica de engenharia de prompts onde instruímos o Modelo de Linguagem (LLM) a "pensar passo a passo" antes de fornecer a resposta final. Em vez de pedir diretamente o JSON, o prompt pedia ao LLM para primeiro:
1.  Analisar o texto da consulta.
2.  Listar as entidades extraídas.
3.  Verificar as regras de negócio aplicáveis.
4.  *Só então* gerar o "JSON FINAL".

**Motivação para Usar (Benefícios):**

A principal motivação foi **aumentar a precisão da extração em consultas complexas**. Forçar o LLM a articular seu raciocínio intermediário demonstrou melhorar significativamente a aderência às regras de negócio complexas, como:
* A precedência do `StatusAnaliseData` sobre o `TipoData` 
* A correta aplicação de regras de coexistência entre `SituacaoNF` e `StatusAnaliseData`.
* A redução geral de erros onde o LLM poderia "esquecer" um filtro ao tentar formatar o JSON diretamente.

**Como poderia ser Implementado:**

1.  **Prompt (`filter_prompts.py`):** Adicionamos a seção "Pense passo a passo..." ao final do `JSON_PARSER_PROMPT`.
    ```python
    # Exemplo do bloco CoT adicionado ao prompt:
    """
    Pense passo a passo antes de gerar o JSON final:
    1.  **Análise do Texto:** (...)
    2.  **Extração de Entidades:** (...)
    3.  **Verificação de Regras:** (...)

    JSON FINAL:
    """
    ```
2.  **Orquestração (`master_chain.py`):** Como a saída do LLM agora continha o "pensamento" + "JSON FINAL:", foi necessário adicionar um passo extra na `json_parser_chain` usando `RunnableLambda` e uma função auxiliar (`_extract_json_from_output`) para isolar apenas o bloco JSON antes de passá-lo ao `OutputFixingParser`.

**Motivo da Desativação:**

Apesar da melhoria na precisão, o CoT introduziu um **custo computacional significativamente maior** por chamada à API do LLM (Groq, usando `llama-3.1-8b-instant` no *free tier*):
* **Latência Aumentada:** O tempo de resposta por query aumentou consideravelmente, pois o LLM precisava gerar mais texto (o raciocínio).
* **Problemas com Rate Limiting:** A API da Groq (no nível gratuito) possui limites de taxa agressivos (aproximadamente 1 chamada complexa/minuto). O CoT tornava as chamadas "caras", ativando o *throttling* (fila de espera) da API e causando timeouts no nosso script de teste (`debug_runner.py`), mesmo com timeouts de cliente aumentados (120s).

**Decisão Atual:**

Para garantir a **estabilidade dos testes**, e manter uma **performance aceitável** dentro das limitações do *free tier* da Groq, o Chain of Thought foi **desativado**. A precisão resultante (sem CoT, mas com prompts e exemplos refinados) foi considerada **muito boa (~97-100%)** e aceitável para o contexto atual da aplicação (uso interno). A estratégia de rodar testes em lotes com pausas longas (`debug_runner.py`) provou ser eficaz para evitar novos banimentos.

**Considerações Futuras:**

* Se a aplicação migrar para um plano pago da API LLM com limites de taxa mais altos.
* Se testes futuros revelarem uma queda inaceitável na precisão para casos de uso críticos.
* Nesses cenários, a **reativação do CoT** pode ser reconsiderada como uma forma de maximizar a robustez da interpretação.

---
## Próximas Implementações
- [ ] Monitorar a frequência de erros 400 (JSON nulo) em produção para avaliar a necessidade futura de um Gatekeeper Prompt.
- [ ] Expandir o roteiro de testes com mais casos de borda e combinações complexas.
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

# 💾 Componente de Banco de Dados

## Stored Procedure: `SP_TK_NOTAS_AI_HOM`

Representa o estágio final do fluxo de dados iniciado pela consulta do usuário. Esta Stored Procedure, localizada no diretório [`/sql`](./sql/), é a **consumidora direta** do objeto JSON gerado pelo microsserviço Intent AI.

**Responsabilidades Principais:**

1.  **Receber Filtros:** Aceita todos os parâmetros extraídos pela IA (datas, `TipoData`, `Cliente`, `Transportadora`, `UFDestino`, `CidadeDestino`, `Operacao`, `SituacaoNF`, `StatusAnaliseData`, `CNPJRaizTransp`, `SortColumn`, `SortDirection`) como parâmetros de entrada.
2.  **Consulta Dinâmica:** Constrói e executa uma consulta SQL dinâmica sobre a view principal (`VW_NOTAS`), aplicando apenas os filtros que foram fornecidos (não nulos) no JSON.
3.  **Otimização:** Utiliza uma tabela temporária (`#FilteredData`) para aplicar os filtros iniciais de forma eficiente antes de realizar JOINs mais complexos para enriquecimento de dados.
4.  **Lógica de Negócio e Permissões:** Inclui lógicas específicas do New Tracking, como o tratamento de datas padrão ('1900-01-01'), formatação de saída e, crucialmente, a aplicação de regras de permissão de acesso baseadas no `@IdUsuario`.
5.  **Ordenação:** Implementa a ordenação dinâmica dos resultados com base nos parâmetros `@SortColumn` e `@SortDirection`.

> [!TIP]
> **Documentação Detalhada da Procedure:**
> A Stored Procedure `SP_TK_NOTAS_AI_HOM` possui uma lógica SQL complexa e otimizações específicas. Para uma análise aprofundada de seus parâmetros, blocos lógicos (validação, pré-filtragem, joins, permissões, ordenação), dependências (como `VW_NOTAS`) e exemplos de execução direta no banco, consulte o arquivo de documentação dedicado:
>
> **[`./sql/PROCEDURE_SP_TK_NOTAS_AI_HOM_DOCS.md`](./sql/PROCEDURE_SP_TK_NOTAS_AI_HOM_DOCS.md)**

---

# 🚀 Instalação e Configuração Local

Siga os passos abaixo para configurar e executar o microsserviço `nt-ai` em seu ambiente de desenvolvimento local.

## Pré-requisitos

Certifique-se de ter os seguintes softwares instalados em sua máquina:

* [Python](https://www.python.org/downloads/) (Versão **3.12** ou superior)
* [Git](https://git-scm.com/downloads/)
* Opcional, mas recomendado: [uv](https://github.com/astral-sh/uv) (um instalador e resolvedor Python extremamente rápido, compatível com `pip`)
* Um editor de código (como [VS Code](https://code.visualstudio.com/))
* Acesso à internet para baixar dependências e interagir com a API da Groq.

## Passos de Instalação

1.  **Clonar o Repositório:**
    Abra seu terminal ou Git Bash e clone o projeto:
    ```bash
    git clone <URL_DO_SEU_REPOSITÓRIO_GIT>
    cd nt-ai
    ```
    *(Substitua `<URL_DO_SEU_REPOSITÓRIO_GIT>` pela URL real do seu repositório)*

2.  **Criar e Ativar o Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto. Navegue até a pasta raiz do projeto (`nt-ai`) no terminal.

    * **Usando `uv` (Recomendado, mais rápido):**
        ```bash
        # Criar o ambiente virtual com uv (já instala pip por padrão)
        uv venv venvntai

        # Ativar o ambiente virtual
        # No Windows (PowerShell):
        .\venvntai\Scripts\Activate.ps1
        # No Windows (Git Bash):
        source venvntai/Scripts/activate
        # No macOS/Linux:
        # source venvntai/bin/activate
        ```

    * **Alternativa com `python -m venv` (Padrão):**
        ```bash
        # Criar o ambiente virtual
        python -m venv venvntai

        # Ativar o ambiente virtual (mesmos comandos acima)
        # Windows (PowerShell): .\venvntai\Scripts\Activate.ps1
        # Windows (Git Bash): source venvntai/Scripts/activate
        # macOS/Linux: source venvntai/bin/activate
        ```
    Você saberá que o ambiente está ativo pois o nome `(venvntai)` aparecerá no início do prompt do seu terminal.

3.  **Instalar as Dependências:**
    Com o ambiente virtual ativado, instale todas as bibliotecas Python necessárias listadas no arquivo `requirements.txt`.

    * **Usando `uv` (Recomendado, muito mais rápido):**
        ```bash
        uv pip install -r requirements.txt
        ```

    * **Alternativa com `pip` (Padrão):**
        ```bash
        pip install -r requirements.txt
        ```

4.  **Configurar Variáveis de Ambiente:**
    Este projeto requer uma chave de API para se comunicar com o serviço LLM da Groq.
    * Crie um arquivo chamado `.env` na **raiz do projeto** (`nt-ai/`).
    * Abra o arquivo `.env` e adicione a seguinte linha, substituindo `<SUA_CHAVE_API_GROQ>` pela sua chave real obtida no [Console da Groq](https://console.groq.com/keys):
        ```env
        GROQ_API_KEY=<SUA_CHAVE_API_GROQ>
        ```
    * **Importante:** Certifique-se de que o arquivo `.env` esteja listado no seu `.gitignore` para não commitar sua chave secreta no repositório Git.

## Executando a Aplicação

*(O restante da seção permanece igual: Iniciar o Servidor FastAPI, Verificar a Aplicação, Ferramentas de Teste)*

---

## Executando a Aplicação

1.  **Iniciar o Servidor FastAPI:**
    Com o ambiente virtual ainda ativado e na pasta raiz do projeto, execute o seguinte comando para iniciar o servidor web local usando Uvicorn:
    ```bash
    uvicorn app.main:app --reload --port 5001
    ```
    * `app.main:app`: Indica ao Uvicorn para encontrar a instância `app` do FastAPI dentro do arquivo `app/main.py`.
    * `--reload`: Habilita o recarregamento automático do servidor sempre que um arquivo Python for modificado (ótimo para desenvolvimento).
    * `--port 5001`: Define a porta em que o servidor irá rodar (você pode alterar se necessário).

2.  **Verificar a Aplicação:**
    Se tudo estiver correto, você verá mensagens no terminal indicando que o servidor Uvicorn iniciou e está escutando na `http://127.0.0.1:5001`.
    * Abra seu navegador e acesse `http://127.0.0.1:5001/docs`. Você deverá ver a interface interativa da documentação Swagger UI/OpenAPI, onde pode explorar e testar os endpoints.

## Ferramentas de Teste e Desenvolvimento

Além de rodar o servidor principal, você pode usar as seguintes ferramentas:

1.  **Executor de Testes em Lote (`debug_runner.py`):**
    Use este script para rodar um conjunto de queries de um arquivo `.txt` contra o endpoint `/debug-query`. Lembre-se da estratégia de *batch throttling* para evitar problemas com a API da Groq.
    ```bash
    # Certifique-se de que o servidor FastAPI (uvicorn) esteja rodando em outra janela do terminal
    python scripts/debug_runner.py tests_case/testes_mestre.txt
    ```

2.  **Interface de Teste Streamlit (`test_ui.py`):**
    Para testes interativos individuais e visualização do fluxo da IA, execute a interface Streamlit:
    ```bash
    # Certifique-se de que o servidor FastAPI (uvicorn) esteja rodando em outra janela do terminal
    streamlit run scripts/test_ui.py
    ```
    Isso abrirá uma nova aba no seu navegador com a interface de teste.

---