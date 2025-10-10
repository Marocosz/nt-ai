CREATE
OR ALTER PROC [dbo].[SP_TK_NOTAS_AI_HOM] (
    -- Parâmetros Originais
    @IdUsuario INT,
    @NF INT = NULL,
    @DE DATETIME = NULL,
    @ATE DATETIME = NULL,
    @TipoData VARCHAR(1) = NULL,
    -- Novos Parâmetros para a IA (Opcionais)
    @Cliente VARCHAR(100) = NULL,
    @Transportadora VARCHAR(100) = NULL,
    @UFDestino CHAR(2) = NULL,
    @CidadeDestino VARCHAR(100) = NULL,
    @Operacao VARCHAR(100) = NULL,
    @SituacaoNF VARCHAR(100) = NULL,
    @StatusAnaliseData VARCHAR(100) = NULL,
    @CNPJRaizTransp VARCHAR(8) = NULL,
    -- Novos Parâmetros de Ordenação
    @SortColumn VARCHAR(50) = NULL,
    @SortDirection VARCHAR(4) = 'ASC'
) AS BEGIN
SET
    NOCOUNT ON;

-- Ajusta a data final para incluir todas as horas do dia.
IF @ATE IS NOT NULL
SET
    @ATE = DATEADD(SECOND, -1, DATEADD(DAY, 1, CAST(@ATE AS DATE)));

-- 1. PRÉ-FILTRAGEM (Otimização Principal)
-- Insere em uma tabela temporária apenas os dados que correspondem aos filtros primários.
SELECT
    * INTO #FilteredData
FROM
    VW_NOTAS vw
WHERE
    -- Filtro por Nota Fiscal (tem prioridade)
    (
        @NF IS NOT NULL
        AND vw.NotaFiscal = @NF
    )
    OR -- Filtro por Período de Data (se NF não for especificada)
    (
        @NF IS NULL
        AND @TipoData IS NOT NULL
        AND (
            (
                @TipoData = '1'
                AND vw.DataAgenda BETWEEN @DE
                AND @ATE
            )
            OR (
                @TipoData = '2'
                AND vw.DataEntrega BETWEEN @DE
                AND @ATE
            )
            OR (
                @TipoData = '3'
                AND vw.EmissaoNota BETWEEN @DE
                AND @ATE
            )
            OR (
                @TipoData = '4'
                AND vw.PrevisaoEntrega BETWEEN @DE
                AND @ATE
            )
            OR (
                @TipoData = '5'
                AND vw.PrevisaoReal BETWEEN @DE
                AND @ATE
            )
            OR (
                @TipoData = '6'
                AND vw.DataOcorrencia BETWEEN @DE
                AND @ATE
                AND vw.CodOcorrencia IN (1, 7)
            )
        )
    ) -- Filtros adicionais da IA (aplicados já nesta primeira etapa para máxima performance)
    AND (
        @Cliente IS NULL
        OR vw.Tomador LIKE '%' + @Cliente + '%'
    )
    AND (
        @Transportadora IS NULL
        OR vw.Parceiro LIKE '%' + @Transportadora + '%'
    )
    AND (
        @UFDestino IS NULL
        OR vw.UFDestino = @UFDestino
    )
    AND (
        @CidadeDestino IS NULL
        OR vw.Destino LIKE '%' + @CidadeDestino + '%'
    )
    AND (
        @Operacao IS NULL
        OR vw.Operacao = @Operacao
    )
    AND (
        @SituacaoNF IS NULL
        OR vw.SituacaoNF = @SituacaoNF
    )
    AND (
        @StatusAnaliseData IS NULL
        OR vw.AnaliseData = @StatusAnaliseData
    )
    AND (
        @CNPJRaizTransp IS NULL
        OR vw.CNPJRaizTransp = @CNPJRaizTransp
    );

