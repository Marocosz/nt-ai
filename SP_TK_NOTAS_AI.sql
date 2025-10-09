CREATE
OR ALTER PROC [dbo].[SP_TK_NOTAS_AI] (
    @IdUsuario INT,
    @NF INT,
    @DE DATETIME,
    @ATE DATETIME,
    @TipoData VARCHAR(1)
) AS BEGIN
SET
    NOCOUNT ON;

-- Bloco principal para busca por período
IF (@NF = 0) BEGIN -- Ajusta a data final para incluir o dia inteiro
SET
    @ATE = DATEADD(SECOND, -1, DATEADD(DAY, 1, CAST(@ATE AS DATE)));

-- Tabela temporária para otimizar a seleção de colunas e evitar repetição do SELECT *
CREATE TABLE #FinalResult (
[SituacaoNF] VARCHAR(100),
[BancoOrigem] VARCHAR(50),
[StatusAtualizacao] VARCHAR(100),
[AnaliseData] VARCHAR(100),
[Operacao] VARCHAR(100),
[Frete] VARCHAR(100),
[Tomador] VARCHAR(200),
[Origem] VARCHAR(100),
[Destino] VARCHAR(100),
[UFDestino] CHAR(2),
[SerieNF] VARCHAR(10),
[NotaFiscal] INT,
[ClienteDestino] VARCHAR(200),
[EmissaoNota] VARCHAR(20),
[MontagemCarga] VARCHAR(20),
[ID_NFC] INT,
[CODFIL] VARCHAR(20),
[SERCON] VARCHAR(3),
[CODCON] VARCHAR(9),
[Documento] VARCHAR(32),
[DataExpedicao] VARCHAR(20),
[PrevisaoEntrega] VARCHAR(20),
[Agenda] VARCHAR(3),
[DataAgenda] VARCHAR(20),
[DescricaoAgenda] VARCHAR(200),
[DataEntrega] VARCHAR(20),
[ValorNF] DECIMAL(18, 2),
[Analista] VARCHAR(200),
[Ocorrencia] VARCHAR(500),
[DataOcorrencia] VARCHAR(20),
[Observacao] VARCHAR(MAX),
[CODTRANSP] INT,
[Parceiro] VARCHAR(200),
[CNPJRaizTransp] VARCHAR(10),
[TipoCte] VARCHAR(50),
[EntregaFinalizada] VARCHAR(3),
[CNPJDestino] VARCHAR(20),
[CODREM] INT,
[CODDES] INT,
[CNPJRaizREM] VARCHAR(10),
[Avaliacao] VARCHAR(50),
[STATUS_REAVALIACAO_CRM] VARCHAR(50),
[IdNivelServicoResponsavelMotivo] INT,
[ResponsavelMotivo] VARCHAR(200),
[OBSERVACAO_CRM] VARCHAR(MAX),
[DATA_REAVALIACAO_CRM] VARCHAR(20),
[IdUsuario_CRM] INT,
[NomeUsuarioCRM] VARCHAR(200),
[STATUS_REAVALIACAO_PARCEIRO] VARCHAR(50),
[OBSERVACAO_PARCEIRO] VARCHAR(MAX),
[DATA_REAVALIACAO_PARCEIRO] VARCHAR(20),
[IdUsuario_PARCEIRO] INT,
[NomeUsuarioParceiro] VARCHAR(200),
[STATUS_REAVALIACAO_TRANSPORTES] VARCHAR(50),
[OBSERVACAO_TRANSPORTES] VARCHAR(MAX),
[DATA_REAVALIACAO_TRANSPORTES] VARCHAR(20),
[IdUsuario_TRANSPORTES] INT,
[NomeUsuarioTransportes] VARCHAR(200),
[STATUS_REAVALIACAO_GESTOR_CRM] VARCHAR(50),
[OBSERVACAO_GESTOR_CRM] VARCHAR(MAX),
[DATA_REAVALIACAO_GESTOR_CRM] VARCHAR(20),
[IdUsuario_GESTOR_CRM] INT,
[NomeUsuarioGESTOR_CRM] VARCHAR(200),
[Esteira] VARCHAR(50),
[PrevisaoReal] VARCHAR(20),
[TipFrete] VARCHAR(1),
[PesoReal] DECIMAL(18, 2),
[Cubagem] DECIMAL(18, 4),
[QtdeVol] INT,
[ValTotal] DECIMAL(18, 2),
[MacroMotivoAtraso] VARCHAR(50),
[AtrasoPertinente] VARCHAR(50),
[EmailAnalista] VARCHAR(200),
[AnalistaTransp] VARCHAR(200)
);

