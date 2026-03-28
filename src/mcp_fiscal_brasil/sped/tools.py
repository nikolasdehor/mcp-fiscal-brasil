"""Ferramentas MCP para analise de arquivos SPED."""

import logging
from datetime import date

from .schemas import InfoAberturaSPED, ResumoPeriodoSPED, SPEDAnaliseResponse

logger = logging.getLogger(__name__)

# Identificação do tipo de SPED pelo registro 0000 campo tipo_escrituracao
TIPOS_SPED: dict[str, str] = {
    "0": "EFD-ICMS-IPI",
    "1": "EFD-Contribuicoes",
    "2": "ECD",
    "3": "ECF",
}


def _parse_linha_sped(linha: str) -> list[str]:
    """Analisa uma linha SPED (delimitada por '|') e remove os pipes externos."""
    if linha.startswith("|"):
        linha = linha[1:]
    if linha.endswith("|"):
        linha = linha[:-1]
    return linha.split("|")


def _to_date(valor: str) -> date | None:
    """Converte data SPED (DDMMAAAA) em objeto date."""
    valor = valor.strip()
    if len(valor) == 8 and valor.isdigit():
        try:
            return date(int(valor[4:]), int(valor[2:4]), int(valor[:2]))
        except ValueError:
            return None
    return None


def _parse_abertura(campos: list[str]) -> InfoAberturaSPED:
    """Analisa o registro 0000 (abertura) do arquivo SPED."""

    # Leiaute EFD ICMS/IPI e EFD Contribuições:
    # |REG|COD_VER|TIP_ESCRIT|IND_SIT|NUM_REC_SCP|NOME|CNPJ|CPF|UF|IE|COD_MUN|SUFRAMA|IND_PERFIL|IND_ATIV|
    def get(i: int) -> str | None:
        return campos[i].strip() if i < len(campos) and campos[i].strip() else None

    return InfoAberturaSPED(
        codigo_versao_leiaute=get(1),
        tipo_escrituracao=get(2),
        indicador_situacao=get(3),
        num_rec_scp=get(4),
        nome_empresarial=get(5),
        cnpj=get(6),
        cpf=get(7),
        uf=get(8),
        ie=get(9),
        cod_municipio=get(10),
        suframa=get(11),
        ind_perfil=get(12),
        ind_ativ=get(13),
    )


async def analisar_sped(conteudo: str, nome_arquivo: str | None = None) -> SPEDAnaliseResponse:
    """
    Analisa um arquivo SPED e extrai informações sobre o período, empresa e tipos de registros.

    Suporta EFD-ICMS/IPI, EFD-Contribuições, ECD e ECF.

    Args:
        conteudo: Conteúdo do arquivo SPED como string (formato pipe-delimitado)
        nome_arquivo: Nome do arquivo (opcional, para informação)

    Returns:
        SPEDAnaliseResponse com resumo do arquivo, informações da empresa e contagem de registros.
    """
    logger.info("Analisando arquivo SPED: %s", nome_arquivo or "desconhecido")

    abertura: InfoAberturaSPED | None = None
    tipos_registros: dict[str, int] = {}
    erros: list[str] = []
    avisos: list[str] = []
    periodo_inicial: date | None = None
    periodo_final: date | None = None

    linhas = conteudo.strip().splitlines()
    total = len(linhas)

    for _num_linha, linha in enumerate(linhas, 1):
        linha = linha.strip()
        if not linha:
            continue
        campos = _parse_linha_sped(linha)
        if not campos:
            continue

        registro = campos[0]
        tipos_registros[registro] = tipos_registros.get(registro, 0) + 1

        # Registro de abertura
        if registro == "0000" and abertura is None:
            abertura = _parse_abertura(campos)
            # Período fica no próximo campo após ind_ativ (índice 14 e 15)
            if len(campos) > 15:
                periodo_inicial = _to_date(campos[14])
                periodo_final = _to_date(campos[15])

    tipo_sped = "Desconhecido"
    if abertura and abertura.tipo_escrituracao:
        tipo_sped = TIPOS_SPED.get(abertura.tipo_escrituracao, f"Tipo {abertura.tipo_escrituracao}")

    # Verifica presença de registros obrigatórios
    if "0000" not in tipos_registros:
        erros.append("Registro 0000 (abertura) não encontrado - arquivo possivelmente inválido")
    if "9999" not in tipos_registros:
        avisos.append("Registro 9999 (encerramento) não encontrado - arquivo pode estar incompleto")

    resumo = ResumoPeriodoSPED(
        periodo_inicial=periodo_inicial,
        periodo_final=periodo_final,
        total_registros=total,
        tipos_registros=tipos_registros,
        cnpj=abertura.cnpj if abertura else None,
        razao_social=abertura.nome_empresarial if abertura else None,
        uf=abertura.uf if abertura else None,
    )

    return SPEDAnaliseResponse(
        tipo_sped=tipo_sped,
        abertura=abertura,
        resumo=resumo,
        avisos=avisos,
        erros=erros,
    )


async def listar_registros_sped(conteudo: str, tipo_registro: str) -> list[dict[str, str]]:
    """
    Lista todos os registros de um determinado tipo em um arquivo SPED.

    Args:
        conteudo: Conteúdo do arquivo SPED
        tipo_registro: Código do registro a buscar (ex: 'C100', 'E110', '0140')

    Returns:
        Lista de dicionários com os campos de cada ocorrência do registro.
    """
    tipo_registro = tipo_registro.upper().strip()
    resultado = []

    for linha in conteudo.strip().splitlines():
        linha = linha.strip()
        if not linha:
            continue
        campos = _parse_linha_sped(linha)
        if campos and campos[0] == tipo_registro:
            resultado.append(
                {"registro": tipo_registro, "campos": "|".join(campos[1:]), "raw": linha}
            )

    return resultado
