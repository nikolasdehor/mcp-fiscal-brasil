"""Cliente para consulta de CNPJ via BrasilAPI e ReceitaWS."""

import logging
from datetime import date
from typing import Any

from ..shared.http_client import FiscalHTTPClient
from ..shared.rate_limiter import brasil_api_limiter, receita_limiter
from .schemas import AtividadeCNAE, CNPJResponse, Endereco, QSASocio

logger = logging.getLogger(__name__)

BRASIL_API_BASE = "https://brasilapi.com.br/api"
RECEITA_WS_BASE = "https://receitaws.com.br/v1"


class CNPJClient:
    """Cliente para busca de dados de CNPJ em fontes publicas."""

    async def consultar(self, cnpj: str) -> CNPJResponse:
        """
        Consulta os dados de um CNPJ.

        Tenta BrasilAPI primeiro; em caso de falha, tenta ReceitaWS.
        """
        cnpj_limpo = "".join(c for c in cnpj if c.isdigit())
        logger.info("Consultando CNPJ %s", cnpj_limpo)

        try:
            return await self._consultar_brasil_api(cnpj_limpo)
        except Exception as e:
            logger.warning("BrasilAPI falhou para CNPJ %s: %s. Tentando ReceitaWS...", cnpj_limpo, e)
            return await self._consultar_receita_ws(cnpj_limpo)

    async def _consultar_brasil_api(self, cnpj: str) -> CNPJResponse:
        async with FiscalHTTPClient(BRASIL_API_BASE, rate_limiter=brasil_api_limiter) as client:
            data: dict[str, Any] = await client.get(  # type: ignore[assignment]
                f"/cnpj/v1/{cnpj}",
                rate_limit_key="brasilapi/cnpj",
            )
        return self._parse_brasil_api(data, cnpj)

    async def _consultar_receita_ws(self, cnpj: str) -> CNPJResponse:
        async with FiscalHTTPClient(RECEITA_WS_BASE, rate_limiter=receita_limiter) as client:
            data: dict[str, Any] = await client.get(  # type: ignore[assignment]
                f"/cnpj/{cnpj}",
                rate_limit_key="receitaws/cnpj",
            )
        return self._parse_receita_ws(data, cnpj)

    def _parse_brasil_api(self, data: dict[str, Any], cnpj: str) -> CNPJResponse:
        """Transforma resposta da BrasilAPI em CNPJResponse."""
        atividade_principal = None
        if data.get("cnae_fiscal") and data.get("cnae_fiscal_descricao"):
            atividade_principal = AtividadeCNAE(
                codigo=str(data["cnae_fiscal"]),
                descricao=data["cnae_fiscal_descricao"],
            )

        atividades_secundarias = []
        for cnae in data.get("cnaes_secundarios", []):
            if cnae.get("codigo") and cnae.get("descricao"):
                atividades_secundarias.append(
                    AtividadeCNAE(codigo=str(cnae["codigo"]), descricao=cnae["descricao"])
                )

        endereco = Endereco(
            logradouro=data.get("logradouro"),
            numero=data.get("numero"),
            complemento=data.get("complemento"),
            bairro=data.get("bairro"),
            municipio=data.get("municipio"),
            uf=data.get("uf"),
            cep=data.get("cep"),
        )

        qsa = []
        for socio in data.get("qsa", []):
            qsa.append(
                QSASocio(
                    nome=socio.get("nome_socio", ""),
                    qualificacao=socio.get("qualificacao_socio", ""),
                    cpf_cnpj_socio=socio.get("cnpj_cpf_do_socio"),
                    faixa_etaria=socio.get("faixa_etaria"),
                )
            )

        data_abertura = None
        if data.get("data_inicio_atividade"):
            try:
                data_abertura = date.fromisoformat(data["data_inicio_atividade"])
            except ValueError:
                pass

        return CNPJResponse(
            cnpj=cnpj,
            razao_social=data.get("razao_social", ""),
            nome_fantasia=data.get("nome_fantasia") or None,
            situacao_cadastral=data.get("descricao_situacao_cadastral", ""),
            natureza_juridica=data.get("natureza_juridica", ""),
            porte=data.get("porte"),
            capital_social=data.get("capital_social"),
            data_abertura=data_abertura,
            atividade_principal=atividade_principal,
            atividades_secundarias=atividades_secundarias,
            endereco=endereco,
            telefone=data.get("ddd_telefone_1"),
            email=data.get("email"),
            qsa=qsa,
            origem="BrasilAPI",
        )

    def _parse_receita_ws(self, data: dict[str, Any], cnpj: str) -> CNPJResponse:
        """Transforma resposta da ReceitaWS em CNPJResponse."""
        atividade_principal = None
        for ativ in data.get("atividade_principal", []):
            atividade_principal = AtividadeCNAE(
                codigo=ativ.get("code", ""),
                descricao=ativ.get("text", ""),
            )
            break

        atividades_secundarias = [
            AtividadeCNAE(codigo=a.get("code", ""), descricao=a.get("text", ""))
            for a in data.get("atividades_secundarias", [])
        ]

        endereco = Endereco(
            logradouro=data.get("logradouro"),
            numero=data.get("numero"),
            complemento=data.get("complemento"),
            bairro=data.get("bairro"),
            municipio=data.get("municipio"),
            uf=data.get("uf"),
            cep=data.get("cep"),
        )

        qsa = [
            QSASocio(
                nome=s.get("nome", ""),
                qualificacao=s.get("qual", ""),
            )
            for s in data.get("qsa", [])
        ]

        return CNPJResponse(
            cnpj=cnpj,
            razao_social=data.get("nome", ""),
            nome_fantasia=data.get("fantasia") or None,
            situacao_cadastral=data.get("situacao", ""),
            natureza_juridica=data.get("natureza_juridica", ""),
            porte=data.get("porte"),
            capital_social=None,
            atividade_principal=atividade_principal,
            atividades_secundarias=atividades_secundarias,
            endereco=endereco,
            telefone=data.get("telefone"),
            email=data.get("email"),
            qsa=qsa,
            origem="ReceitaWS",
        )
