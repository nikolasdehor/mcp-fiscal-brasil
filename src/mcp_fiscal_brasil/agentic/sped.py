"""Sumarizacao executiva de arquivos SPED."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from mcp_fiscal_brasil._core import get_logger

from ..sped.tools import analisar_sped
from .schemas import SPEDSummary

logger = get_logger(__name__)


_TIPO_MAP: dict[str, Literal["fiscal", "contribuicoes", "ecf", "ecd"]] = {
    "EFD-ICMS-IPI": "fiscal",
    "EFD-Contribuicoes": "contribuicoes",
    "ECD": "ecd",
    "ECF": "ecf",
}


async def summarize_sped(file_path: str | Path) -> SPEDSummary:
    """
    Sumarizacao executiva de um arquivo SPED.

    Le o arquivo, identifica tipo (Fiscal, Contribuicoes, ECF, ECD), extrai
    periodo, empresa, total de registros e produz resumo em pt-BR.

    Args:
        file_path: Caminho para arquivo .txt do SPED.

    Returns:
        SPEDSummary com periodo, empresa, metricas e resumo executivo.

    Exemplo:
        sumario = await summarize_sped("/tmp/sped_fiscal_201912.txt")
        print(sumario.resumo)
        for metrica, valor in sumario.metricas_chave.items():
            print(f"{metrica}: {valor}")
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo SPED nao encontrado: {file_path}")

    conteudo = path.read_text(encoding="latin-1")
    analise = await analisar_sped(conteudo, nome_arquivo=path.name)

    tipo_norm = _TIPO_MAP.get(analise.tipo_sped, "fiscal")

    cnpj = None
    razao = None
    periodo_ini = None
    periodo_fim = None
    total_registros = 0
    tipos_registros: dict[str, int] = {}

    if analise.abertura:
        cnpj = analise.abertura.cnpj
        razao = analise.abertura.nome_empresarial

    if analise.resumo:
        periodo_ini = analise.resumo.periodo_inicial
        periodo_fim = analise.resumo.periodo_final
        total_registros = analise.resumo.total_registros
        tipos_registros = analise.resumo.tipos_registros
        if not cnpj:
            cnpj = analise.resumo.cnpj
        if not razao:
            razao = analise.resumo.razao_social

    total_blocos = len({k[0] for k in tipos_registros if k})

    metricas: dict[str, float] = {
        "total_registros": float(total_registros),
        "tipos_distintos": float(len(tipos_registros)),
    }

    inconsistencias = list(analise.erros) + [f"AVISO: {a}" for a in analise.avisos]

    periodo_str = ""
    if periodo_ini and periodo_fim:
        periodo_str = f" entre {periodo_ini.isoformat()} e {periodo_fim.isoformat()}"
    elif periodo_ini:
        periodo_str = f" iniciado em {periodo_ini.isoformat()}"

    empresa_str = f" para {razao}" if razao else ""
    resumo = (
        f"Arquivo SPED {analise.tipo_sped}{empresa_str}{periodo_str}: "
        f"{total_registros} registros validos em {total_blocos} blocos. "
        f"{len(inconsistencias)} inconsistencia(s) identificada(s)."
    )

    return SPEDSummary(
        arquivo=path.name,
        tipo=tipo_norm,
        periodo_inicio=periodo_ini,
        periodo_fim=periodo_fim,
        total_registros=total_registros,
        total_blocos=total_blocos,
        cnpj=cnpj,
        razao_social=razao,
        inconsistencias=inconsistencias,
        metricas_chave=metricas,
        resumo=resumo,
    )