-- Bloco de código para cada TipoData para otimizar a consulta
IF @TipoData = '1' BEGIN
INSERT INTO
    #FinalResult SELECT SituacaoNF, BancoOrigem, StatusAtualizacao, AnaliseData, Operacao, Frete, Tomador, Origem, Destino, UFDestino, SerieNF, NotaFiscal, ClienteDestino, EmissaoNota, MontagemCarga, ID_NFC, CODFIL, SERCON, CODCON, Documento, DataExpedicao, PrevisaoEntrega, Agenda, DataAgenda, DescricaoAgenda, DataEntrega, ValorNF, Analista, Ocorrencia, DataOcorrencia, Observacao, CODTRANSP, Parceiro, CNPJRaizTransp, TipoCte, EntregaFinalizada, CNPJDestino, CODREM, CODDES, CNPJRaizREM, Avaliacao, STATUS_REAVALIACAO_CRM, IdNivelServicoResponsavelMotivo, ResponsavelMotivo, OBSERVACAO_CRM, DATA_REAVALIACAO_CRM, IdUsuario_CRM, NomeUsuarioCRM, STATUS_REAVALIACAO_PARCEIRO, OBSERVACAO_PARCEIRO, DATA_REAVALIACAO_PARCEIRO, IdUsuario_PARCEIRO, NomeUsuarioParceiro, STATUS_REAVALIACAO_TRANSPORTES, OBSERVACAO_TRANSPORTES, DATA_REAVALIACAO_TRANSPORTES, IdUsuario_TRANSPORTES, NomeUsuarioTransportes, STATUS_REAVALIACAO_GESTOR_CRM, OBSERVACAO_GESTOR_CRM, DATA_REAVALIACAO_GESTOR_CRM, IdUsuario_GESTOR_CRM, NomeUsuarioGESTOR_CRM, Esteira, PrevisaoReal, TipFrete, PesoReal, Cubagem, QtdeVol, ValTotal, MacroMotivoAtraso, AtrasoPertinente, EmailAnalista, AnalistaTransp FROM dbo.FN_TK_NOTAS_AI_AUX(@IdUsuario) WHERE DataAgenda_Raw BETWEEN @DE AND @ATE;
END
ELSE IF @TipoData = '2' BEGIN
INSERT INTO
    #FinalResult SELECT SituacaoNF, BancoOrigem, StatusAtualizacao, AnaliseData, Operacao, Frete, Tomador, Origem, Destino, UFDestino, SerieNF, NotaFiscal, ClienteDestino, EmissaoNota, MontagemCarga, ID_NFC, CODFIL, SERCON, CODCON, Documento, DataExpedicao, PrevisaoEntrega, Agenda, DataAgenda, DescricaoAgenda, DataEntrega, ValorNF, Analista, Ocorrencia, DataOcorrencia, Observacao, CODTRANSP, Parceiro, CNPJRaizTransp, TipoCte, EntregaFinalizada, CNPJDestino, CODREM, CODDES, CNPJRaizREM, Avaliacao, STATUS_REAVALIACAO_CRM, IdNivelServicoResponsavelMotivo, ResponsavelMotivo, OBSERVACAO_CRM, DATA_REAVALIACAO_CRM, IdUsuario_CRM, NomeUsuarioCRM, STATUS_REAVALIACAO_PARCEIRO, OBSERVACAO_PARCEIRO, DATA_REAVALIACAO_PARCEIRO, IdUsuario_PARCEIRO, NomeUsuarioParceiro, STATUS_REAVALIACAO_TRANSPORTES, OBSERVACAO_TRANSPORTES, DATA_REAVALIACAO_TRANSPORTES, IdUsuario_TRANSPORTES, NomeUsuarioTransportes, STATUS_REAVALIACAO_GESTOR_CRM, OBSERVACAO_GESTOR_CRM, DATA_REAVALIACAO_GESTOR_CRM, IdUsuario_GESTOR_CRM, NomeUsuarioGESTOR_CRM, Esteira, PrevisaoReal, TipFrete, PesoReal, Cubagem, QtdeVol, ValTotal, MacroMotivoAtraso, AtrasoPertinente, EmailAnalista, AnalistaTransp FROM dbo.FN_TK_NOTAS_AI_AUX(@IdUsuario) WHERE DataEntrega_Raw BETWEEN @DE AND @ATE;