-- 2. CONSULTA PRINCIPAL (Executada uma única vez sobre os dados pré-filtrados)
SELECT
    VW.SituacaoNF,
    VW.BancoOrigem,
    VW.StatusAtualizacao,
    VW.AnaliseData,
    VW.Operacao,
    VW.Frete,
    VW.Tomador,
    VW.Origem,
    VW.Destino,
    VW.UFDestino,
    VW.SerieNF,
    VW.NotaFiscal,
    VW.ClienteDestino,
    CASE
        VW.EmissaoNota
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.EmissaoNota, 103)
    END AS EmissaoNota,
    CASE
        VW.MontagemCarga
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.MontagemCarga, 103)
    END AS MontagemCarga,
    VW.ID_NFC,
    VW.CODFIL,
    VW.SERCON,
    VW.CODCON,
    VW.Documento,
    CASE
        VW.DataExpedicao
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.DataExpedicao, 103)
    END AS DataExpedicao,
    CASE
        VW.PrevisaoEntrega
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.PrevisaoEntrega, 103)
    END AS PrevisaoEntrega,
    VW.Agenda,
    CASE
        VW.DataAgenda
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.DataAgenda, 103) + ' ' + CONVERT(VARCHAR(8), VW.DataAgenda, 108)
    END AS DataAgenda,
    VW.DescricaoAgenda,
    CASE
        VW.DataEntrega
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.DataEntrega, 103)
    END AS DataEntrega,
    VW.ValorNF,
    ISNULL(TS.Nome, 'SEM ASSOCIAÇÃO') AS Analista,
    VW.Ocorrencia AS Ocorrencia,
    CASE
        VW.DataOcorrencia
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.DataOcorrencia, 103) + ' ' + CONVERT(VARCHAR(8), VW.DataOcorrencia, 108)
    END AS DataOcorrencia,
    VW.Observacao,
    VW.CODTRANSP,
    VW.Parceiro AS Parceiro,
    VW.CNPJRaizTransp,
    VW.TipoCte,
    VW.EntregaFinalizada,
    VW.CNPJDestino,
    VW.CODREM,
    VW.CODDES,
    VW.CNPJRaizREM,
    VW.Avaliacao,
    CASE
        COALESCE(
            NS.STATUS_REAVALIACAO,
            NS_PROTHEUS.STATUS_REAVALIACAO
        )
        WHEN '1' THEN 'Atraso'
        WHEN '2' THEN 'Cumpriu'
        WHEN '3' THEN 'Perda Agenda'
        WHEN '4' THEN 'Reagenda'
        WHEN '5' THEN 'No Prazo / Cumpriu'
    END AS STATUS_REAVALIACAO_CRM,
    M.IdNivelServicoResponsavelMotivo,
    M.Nome AS ResponsavelMotivo,
    COALESCE(NS.OBSERVACAO, NS_PROTHEUS.OBSERVACAO) AS OBSERVACAO_CRM,
    CASE
        COALESCE(
            NS.DATA_REAVALIACAO,
            NS_PROTHEUS.DATA_REAVALIACAO
        )
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(
            varchar(20),
            COALESCE(
                NS.DATA_REAVALIACAO,
                NS_PROTHEUS.DATA_REAVALIACAO
            ),
            103
        ) + ' ' + CONVERT(
            VARCHAR(8),
            COALESCE(
                NS.DATA_REAVALIACAO,
                NS_PROTHEUS.DATA_REAVALIACAO
            ),
            108
        )
    END AS DATA_REAVALIACAO_CRM,
    UCRM.IdUsuario AS IdUsuario_CRM,
    UCRM.Nome AS NomeUsuarioCRM,
    CASE
        COALESCE(
            NS.STATUS_REAVALIACAO_PARCEIRO,
            NS_PROTHEUS.STATUS_REAVALIACAO_PARCEIRO
        )
        WHEN '501' THEN 'Concordo'
        WHEN '502' THEN 'Discordo'
    END AS STATUS_REAVALIACAO_PARCEIRO,
    COALESCE(
        NS.OBSERVACAO_PARCEIRO,
        NS_PROTHEUS.OBSERVACAO_PARCEIRO
    ) AS OBSERVACAO_PARCEIRO,
    CASE
        COALESCE(
            NS.DATA_REAVALIACAO_PARCEIRO,
            NS_PROTHEUS.DATA_REAVALIACAO_PARCEIRO
        )
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(
            varchar(20),
            COALESCE(
                NS.DATA_REAVALIACAO_PARCEIRO,
                NS_PROTHEUS.DATA_REAVALIACAO_PARCEIRO
            ),
            103
        ) + ' ' + CONVERT(
            VARCHAR(8),
            COALESCE(
                NS.DATA_REAVALIACAO_PARCEIRO,
                NS_PROTHEUS.DATA_REAVALIACAO_PARCEIRO
            ),
            108
        )
    END AS DATA_REAVALIACAO_PARCEIRO,
    UPAR.IdUsuario AS IdUsuario_PARCEIRO,
    UPAR.Nome AS NomeUsuarioParceiro,
    CASE
        COALESCE(
            NS.STATUS_REAVALIACAO_TRANSPORTES,
            NS_PROTHEUS.STATUS_REAVALIACAO_TRANSPORTES
        )
        WHEN '401' THEN 'Atrasou'
        WHEN '402' THEN 'Cumpriu'
    END AS STATUS_REAVALIACAO_TRANSPORTES,
    COALESCE(
        NS.OBSERVACAO_TRANSPORTES,
        NS_PROTHEUS.OBSERVACAO_TRANSPORTES
    ) AS OBSERVACAO_TRANSPORTES,
    CASE
        COALESCE(
            NS.DATA_REAVALIACAO_TRANSPORTES,
            NS_PROTHEUS.DATA_REAVALIACAO_TRANSPORTES
        )
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(
            varchar(20),
            COALESCE(
                NS.DATA_REAVALIACAO_TRANSPORTES,
                NS_PROTHEUS.DATA_REAVALIACAO_TRANSPORTES
            ),
            103
        ) + ' ' + CONVERT(
            VARCHAR(8),
            COALESCE(
                NS.DATA_REAVALIACAO_TRANSPORTES,
                NS_PROTHEUS.DATA_REAVALIACAO_TRANSPORTES
            ),
            108
        )
    END AS DATA_REAVALIACAO_TRANSPORTES,
    UTRA.IdUsuario AS IdUsuario_TRANSPORTES,
    UTRA.Nome AS NomeUsuarioTransportes,
    CASE
        COALESCE(
            NS.STATUS_REAVALIACAO_GESTOR_CRM,
            NS_PROTHEUS.STATUS_REAVALIACAO_GESTOR_CRM
        )
        WHEN '601' THEN 'Atrasou'
        WHEN '602' THEN 'Cumpriu'
    END AS STATUS_REAVALIACAO_GESTOR_CRM,
    COALESCE(
        NS.OBSERVACAO_GESTOR_CRM,
        NS_PROTHEUS.OBSERVACAO_GESTOR_CRM
    ) AS OBSERVACAO_GESTOR_CRM,
    CASE
        COALESCE(
            NS.DATA_REAVALIACAO_GESTOR_CRM,
            NS_PROTHEUS.DATA_REAVALIACAO_GESTOR_CRM
        )
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(
            varchar(20),
            COALESCE(
                NS.DATA_REAVALIACAO_GESTOR_CRM,
                NS_PROTHEUS.DATA_REAVALIACAO_GESTOR_CRM
            ),
            103
        ) + ' ' + CONVERT(
            VARCHAR(8),
            COALESCE(
                NS.DATA_REAVALIACAO_GESTOR_CRM,
                NS_PROTHEUS.DATA_REAVALIACAO_GESTOR_CRM
            ),
            108
        )
    END AS DATA_REAVALIACAO_GESTOR_CRM,
    UPAG.IdUsuario AS IdUsuario_GESTOR_CRM,
    UPAG.Nome AS NomeUsuarioGESTOR_CRM,
    COALESCE(NS.Esteira, NS_PROTHEUS.Esteira) AS Esteira,
    CASE
        VW.PrevisaoReal
        WHEN '1900-01-01' THEN ''
        ELSE CONVERT(varchar(20), VW.PrevisaoReal, 103) + ' ' + CONVERT(VARCHAR(8), VW.PrevisaoReal, 108)
    END AS PrevisaoReal,
    VW.TipFrete,
    VW.PesoReal,
    VW.Cubagem,
    VW.QtdeVol,
    VW.ValTotal,
    ISNULL(
        COALESCE(NS.MACRO_MOTIVO, NS_PROTHEUS.MACRO_MOTIVO),
        ''
    ) AS MacroMotivoAtraso,
    ISNULL(
        COALESCE(
            NS.ATRASO_PERTINENTE,
            NS_PROTHEUS.ATRASO_PERTINENTE
        ),
        ''
    ) AS AtrasoPertinente,
    ISNULL(TS.Email, '') AS EmailAnalista,
    ISNULL(VW.AnalistaTransp, 'SEM ASSOCIAÇÃO') AS AnalistaTransp
