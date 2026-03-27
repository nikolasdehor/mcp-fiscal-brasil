"""Schemas para Simples Nacional."""

from datetime import date

from ..shared.schemas import BaseResponse


class SimplesNacionalResponse(BaseResponse):
    """Situacao de uma empresa no Simples Nacional."""

    cnpj: str
    razao_social: str | None = None
    optante_simples: bool
    data_opcao_simples: date | None = None
    data_exclusao_simples: date | None = None
    optante_mei: bool = False
    data_opcao_mei: date | None = None
    data_exclusao_mei: date | None = None
    periodo_apuracao: str | None = None
