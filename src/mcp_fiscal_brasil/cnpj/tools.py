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

    Aceita o CNPJ com ou sem formatação (pontos, barra, traço).
    Retorna razão social, endereço, atividades econômicas, sócios e situação cadastral.

    Args:
        cnpj: Número do CNPJ (ex: '11.222.333/0001-81' ou '11222333000181')

    Returns:
        CNPJResponse com os dados completos da empresa.

    Raises:
        ValidationError: Se o CNPJ for inválido.
        NotFoundError: Se o CNPJ não for encontrado na Receita Federal.
        APIError: Em caso de falha nas APIs consultadas.
    """
    if not validate_cnpj(cnpj):
        raise ValidationError(
            field="cnpj",
            value=cnpj,
            reason="CNPJ inválido. Verifique os 14 dígitos e o dígito verificador.",
        )

    cnpj_formatado = format_cnpj(cnpj)
    logger.info("Consultando CNPJ: %s", cnpj_formatado)
    return await _client.consultar(cnpj)


async def listar_cnpjs_por_nome(nome: str, uf: str | None = None) -> list[dict[str, str]]:
    """
    Busca empresas pelo nome ou razão social.

    Retorna uma lista simplificada com CNPJ e razão social.
    Nota: esta funcionalidade depende de APIs de terceiros com disponibilidade variável.

    Args:
        nome: Nome ou parte da razão social da empresa.
        uf: Sigla do estado para filtrar (ex: 'SP', 'MG'). Opcional.

    Returns:
        Lista de dicionários com 'cnpj' e 'razao_social'.
    """
    # Esta implementação é um stub - a busca por nome requer APIs pagas
    # como a da Receita Federal (acesso via certificado digital) ou serviços como CNPJ.ws
    logger.info("Busca por nome '%s' (UF=%s) - funcionalidade limitada", nome, uf)
    return [
        {
            "aviso": (
                "A busca por nome de empresa requer acesso a APIs pagas ou "
                "ao portal da Receita Federal. Use consultar_cnpj com o CNPJ específico."
            )
        }
    ]