END
ELSE IF @TipoData = '3' BEGIN
INSERT INTO
    #FinalResult SELECT SituacaoNF, BancoOrigem, StatusAtualizacao, AnaliseData, Operacao, Frete, Tomador, Origem, Destino, UFDestino, SerieNF, NotaFiscal, ClienteDestino, EmissaoNota, MontagemCarga, ID_NFC, CODFIL, SERCON, CODCON, Documento, DataExpedicao, PrevisaoEntrega, Agenda, DataAgenda, DescricaoAgenda, DataEntrega, ValorNF, Analista, Ocorrencia, DataOcorrencia, Observacao, CODTRANSP, Parceiro, CNPJRaizTransp, TipoCte, EntregaFinalizada, CNPJDestino, CODREM, CODDES, CNPJRaizREM, Avaliacao, STATUS_REAVALIACAO_CRM, IdNivelServicoResponsavelMotivo, ResponsavelMotivo, OBSERVACAO_CRM, DATA_REAVALIACAO_CRM, IdUsuario_CRM, NomeUsuarioCRM, STATUS_REAVALIACAO_PARCEIRO, OBSERVACAO_PARCEIRO, DATA_REAVALIACAO_PARCEIRO, IdUsuario_PARCEIRO, NomeUsuarioParceiro, STATUS_REAVALIACAO_TRANSPORTES, OBSERVACAO_TRANSPORTES, DATA_REAVALIACAO_TRANSPORTES, IdUsuario_TRANSPORTES, NomeUsuarioTransportes, STATUS_REAVALIACAO_GESTOR_CRM, OBSERVACAO_GESTOR_CRM, DATA_REAVALIACAO_GESTOR_CRM, IdUsuario_GESTOR_CRM, NomeUsuarioGESTOR_CRM, Esteira, PrevisaoReal, TipFrete, PesoReal, Cubagem, QtdeVol, ValTotal, MacroMotivoAtraso, AtrasoPertinente, EmailAnalista, AnalistaTransp FROM dbo.FN_TK_NOTAS_AI_AUX(@IdUsuario) WHERE EmissaoNota_Raw BETWEEN @DE AND @ATE;
