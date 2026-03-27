"""Testes para o modulo CPF."""

from mcp_fiscal_brasil.cpf.tools import validar_cpf_tool


class TestValidarCPFTool:
    async def test_cpf_valido(self, cpf_valido: str) -> None:
        resultado = await validar_cpf_tool(cpf_valido)
        assert resultado.valido is True
        assert resultado.cpf_formatado == cpf_valido
        assert resultado.motivo is None

    async def test_cpf_invalido_digitos_repetidos(self) -> None:
        resultado = await validar_cpf_tool("111.111.111-11")
        assert resultado.valido is False
        assert resultado.motivo is not None

    async def test_cpf_invalido_dv_errado(self) -> None:
        resultado = await validar_cpf_tool("529.982.247-26")
        assert resultado.valido is False
        assert "verificador" in resultado.motivo.lower() or "invalido" in resultado.motivo.lower()

    async def test_cpf_invalido_tamanho_errado(self) -> None:
        resultado = await validar_cpf_tool("123")
        assert resultado.valido is False
        assert resultado.motivo is not None

    async def test_cpf_sem_mascara_valido(self) -> None:
        resultado = await validar_cpf_tool("52998224725")
        assert resultado.valido is True
        assert resultado.cpf_formatado == "529.982.247-25"