FROM
    #FilteredData VW
    LEFT JOIN TK_USUARIO TS WITH (NOLOCK) ON TS.IdUsuario = VW.IdUsuario
    LEFT JOIN TK_NIVEL_SERVICO NS WITH (NOLOCK) ON VW.BancoOrigem <> 'protheus'
    AND NS.BancoOrigem = VW.BancoOrigem
    AND NS.ID_NFC = VW.ID_NFC
    LEFT JOIN TK_NIVEL_SERVICO NS_PROTHEUS WITH (NOLOCK) ON VW.BancoOrigem = 'protheus'
    AND NS_PROTHEUS.BancoOrigem = VW.BancoOrigem
    AND NS_PROTHEUS.CODFIL = VW.CODFIL
    AND NS_PROTHEUS.SERCON = VW.SERCON
    AND NS_PROTHEUS.CODCON = VW.CODCON
    AND NS_PROTHEUS.SerieNF = VW.SerieNF
    AND NS_PROTHEUS.NotaFiscal = VW.NotaFiscal
    LEFT JOIN TK_USUARIO UCRM WITH (NOLOCK) ON UCRM.IdUsuario = COALESCE(NS.IdUsuario, NS_PROTHEUS.IdUsuario)
    LEFT JOIN TK_USUARIO UTRA WITH (NOLOCK) ON UTRA.IdUsuario = COALESCE(
        NS.IdUsuario_TRANSPORTES,
        NS_PROTHEUS.IdUsuario_TRANSPORTES
    )
    LEFT JOIN TK_USUARIO UPAR WITH (NOLOCK) ON UPAR.IdUsuario = COALESCE(
        NS.IdUsuario_PARCEIRO,
        NS_PROTHEUS.IdUsuario_PARCEIRO
    )
    LEFT JOIN TK_USUARIO UPAG WITH (NOLOCK) ON UPAG.IdUsuario = COALESCE(
        NS.IdUsuario_GESTOR_CRM,
        NS_PROTHEUS.IdUsuario_GESTOR_CRM
    )
    LEFT JOIN TK_NIVEL_SERVICO_RESPONSAVEL_MOTIVO M WITH (NOLOCK) ON M.IdNivelServicoResponsavelMotivo = CASE
        WHEN COALESCE(
            NS.ResponsavelMotivo,
            NS_PROTHEUS.ResponsavelMotivo
        ) = 'Outros' THEN 62
        ELSE COALESCE(
            NS.ResponsavelMotivo,
            NS_PROTHEUS.ResponsavelMotivo
        )
    END
    LEFT JOIN TK_TRANSP_X_CLIENTE_X_USUARIO TRCS WITH (NOLOCK) ON TRCS.CODDES = VW.CODDES
    AND TRCS.CODTRANSP = VW.CODTRANSP
    AND TRCS.BancoOrigem = 'protheus'
    LEFT JOIN TK_USUARIO TST WITH (NOLOCK) ON TST.IdUsuario = TRCS.IdUsuario