END
ELSE IF @TipoData = '4' BEGIN
INSERT INTO
    #FinalResult SELECT SituacaoNF, BancoOrigem, StatusAtualizacao, AnaliseData, Operacao, Frete, Tomador, Origem, Destino, UFDestino, SerieNF, NotaFiscal, ClienteDestino, EmissaoNota, MontagemCarga, ID_NFC, CODFIL, SERCON, CODCON, Documento, DataExpedicao, PrevisaoEntrega, Agenda, DataAgenda, DescricaoAgenda, DataEntrega, ValorNF, Analista, Ocorrencia, DataOcorrencia, Observacao, CODTRANSP, Parceiro, CNPJRaizTransp, TipoCte, EntregaFinalizada, CNPJDestino, CODREM, CODDES, CNPJRaizREM, Avaliacao, STATUS_REAVALIACAO_CRM, IdNivelServicoResponsavelMotivo, ResponsavelMotivo, OBSERVACAO_CRM, DATA_REAVALIACAO_CRM, IdUsuario_CRM, NomeUsuarioCRM, STATUS_REAVALIACAO_PARCEIRO, OBSERVACAO_PARCEIRO, DATA_REAVALIACAO_PARCEIRO, IdUsuario_PARCEIRO, NomeUsuarioParceiro, STATUS_REAVALIACAO_TRANSPORTES, OBSERVACAO_TRANSPORTES, DATA_REAVALIACAO_TRANSPORTES, IdUsuario_TRANSPORTES, NomeUsuarioTransportes, STATUS_REAVALIACAO_GESTOR_CRM, OBSERVACAO_GESTOR_CRM, DATA_REAVALIACAO_GESTOR_CRM, IdUsuario_GESTOR_CRM, NomeUsuarioGESTOR_CRM, Esteira, PrevisaoReal, TipFrete, PesoReal, Cubagem, QtdeVol, ValTotal, MacroMotivoAtraso, AtrasoPertinente, EmailAnalista, AnalistaTransp FROM dbo.FN_TK_NOTAS_AI_AUX(@IdUsuario) WHERE PrevisaoEntrega_Raw BETWEEN @DE AND @ATE;
END
ELSE IF @TipoData = '5' BEGIN
INSERT INTO
    #FinalResult SELECT SituacaoNF, BancoOrigem, StatusAtualizacao, AnaliseData, Operacao, Frete, Tomador, Origem, Destino, UFDestino, SerieNF, NotaFiscal, ClienteDestino, EmissaoNota, MontagemCarga, ID_NFC, CODFIL, SERCON, CODCON, Documento, DataExpedicao, PrevisaoEntrega, Agenda, DataAgenda, DescricaoAgenda, DataEntrega, ValorNF, Analista, Ocorrencia, DataOcorrencia, Observacao, CODTRANSP, Parceiro, CNPJRaizTransp, TipoCte, EntregaFinalizada, CNPJDestino, CODREM, CODDES, CNPJRaizREM, Avaliacao, STATUS_REAVALIACAO_CRM, IdNivelServicoResponsavelMotivo, ResponsavelMotivo, OBSERVACAO_CRM, DATA_REAVALIACAO_CRM, IdUsuario_CRM, NomeUsuarioCRM, STATUS_REAVALIACAO_PARCEIRO, OBSERVACAO_PARCEIRO, DATA_REAVALIACAO_PARCEIRO, IdUsuario_PARCEIRO, NomeUsuarioParceiro, STATUS_REAVALIACAO_TRANSPORTES, OBSERVACAO_TRANSPORTES, DATA_REAVALIACAO_TRANSPORTES, IdUsuario_TRANSPORTES, NomeUsuarioTransportes, STATUS_REAVALIACAO_GESTOR_CRM, OBSERVACAO_GESTOR_CRM, DATA_REAVALIACAO_GESTOR_CRM, IdUsuario_GESTOR_CRM, NomeUsuarioGESTOR_CRM, Esteira, PrevisaoReal, TipFrete, PesoReal, Cubagem, QtdeVol, ValTotal, MacroMotivoAtraso, AtrasoPertinente, EmailAnalista, AnalistaTransp FROM dbo.FN_TK_NOTAS_AI_AUX(@IdUsuario) WHERE PrevisaoReal_Raw BETWEEN @DE AND @ATE;
