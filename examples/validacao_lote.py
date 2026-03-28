"""
Exemplo: Validação em lote de CNPJs e CPFs.

Demonstra dois modos de uso:
1. Validação offline instantânea (sem internet) usando as funções avulsas.
2. Consulta em lote via API para obter dados completos.

Executar:
    python examples/validacao_lote.py
"""

import asyncio

from mcp_fiscal_brasil import FiscalBrasil, validate_cnpj, validate_cpf
from mcp_fiscal_brasil.shared.validators import format_cnpj, format_cpf


def validar_cpfs_offline(cpfs: list[str]) -> None:
    """Valida uma lista de CPFs sem nenhuma chamada de API."""
    print("=== Validação CPF (offline) ===")
    for cpf in cpfs:
        valido = validate_cpf(cpf)
        status = "VALIDO" if valido else "INVALIDO"
        try:
            formatado = (
                format_cpf(cpf) if len("".join(c for c in cpf if c.isdigit())) == 11 else cpf
            )
        except ValueError:
            formatado = cpf
        print(f"  {formatado:15s}  [{status}]")


def validar_cnpjs_offline(cnpjs: list[str]) -> None:
    """Valida uma lista de CNPJs sem nenhuma chamada de API."""
    print("\n=== Validação CNPJ (offline) ===")
    for cnpj in cnpjs:
        valido = validate_cnpj(cnpj)
        status = "VALIDO" if valido else "INVALIDO"
        try:
            numeros = "".join(c for c in cnpj if c.isdigit())
            formatado = format_cnpj(cnpj) if len(numeros) == 14 else cnpj
        except ValueError:
            formatado = cnpj
        print(f"  {formatado:20s}  [{status}]")


async def consultar_cnpjs_lote(
    cnpjs: list[str],
    parar_no_erro: bool = False,
) -> None:
    """
    Consulta dados completos de múltiplos CNPJs via API.

    Args:
        cnpjs: Lista de CNPJs (com ou sem máscara).
        parar_no_erro: Se True, interrompe o lote ao encontrar erro.
                       Se False (padrão), registra o erro e continua.
    """
    print("\n=== Consulta em lote via API ===")

    async with FiscalBrasil() as fiscal:
        for cnpj in cnpjs:
            # Validação offline primeiro (evita chamada de API desnecessária)
            if not fiscal.validar_cnpj(cnpj):
                print(f"  {cnpj:20s}  [INVALIDO - pulado]")
                continue

            try:
                empresa = await fiscal.consultar_cnpj(cnpj)
                simples = await fiscal.consultar_simples(cnpj)

                simples_status = "Simples" if simples.optante_simples else "Lucro Real/Presumido"
                if simples.optante_mei:
                    simples_status = "MEI"

                print(
                    f"  {cnpj:20s}  {empresa.razao_social[:40]:40s}"
                    f"  [{empresa.situacao_cadastral}]  [{simples_status}]"
                )
            except Exception as e:
                print(f"  {cnpj:20s}  [ERRO: {e}]")
                if parar_no_erro:
                    raise


async def verificar_sefaz_todas_ufs() -> None:
    """Verifica o status do SEFAZ para uma lista de UFs em paralelo."""
    print("\n=== Status SEFAZ (consultas paralelas) ===")

    ufs = ["SP", "RJ", "MG", "RS", "PR"]

    async with FiscalBrasil() as fiscal:
        tarefas = [fiscal.status_sefaz(uf) for uf in ufs]
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)

    for uf, resultado in zip(ufs, resultados, strict=True):
        if isinstance(resultado, Exception):
            print(f"  {uf}: ERRO - {resultado}")
        else:
            print(f"  {uf}: {resultado.status} - {resultado.descricao}")


async def main() -> None:
    # --- Validação offline (sem internet) ---
    cpfs = [
        "529.982.247-25",  # válido
        "111.111.111-11",  # inválido (sequência repetida)
        "000.000.000-00",  # inválido
        "12345678909",  # válido
        "98765432100",  # inválido
    ]
    validar_cpfs_offline(cpfs)

    cnpjs = [
        "33.000.167/0001-01",  # Petrobras - válido
        "60.746.948/0001-12",  # Banco do Brasil - válido
        "00.000.000/0000-00",  # inválido
        "11.111.111/1111-11",  # inválido (sequência repetida)
        "abc",  # inválido (não numérico)
    ]
    validar_cnpjs_offline(cnpjs)

    # --- Consulta em lote (requer internet) ---
    cnpjs_lote = [
        "33000167000101",  # Petrobras
        "60746948000112",  # Banco do Brasil
        "00000000000191",  # inválido propositalmente
    ]
    await consultar_cnpjs_lote(cnpjs_lote)

    # --- Status SEFAZ em paralelo ---
    await verificar_sefaz_todas_ufs()


if __name__ == "__main__":
    asyncio.run(main())
