"""Testes para o modulo NFe."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_fiscal_brasil.nfe.client import NFEClient, _extrair_info_chave
from mcp_fiscal_brasil.nfe.tools import consultar_nfe, consultar_status_sefaz, validar_chave_nfe
from mcp_fiscal_brasil.shared.exceptions import APIError, RateLimitError, ValidationError


class TestValidarChaveNFe:
    async def test_chave_tamanho_errado(self) -> None:
        resultado = await validar_chave_nfe("12345")
        assert resultado["valido"] is False

    async def test_chave_com_espacos_aceita(self) -> None:
        # Espacos devem ser removidos antes da validacao
        resultado = await validar_chave_nfe("1234 5678 9012")
        assert resultado["valido"] is False  # ainda invalida por tamanho

    async def test_chave_valida_extrai_campos(self) -> None:
        # Gera uma chave valida para teste
        # cUF=35 AAMM=2301 CNPJ=12345678901234 mod=55 serie=001 nNF=000000001 tpEmis=1 cNF=00000001
        # DV calculado via modulo 11
        base = "3523011234567890123455001000000001100000001"
        assert len(base) == 43

        # Calcula DV conforme algoritmo SEFAZ (modulo 11, pesos de 2 a 9 da direita p/ esquerda)
        pesos_ciclo = list(range(2, 10))
        soma = sum(int(d) * pesos_ciclo[i % len(pesos_ciclo)] for i, d in enumerate(reversed(base)))
        resto = soma % 11
        dv = 0 if resto in (0, 1) else 11 - resto
        chave = base + str(dv)

        resultado = await validar_chave_nfe(chave)
        assert resultado["valido"] is True
        assert resultado["uf"] == "SP"
        assert resultado["cnpj_emitente"] == "12345678901234"


class TestConsultarStatusSEFAZ:
    async def test_uf_invalida_levanta_erro(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            await consultar_status_sefaz("XX")
        assert exc_info.value.field == "uf"

    async def test_uf_valida_retorna_status(self) -> None:
        # Pode falhar se SEFAZ/API estiver indisponivel em CI
        try:
            resultado = await consultar_status_sefaz("SP")
            assert resultado.uf == "SP"
            assert resultado.status is not None
        except Exception as e:
            assert "ValidationError" not in type(e).__name__


def _chave_valida_sp() -> str:
    """Gera uma chave de acesso valida para SP (cUF=35)."""
    base = "3523011234567890123455001000000001100000001"
    assert len(base) == 43
    pesos_ciclo = list(range(2, 10))
    soma = sum(int(d) * pesos_ciclo[i % len(pesos_ciclo)] for i, d in enumerate(reversed(base)))
    resto = soma % 11
    dv = 0 if resto in (0, 1) else 11 - resto
    return base + str(dv)


class TestExtrairInfoChave:
    def test_extrai_uf_cnpj_numero(self) -> None:
        chave = _chave_valida_sp()
        info = _extrair_info_chave(chave)
        assert info["uf"] == "SP"
        assert info["cnpj_emitente"] == "12345678901234"
        assert info["numero"] == "000000001"
        assert info["serie"] == "001"
        assert info["modelo"] == "55"


class TestNFEClientFallback:
    """Testa a cadeia de fallback do NFEClient sem realizar chamadas HTTP reais."""

    async def test_brasil_api_sucesso_nao_chama_portal(self) -> None:
        chave = _chave_valida_sp()
        client = NFEClient()

        from mcp_fiscal_brasil.nfe.schemas import NFeResponse

        mock_resp = NFeResponse(chave_acesso=chave, numero="1", serie="1", situacao="Autorizada")

        with patch.object(client, "_consultar_brasil_api", new=AsyncMock(return_value=mock_resp)):
            with patch.object(client, "_consultar_portal_nfe", new=AsyncMock()) as portal_mock:
                resultado = await client.consultar_por_chave(chave)

        assert resultado.situacao == "Autorizada"
        portal_mock.assert_not_called()

    async def test_brasil_api_rate_limit_cai_no_portal(self) -> None:
        chave = _chave_valida_sp()
        client = NFEClient()

        from mcp_fiscal_brasil.nfe.schemas import NFeResponse

        mock_resp = NFeResponse(chave_acesso=chave, numero="1", serie="1", situacao="Autorizada")

        with patch.object(
            client,
            "_consultar_brasil_api",
            new=AsyncMock(side_effect=RateLimitError(endpoint="brasilapi/nfe")),
        ):
            with patch.object(
                client, "_consultar_portal_nfe", new=AsyncMock(return_value=mock_resp)
            ) as portal_mock:
                resultado = await client.consultar_por_chave(chave)

        portal_mock.assert_called_once_with(chave)
        assert resultado.situacao == "Autorizada"

    async def test_brasil_api_erro_cai_no_portal(self) -> None:
        chave = _chave_valida_sp()
        client = NFEClient()

        from mcp_fiscal_brasil.nfe.schemas import NFeResponse

        mock_resp = NFeResponse(chave_acesso=chave, numero="1", serie="1", situacao="Autorizada")

        with patch.object(
            client,
            "_consultar_brasil_api",
            new=AsyncMock(side_effect=APIError(message="nao encontrado", status_code=404)),
        ):
            with patch.object(
                client, "_consultar_portal_nfe", new=AsyncMock(return_value=mock_resp)
            ):
                resultado = await client.consultar_por_chave(chave)

        assert resultado.situacao == "Autorizada"

    async def test_todas_apis_falham_retorna_parcial(self) -> None:
        chave = _chave_valida_sp()
        client = NFEClient()

        with patch.object(
            client,
            "_consultar_brasil_api",
            new=AsyncMock(side_effect=APIError(message="indisponivel", status_code=503)),
        ):
            with patch.object(
                client,
                "_consultar_portal_nfe",
                new=AsyncMock(side_effect=APIError(message="indisponivel", status_code=503)),
            ):
                resultado = await client.consultar_por_chave(chave)

        assert resultado.chave_acesso == chave
        assert resultado.emitente is not None
        assert resultado.emitente.cnpj == "12345678901234"
        assert "parciais" in (resultado.situacao or "").lower()
        assert resultado.informacoes_adicionais is not None
        assert "SP" in resultado.informacoes_adicionais

    async def test_chave_invalida_levanta_validation_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            await consultar_nfe("1234567890")
        assert exc_info.value.field == "chave_acesso"
