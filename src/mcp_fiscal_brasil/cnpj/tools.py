"""Ferramentas MCP para consulta de CNPJ."""

import logging

from ..shared.exceptions import ValidationError
from ..shared.validators import format_cnpj, validate_cnpj
from .client import CNPJClient
from .schemas import CNPJResponse

logger = logging.getLogger(__name__)

_client = CNPJClient()


async def consultar_cnpj(cnpj: str) -> CNPJResponse:
    """
    Consulta os dados cadastrais de uma empresa pelo CNPJ.

    Aceita o CNPJ com ou sem formatacao (pontos, barra, traco).
    Retorna razao social, endereco, atividades economicas, socios e situacao cadastral.

    Args:
        cnpj: Numero do CNPJ (ex: '11.222.333/0001-81' ou '11222333000181')

    Returns:
        CNPJResponse com os dados completos da empresa.

    Raises:
        ValidationError: Se o CNPJ for invalido.
        NotFoundError: Se o CNPJ nao for encontrado na Receita Federal.
        APIError: Em caso de falha nas APIs consultadas.
    """
    if not validate_cnpj(cnpj):
        raise ValidationError(
            field="cnpj",
            value=cnpj,
            reason="CNPJ invalido. Verifique os 14 digitos e o digito verificador.",
        )

    cnpj_formatado = format_cnpj(cnpj)
    logger.info("Consultando CNPJ: %s", cnpj_formatado)
    return await _client.consultar(cnpj)


async def listar_cnpjs_por_nome(nome: str, uf: str | None = None) -> list[dict[str, str]]:
    """
    Busca empresas pelo nome ou razao social.

    Retorna uma lista simplificada com CNPJ e razao social.
    Nota: esta funcionalidade depende de APIs de terceiros com disponibilidade variavel.

    Args:
        nome: Nome ou parte da razao social da empresa.
        uf: Sigla do estado para filtrar (ex: 'SP', 'MG'). Opcional.

    Returns:
        Lista de dicionarios com 'cnpj' e 'razao_social'.
    """
    # Esta implementacao e um stub - a busca por nome requer APIs pagas
    # como a da Receita Federal (acesso via certificado digital) ou servicos como CNPJ.ws
    logger.info("Busca por nome '%s' (UF=%s) - funcionalidade limitada", nome, uf)
    return [
        {
            "aviso": (
                "A busca por nome de empresa requer acesso a APIs pagas ou "
                "ao portal da Receita Federal. Use consultar_cnpj com o CNPJ especifico."
            )
        }
    ]