WHERE
    -- Filtro final de permissão de usuário
    (
        @IdUsuario = 9999
        OR (
            @IdUsuario = 8888
            AND TS.IdUsuario IS NULL
        )
        OR TS.IdUsuario = @IdUsuario
        OR TST.IdUsuario = @IdUsuario
    ) -- Ordenação dinâmica
ORDER BY
    CASE
        WHEN @SortColumn = 'data_entrega'
        AND @SortDirection = 'ASC' THEN VW.DataEntrega
    END ASC,
    CASE
        WHEN @SortColumn = 'data_entrega'
        AND @SortDirection = 'DESC' THEN VW.DataEntrega
    END DESC,
    CASE
        WHEN @SortColumn = 'valor_nf'
        AND @SortDirection = 'ASC' THEN VW.ValorNF
    END ASC,
    CASE
        WHEN @SortColumn = 'valor_nf'
        AND @SortDirection = 'DESC' THEN VW.ValorNF
    END DESC,
    CASE
        WHEN @SortColumn = 'data_emissao'
        AND @SortDirection = 'ASC' THEN VW.EmissaoNota
    END ASC,
    CASE
        WHEN @SortColumn = 'data_emissao'
        AND @SortDirection = 'DESC' THEN VW.EmissaoNota
    END DESC,
    VW.DataOcorrencia DESC;

-- Ordenação Padrão
-- Limpeza da tabela temporária
DROP TABLE #FilteredData;
SET
    NOCOUNT OFF;

END
GO