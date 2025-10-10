/************************************************************************************
 * ROTEIRO DE TESTES DIRETOS PARA A PROCEDURE [SP_TK_NOTAS_AI_HOM]
 ************************************************************************************/

-- =====================================================================================
-- CENÁRIO 1: Busca ampla por período como Administrador
-- Objetivo: Testar a busca por data, sem filtros de IA, com a visão de admin.
-- =====================================================================================
PRINT 'Executando Cenário 1: Busca ampla por período como Administrador...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM] 
    @IdUsuario = 9999,
    @NF = 0,
    @DE = '2025-09-01',
    @ATE = '2025-09-10',
    @TipoData = '3', -- '3' = Data de Emissão
    @Cliente = NULL,
    @Transportadora = NULL,
    @UFDestino = NULL,
    @CidadeDestino = NULL,
    @Operacao = NULL,
    @SituacaoNF = NULL,
    @StatusAnaliseData = NULL,
    @CNPJRaizTransp = NULL,
    @SortColumn = NULL,
    @SortDirection = 'DESC';
GO


-- =====================================================================================
-- CENÁRIO 2: Busca por uma Nota Fiscal específica
-- Objetivo: Testar a busca direta por @NF, que deve ignorar os filtros de data.
-- =====================================================================================
PRINT 'Executando Cenário 2: Busca por uma Nota Fiscal específica...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM] 
    @IdUsuario = 9999,
    @NF = 35843, -- <<< Altere aqui para uma NF que exista no seu banco de dados
    @DE = NULL,
    @ATE = NULL,
    @TipoData = NULL,
    @Cliente = NULL,
    @Transportadora = NULL,
    @UFDestino = NULL,
    @CidadeDestino = NULL,
    @Operacao = NULL,
    @SituacaoNF = NULL,
    @StatusAnaliseData = NULL,
    @CNPJRaizTransp = NULL,
    @SortColumn = NULL,
    @SortDirection = 'ASC';
GO


-- =====================================================================================
-- CENÁRIO 3: Simulação de busca com IA (Filtros + Ordenação Dinâmica)
-- Objetivo: Simular uma busca da IA que identificou cliente, UF, status e uma ordenação.
-- =====================================================================================
PRINT 'Executando Cenário 3: Simulação de busca com IA...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM] 
    @IdUsuario = 9999,
    @NF = 0,
    @DE = '2025-01-01',
    @ATE = '2025-12-31',
    @TipoData = '3', -- Data de Emissão
    @Cliente = 'CLIENTE A', -- Filtra por Tomador que contenha 'CLIENTE A'
    @Transportadora = NULL,
    @UFDestino = 'SP', -- Filtra por Estado de Destino = SP
    @CidadeDestino = NULL,
    @Operacao = 'VENDA', -- Filtra por Operação = VENDA
    @SituacaoNF = NULL,
    @StatusAnaliseData = 'ATRASADO', -- Filtra por Status da Análise = ATRASADO
    @CNPJRaizTransp = NULL,
    @SortColumn = 'valor_nf', -- Ordena pelo valor da nota fiscal
    @SortDirection = 'DESC'; -- Do maior para o menor
GO


-- =====================================================================================
-- CENÁRIO 4: Busca por Notas "Sem Associação"
-- Objetivo: Testar o comportamento específico do IdUsuario 8888.
-- =====================================================================================
PRINT 'Executando Cenário 4: Busca por Notas "Sem Associação"...';
EXEC [dbo].[SP_TK_NOTAS_AI_HOM] 
    @IdUsuario = 8888,
    @NF = 0,
    @DE = '2025-09-01',
    @ATE = '2025-10-10',
    @TipoData = '3', -- Data de Emissão
    @Cliente = NULL,
    @Transportadora = NULL,
    @UFDestino = NULL,
    @CidadeDestino = NULL,
    @Operacao = NULL,
    @SituacaoNF = NULL,
    @StatusAnaliseData = NULL,
    @CNPJRaizTransp = NULL,
    @SortColumn = NULL, 
    @SortDirection = 'ASC';
GO