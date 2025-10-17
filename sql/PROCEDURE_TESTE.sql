/***************************************************************************************************
 *
 * ROTEIRO DE TESTES DE INTEGRAÇÃO: IA -> BANCO DE DADOS
 * PROCEDURE: [dbo].[SP_TK_NOTAS_AI_HOM]
 *
 * =================================================================================================
 *
 * DESCRIÇÃO:
 * Este script tem como finalidade validar a camada de banco de dados, especificamente a
 * procedure [SP_TK_NOTAS_AI_HOM]. Ele simula o fluxo completo da aplicação, utilizando como
 * entrada os parâmetros exatos que são gerados pelo microsserviço de inteligência
 * artificial (nt-ai) a partir de queries em linguagem natural.
 *
 * O bloco de documentação abaixo contém o log completo da execução dos testes na IA,
 * servindo como referência para os cenários executados neste script.
 *
 * =================================================================================================
 *
 * INSTRUÇÕES:
 * 1. Verifique se o valor do @IdUsuario (9999) está correto para o seu ambiente.
 * 2. Execute o script completo para rodar todos os 14 cenários de teste da IA.
 * 3. Analise os resultados de cada execução para garantir que a procedure está filtrando
 * e ordenando os dados conforme o esperado para cada conjunto de parâmetros.
 *
 ****************************************************************************************************/

