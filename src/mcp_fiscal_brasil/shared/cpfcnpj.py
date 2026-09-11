"""Transporte do provedor premium opcional cpfcnpj.com.br.

Este modulo concentra a comunicacao HTTP com a API da cpfcnpj.com.br, usada de
forma opcional pelos clientes de CNPJ e de NF-e/NFC-e. O provedor so entra em
acao quando um token e configurado via ``CPFCNPJ_TOKEN``; sem token, os clientes
seguem usando exclusivamente as fontes gratuitas padrao.

Formato da chamada: ``GET {base}/{token}/{pacote}/{documento}``. A resposta traz
``status`` igual a 1 em caso de sucesso e igual a 0 em caso de erro, acompanhada
dos campos ``erro`` e ``erroCodigo``.
"""

from __future__ import annotations

from typing import Any

from aiolimiter import AsyncLimiter

from mcp_fiscal_brasil._core import (
    FiscalHTTPError,
    HTTPClient,
    get_logger,
    settings,
)

logger = get_logger(__name__)

# Pacotes de consulta na cpfcnpj.com.br.
PACOTE_NFE = 100
PACOTE_NFCE = 102
# Pacote padrao de CPF: 26 (CPF D Simplificado), o mais barato que traz situacao
# cadastral. O pacote efetivo vem de settings.cpfcnpj_cpf_packet.
PACOTE_CPF = 26

# Teto de requisicoes por segundo da cpfcnpj.com.br. Cada consulta abre um
# HTTPClient novo, entao o limitador precisa ser compartilhado por todas as
# instancias/chamadas: sem isso, consultas concorrentes somariam limitadores
# independentes e poderiam ultrapassar o teto, recebendo o erro 1007 (HTTP 429).
# A maioria dos pacotes (CPF/CNPJ/IE) segue 20 req/s. Os pacotes de NF-e/NFC-e
# por chave (100/102) tem teto proprio de 2 req/s por conta na documentacao do
# provedor; ultrapassar devolve HTTP 429 + erroCodigo 1007 (sem cobrar credito).
CPFCNPJ_MAX_REQUISICOES_POR_SEGUNDO = 20
CPFCNPJ_NFE_MAX_REQUISICOES_POR_SEGUNDO = 2

# Pacotes com teto reduzido de requisicoes por segundo.
PACOTES_LIMITE_REDUZIDO = frozenset({PACOTE_NFE, PACOTE_NFCE})

_limiter_padrao: AsyncLimiter | None = None
_limiter_nfe: AsyncLimiter | None = None


def _rate_limit_para(pacote: int) -> int:
    """Teto de req/s do pacote: 2 para NF-e/NFC-e (100/102), 20 para os demais."""
    if pacote in PACOTES_LIMITE_REDUZIDO:
        return CPFCNPJ_NFE_MAX_REQUISICOES_POR_SEGUNDO
    return CPFCNPJ_MAX_REQUISICOES_POR_SEGUNDO


def _get_limiter(pacote: int) -> AsyncLimiter:
    """Retorna o limitador (singleton de modulo) do pacote.

    Os pacotes 100/102 compartilham um limitador de 2 req/s entre si; todos os
    demais compartilham o limitador de 20 req/s. Cada limitador e criado uma vez.
    """
    global _limiter_padrao, _limiter_nfe
    if pacote in PACOTES_LIMITE_REDUZIDO:
        if _limiter_nfe is None:
            _limiter_nfe = AsyncLimiter(
                CPFCNPJ_NFE_MAX_REQUISICOES_POR_SEGUNDO,
                CPFCNPJ_NFE_MAX_REQUISICOES_POR_SEGUNDO,
            )
        return _limiter_nfe
    if _limiter_padrao is None:
        _limiter_padrao = AsyncLimiter(
            CPFCNPJ_MAX_REQUISICOES_POR_SEGUNDO,
            CPFCNPJ_MAX_REQUISICOES_POR_SEGUNDO,
        )
    return _limiter_padrao


def provedor_configurado() -> bool:
    """Indica se o provedor premium cpfcnpj.com.br esta habilitado (token definido)."""
    return bool(settings.cpfcnpj_token.strip())


def _http_client(pacote: int) -> HTTPClient:
    return HTTPClient(
        settings.cpfcnpj_base_url,
        timeout=settings.cpfcnpj_timeout,
        max_retries=settings.mcp_fiscal_max_retries,
        cache_ttl=settings.mcp_fiscal_cache_ttl,
        rate_limit_per_second=_rate_limit_para(pacote),
        limiter=_get_limiter(pacote),
        # O token viaja no primeiro segmento do path: mascarar nos erros. Passar
        # o token como segredo literal cobre tambem bases com prefixo de path
        # (ex.: CPFCNPJ_BASE_URL=https://proxy/cpfcnpj), removendo-o de qualquer
        # url/mensagem/details mesmo fora do formato esperado.
        mask_first_path_segment=True,
        mask_secret=settings.cpfcnpj_token.strip() or None,
    )


async def consultar(pacote: int, documento: str) -> dict[str, Any]:
    """Consulta um documento na cpfcnpj.com.br e retorna o corpo JSON de sucesso.

    Args:
        pacote: Identificador do pacote de consulta (ex.: 6 para CNPJ, 100 para NF-e).
        documento: Documento consultado sem máscara (CNPJ numérico ou alfanumérico,
            CPF ou chave de acesso). O provedor aceita CNPJ alfanumérico no caminho da URL.

    Returns:
        dict com o corpo da resposta quando ``status`` e igual a 1.

    Raises:
        FiscalHTTPError: Quando o provedor nao esta configurado ou retorna erro
            (``status`` diferente de 1).
    """
    token = settings.cpfcnpj_token.strip()
    if not token:
        raise FiscalHTTPError(
            "Provedor cpfcnpj.com.br nao configurado (CPFCNPJ_TOKEN ausente).",
            status_code=0,
            url=settings.cpfcnpj_base_url,
        )

    path = f"/{token}/{pacote}/{documento}"
    async with _http_client(pacote) as client:
        data = await client.get(path)

    if data.get("status") != 1:
        codigo = data.get("erroCodigo")
        mensagem = data.get("erro") or "Consulta cpfcnpj.com.br sem sucesso."
        raise FiscalHTTPError(
            f"cpfcnpj.com.br retornou erro: {mensagem}",
            status_code=int(codigo) if isinstance(codigo, int) else 0,
            url=f"{settings.cpfcnpj_base_url}/***/{pacote}/{documento}",
            detail={"erro": mensagem, "erroCodigo": codigo},
        )

    return data


__all__ = [
    "PACOTE_CPF",
    "PACOTE_NFCE",
    "PACOTE_NFE",
    "consultar",
    "provedor_configurado",
]
