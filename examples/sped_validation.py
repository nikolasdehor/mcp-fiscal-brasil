"""Demonstra validacao basica de SPED Fiscal usando conteudo mockado."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mcp_fiscal_brasil.sped.tools import analisar_sped, listar_registros_sped  # noqa: E402, I001


MOCK_SPED = """
|0000|015|0|N||EMPRESA TESTE LTDA|12345678000195||SP|123456789|3550308|||0|01012024|31012024|
|0001|0|
|C100|0|1|55|00|123|31012024|100.00|
|C100|0|1|55|00|124|31012024|250.00|
|9999|5|
"""


async def main() -> None:
    analysis = await analisar_sped(MOCK_SPED, "sped_mock.txt")
    c100_records = await listar_registros_sped(MOCK_SPED, "C100")

    print("=== Validacao SPED Fiscal mock ===")
    print(f"Tipo: {analysis.tipo_sped}")
    if analysis.resumo:
        print(f"Empresa: {analysis.resumo.razao_social}")
        print(f"CNPJ: {analysis.resumo.cnpj}")
        print(f"UF: {analysis.resumo.uf}")
        print(f"Total de registros: {analysis.resumo.total_registros}")
        print(f"Registros C100: {len(c100_records)}")

    if analysis.erros:
        print("Erros:")
        for error in analysis.erros:
            print(f"  - {error}")
    else:
        print("Erros: nenhum")

    if analysis.avisos:
        print("Avisos:")
        for warning in analysis.avisos:
            print(f"  - {warning}")
    else:
        print("Avisos: nenhum")


if __name__ == "__main__":
    asyncio.run(main())