/*
====================================================================================================
==
==    LOG DE RESULTADOS DO MICROSSERVIÇO DE IA (nt-ai)
==
==    Origem: Saída do script `debug_runner.py`
==    Data dos Testes: 15 de Outubro de 2025
==
====================================================================================================

=============================================
 INICIANDO ROTEIRO DE TESTES - New Tracking Intent AI
=============================================

--- TESTE #1/14 ---
Query Original: me mostre a nota fiscal 55432
1. Query Otimizada (pela IA): Me mostre a nota fiscal 55432.
2. JSON de Filtros Gerado:
{
  "NF": 55432,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
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
---------------------
--- TESTE #2/14 ---
Query Original: quais notas foram entregues hoje?
1. Query Otimizada (pela IA): Quais notas fiscais foram entregues hoje?
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": "2025-10-15",
  "ATE": "2025-10-15",
  "TipoData": "2",
  "Cliente": null,
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
---------------------
--- TESTE #3/14 ---
Query Original: o que foi baixado na última semana?
1. Query Otimizada (pela IA): O que foi baixado na última semana?
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": "2025-10-08",
  "ATE": "2025-10-15",
  "TipoData": "6",
  "Cliente": null,
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
---------------------
--- TESTE #4/14 ---
Query Original: notas previstas entre 1 e 15 de setembro de 2025
1. Query Otimizada (pela IA): Me mostre as notas fiscais previstas entre 1 e 15 de setembro de 2025.
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": "2025-09-01",
  "ATE": "2025-09-15",
  "TipoData": "4",
  "Cliente": null,
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
---------------------
--- TESTE #5/14 ---
Query Original: notas com operação InBound-IPO
1. Query Otimizada (pela IA): Me mostre as notas fiscais com operação InBound-IPO.
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
  "Transportadora": null,
  "UFDestino": null,
  "CidadeDestino": null,
  "Operacao": "InBound-IPO",
  "SituacaoNF": null,
  "StatusAnaliseData": null,
  "CNPJRaizTransp": null,
  "SortColumn": null,
  "SortDirection": null
}
---------------------
--- TESTE #6/14 ---
Query Original: uais notas foram retidas?
1. Query Otimizada (pela IA): Quais notas foram retidas?
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
  "Transportadora": null,
  "UFDestino": null,
  "CidadeDestino": null,
  "Operacao": null,
  "SituacaoNF": "RETIDA",
  "StatusAnaliseData": null,
  "CNPJRaizTransp": null,
  "SortColumn": null,
  "SortDirection": null
}
---------------------
--- TESTE #7/14 ---
Query Original: me mostre as notas com status DO DIA
1. Query Otimizada (pela IA): Me mostre as notas com status de análise DO DIA.
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
  "Transportadora": null,
  "UFDestino": null,
  "CidadeDestino": null,
  "Operacao": null,
  "SituacaoNF": null,
  "StatusAnaliseData": "DO DIA",
  "CNPJRaizTransp": null,
  "SortColumn": null,
  "SortDirection": null
}
---------------------
--- TESTE #8/14 ---
Query Original: notas entregues ontem
1. Query Otimizada (pela IA): Quais notas fiscais foram entregues ontem?
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": "2025-10-14",
  "ATE": "2025-10-14",
  "TipoData": "2",
  "Cliente": null,
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
---------------------
--- TESTE #9/14 ---
Query Original: notas com status entregue
1. Query Otimizada (pela IA): Quais notas fiscais têm status de entregue?
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
  "Transportadora": null,
  "UFDestino": null,
  "CidadeDestino": null,
  "Operacao": null,
  "SituacaoNF": "ENTREGUE",
  "StatusAnaliseData": null,
  "CNPJRaizTransp": null,
  "SortColumn": null,
  "SortDirection": null
}
---------------------
--- TESTE #10/14 ---
Query Original: notas rodando ordenadas pelo mais caro
1. Query Otimizada (pela IA): Me mostre as notas fiscais em trânsito ordenadas pelo maior valor
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
  "Transportadora": null,
  "UFDestino": null,
  "CidadeDestino": null,
  "Operacao": null,
  "SituacaoNF": "TRÂNSITO",
  "StatusAnaliseData": null,
  "CNPJRaizTransp": null,
  "SortColumn": "valor_nf",
  "SortDirection": "DESC"
}
---------------------
--- TESTE #11/14 ---
Query Original: mostre as notas para a cidade de São Paulo
1. Query Otimizada (pela IA): Me mostre as notas fiscais para a cidade de São Paulo.
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
  "Transportadora": null,
  "UFDestino": "SP",
  "CidadeDestino": "São Paulo",
  "Operacao": null,
  "SituacaoNF": null,
  "StatusAnaliseData": null,
  "CNPJRaizTransp": null,
  "SortColumn": null,
  "SortDirection": null
}
---------------------
--- TESTE #12/14 ---
Query Original: quais notas da transportadora RápidoLog para Manaus foram baixadas na semana passada e estão com análise ATRASO?
1. Query Otimizada (pela IA): Me mostre as notas fiscais da transportadora RápidoLog para Manaus que foram baixadas na semana passada e estão com status de análise ATRASO.
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": "2025-10-08",
  "ATE": "2025-10-15",
  "TipoData": "6",
  "Cliente": null,
  "Transportadora": "RápidoLog",
  "UFDestino": "AM",
  "CidadeDestino": "Manaus",
  "Operacao": null,
  "SituacaoNF": null,
  "StatusAnaliseData": "ATRASO",
  "CNPJRaizTransp": null,
  "SortColumn": null,
  "SortDirection": null
}
---------------------
--- TESTE #13/14 ---
Query Original: qual o status da entrega?
1. Query Otimizada (pela IA): Qual o status da entrega?
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
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
---------------------
--- TESTE #14/14 ---
Query Original: quais são os clientes?
1. Query Otimizada (pela IA): Quais são os clientes?
2. JSON de Filtros Gerado:
{
  "NF": null,
  "DE": null,
  "ATE": null,
  "TipoData": null,
  "Cliente": null,
  "Transportadora": null,
  "UFDestino": null,
  "CidadeDestino": null,
  "Operacao": null,
  "Operacao": null,
  "StatusAnaliseData": null,
  "StatusAnaliseData": null,
  "CNPJRaizTransp": null,
  "SortColumn": null,
  "SortDirection": null
}
---------------------
=============================================
     ROTEIRO DE TESTES FINALIZADO
=============================================
*/

-- =====================================================================================
-- IA TESTE #1: Busca por NF específica
-- Query Original: "me mostre a nota fiscal 55432"
-- =====================================================================================
PRINT 'Executando IA Teste #1: Busca por NF específica (55432)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM] @IdUsuario = 9999, @NF = 55432;

-- =====================================================================================
-- IA TESTE #2: Busca por data relativa (hoje) e tipo de data
-- Query Original: "quais notas foram entregues hoje?"
-- =====================================================================================
PRINT 'Executando IA Teste #2: Notas entregues hoje...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @DE = '2025-10-15',
    @ATE = '2025-10-15',
    @TipoData = '2'; -- '2' = Entregue

