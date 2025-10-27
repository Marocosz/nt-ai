from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, Dict, Any

class ParsedFilters(BaseModel):
    """
    Modelo Pydantic para validar a estrutura e os tipos do JSON
    gerado pela cadeia de parsing da IA (json_parser_chain).
    Espelha os parâmetros esperados pela SP_TK_NOTAS_AI_HOM.
    """
    NF: Optional[int] = None
    DE: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$') # Valida formato YYYY-MM-DD
    ATE: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$') # Valida formato YYYY-MM-DD
    TipoData: Optional[Literal['1', '2', '3', '4', '5', '6']] = None
    Cliente: Optional[str] = None
    Transportadora: Optional[str] = None
    UFDestino: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$') # Valida formato UF (2 letras maiúsculas)
    CidadeDestino: Optional[str] = None
    Operacao: Optional[Literal[
        'InBound-IPO', 'InBound-MAO', 'InBound-UDI',
        'OutBound-BAR', 'OutBound-BAR-MAT.PRIMA', 'OutBound-IPO',
        'OutBound-MAO', 'OutBound-RIO', 'OutBound-SPO', 'OutBound-UDI'
    ]] = None
    SituacaoNF: Optional[Literal['ENTREGUE', 'RETIDA', 'TRÂNSITO']] = None
    StatusAnaliseData: Optional[Literal[
        'ATRASO', 'DIA SEGUINTE', 'DO DIA', 'ENTREGUE', 'FUTURO', 'PREVISTO PARA 2 DIAS'
    ]] = None
    CNPJRaizTransp: Optional[str] = Field(None, pattern=r'^\d{8}$') # Valida 8 dígitos numéricos
    SortColumn: Optional[Literal['data_entrega', 'valor_nf', 'data_emissao']] = None
    SortDirection: Optional[Literal['ASC', 'DESC']] = None

    @model_validator(mode='after')
    def check_sort_direction_requires_column(self) -> 'ParsedFilters':
        """Valida que SortDirection só pode ser definido se SortColumn também estiver definido."""
        if self.SortDirection is not None and self.SortColumn is None:
            # Pydantic espera que validadores retornem 'self' ou levantem ValueError
            # Vamos levantar o erro para sinalizar falha na validação
            raise ValueError('SortDirection cannot be set if SortColumn is null')
        return self
