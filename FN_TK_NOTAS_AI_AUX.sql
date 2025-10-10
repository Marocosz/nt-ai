CREATE
OR ALTER FUNCTION [dbo].[FN_TK_NOTAS_AI_AUX] (@IdUsuario INT) RETURNS TABLE AS RETURN (
    -- Bloco para dados que NÃO são do Protheus
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
            WHEN VW.EmissaoNota = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.EmissaoNota, 103)
        END AS EmissaoNota,
        CASE
            WHEN VW.MontagemCarga = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.MontagemCarga, 103)
        END AS MontagemCarga,
        VW.ID_NFC,
        VW.CODFIL,
        VW.SERCON,
        VW.CODCON,
        VW.Documento,
        CASE
            WHEN VW.DataExpedicao = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataExpedicao, 103)
        END AS DataExpedicao,
        CASE
            WHEN VW.PrevisaoEntrega = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.PrevisaoEntrega, 103)
        END AS PrevisaoEntrega,
        VW.Agenda,
        CASE
            WHEN VW.DataAgenda = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataAgenda, 103) + ' ' + CONVERT(VARCHAR(8), VW.DataAgenda, 108)
        END AS DataAgenda,
        VW.DescricaoAgenda,
        CASE
            WHEN VW.DataEntrega = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataEntrega, 103)
        END AS DataEntrega,
        VW.ValorNF,
        ISNULL(TS.Nome, 'SEM ASSOCIAÇÃO') AS Analista,
        VW.Ocorrencia,
        CASE
            WHEN VW.DataOcorrencia = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataOcorrencia, 103) + ' ' + CONVERT(VARCHAR(8), VW.DataOcorrencia, 108)
        END AS DataOcorrencia,
        VW.Observacao,
        VW.CODTRANSP,
        VW.Parceiro,
        VW.CNPJRaizTransp,
        VW.TipoCte,
        VW.EntregaFinalizada,
        VW.CNPJDestino,
        VW.CODREM,
        VW.CODDES,
        VW.CNPJRaizREM,
        VW.Avaliacao,
        CASE
            NS.STATUS_REAVALIACAO
            WHEN '1' THEN 'Atraso'
            WHEN '2' THEN 'Cumpriu'
            WHEN '3' THEN 'Perda Agenda'
            WHEN '4' THEN 'Reagenda'
            WHEN '5' THEN 'No Prazo / Cumpriu'
        END AS STATUS_REAVALIACAO_CRM,
        M.IdNivelServicoResponsavelMotivo,
        M.Nome AS ResponsavelMotivo,
        NS.OBSERVACAO AS OBSERVACAO_CRM,
        CASE
            WHEN NS.DATA_REAVALIACAO = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), NS.DATA_REAVALIACAO, 103) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO, 108)
        END AS DATA_REAVALIACAO_CRM,
        UCRM.IdUsuario AS IdUsuario_CRM,
        UCRM.Nome AS NomeUsuarioCRM,
        CASE
            NS.STATUS_REAVALIACAO_PARCEIRO
            WHEN '501' THEN 'Concordo'
            WHEN '502' THEN 'Discordo'
        END AS STATUS_REAVALIACAO_PARCEIRO,
        NS.OBSERVACAO_PARCEIRO,
        CASE
            WHEN NS.DATA_REAVALIACAO_PARCEIRO = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), NS.DATA_REAVALIACAO_PARCEIRO, 103) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO_PARCEIRO, 108)
        END AS DATA_REAVALIACAO_PARCEIRO,
        UPAR.IdUsuario AS IdUsuario_PARCEIRO,
        UPAR.Nome AS NomeUsuarioParceiro,
        CASE
            NS.STATUS_REAVALIACAO_TRANSPORTES
            WHEN '401' THEN 'Atrasou'
            WHEN '402' THEN 'Cumpriu'
        END AS STATUS_REAVALIACAO_TRANSPORTES,
        NS.OBSERVACAO_TRANSPORTES,
        CASE
            WHEN NS.DATA_REAVALIACAO_TRANSPORTES = '1900-01-01' THEN ''
            ELSE CONVERT(
                varchar(10),
                NS.DATA_REAVALIACAO_TRANSPORTES,
                103
            ) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO_TRANSPORTES, 108)
        END AS DATA_REAVALIACAO_TRANSPORTES,
        UTRA.IdUsuario AS IdUsuario_TRANSPORTES,
        UTRA.Nome AS NomeUsuarioTransportes,
        CASE
            NS.STATUS_REAVALIACAO_GESTOR_CRM
            WHEN '601' THEN 'Atrasou'
            WHEN '602' THEN 'Cumpriu'
        END AS STATUS_REAVALIACAO_GESTOR_CRM,
        NS.OBSERVACAO_GESTOR_CRM,
        CASE
            WHEN NS.DATA_REAVALIACAO_GESTOR_CRM = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), NS.DATA_REAVALIACAO_GESTOR_CRM, 103) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO_GESTOR_CRM, 108)
        END AS DATA_REAVALIACAO_GESTOR_CRM,
        UPAG.IdUsuario AS IdUsuario_GESTOR_CRM,
        UPAG.Nome AS NomeUsuarioGESTOR_CRM,
        NS.Esteira,
        CASE
            WHEN VW.PrevisaoReal = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.PrevisaoReal, 103) + ' ' + CONVERT(VARCHAR(8), VW.PrevisaoReal, 108)
        END AS PrevisaoReal,
        VW.TipFrete,
        VW.PesoReal,
        VW.Cubagem,
        VW.QtdeVol,
        VW.ValTotal,
        ISNULL(NS.MACRO_MOTIVO, '') AS MacroMotivoAtraso,
        ISNULL(NS.ATRASO_PERTINENTE, '') AS AtrasoPertinente,
        ISNULL(TS.Email, '') AS EmailAnalista,
        ISNULL(VW.AnalistaTransp, 'SEM ASSOCIAÇÃO') AS AnalistaTransp,
        VW.CodOcorrencia,
        -- Colunas originais para filtro, sem formatação
        VW.DataAgenda AS DataAgenda_Raw,
        VW.DataEntrega AS DataEntrega_Raw,
        VW.EmissaoNota AS EmissaoNota_Raw,
        VW.PrevisaoEntrega AS PrevisaoEntrega_Raw,
        VW.PrevisaoReal AS PrevisaoReal_Raw,
        VW.DataOcorrencia AS DataOcorrencia_Raw
    FROM
        VW_NOTAS VW WITH (NOLOCK)
        LEFT JOIN TK_USUARIO TS WITH (NOLOCK) ON TS.IdUsuario = VW.IdUsuario
        LEFT JOIN TK_NIVEL_SERVICO NS WITH (NOLOCK) ON NS.BancoOrigem = VW.BancoOrigem
        AND NS.ID_NFC = VW.ID_NFC
        LEFT JOIN TK_USUARIO UCRM WITH (NOLOCK) ON UCRM.IdUsuario = NS.IdUsuario
        LEFT JOIN TK_USUARIO UTRA WITH (NOLOCK) ON UTRA.IdUsuario = NS.IdUsuario_TRANSPORTES
        LEFT JOIN TK_USUARIO UPAR WITH (NOLOCK) ON UPAR.IdUsuario = NS.IdUsuario_PARCEIRO
        LEFT JOIN TK_USUARIO UPAG WITH (NOLOCK) ON UPAG.IdUsuario = NS.IdUsuario_GESTOR_CRM
        LEFT JOIN TK_NIVEL_SERVICO_RESPONSAVEL_MOTIVO M WITH (NOLOCK) ON M.IdNivelServicoResponsavelMotivo = CASE WHEN NS.ResponsavelMotivo = 'Outros' THEN 62 ELSE NS.ResponsavelMotivo END
        LEFT JOIN TK_TRANSP_X_CLIENTE_X_USUARIO TRCS WITH (NOLOCK) ON TRCS.CODDES = VW.CODDES
        AND TRCS.CODTRANSP = VW.CODTRANSP
        AND TRCS.BancoOrigem = VW.BancoOrigem
        LEFT JOIN TK_USUARIO TST WITH (NOLOCK) ON TST.IdUsuario = TRCS.IdUsuario
    WHERE
        VW.BancoOrigem <> 'protheus'
        AND (
            @IdUsuario = 9999
            OR (
                @IdUsuario = 8888
                AND TS.IdUsuario IS NULL
            )
            OR TS.IdUsuario = @IdUsuario
            OR TST.IdUsuario = @IdUsuario
        )
    UNION
    ALL -- Bloco para dados do PROTHEUS
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
            WHEN VW.EmissaoNota = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.EmissaoNota, 103)
        END AS EmissaoNota,
        CASE
            WHEN VW.MontagemCarga = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.MontagemCarga, 103)
        END AS MontagemCarga,
        VW.ID_NFC,
        VW.CODFIL,
        VW.SERCON,
        VW.CODCON,
        VW.Documento,
        CASE
            WHEN VW.DataExpedicao = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataExpedicao, 103)
        END AS DataExpedicao,
        CASE
            WHEN VW.PrevisaoEntrega = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.PrevisaoEntrega, 103)
        END AS PrevisaoEntrega,
        VW.Agenda,
        CASE
            WHEN VW.DataAgenda = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataAgenda, 103) + ' ' + CONVERT(VARCHAR(8), VW.DataAgenda, 108)
        END AS DataAgenda,
        VW.DescricaoAgenda,
        CASE
            WHEN VW.DataEntrega = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataEntrega, 103)
        END AS DataEntrega,
        VW.ValorNF,
        ISNULL(TS.Nome, 'SEM ASSOCIAÇÃO') AS Analista,
        VW.Ocorrencia,
        CASE
            WHEN VW.DataOcorrencia = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.DataOcorrencia, 103) + ' ' + CONVERT(VARCHAR(8), VW.DataOcorrencia, 108)
        END AS DataOcorrencia,
        VW.Observacao,
        VW.CODTRANSP,
        VW.Parceiro,
        VW.CNPJRaizTransp,
        VW.TipoCte,
        VW.EntregaFinalizada,
        VW.CNPJDestino,
        VW.CODREM,
        VW.CODDES,
        VW.CNPJRaizREM,
        VW.Avaliacao,
        CASE
            NS.STATUS_REAVALIACAO
            WHEN '1' THEN 'Atraso'
            WHEN '2' THEN 'Cumpriu'
            WHEN '3' THEN 'Perda Agenda'
            WHEN '4' THEN 'Reagenda'
            WHEN '5' THEN 'No Prazo / Cumpriu'
        END AS STATUS_REAVALIACAO_CRM,
        M.IdNivelServicoResponsavelMotivo,
        M.Nome AS ResponsavelMotivo,
        NS.OBSERVACAO AS OBSERVACAO_CRM,
        CASE
            WHEN NS.DATA_REAVALIACAO = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), NS.DATA_REAVALIACAO, 103) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO, 108)
        END AS DATA_REAVALIACAO_CRM,
        UCRM.IdUsuario AS IdUsuario_CRM,
        UCRM.Nome AS NomeUsuarioCRM,
        CASE
            NS.STATUS_REAVALIACAO_PARCEIRO
            WHEN '501' THEN 'Concordo'
            WHEN '502' THEN 'Discordo'
        END AS STATUS_REAVALIACAO_PARCEIRO,
        NS.OBSERVACAO_PARCEIRO,
        CASE
            WHEN NS.DATA_REAVALIACAO_PARCEIRO = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), NS.DATA_REAVALIACAO_PARCEIRO, 103) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO_PARCEIRO, 108)
        END AS DATA_REAVALIACAO_PARCEIRO,
        UPAR.IdUsuario AS IdUsuario_PARCEIRO,
        UPAR.Nome AS NomeUsuarioParceiro,
        CASE
            NS.STATUS_REAVALIACAO_TRANSPORTES
            WHEN '401' THEN 'Atrasou'
            WHEN '402' THEN 'Cumpriu'
        END AS STATUS_REAVALIACAO_TRANSPORTES,
        NS.OBSERVACAO_TRANSPORTES,
        CASE
            WHEN NS.DATA_REAVALIACAO_TRANSPORTES = '1900-01-01' THEN ''
            ELSE CONVERT(
                varchar(10),
                NS.DATA_REAVALIACAO_TRANSPORTES,
                103
            ) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO_TRANSPORTES, 108)
        END AS DATA_REAVALIACAO_TRANSPORTES,
        UTRA.IdUsuario AS IdUsuario_TRANSPORTES,
        UTRA.Nome AS NomeUsuarioTransportes,
        CASE
            NS.STATUS_REAVALIACAO_GESTOR_CRM
            WHEN '601' THEN 'Atrasou'
            WHEN '602' THEN 'Cumpriu'
        END AS STATUS_REAVALIACAO_GESTOR_CRM,
        NS.OBSERVACAO_GESTOR_CRM,
        CASE
            WHEN NS.DATA_REAVALIACAO_GESTOR_CRM = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), NS.DATA_REAVALIACAO_GESTOR_CRM, 103) + ' ' + CONVERT(VARCHAR(8), NS.DATA_REAVALIACAO_GESTOR_CRM, 108)
        END AS DATA_REAVALIACAO_GESTOR_CRM,
        UPAG.IdUsuario AS IdUsuario_GESTOR_CRM,
        UPAG.Nome AS NomeUsuarioGESTOR_CRM,
        NS.Esteira,
        CASE
            WHEN VW.PrevisaoReal = '1900-01-01' THEN ''
            ELSE CONVERT(varchar(10), VW.PrevisaoReal, 103) + ' ' + CONVERT(VARCHAR(8), VW.PrevisaoReal, 108)
        END AS PrevisaoReal,
        VW.TipFrete,
        VW.PesoReal,
        VW.Cubagem,
        VW.QtdeVol,
        VW.ValTotal,
        ISNULL(NS.MACRO_MOTIVO, '') AS MacroMotivoAtraso,
        ISNULL(NS.ATRASO_PERTINENTE, '') AS AtrasoPertinente,
        ISNULL(TS.Email, '') AS EmailAnalista,
        ISNULL(VW.AnalistaTransp, 'SEM ASSOCIAÇÃO') AS AnalistaTransp,
        VW.CodOcorrencia,
        -- Colunas originais para filtro, sem formatação
        VW.DataAgenda AS DataAgenda_Raw,
        VW.DataEntrega AS DataEntrega_Raw,
        VW.EmissaoNota AS EmissaoNota_Raw,
        VW.PrevisaoEntrega AS PrevisaoEntrega_Raw,
        VW.PrevisaoReal AS PrevisaoReal_Raw,
        VW.DataOcorrencia AS DataOcorrencia_Raw
    FROM
        VW_NOTAS VW WITH (NOLOCK)
        LEFT JOIN TK_USUARIO TS WITH (NOLOCK) ON TS.IdUsuario = VW.IdUsuario
        LEFT JOIN TK_NIVEL_SERVICO NS WITH (NOLOCK) ON NS.BancoOrigem = VW.BancoOrigem
        AND NS.CODFIL = VW.CODFIL
        AND NS.SERCON = VW.SERCON
        AND NS.CODCON = VW.CODCON
        AND NS.SerieNF = VW.SerieNF
        AND NS.NotaFiscal = VW.NotaFiscal
        LEFT JOIN TK_USUARIO UCRM WITH (NOLOCK) ON UCRM.IdUsuario = NS.IdUsuario
        LEFT JOIN TK_USUARIO UTRA WITH (NOLOCK) ON UTRA.IdUsuario = NS.IdUsuario_TRANSPORTES
        LEFT JOIN TK_USUARIO UPAR WITH (NOLOCK) ON UPAR.IdUsuario = NS.IdUsuario_PARCEIRO
        LEFT JOIN TK_USUARIO UPAG WITH (NOLOCK) ON UPAG.IdUsuario = NS.IdUsuario_GESTOR_CRM
        LEFT JOIN TK_NIVEL_SERVICO_RESPONSAVEL_MOTIVO M WITH (NOLOCK) ON M.IdNivelServicoResponsavelMotivo = CASE WHEN NS.ResponsavelMotivo = 'Outros' THEN 62 ELSE NS.ResponsavelMotivo END
        LEFT JOIN TK_TRANSP_X_CLIENTE_X_USUARIO TRCS WITH (NOLOCK) ON TRCS.CODDES = VW.CODDES
        AND TRCS.CODTRANSP = VW.CODTRANSP
        AND TRCS.BancoOrigem = VW.BancoOrigem
        LEFT JOIN TK_USUARIO TST WITH (NOLOCK) ON TST.IdUsuario = TRCS.IdUsuario
    WHERE
        VW.BancoOrigem = 'protheus'
        AND (
            @IdUsuario = 9999
            OR (
                @IdUsuario = 8888
                AND TS.IdUsuario IS NULL
            )
            OR TS.IdUsuario = @IdUsuario
            OR TST.IdUsuario = @IdUsuario
        )
);

GO