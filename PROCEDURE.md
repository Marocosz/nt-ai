# Documentação Técnica: Stored Procedure `SP_TK_NOTAS_AI_HOM`

## 1. Visão Geral
A Stored Procedure **`SP_TK_NOTAS_AI_HOM`** é o motor de execução da funcionalidade de **Busca Inteligente (Intent AI)** do sistema de Tracking. 
Diferente das procedures tradicionais que esperam inputs rígidos, esta SP foi desenhada para ser **altamente flexível e tolerante a falhas**, aceitando combinações dinâmicas de parâmetros gerados por um modelo de Linguagem Natural (LLM).

Ela atua como a interface final entre a interpretação semântica da IA (que gera um JSON de filtros) e os dados brutos armazenados no SQL Server.

---

## 2. Assinatura e Parâmetros

Abaixo, detalhamos cada parâmetro aceito pela procedure, sua tipagem técnica e o conceito de negócio que ele representa no contexto da IA.

### Parâmetros de Controle e Segurança

| Parâmetro | Tipo | Obrigatório? | Descrição Técnica & Utilidade |
| :--- | :--- | :--- | :--- |
| **`@IdUsuario`** | `INT` | **SIM** | **O Guardião da Segurança.**<br>Define o contexto de segurança da execução (Row-Level Security). A procedure usa este ID para filtrar na cláusula `WHERE` final apenas as notas que o usuário tem permissão para ver (seja ele Tomador, Transportadora ou Interno).<br>*Ex: Impede que a Coca-Cola veja notas da Pepsi.* |

### Parâmetros de Filtro (Extraídos da IA)

Todos os parâmetros abaixo são opcionais (`DEFAULT NULL`). A IA preenche apenas o que conseguir extrair da frase do usuário.

| Parâmetro | Tipo | Mapeamento AI | Descrição e Lógica de Negócio |
| :--- | :--- | :--- | :--- |
| **`@NF`** | `INT` | `NF` | **Busca Exata.**<br>Usado quando o usuário cita um número específico. Se preenchido, ele "curto-circuita" a lógica de data (Bloco 1), pois um número de nota é único e atemporal. |
| **`@DE`** | `DATETIME` | `DE` | **Início do Período.**<br>Data inicial para filtro temporal. Se `NULL`, a procedure assume automaticamente `DATEADD(MONTH, -1, GETDATE())` para evitar scan na tabela inteira. |
| **`@ATE`** | `DATETIME` | `ATE` | **Fim do Período.**<br>Data final. Se `NULL`, assume `DATEADD(MONTH, 1, GETDATE())`.<br>*Tratamento Técnico:* Recebe ajuste de segundos (`23:59:59`) no Bloco 1 para garantir a inclusão do dia final inteiro. |
| **`@TipoData`** | `VARCHAR(1)` | `TipoData` | **Seletor de Coluna de Data.**<br>Define *qual* coluna de data será filtrada pelo range `@DE` e `@ATE`.<br>`1`: Data Agenda<br>`2`: Data Entrega<br>`3`: Emissão (Padrão)<br>`4`: Previsão Entrega<br>`5`: Previsão Real<br>`6`: Data Ocorrência |
| **`@Cliente`** | `VARCHAR` | `Cliente` | **Busca Aproximada (`LIKE`).**<br>Filtra pelo nome do Tomador. Aceita nomes parciais.<br>*Ex:* "Mendes" encontra "W.C. MENDES". |
| **`@Transportadora`** | `VARCHAR` | `Transportadora` | **Busca Aproximada (`LIKE`).**<br>Filtra pelo nome do Parceiro/Transportadora. Aceita nomes parciais. |
| **`@UFDestino`** | `CHAR(2)` | `UFDestino` | **Filtro Geográfico (Estado).**<br>Busca exata pela sigla da UF. Alimentado pela regra de "Geografia Inteligente" da IA que converte "Minas Gerais" para "MG". |
| **`@CidadeDestino`** | `VARCHAR` | `CidadeDestino` | **Filtro Geográfico (Cidade).**<br>Busca Aproximada (`LIKE`) pelo nome da cidade de destino. |
| **`@Operacao`** | `VARCHAR` | `Operacao` | **Filtro de Categoria.**<br>Busca exata pelo tipo de operação logística (ex: 'InBound-IPO', 'OutBound-SPO'). |
| **`@SituacaoNF`** | `VARCHAR` | `SituacaoNF` | **Status Físico/Logístico.**<br>Filtra onde a nota *está* fisicamente.<br>*Valores:* 'ENTREGUE', 'TRÂNSITO', 'RETIDA'. |
| **`@StatusAnaliseData`**| `VARCHAR` | `StatusAnaliseData`| **Status de Performance (SLA).**<br>Filtra o cumprimento do prazo.<br>*Valores:* 'ATRASO', 'DIA SEGUINTE', 'DO DIA', 'ENTREGUE' (no contexto de performance).<br>*Tratamento:* Sofre `LTRIM(RTRIM)` para evitar erros de espaços. |
| **`@CNPJRaizTransp`** | `VARCHAR` | `CNPJRaizTransp`| **Filtro Técnico.**<br>Permite filtrar pela raiz do CNPJ (8 primeiros dígitos), útil para grandes grupos de transporte. |

### Parâmetros de Ordenação

