"""Cliente para consulta de CNPJ via BrasilAPI e ReceitaWS."""

from datetime import date
from typing import Any

from mcp_fiscal_brasil._core import HTTPClient, Settings, get_logger

from ..shared.schemas import Endereco
from .schemas import AtividadeCNAE, CNPJResponse, QSASocio

logger = get_logger(__name__)
_settings = Settings()


class CNPJClient:
    """Cliente para busca de dados de CNPJ em fontes publicas."""

    def _http_client(self, base_url: str) -> HTTPClient:
        return HTTPClient(
            base_url,
            timeout=_settings.mcp_fiscal_http_timeout,
            max_retries=_settings.mcp_fiscal_max_retries,
            cache_ttl=_settings.mcp_fiscal_cache_ttl,
            rate_limit_per_second=_settings.mcp_fiscal_rate_limit,
        )

    async def consultar(self, cnpj: str) -> CNPJResponse:
        """
        Consulta os dados de um CNPJ.

        Tenta BrasilAPI primeiro; em caso de falha, tenta ReceitaWS.
        """
        cnpj_limpo = "".join(c for c in cnpj if c.isdigit())
        logger.info("cnpj_lookup_started", cnpj=cnpj_limpo)

        try:
            return await self._consultar_brasil_api(cnpj_limpo)
        except Exception as exc:
            logger.warning(
                "brasilapi_cnpj_lookup_failed",
                cnpj=cnpj_limpo,
                error=str(exc),
                fallback="receitaws",
            )
            return await self._consultar_receita_ws(cnpj_limpo)

    async def _consultar_brasil_api(self, cnpj: str) -> CNPJResponse:
        async with self._http_client(_settings.brasilapi_base_url) as client:
            data = await client.get(f"/cnpj/v1/{cnpj}")
        return self._parse_brasil_api(data, cnpj)

    async def _consultar_receita_ws(self, cnpj: str) -> CNPJResponse:
        async with self._http_client(_settings.receita_base_url) as client:
            data = await client.get(f"/cnpj/{cnpj}")
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
        for cnae in data.get("cnaes_secundarios") or []:
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
        for socio in data.get("qsa") or []:
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
        for ativ in data.get("atividade_principal") or []:
            atividade_principal = AtividadeCNAE(
                codigo=ativ.get("code", ""),
                descricao=ativ.get("text", ""),
            )
            break

        atividades_secundarias = [
            AtividadeCNAE(codigo=a.get("code", ""), descricao=a.get("text", ""))
            for a in data.get("atividades_secundarias") or []
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
            for s in data.get("qsa") or []
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
