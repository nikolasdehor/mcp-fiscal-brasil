"""Cliente para consulta de optantes do Simples Nacional via BrasilAPI."""

import logging
from datetime import date
from typing import Any

from ..shared.http_client import FiscalHTTPClient
from ..shared.rate_limiter import brasil_api_limiter
from .schemas import SimplesNacionalResponse

logger = logging.getLogger(__name__)
BRASIL_API_BASE = "https://brasilapi.com.br/api"


class SimplesClient:
    """Consulta situacao no Simples Nacional pelo CNPJ."""

    async def consultar(self, cnpj: str) -> SimplesNacionalResponse:
        cnpj_limpo = "".join(c for c in cnpj if c.isdigit())
        logger.info("Consultando Simples Nacional CNPJ %s", cnpj_limpo)

        async with FiscalHTTPClient(BRASIL_API_BASE, rate_limiter=brasil_api_limiter) as client:
            data: dict[str, Any] = await client.get(  # type: ignore[assignment]
                f"/simples/v1/{cnpj_limpo}",
                rate_limit_key="brasilapi/simples",
            )

        return self._parse(data, cnpj_limpo)

    def _parse(self, data: dict[str, Any], cnpj: str) -> SimplesNacionalResponse:
        def to_date(value: str | None) -> date | None:
            if not value:
                return None
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return None

        simples = data.get("simples", {}) or {}
        mei = data.get("mei", {}) or {}

        return SimplesNacionalResponse(
            cnpj=cnpj,
            razao_social=data.get("razao_social"),
            optante_simples=simples.get("optante", False),
            data_opcao_simples=to_date(simples.get("data_opcao")),
            data_exclusao_simples=to_date(simples.get("data_exclusao")),
            optante_mei=mei.get("optante", False),
            data_opcao_mei=to_date(mei.get("data_opcao")),
            data_exclusao_mei=to_date(mei.get("data_exclusao")),
        )
