"""Ferramentas MCP para Simples Nacional."""

from ..shared.exceptions import ValidationError
from ..shared.validators import validate_cnpj
from .client import SimplesClient
from .schemas import SimplesNacionalResponse

_client = SimplesClient()


async def consultar_simples_nacional(cnpj: str) -> SimplesNacionalResponse:
    """
    Consulta se uma empresa e optante do Simples Nacional ou MEI.

    Args:
        cnpj: CNPJ da empresa (com ou sem formatacao)

    Returns:
        SimplesNacionalResponse com situacao no Simples e MEI, incluindo datas de opcao/exclusao.

    Raises:
        ValidationError: Se o CNPJ for invalido.
        NotFoundError: Se o CNPJ nao for encontrado.
        APIError: Em caso de falha na API.
    """
    if not validate_cnpj(cnpj):
        raise ValidationError(
            field="cnpj",
            value=cnpj,
            reason="CNPJ invalido. Verifique os 14 digitos e o digito verificador.",
        )
    return await _client.consultar(cnpj)
