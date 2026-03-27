"""Schemas para certidoes negativas de debito."""

from datetime import date, datetime

from pydantic import BaseModel

from ..shared.schemas import BaseResponse


class CertidaoResponse(BaseResponse):
    """Dados de uma certidao negativa ou positiva de debitos."""

    tipo: str  # "CND", "CPEND", "CPEN"
    orgao: str  # "Receita Federal", "FGTS", "Trabalhista"
    cnpj_cpf: str
    situacao: str  # "Negativa", "Positiva", "Positiva com Efeito de Negativa"
    numero_certidao: str | None = None
    data_emissao: datetime | None = None
    data_validade: date | None = None
    codigo_controle: str | None = None
    url_verificacao: str | None = None
    observacoes: str | None = None
