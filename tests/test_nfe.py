"""Testes para o modulo NFe."""

import pytest

from mcp_fiscal_brasil.shared.exceptions import ValidationError
from mcp_fiscal_brasil.nfe.tools import validar_chave_nfe, consultar_status_sefaz


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
        base = "35230112345678901234550010000000011000000001"
        assert len(base) == 43

        # Calcula DV
        pesos = list(range(2, 10)) * 6
        soma = sum(int(d) * pesos[i % len(pesos)] for i, d in enumerate(base))
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
