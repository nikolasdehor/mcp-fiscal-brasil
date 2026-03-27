"""Cliente para consulta de NFe via SEFAZ e APIs de terceiros."""

import logging
from typing import Any

from ..shared.constants import CODIGO_UF
from ..shared.exceptions import APIError, RateLimitError
from ..shared.http_client import FiscalHTTPClient
from ..shared.rate_limiter import brasil_api_limiter
from .schemas import NFeResponse, StatusSEFAZResponse
from .xml_parser import parse_nfe_xml

logger = logging.getLogger(__name__)

# URL da API de consulta publica do SEFAZ (ambiente nacional)
SEFAZ_CONSULTA_URL = "https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx"

# Portal Nacional da NFe - endpoint de consulta publica (nao requer autenticacao)
PORTAL_NFE_BASE = "https://www.nfe.fazenda.gov.br/portal"

# BrasilAPI oferece consulta de NFe por chave
BRASIL_API_BASE = "https://brasilapi.com.br/api"


def _extrair_info_chave(chave: str) -> dict[str, str]:
    """Extrai campos estruturais da chave de acesso de 44 digitos."""
    cod_uf = int(chave[:2])
    return {
        "uf": CODIGO_UF.get(cod_uf, f"UF {cod_uf}"),
        "ano_mes": f"{chave[4:6]}/{chave[2:4]}",
        "cnpj_emitente": chave[6:20],
        "modelo": chave[20:22],
        "serie": chave[22:25],
        "numero": chave[25:34],
    }


class NFEClient:
    """Cliente para consulta de NFe."""

    async def consultar_por_chave(self, chave: str) -> NFeResponse:
        """
        Consulta os dados de uma NFe pela chave de acesso de 44 digitos.

        Cadeia de fallback:
          1. BrasilAPI (cobertura parcial por estado)
          2. Portal Nacional NFe (consulta publica, sem autenticacao)
          3. Informacoes parciais extraidas da propria chave
        """
        logger.info("Consultando NFe chave: %s", chave)

        # Tentativa 1: BrasilAPI
        try:
            resultado = await self._consultar_brasil_api(chave)
            logger.info("NFe %s consultada via BrasilAPI com sucesso", chave[:10])
            return resultado
        except RateLimitError as e:
            logger.warning(
                "BrasilAPI retornou rate limit (429) para NFe %s: %s. Tentando Portal NFe.",
                chave[:10],
                e,
            )
        except APIError as e:
            logger.warning(
                "BrasilAPI falhou para NFe %s (status=%s): %s. Tentando Portal NFe.",
                chave[:10],
                e.status_code,
                e,
            )
        except Exception as e:
            logger.warning(
                "BrasilAPI erro inesperado para NFe %s: %s. Tentando Portal NFe.",
                chave[:10],
                e,
            )

        # Tentativa 2: Portal Nacional NFe
        try:
            resultado = await self._consultar_portal_nfe(chave)
            logger.info("NFe %s consultada via Portal NFe com sucesso", chave[:10])
            return resultado
        except Exception as e:
            logger.warning(
                "Portal NFe falhou para NFe %s: %s. Retornando dados parciais da chave.",
                chave[:10],
                e,
            )

        # Fallback final: dados extraidos da propria chave
        logger.info(
            "Todas as APIs falharam para NFe %s. Retornando dados parciais extraidos da chave.",
            chave[:10],
        )
        return self._resposta_parcial_da_chave(chave)

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

    async def _consultar_portal_nfe(self, chave: str) -> NFeResponse:
        """
        Consulta NFe via Portal Nacional da NFe (SEFAZ federal).

        O portal oferece consulta publica por chave sem necessidade de certificado digital.
        Retorna XML da NFe quando disponivel.
        """
        async with FiscalHTTPClient(PORTAL_NFE_BASE) as client:
            # Endpoint de consulta resumida publica do Portal NFe
            data = await client.get(
                "/consultaRecaptcha.aspx",
                params={
                    "tipoConsulta": "completa",
                    "tipoConteudo": "XML",
                    "nfe": chave,
                },
                rate_limit_key="portal-nfe/consulta",
            )

        if isinstance(data, str) and data.strip():
            return parse_nfe_xml(data, chave)

        raise APIError(
            message="Portal NFe retornou resposta vazia ou em formato nao suportado",
            endpoint=PORTAL_NFE_BASE,
        )

    def _resposta_parcial_da_chave(self, chave: str) -> NFeResponse:
        """
        Constroi uma NFeResponse com os dados extraidos da propria chave de acesso.

        Util quando nenhuma API consegue fornecer os dados completos. Fornece ao
        chamador ao menos UF, CNPJ do emitente, numero e serie da nota.
        """
        info = _extrair_info_chave(chave)
        from .schemas import EnderecoNFe

        emitente = EnderecoNFe(cnpj=info["cnpj_emitente"])
        return NFeResponse(
            chave_acesso=chave,
            numero=info["numero"].lstrip("0") or info["numero"],
            serie=info["serie"].lstrip("0") or info["serie"],
            modelo=info["modelo"],
            emitente=emitente,
            situacao="Dados parciais - consulta indisponivel nas APIs externas",
            informacoes_adicionais=(
                f"UF de emissao: {info['uf']}. "
                f"Emissao: {info['ano_mes']}. "
                "Dados completos indisponiveis: BrasilAPI sem cobertura para este estado "
                "e Portal NFe inacessivel no momento."
            ),
        )

    async def consultar_status_servico(
        self, uf: str, ambiente: str = "producao"
    ) -> StatusSEFAZResponse:
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