| Parâmetro | Tipo | Mapeamento AI | Descrição |
| :--- | :--- | :--- | :--- |
| **`@SortColumn`** | `VARCHAR` | `SortColumn` | Define a coluna de ordenação (`data_entrega`, `valor_nf`, `data_emissao`). A IA traduz termos como "mais caro" para `valor_nf`. |
| **`@SortDirection`** | `VARCHAR` | `SortDirection` | Define a direção: `'ASC'` (Crescente) ou `'DESC'` (Decrescente). |

---

## 3. Estrutura Lógica Interna

A procedure é dividida em blocos lógicos para garantir performance e integridade dos dados.

### 3.1. Blindagem e Limpeza
* `WITH RECOMPILE`: Força o SQL Server a gerar um novo plano de execução a cada chamada. Isso é **crítico** para buscas dinâmicas, pois um plano otimizado para uma busca por "Data" pode ser péssimo para uma busca por "Nota Fiscal". Evita o problema de *Parameter Sniffing*.
* `LTRIM(RTRIM)`: Higieniza inputs de texto que são sensíveis a espaços (como o Status de Análise).

### 3.2. Bloco 1: Inteligência Temporal (Fallback)
Aqui reside uma lógica de proteção importante. A IA nem sempre envia datas.
* **Regra:** Se o usuário não enviou Datas (`DE/ATE`) E não enviou filtros específicos (como `NF` ou `Status`), a procedure assume automaticamente o **Mês Corrente (+/- 30 dias)**.
* **Por que:** Evita rodar um `SELECT *` na base inteira (milhões de linhas) se o usuário disser apenas "notas da coca-cola", protegendo a performance do banco.

### 3.3. Bloco 2: Validação de Segurança (Early Return)
* Se **todos** os parâmetros de filtro forem `NULL`, a procedure aborta imediatamente (`RETURN`), retornando 0 linhas.
* **Utilidade:** Previne consultas acidentais "em branco" que poderiam travar a aplicação.

### 3.4. Bloco 3: A Pré-Filtragem (`#FilteredData`)
Esta é a etapa de performance. Em vez de fazer joins pesados logo de cara, a procedure primeiro aplica todos os filtros na View principal (`VW_NOTAS`) e joga o resultado numa tabela temporária.

* **Busca Dinâmica (`OR` Logic):** Utiliza o padrão `(@Parametro IS NULL OR Coluna = @Parametro)`. Isso permite que o SQL ignore filtros não enviados pela IA.
* **Mapeamento de `@TipoData`:** Um `CASE` complexo (via `OR`) decide qual coluna de data comparar baseada no valor numérico enviado pela IA (1 a 6).
* **Cast de Segurança:** O filtro `@StatusAnaliseData` força um `CAST AS VARCHAR(100)` para evitar conflitos de *collation* ou *unicode* que podem ocorrer na comunicação Node.js -> SQL Server.

### 3.5. Bloco 4: Enriquecimento e Retorno
Após filtrar os dados "brutos" na temporária, a procedure faz os `JOINs` com tabelas auxiliares (`TK_USUARIO`, `TK_NIVEL_SERVICO`, etc.) para buscar nomes, e-mails e detalhes do CRM.

* **Formatação de Datas:** Converte datas ISO do banco para formato brasileiro (`dd/mm/aaaa`), facilitando a exibição no Frontend sem processamento adicional.
* **Ordenação Dinâmica:** Utiliza um `CASE` dentro do `ORDER BY` para respeitar a escolha de coluna (`@SortColumn`) e direção (`@SortDirection`) da IA. Se a IA não pedir ordenação, o padrão é `DataOcorrencia DESC` (mais recentes primeiro).

---

## 4. Integração com a IA (Prompt Engineering)

A procedure foi desenhada "de trás para frente", baseada nas capacidades do prompt definido em `filter_prompts.py`.

### Casos de Uso Específicos:

1.  **"Notas para Minas Gerais"**
    * *Prompt:* Detecta estado -> JSON `{ UFDestino: 'MG', CidadeDestino: NULL }`.
    * *Procedure:* O parâmetro `@UFDestino` recebe 'MG'. O filtro `vw.UFDestino = @UFDestino` é ativado. O filtro de cidade é ignorado.

2.  **"W.C. Mendes"**
    * *Prompt:* Detecta cliente -> JSON `{ Cliente: 'w c mendes' }`.
    * *Procedure:* O parâmetro `@Cliente` recebe o valor. A cláusula `vw.Tomador LIKE '%w c mendes%'` é ativada, encontrando o registro mesmo que o nome completo seja diferente.

3.  **"Notas entregues semana passada"**
    * *Prompt:* Detecta evento 'entregue' (TipoData=2) e calcula datas relativas.
    * *Procedure:* Recebe `@TipoData = '2'` e o range de datas. O bloco `WHERE` ativa a comparação na coluna `vw.DataEntrega`.

4.  **"Notas com atraso"**
    * *Prompt:* Detecta performance -> JSON `{ StatusAnaliseData: 'ATRASO' }`.
    * *Procedure:* Recebe o parâmetro. A cláusula `vw.AnaliseData LIKE '%ATRASO%'` filtra as notas fora do prazo.

---

## 5. Conclusão Técnica

A `SP_TK_NOTAS_AI_HOM` é um componente híbrido que une a **rigidez necessária** de um banco relacional (tipagem, segurança) com a **fluidez** necessária para interfaces de conversação. O uso de parâmetros opcionais, buscas aproximadas (`LIKE`) e janelas de tempo automáticas garante que a experiência do usuário seja natural ("funciona como mágica"), enquanto o DBA tem garantias de que a query não derrubará o servidor.