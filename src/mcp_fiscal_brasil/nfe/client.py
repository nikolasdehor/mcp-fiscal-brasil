"""Cliente para consulta de NFe via SEFAZ e APIs de terceiros."""

import logging
from typing import Any

from ..shared.http_client import FiscalHTTPClient
from ..shared.rate_limiter import brasil_api_limiter, sefaz_limiter
from .schemas import NFeResponse, StatusSEFAZResponse
from .xml_parser import parse_nfe_xml

logger = logging.getLogger(__name__)

# URL da API de consulta publica do SEFAZ (ambiente nacional)
SEFAZ_CONSULTA_URL = "https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx"

# BrasilAPI oferece consulta de NFe por chave
BRASIL_API_BASE = "https://brasilapi.com.br/api"


class NFEClient:
    """Cliente para consulta de NFe."""

    async def consultar_por_chave(self, chave: str) -> NFeResponse:
        """
        Consulta os dados de uma NFe pela chave de acesso de 44 digitos.

        Tenta BrasilAPI primeiro (se disponivel), depois SEFAZ diretamente.
        """
        logger.info("Consultando NFe chave: %s", chave)
        # BrasilAPI tem endpoint de NFe em alguns estados
        try:
            return await self._consultar_brasil_api(chave)
        except Exception as e:
            logger.warning("BrasilAPI falhou para NFe %s: %s", chave[:10], e)
            raise

    async def _consultar_brasil_api(self, chave: str) -> NFeResponse:
        """Consulta NFe via BrasilAPI (endpoint nfe/v1)."""
        async with FiscalHTTPClient(BRASIL_API_BASE, rate_limiter=brasil_api_limiter) as client:
            data: dict[str, Any] = await client.get(  # type: ignore[assignment]
                f"/nfe/v1/{chave}",
                rate_limit_key="brasilapi/nfe",
            )

        # BrasilAPI pode retornar JSON ou XML dependendo do estado
        if isinstance(data, str):
            return parse_nfe_xml(data, chave)

        # Se retornar JSON, mapeia para NFeResponse
        return NFeResponse(
            chave_acesso=chave,
            numero=str(data.get("numero", "")),
            serie=str(data.get("serie", "")),
            situacao=data.get("situacao"),
        )

    async def consultar_status_servico(self, uf: str, ambiente: str = "producao") -> StatusSEFAZResponse:
        """
        Consulta o status do servico SEFAZ de uma UF.

        Usa BrasilAPI como proxy para o webservice SEFAZ.
        """
        logger.info("Consultando status SEFAZ %s (ambiente=%s)", uf, ambiente)

        async with FiscalHTTPClient(BRASIL_API_BASE, rate_limiter=brasil_api_limiter) as client:
            try:
                data: dict[str, Any] = await client.get(  # type: ignore[assignment]
                    f"/nfe/v1/status/{uf.upper()}",
                    rate_limit_key="brasilapi/nfe-status",
                )
                return StatusSEFAZResponse(
                    uf=uf.upper(),
                    status=data.get("status", "Desconhecido"),
                    descricao=data.get("descricao", ""),
                    codigo=data.get("cStat"),
                    ambiente=ambiente,
                )
            except Exception:
                # Fallback: retorna status indisponivel se nao conseguir consultar
                return StatusSEFAZResponse(
                    uf=uf.upper(),
                    status="Indisponivel",
                    descricao="Nao foi possivel consultar o status do servico SEFAZ.",
                    ambiente=ambiente,
                )