-- =====================================================================================
-- IA TESTE #3: Busca por data relativa (última semana)
-- Query Original: "o que foi baixado na última semana?"
-- =====================================================================================
PRINT 'Executando IA Teste #3: Notas baixadas na última semana...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @DE = '2025-10-08',
    @ATE = '2025-10-15',
    @TipoData = '6'; -- '6' = Baixada

-- =====================================================================================
-- IA TESTE #4: Busca por data absoluta
-- Query Original: "notas previstas entre 1 e 15 de setembro de 2025"
-- =====================================================================================
PRINT 'Executando IA Teste #4: Notas previstas em um intervalo específico...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @DE = '2025-09-01',
    @ATE = '2025-09-15',
    @TipoData = '4'; -- '4' = Previsto

-- =====================================================================================
-- IA TESTE #5: Filtro por Operação
-- Query Original: "notas com operação InBound-IPO"
-- =====================================================================================
PRINT 'Executando IA Teste #5: Filtro por Operação (InBound-IPO)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @Operacao = 'InBound-IPO';

-- =====================================================================================
-- IA TESTE #6: Filtro por Situação da NF
-- Query Original: "quais notas foram retidas?"
-- =====================================================================================
PRINT 'Executando IA Teste #6: Filtro por Situação da NF (RETIDA)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @SituacaoNF = 'RETIDA';

-- =====================================================================================
-- IA TESTE #7: Filtro por Status da Análise
-- Query Original: "me mostre as notas com status DO DIA"
-- =====================================================================================
PRINT 'Executando IA Teste #7: Filtro por Status da Análise (DO DIA)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @StatusAnaliseData = 'DO DIA';

-- =====================================================================================
-- IA TESTE #8: Desambiguação de Data (evento com data)
-- Query Original: "notas entregues ontem"
-- =====================================================================================
PRINT 'Executando IA Teste #8: Desambiguação (evento com data)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @DE = '2025-10-14',
    @ATE = '2025-10-14',
    @TipoData = '2'; -- '2' = Entregue

-- =====================================================================================
-- IA TESTE #9: Desambiguação de Status (estado sem data)
-- Query Original: "notas com status entregue"
-- =====================================================================================
PRINT 'Executando IA Teste #9: Desambiguação (estado sem data)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @SituacaoNF = 'ENTREGUE';

-- =====================================================================================
-- IA TESTE #10: Filtro de Status com Ordenação
-- Query Original: "notas rodando ordenadas pelo mais caro"
-- =====================================================================================
PRINT 'Executando IA Teste #10: Filtro de Status com Ordenação...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @SituacaoNF = 'TRÂNSITO',
    @SortColumn = 'valor_nf',
    @SortDirection = 'DESC';

-- =====================================================================================
-- IA TESTE #11: Filtro Geográfico Específico (Cidade e Estado)
-- Query Original: "mostre as notas para a cidade de São Paulo"
-- =====================================================================================
PRINT 'Executando IA Teste #11: Filtro Geográfico (Cidade e Estado)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @UFDestino = 'SP',
    @CidadeDestino = 'São Paulo';

-- =====================================================================================
-- IA TESTE #12: Busca Complexa com Múltiplos Filtros
-- Query Original: "quais notas da transportadora RápidoLog para Manaus foram baixadas na semana passada e estão com análise ATRASO?"
-- =====================================================================================
PRINT 'Executando IA Teste #12: Busca Complexa com Múltiplos Filtros...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999,
    @DE = '2025-10-08',
    @ATE = '2025-10-15',
    @TipoData = '6', -- '6' = Baixada
    @Transportadora = 'RápidoLog',
    @UFDestino = 'AM',
    @CidadeDestino = 'Manaus',
    @StatusAnaliseData = 'ATRASO';

-- =====================================================================================
-- IA TESTE #13 & #14: Consultas Vagas (JSON nulo)
-- Query Original: "qual o status da entrega?" e "quais são os clientes?"
-- Objetivo: Testar a busca mais ampla possível, sem filtros da IA.
-- =====================================================================================
PRINT 'Executando IA Teste #13 & #14: Consulta Vaga (sem filtros)...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM]
    @IdUsuario = 9999;