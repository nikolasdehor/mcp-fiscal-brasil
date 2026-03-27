"""Schemas para SPED Fiscal, Contabil e Contribuicoes."""

from datetime import date

from pydantic import BaseModel, Field

from ..shared.schemas import BaseResponse


class RegistroSPED(BaseModel):
    """Registro generico de um arquivo SPED."""

    tipo: str  # Ex: "0000", "C100", "E110"
    campos: list[str]
    linha: int | None = None


class InfoAberturaSPED(BaseModel):
    """Registro de abertura do arquivo SPED (registro 0000)."""

    codigo_versao_leiaute: str | None = None
    tipo_escrituracao: str | None = None
    indicador_situacao: str | None = None
    num_rec_scp: str | None = None
    nome_empresarial: str | None = None
    cnpj: str | None = None
    cpf: str | None = None
    uf: str | None = None
    ie: str | None = None
    cod_municipio: str | None = None
    suframa: str | None = None
    ind_perfil: str | None = None
    ind_ativ: str | None = None
    periodo_inicial: date | None = None
    periodo_final: date | None = None


class ResumoPeriodoSPED(BaseModel):
    """Resumo de um periodo do SPED Fiscal."""

    periodo_inicial: date | None = None
    periodo_final: date | None = None
    total_registros: int = 0
    tipos_registros: dict[str, int] = Field(default_factory=dict)
    cnpj: str | None = None
    razao_social: str | None = None
    uf: str | None = None


class SPEDAnaliseResponse(BaseResponse):
    """Resultado da analise de um arquivo SPED."""

    tipo_sped: str  # "EFD-ICMS-IPI", "EFD-Contribuicoes", "ECD", "ECF"
    abertura: InfoAberturaSPED | None = None
    resumo: ResumoPeriodoSPED | None = None
    avisos: list[str] = Field(default_factory=list)
    erros: list[str] = Field(default_factory=list)
