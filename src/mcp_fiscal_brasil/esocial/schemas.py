"""Schemas para eSocial."""

from pydantic import BaseModel, Field

from ..shared.schemas import BaseResponse


class EventoESocial(BaseModel):
    """Descricao de um evento eSocial."""

    codigo: str
    nome: str
    grupo: str
    descricao: str
    obrigatorio: bool = True


class ValidacaoESocialResponse(BaseResponse):
    """Resultado da validacao de um XML de evento eSocial."""

    evento: str
    versao: str | None = None
    valido: bool
    erros: list[str] = Field(default_factory=list)
    avisos: list[str] = Field(default_factory=list)