END
ELSE IF @TipoData = '6' BEGIN
INSERT INTO
    #FinalResult SELECT SituacaoNF, BancoOrigem, StatusAtualizacao, AnaliseData, Operacao, Frete, Tomador, Origem, Destino, UFDestino, SerieNF, NotaFiscal, ClienteDestino, EmissaoNota, MontagemCarga, ID_NFC, CODFIL, SERCON, CODCON, Documento, DataExpedicao, PrevisaoEntrega, Agenda, DataAgenda, DescricaoAgenda, DataEntrega, ValorNF, Analista, Ocorrencia, DataOcorrencia, Observacao, CODTRANSP, Parceiro, CNPJRaizTransp, TipoCte, EntregaFinalizada, CNPJDestino, CODREM, CODDES, CNPJRaizREM, Avaliacao, STATUS_REAVALIACAO_CRM, IdNivelServicoResponsavelMotivo, ResponsavelMotivo, OBSERVACAO_CRM, DATA_REAVALIACAO_CRM, IdUsuario_CRM, NomeUsuarioCRM, STATUS_REAVALIACAO_PARCEIRO, OBSERVACAO_PARCEIRO, DATA_REAVALIACAO_PARCEIRO, IdUsuario_PARCEIRO, NomeUsuarioParceiro, STATUS_REAVALIACAO_TRANSPORTES, OBSERVACAO_TRANSPORTES, DATA_REAVALIACAO_TRANSPORTES, IdUsuario_TRANSPORTES, NomeUsuarioTransportes, STATUS_REAVALIACAO_GESTOR_CRM, OBSERVACAO_GESTOR_CRM, DATA_REAVALIACAO_GESTOR_CRM, IdUsuario_GESTOR_CRM, NomeUsuarioGESTOR_CRM, Esteira, PrevisaoReal, TipFrete, PesoReal, Cubagem, QtdeVol, ValTotal, MacroMotivoAtraso, AtrasoPertinente, EmailAnalista, AnalistaTransp FROM dbo.FN_TK_NOTAS_AI_AUX(@IdUsuario) WHERE DataOcorrencia_Raw BETWEEN @DE AND @ATE AND CodOcorrencia IN (1, 7);
END
SELECT
    *
FROM
    #FinalResult ORDER BY DataOcorrencia;
    DROP TABLE #FinalResult;
END -- Bloco para busca por NF específica
ELSE BEGIN
SELECT
    SituacaoNF,
    BancoOrigem,
    StatusAtualizacao,
    AnaliseData,
    Operacao,
    Frete,
    Tomador,
    Origem,
    Destino,
    UFDestino,
    SerieNF,
    NotaFiscal,
    ClienteDestino,
    EmissaoNota,
    MontagemCarga,
    ID_NFC,
    CODFIL,
    SERCON,
    CODCON,
    Documento,
    DataExpedicao,
    PrevisaoEntrega,
    Agenda,
    DataAgenda,
    DescricaoAgenda,
    DataEntrega,
    ValorNF,
    Analista,
    Ocorrencia,
    DataOcorrencia,
    Observacao,
    CODTRANSP,
    Parceiro,
    CNPJRaizTransp,
    TipoCte,
    EntregaFinalizada,
    CNPJDestino,
    CODREM,
    CODDES,
    CNPJRaizREM,
    Avaliacao,
    STATUS_REAVALIACAO_CRM,
    IdNivelServicoResponsavelMotivo,
    ResponsavelMotivo,
    OBSERVACAO_CRM,
    DATA_REAVALIACAO_CRM,
    IdUsuario_CRM,
    NomeUsuarioCRM,
    STATUS_REAVALIACAO_PARCEIRO,
    OBSERVACAO_PARCEIRO,
    DATA_REAVALIACAO_PARCEIRO,
    IdUsuario_PARCEIRO,
    NomeUsuarioParceiro,
    STATUS_REAVALIACAO_TRANSPORTES,
    OBSERVACAO_TRANSPORTES,
    DATA_REAVALIACAO_TRANSPORTES,
    IdUsuario_TRANSPORTES,
    NomeUsuarioTransportes,
    STATUS_REAVALIACAO_GESTOR_CRM,
    OBSERVACAO_GESTOR_CRM,
    DATA_REAVALIACAO_GESTOR_CRM,
    IdUsuario_GESTOR_CRM,
    NomeUsuarioGESTOR_CRM,
    Esteira,
    PrevisaoReal,
    TipFrete,
    PesoReal,
    Cubagem,
    QtdeVol,
    ValTotal,
    MacroMotivoAtraso,
    AtrasoPertinente,
    EmailAnalista,
    AnalistaTransp
FROM
    dbo.FN_TK_NOTAS_AI_AUX(@IdUsuario)
WHERE
    NotaFiscal = @NF
ORDER BY
    DataOcorrencia;

END
SET
    NOCOUNT OFF;

END
GO