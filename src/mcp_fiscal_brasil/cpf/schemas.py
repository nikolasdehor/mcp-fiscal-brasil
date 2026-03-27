"""Schemas para validacao de CPF."""

from pydantic import BaseModel


class CPFValidacaoResponse(BaseModel):
    """Resultado da validacao de um CPF."""

    cpf_informado: str
    cpf_formatado: str | None = None
    valido: bool
    motivo: str | None = None
