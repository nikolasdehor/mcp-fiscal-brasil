"""Tests for SPED parsing edge cases."""

from mcp_fiscal_brasil.sped.tools import analisar_sped, listar_registros_sped


async def test_analisar_sped_ignores_blank_lines_in_total_records() -> None:
    content = (
        "|0000|015|0|N||EMPRESA TESTE LTDA|12345678000195||SP|123456789|3550308|||0|01012024|31012024|\n"
        "\n"
        "|9999|2|\n"
    )

    response = await analisar_sped(content)

    assert response.resumo is not None
    assert response.resumo.total_registros == 2
    assert response.resumo.tipos_registros == {"0000": 1, "9999": 1}
    assert response.erros == []


async def test_analisar_sped_empty_content_reports_missing_opening() -> None:
    response = await analisar_sped(" \n ")

    assert response.resumo is not None
    assert response.resumo.total_registros == 0
    assert response.resumo.tipos_registros == {}
    assert "Registro 0000" in response.erros[0]


async def test_listar_registros_sped_strips_requested_record_type() -> None:
    content = (
        "|C100|0|1|55|00|123|31012024|100.00|\n|C100|0|1|55|00|124|31012024|250.00|\n|9999|3|\n"
    )

    records = await listar_registros_sped(content, " c100 ")

    assert [record["registro"] for record in records] == ["C100", "C100"]
    assert records[0]["raw"] == "|C100|0|1|55|00|123|31012024|100.00|"
