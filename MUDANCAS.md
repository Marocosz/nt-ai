# Documentação Técnica: Implementação da Busca Inteligente (IA Generativa) - Projeto Tracking

## 1. Visão Executiva
Esta documentação detalha a implementação do recurso de **Busca por Linguagem Natural** no sistema de Tracking. 
A arquitetura foi desenhada seguindo o princípio de **Isolamento de Funcionalidades**, criando uma "via expressa" paralela para a IA sem alterar ou refatorar as regras de negócio legadas já existentes.

---

## 2. Arquitetura da Solução: O Modelo de "Vias Paralelas"

Imagine o sistema como uma rodovia. Nós não alteramos a pista existente (Filtros Tradicionais), apenas construímos uma nova pista ao lado (Busca IA) que leva ao mesmo destino (A Tabela de Visualização).

### Diagrama Lógico de Fluxo
1. **Via Tradicional (Legado):** Inputs Manuais -> `filtrar()` -> `getData()` -> `SP_TK_NOTAS` -> Tabela.
2. **Via Inteligente (Nova):** Texto Livre -> `filtrarGlobal()` -> `getDataIA()` -> Python/LLM -> `SP_TK_NOTAS_AI_HOM` -> Tabela.

**Ponto de Convergência:** Ambas as vias terminam na função `this.source.load(dados)`, que é o motor de renderização da `ng2-smart-table`.

---

## 3. Detalhamento por Camada

### 3.1. Frontend (Angular)

#### Arquivo: `notas.component.ts`
**O que foi mantido (INTACTO):**
* `ngOnInit()`: Continua carregando os dados iniciais via `getData`.
* Filtros de Data/Status/NF: Continuam usando suas variáveis e bindings originais.
* Estrutura da Tabela: `settings`, `columns` e configurações da `ng2-smart-table` não foram tocadas.

**O que foi adicionado (NOVO):**
* **Variáveis de Controle UI:** `searchOpen` (abre/fecha balão), `termoBusca` (texto do input).
* **Função `filtrarGlobal()`:** Esta é a nova "gatilho". Ela substitui a lógica de pegar campos separados e envia apenas o texto e o ID do usuário para o serviço da IA.
    * *Destaque:* Implementamos uma lógica robusta para identificar o `idUsuario` correto, verificando se o perfil é `Tomador`, `Parceiro` ou `Usuário Interno` (Atribuído), replicando a segurança do legado.
* **Tratamento de Dados:** Copiamos a lógica de `Map` e `Deduplicação` existente no legado para dentro do `filtrarGlobal`. Isso garante que os dados vindos da IA passem pela mesma "higienização" que os dados legados, evitando bugs visuais, mas sem depender da função antiga.

#### Arquivo: `notas.component.html`
**Alterações:**
* A inserção do bloco HTML contendo o botão de "Lupa/Sparkle" e o `textarea` para digitação.
* Nenhuma estrutura de layout existente foi removida ou alterada.

---

### 3.2. Camada de Serviço (Service)

#### Arquivo: `notas.service.ts`
**O que foi mantido (INTACTO):**
* `getData(nf, de, ate, tipodata)`: Método original que atende os filtros manuais.
* `getDataExcel(...)`: Método de exportação.

**O que foi adicionado (NOVO):**
* `getDataIA(idUsuario, query)`: Um novo método isolado.
    * **Responsabilidade:** Fazer a requisição POST para o backend Node.js na rota `/V1/tracking/notas/ia`.
    * **Isolamento:** Se este método falhar, os filtros normais continuam funcionando 100%.

---

### 3.3. Backend (Node.js)

#### Arquivo: `src/tracking.js`
**O que foi mantido (INTACTO):**
* Todas as rotas existentes (`/V1/tracking/notas/...`).
* Configurações de conexão com o SQL Server e TypeORM.

**O que foi adicionado (NOVO):**
* **Rota POST `/V1/tracking/notas/ia`**:
    1.  Recebe `idUsuario` e `query` (texto).
    2.  Comunica-se com o Microserviço Python via HTTP (`axios`).
    3.  Recebe o JSON de filtros interpretados pela IA (ex: `{ "DE": "2026-01-12", "TipoData": "2" }`).
    4.  Executa a procedure SQL dedicada (`SP_TK_NOTAS_AI_HOM`).
    5.  Retorna o `recordset` (linhas da tabela) para o Angular.

* *Configuração:* Ajustamos o `timeout` do axios para **60000ms (60s)** para acomodar o tempo de "pensamento" de modelos de IA mais complexos.

---

### 3.4. Microserviço de IA (Python/FastAPI)

#### Componentes Novos:
* **`main.py`**: Servidor API que recebe o texto do Node.js.
* **`app/chains/master_chain.py`**: O "Cérebro".
    * Usa `LangChain` para orquestrar o pensamento.
    * Contém os prompts que ensinam a IA sobre as regras de negócio (ex: "Entregue" = código "2").
* **`app/core/llm.py`**: Fábrica de conexões com LLMs (OpenAI GPT-4o-mini, Google Gemini, Groq). Configurado atualmente para **OpenAI**.

**Fluxo:**
`Texto do Usuário` -> `Prompt de Classificação` -> `Extração de Entidades (Datas, NF)` -> `JSON Estruturado`.

---

### 3.5. Banco de Dados (SQL Server)

#### Procedures:
* **Legado:** `SP_TK_NOTAS...` (Mantida intacta).
* **Nova:** `SP_TK_NOTAS_AI_HOM`.
    * Criada especificamente para aceitar os parâmetros flexíveis que a IA gera.
    * Não interfere nas procedures usadas pelos relatórios ou telas antigas.

---

## 4. Análise de Segurança e Risco

### Por que é seguro rodar em produção?

1.  **Princípio da Aditividade:** Todo código novo foi *adicionado*. Nenhuma linha de lógica de negócio antiga foi *apagada* ou *modificada*.
2.  **Independência de Falha:**
    * Se a API da OpenAI cair, a busca inteligente falha (dá erro no Toastr), mas a tabela e os filtros normais continuam funcionando.
    * Se o Python cair, o Node retorna erro apenas na rota `/ia`, sem derrubar o servidor principal.
3.  **Renderização Compartilhada:**
    * Ao usar `this.source.load(dados)` no final do processo, garantimos que a **visualização** dos dados é idêntica à original. Não criamos uma "segunda tabela" que poderia ter estilos ou comportamentos diferentes (paginação, ordenação, etc).

---

## 5. Como Manter

* **Para alterar o modelo de IA:** Edite `nt-ai/app/core/llm.py` e a chamada em `master_chain.py`.
* **Para ajustar regras de interpretação (ex: ensinar uma gíria nova):** Edite os prompts em `nt-ai/app/core/prompts.py`.
* **Para mudar a query do banco:** Altere a procedure `SP_TK_NOTAS_AI_HOM` no SQL Server.
* **Para mudar o visual do botão:** Edite `notas.component.scss`.

## 6. Conclusão

O sistema agora opera em **Modo Híbrido**:
1.  **Determinístico (Legado):** Para quando o usuário quer controle exato (clicar na data, digitar o número).
2.  **Probabilístico/Inteligente (IA):** Para quando o usuário quer agilidade ("notas de ontem").

Ambos convivem harmonicamente no mesmo ecossistema.