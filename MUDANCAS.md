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
* **Controle de Acesso (Feature Flag):** Adicionada a variável `podeUsarIA`. No `ngOnInit`, verificamos se o e-mail do usuário logado (via `localStorage`) consta em uma **lista de permissão (Allowlist)**. O botão da IA só é renderizado se essa validação for verdadeira.
* **Variáveis de Controle UI:** `searchOpen` (abre/fecha balão), `termoBusca` (texto do input).
* **Função `filtrarGlobal()`:** Esta é a nova "gatilho". Ela substitui a lógica de pegar campos separados e envia apenas o texto e o ID do usuário para o serviço da IA.
    * *Destaque:* Implementamos uma lógica robusta para identificar o `idUsuario` correto, verificando se o perfil é `Tomador`, `Parceiro` ou `Usuário Interno` (Atribuído), replicando a segurança do legado.
* **Tratamento de Dados:** Copiamos a lógica de `Map` e `Deduplicação` existente no legado para dentro do `filtrarGlobal`. Isso garante que os dados vindos da IA passem pela mesma "higienização" que os dados legados.

#### Arquivo: `notas.component.html`
**Alterações:**
* A inserção do bloco HTML contendo o botão de "Lupa/Sparkle".
* **Diretiva Condicional:** O bloco inteiro da busca IA está envolvido em um `*ngIf="podeUsarIA"`, garantindo que usuários não autorizados não tenham acesso visual nem ao código HTML do componente.

---

### 3.2. Camada de Serviço (Service)

#### Arquivo: `notas.service.ts`
**O que foi mantido (INTACTO):**
* `getData(...)`: Método original que atende os filtros manuais.

**O que foi adicionado (NOVO):**
* `getDataIA(idUsuario, query)`: Um novo método isolado responsável por fazer a requisição POST para o backend Node.js na rota `/V1/tracking/notas/ia`.

---

### 3.3. Backend (Node.js)

#### Arquivo: `src/tracking.js`
**Alterações Recentes [ATUALIZADO]:**
* **Rota POST `/V1/tracking/notas/ia`**:
    1.  Recebe `idUsuario` e `query`.
    2.  Chama o Python.
    3.  Executa a procedure `SP_TK_NOTAS_AI_HOM`.
    4.  **Logging Otimizado:** Implementamos logs estratégicos que mostram a *Query do Usuário*, a *Interpretação da IA (JSON Formated)* e a *Contagem de Resultados*, removendo logs ruidosos de SQL bruto e dados massivos.

---

### 3.4. Microserviço de IA (Python/FastAPI)

#### Arquitetura de Prompts [ATUALIZADO]:
* **Abordagem Unificada (Turbo):** Migramos de um modelo de dois passos (Tradutor -> Extrator) para um modelo de passo único (`JSON_PARSER_PROMPT`). Isso reduziu a latência pela metade.
* **Geografia Inteligente [NOVO]:** Implementamos regras específicas no `filter_prompts.py` para desambiguidade geográfica:
    * Se o usuário digita um estado por extenso ("Minas Gerais"), a IA converte para UF (`MG`) e força `CidadeDestino = null`.
    * Evita o erro de buscar cidades inexistentes com nomes de estados.



---

### 3.5. Banco de Dados (SQL Server)

#### Procedures:
* **Nova:** `SP_TK_NOTAS_AI_HOM`. Criada para aceitar parâmetros flexíveis (muitos `NULLs`) gerados pela IA.

---

## 4. Análise de Segurança e Risco [ATUALIZADO]

### Por que é seguro rodar em produção?

1.  **Controle de Acesso Granular (Beta Privado):** A funcionalidade está protegida por uma verificação de e-mail no Frontend. Apenas usuários explicitamente listados (Equipe de TI e Stakeholders selecionados) podem ver e interagir com o recurso.
2.  **Princípio da Aditividade:** Todo código novo foi *adicionado*. Nenhuma linha de lógica de negócio antiga foi apagada.
3.  **Independência de Falha:** Falhas na OpenAI ou no Python não derrubam a tabela principal.

---

## 5. Como Manter

* **Para liberar acesso a novos usuários:** Adicionar o e-mail na lista `emailsPermitidos` dentro do `ngOnInit` em `notas.component.ts`.
* **Para ajustar regras de interpretação:** Edite `nt-ai/app/prompts/filter_prompts.py`.
* **Para mudar o visual:** Edite `notas.component.scss` (Bloco "Novo Design de Pesquisa").