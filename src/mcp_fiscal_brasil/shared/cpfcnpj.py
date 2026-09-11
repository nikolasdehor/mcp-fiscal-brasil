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

import asyncio
import weakref
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
# instancias/chamadas do mesmo event loop: sem isso, consultas concorrentes
# somariam limitadores independentes e poderiam ultrapassar o teto, recebendo o
# erro 1007 (HTTP 429). A maioria dos pacotes (CPF/CNPJ/IE) segue 20 req/s. Os
# pacotes de NF-e/NFC-e por chave (100/102) tem teto proprio de 2 req/s por conta
# na documentacao do provedor; ultrapassar devolve HTTP 429 + erroCodigo 1007
# (sem cobrar credito).
CPFCNPJ_MAX_REQUISICOES_POR_SEGUNDO = 20
CPFCNPJ_NFE_MAX_REQUISICOES_POR_SEGUNDO = 2

# Pacotes com teto reduzido de requisicoes por segundo.
PACOTES_LIMITE_REDUZIDO = frozenset({PACOTE_NFE, PACOTE_NFCE})

# Limitadores por (event loop em execucao, grupo de req/s). O aiolimiter amarra o
# AsyncLimiter ao event loop corrente (usa call_later/eventos do loop ao adquirir),
# entao reusar o mesmo objeto entre loops quebra: consultar_cpf_sync/consultar_cnpj_sync
# do SDK chamam asyncio.run, abrindo um loop novo a cada chamada. Guardar um
# limitador por loop, com WeakKeyDictionary, deixa o GC recolher a entrada quando o
# loop e coletado, sem vazar limitadores de loops mortos. Fora de um loop em
# execucao (construcao sincrona, ex.: testes), cai no conjunto de fallback de modulo.
_limiters_por_loop: weakref.WeakKeyDictionary[
    asyncio.AbstractEventLoop, dict[int, AsyncLimiter]
] = weakref.WeakKeyDictionary()
_limiters_sem_loop: dict[int, AsyncLimiter] = {}


def _rate_limit_para(pacote: int) -> int:
    """Teto de req/s do pacote: 2 para NF-e/NFC-e (100/102), 20 para os demais."""
    if pacote in PACOTES_LIMITE_REDUZIDO:
        return CPFCNPJ_NFE_MAX_REQUISICOES_POR_SEGUNDO
    return CPFCNPJ_MAX_REQUISICOES_POR_SEGUNDO


def _get_limiter(pacote: int) -> AsyncLimiter:
    """Retorna o limitador do grupo do pacote para o event loop em execucao.

    Pacotes 100/102 compartilham um limitador de 2 req/s; os demais, um de 20 req/s.
    Cada event loop tem o seu proprio conjunto: o AsyncLimiter nao pode ser reusado
    entre loops (o aiolimiter o amarra ao loop corrente), entao dentro de um mesmo
    loop o mesmo grupo devolve o mesmo objeto, e loops distintos recebem objetos
    distintos. Sem loop em execucao, usa um conjunto de fallback de modulo.
    """
    grupo = _rate_limit_para(pacote)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        por_grupo = _limiters_sem_loop
    else:
        por_grupo = _limiters_por_loop.setdefault(loop, {})

    limiter = por_grupo.get(grupo)
    if limiter is None:
        limiter = AsyncLimiter(grupo, grupo)
        por_grupo[grupo] = limiter
    return limiter


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
            # Mascara o token (1o segmento) e tambem o documento (ultimo segmento):
            # a url viaja para access log/trace/proxy e nao pode expor o CPF/CNPJ/chave
            # consultado. A url real da requisicao (path acima) nao e alterada.
            url=f"{settings.cpfcnpj_base_url}/***/{pacote}/***",
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
