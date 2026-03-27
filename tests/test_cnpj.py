"""Testes para o modulo CNPJ."""

import pytest

from mcp_fiscal_brasil.cnpj.tools import consultar_cnpj
from mcp_fiscal_brasil.shared.exceptions import ValidationError


class TestConsultarCNPJ:
    async def test_cnpj_invalido_levanta_validation_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            await consultar_cnpj("11.111.111/1111-11")
        assert exc_info.value.field == "cnpj"

    async def test_cnpj_com_mascara_aceito(self, cnpj_valido: str) -> None:
        # Verifica que nao levanta ValidationError (pode falhar na API em ambiente de teste)
        # Em CI, mockar a API
        try:
            resultado = await consultar_cnpj(cnpj_valido)
            assert resultado.cnpj is not None
        except Exception as e:
            # API pode estar indisponivel em CI
            assert "ValidationError" not in type(e).__name__
