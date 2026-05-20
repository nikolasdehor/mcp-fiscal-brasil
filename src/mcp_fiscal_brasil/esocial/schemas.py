"""Schemas para eSocial."""

from pydantic import BaseModel, Field

from ..shared.schemas import BaseResponse


class EventoESocial(BaseModel):
    """Descricao de um evento eSocial."""

    código: str
    nome: str
    grupo: str
    descrição: str
    obrigatório: bool = True


class ValidacaoESocialResponse(BaseResponse):
    """Resultado da validação de um XML de evento eSocial."""

    evento: str
    versão: str | None = None
    válido: bool
    erros: list[str] = Field(default_factory=list)
    avisos: list[str] = Field(default_factory=list)
