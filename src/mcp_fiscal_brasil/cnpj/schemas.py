"""Schemas Pydantic para dados de CNPJ."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from ..shared.schemas import BaseResponse, Endereco


class QSASocio(BaseModel):
    """Socio do Quadro Societario e Administrativo (QSA)."""

    nome: str
    qualificacao: str
    cpf_cnpj_socio: str | None = None
    pais_origem: str | None = None
    nome_representante_legal: str | None = None
    qualificacao_representante_legal: str | None = None
    faixa_etaria: str | None = None


class AtividadeCNAE(BaseModel):
    """Atividade economica conforme CNAE."""

    codigo: str
    descricao: str


class CNPJResponse(BaseResponse):
    """Resposta completa de consulta de CNPJ."""

    cnpj: str
    razao_social: str
    nome_fantasia: str | None = None
    situacao_cadastral: str
    data_situacao_cadastral: date | None = None
    motivo_situacao_cadastral: str | None = None
    natureza_juridica: str
    porte: str | None = None
    capital_social: float | None = None
    data_abertura: date | None = None
    atividade_principal: AtividadeCNAE | None = None
    atividades_secundarias: list[AtividadeCNAE] = Field(default_factory=list)
    endereco: Endereco | None = None
    telefone: str | None = None
    email: str | None = None
    qsa: list[QSASocio] = Field(default_factory=list)
    simples_nacional: bool | None = None
    mei: bool | None = None
    opcao_simples: dict[str, Any] | None = None
    origem: str = "BrasilAPI"
