"""Ferramentas MCP para NFe."""

import logging

from ..shared.exceptions import ValidationError
from ..shared.validators import validate_chave_nfe
from .client import NFEClient
from .schemas import NFeResponse, StatusSEFAZResponse

logger = logging.getLogger(__name__)

_client = NFEClient()

# UFs validas para consulta SEFAZ
UFS_VALIDAS = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}


async def consultar_nfe(chave_acesso: str) -> NFeResponse:
    """
    Consulta os dados de uma NFe (Nota Fiscal Eletronica) pela chave de acesso.

    A chave de acesso tem 44 digitos e pode ser encontrada no DANFE (documento impresso da nota).

    Args:
        chave_acesso: Chave de acesso da NFe com 44 digitos (aceita com ou sem espacos)

    Returns:
        NFeResponse com emitente, destinatario, itens e totais da nota.

    Raises:
        ValidationError: Se a chave de acesso for invalida.
        NotFoundError: Se a NFe nao for encontrada.
        APIError: Em caso de falha no servico SEFAZ ou APIs consultadas.
    """
    # Remove espacos e outros separadores
    chave_limpa = "".join(c for c in chave_acesso if c.isdigit())

    if not validate_chave_nfe(chave_limpa):
        raise ValidationError(
            field="chave_acesso",
            value=chave_acesso,
            reason="Chave de acesso NFe invalida. Deve ter 44 digitos com digito verificador correto.",
        )

    return await _client.consultar_por_chave(chave_limpa)


async def validar_chave_nfe(chave_acesso: str) -> dict[str, object]:
    """
    Valida o formato e digito verificador de uma chave de acesso de NFe.

    Nao consulta APIs - apenas verifica o calculo matematico (modulo 11).

    Args:
        chave_acesso: Chave de acesso com 44 digitos

    Returns:
        Dicionario com 'valido', 'chave_formatada', 'uf', 'data_emissao', 'cnpj_emitente', 'numero'
    """
    chave_limpa = "".join(c for c in chave_acesso if c.isdigit())
    valido = validate_chave_nfe(chave_limpa)

    resultado: dict[str, object] = {
        "valido": valido,
        "chave_formatada": " ".join(chave_limpa[i : i + 4] for i in range(0, 44, 4))
        if len(chave_limpa) == 44
        else None,
    }

    if valido and len(chave_limpa) == 44:
        from ..shared.constants import CODIGO_UF

        cod_uf = int(chave_limpa[:2])
        resultado.update(
            {
                "uf": CODIGO_UF.get(cod_uf, f"UF {cod_uf}"),
                "ano_mes_emissao": f"{chave_limpa[4:6]}/{chave_limpa[2:4]}",
                "cnpj_emitente": chave_limpa[6:20],
                "modelo": chave_limpa[20:22],
                "serie": chave_limpa[22:25],
                "numero": chave_limpa[25:34],
            }
        )

    return resultado


async def consultar_status_sefaz(uf: str) -> StatusSEFAZResponse:
    """
    Consulta o status atual do servico SEFAZ de um estado.

    Verifica se o webservice da SEFAZ para emissao de NFe esta operacional.

    Args:
        uf: Sigla do estado (ex: 'SP', 'MG', 'RJ')

    Returns:
        StatusSEFAZResponse com o status atual e descricao.

    Raises:
        ValidationError: Se a UF for invalida.
    """
    uf_upper = uf.upper().strip()
    if uf_upper not in UFS_VALIDAS:
        raise ValidationError(
            field="uf",
            value=uf,
            reason=f"UF invalida. Use uma das siglas: {', '.join(sorted(UFS_VALIDAS))}",
        )

    return await _client.consultar_status_servico(uf_upper)
