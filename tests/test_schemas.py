"""Testes para schemas base."""

from datetime import datetime

from mcp_fiscal_brasil.shared.schemas import (
    BaseResponse,
    Endereco,
    ErrorResponse,
    PaginatedResponse,
)


class TestBaseResponse:
    def test_sucesso_padrao(self) -> None:
        resp = BaseResponse()
        assert resp.sucesso is True
        assert isinstance(resp.consultado_em, datetime)

    def test_serializa_json(self) -> None:
        resp = BaseResponse()
        dados = resp.model_dump(mode="json")
        assert dados["sucesso"] is True
        assert "consultado_em" in dados


class TestErrorResponse:
    def test_criacao(self) -> None:
        err = ErrorResponse(codigo_erro="TEST_ERR", mensagem="Teste de erro")
        assert err.sucesso is False
        assert err.codigo_erro == "TEST_ERR"
        assert err.mensagem == "Teste de erro"
        assert err.detalhes == {}


class TestEndereco:
    def test_formatado_completo(self) -> None:
        end = Endereco(
            logradouro="Rua das Flores",
            numero="100",
            bairro="Centro",
            municipio="Sao Paulo",
            uf="SP",
            cep="01310-100",
        )
        formatado = end.formatado()
        assert "Rua das Flores" in formatado
        assert "Sao Paulo/SP" in formatado
        assert "01310-100" in formatado

    def test_formatado_parcial(self) -> None:
        end = Endereco(municipio="Belo Horizonte", uf="MG")
        formatado = end.formatado()
        assert "Belo Horizonte/MG" in formatado


class TestPaginatedResponse:
    def test_total_paginas(self) -> None:
        resp = PaginatedResponse(itens=[], total=100, por_pagina=20)
        assert resp.total_paginas == 5

    def test_total_paginas_com_resto(self) -> None:
        resp = PaginatedResponse(itens=[], total=101, por_pagina=20)
        assert resp.total_paginas == 6

    def test_total_paginas_zero(self) -> None:
        resp = PaginatedResponse(itens=[], total=0, por_pagina=20)
        assert resp.total_paginas == 0
