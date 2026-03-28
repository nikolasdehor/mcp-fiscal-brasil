"""
Exemplo: Integração com sistema contábil/ERP.

Demonstra padrões reais de uso em sistemas de gestão:
- Cadastro automático de fornecedor a partir do CNPJ
- Enriquecimento de base de dados com dados fiscais
- Verificação de regularidade fiscal antes de pagamento
- Classificação automática por regime tributário

Executar:
    python examples/erp_contabil.py
"""

import asyncio
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from mcp_fiscal_brasil import FiscalBrasil


@dataclass
class Fornecedor:
    """Modelo simplificado de fornecedor para o exemplo."""

    cnpj: str
    razao_social: str
    nome_fantasia: str | None = None
    endereco: str | None = None
    cnae_codigo: str | None = None
    cnae_descricao: str | None = None
    regime_tributario: str = "Lucro Real/Presumido"
    mei: bool = False
    situacao_cadastral: str = "ATIVA"
    data_abertura: date | None = None
    socios: list[str] = field(default_factory=list)
    origem_consulta: str = "BrasilAPI"


async def cadastrar_fornecedor(cnpj: str) -> Fornecedor:
    """
    Cadastra um fornecedor automaticamente a partir do CNPJ.

    Fluxo:
    1. Valida o CNPJ (offline)
    2. Consulta dados na Receita Federal via API
    3. Verifica situação no Simples Nacional
    4. Monta e retorna o objeto Fornecedor preenchido
    """
    async with FiscalBrasil() as fiscal:
        # 1. Validar CNPJ antes de qualquer chamada de API
        if not fiscal.validar_cnpj(cnpj):
            raise ValueError(f"CNPJ inválido: {cnpj}")

        print(f"  Consultando dados para CNPJ {cnpj}...")

        # 2. Buscar dados na Receita Federal
        empresa = await fiscal.consultar_cnpj(cnpj)
        print(f"  Empresa encontrada: {empresa.razao_social}")

        # 3. Verificar Simples Nacional e MEI
        try:
            simples = await fiscal.consultar_simples(cnpj)
            optante_simples = simples.optante_simples
            optante_mei = simples.optante_mei
        except Exception as e:
            print(f"  Aviso: não foi possível consultar Simples Nacional: {e}")
            optante_simples = False
            optante_mei = False

        # 4. Determinar regime tributario
        if optante_mei:
            regime = "MEI"
        elif optante_simples:
            regime = "Simples Nacional"
        else:
            regime = "Lucro Real/Presumido"

        # 5. Montar endereço formatado
        endereco_str = None
        if empresa.endereco:
            endereco_str = empresa.endereco.formatado()

        # 6. Extrair sócios do QSA
        socios = [s.nome for s in empresa.qsa[:3]]  # Top 3 sócios

        return Fornecedor(
            cnpj=cnpj,
            razao_social=empresa.razao_social,
            nome_fantasia=empresa.nome_fantasia,
            endereco=endereco_str,
            cnae_codigo=empresa.atividade_principal.codigo if empresa.atividade_principal else None,
            cnae_descricao=(
                empresa.atividade_principal.descricao if empresa.atividade_principal else None
            ),
            regime_tributario=regime,
            mei=optante_mei,
            situacao_cadastral=empresa.situacao_cadastral,
            data_abertura=empresa.data_abertura,
            socios=socios,
            origem_consulta=empresa.origem,
        )


async def verificar_regularidade_antes_pagamento(cnpj: str) -> dict[str, Any]:
    """
    Verifica a regularidade fiscal de um fornecedor antes de autorizar pagamento.

    Retorna um dicionário com:
    - apto_pagamento (bool): Se passou em todas as verificações.
    - situacao_receita (str): Status na Receita Federal.
    - simples_regular (bool): Se a situação no Simples está regular.
    - alertas (list[str]): Lista de alertas que requerem atenção.
    """
    alertas = []
    apto = True

    async with FiscalBrasil() as fiscal:
        if not fiscal.validar_cnpj(cnpj):
            return {
                "apto_pagamento": False,
                "alertas": ["CNPJ inválido"],
                "situacao_receita": "N/A",
                "simples_regular": False,
            }

        # Consultar situacao cadastral
        empresa = await fiscal.consultar_cnpj(cnpj)
        situacao = empresa.situacao_cadastral.upper()

        if "ATIVA" not in situacao:
            apto = False
            alertas.append(f"Empresa com situacao cadastral: {empresa.situacao_cadastral}")

        # Consultar Simples Nacional
        simples_regular = True
        try:
            simples = await fiscal.consultar_simples(cnpj)
            if simples.optante_simples and simples.data_exclusao_simples:
                alertas.append(f"Empresa excluida do Simples em {simples.data_exclusao_simples}")
                simples_regular = False
        except Exception:
            alertas.append("Não foi possível verificar situação no Simples Nacional")
            simples_regular = False

        return {
            "apto_pagamento": apto,
            "situacao_receita": empresa.situacao_cadastral,
            "simples_regular": simples_regular,
            "alertas": alertas,
            "razao_social": empresa.razao_social,
        }


async def enriquecer_base_fornecedores(
    cnpjs: list[str],
) -> list[dict[str, Any]]:
    """
    Enriquece uma lista de CNPJs com dados fiscais completos.

    Ideal para rodar em batch noturno para manter cadastro atualizado.

    Args:
        cnpjs: Lista de CNPJs a consultar.

    Returns:
        Lista de dicionários com dados enriquecidos ou erro por CNPJ.
    """
    resultados = []
    erros = 0

    async with FiscalBrasil() as fiscal:
        for cnpj in cnpjs:
            if not fiscal.validar_cnpj(cnpj):
                resultados.append({"cnpj": cnpj, "status": "invalido", "erro": "CNPJ inválido"})
                erros += 1
                continue

            try:
                empresa = await fiscal.consultar_cnpj(cnpj)
                simples = await fiscal.consultar_simples(cnpj)

                resultados.append(
                    {
                        "cnpj": cnpj,
                        "status": "ok",
                        "razao_social": empresa.razao_social,
                        "situacao": empresa.situacao_cadastral,
                        "uf": empresa.endereco.uf if empresa.endereco else None,
                        "cnae": empresa.atividade_principal.codigo
                        if empresa.atividade_principal
                        else None,
                        "simples": simples.optante_simples,
                        "mei": simples.optante_mei,
                        "origem": empresa.origem,
                    }
                )
            except Exception as e:
                resultados.append({"cnpj": cnpj, "status": "erro", "erro": str(e)})
                erros += 1

    print(f"\n  Processados: {len(cnpjs)} CNPJs | Erros: {erros}")
    return resultados


async def main() -> None:
    print("=== Cadastro automático de fornecedor ===")
    try:
        fornecedor = await cadastrar_fornecedor("33.000.167/0001-01")
        print(f"  CNPJ: {fornecedor.cnpj}")
        print(f"  Razão Social: {fornecedor.razao_social}")
        print(f"  Nome Fantasia: {fornecedor.nome_fantasia or '-'}")
        print(f"  Regime: {fornecedor.regime_tributario}")
        print(f"  Situação: {fornecedor.situacao_cadastral}")
        print(f"  Abertura: {fornecedor.data_abertura or '-'}")
        print(f"  Endereço: {fornecedor.endereco or '-'}")
        if fornecedor.cnae_codigo:
            print(f"  CNAE: {fornecedor.cnae_codigo} - {fornecedor.cnae_descricao}")
        if fornecedor.socios:
            print(f"  Sócios: {', '.join(fornecedor.socios)}")
        print(f"  Fonte: {fornecedor.origem_consulta}")
    except Exception as e:
        print(f"  Erro: {e}")

    print("\n=== Verificação antes de pagamento ===")
    try:
        resultado = await verificar_regularidade_antes_pagamento("33.000.167/0001-01")
        print(f"  Empresa: {resultado.get('razao_social', '-')}")
        print(f"  Apto para pagamento: {'SIM' if resultado['apto_pagamento'] else 'NAO'}")
        print(f"  Situação RF: {resultado['situacao_receita']}")
        if resultado["alertas"]:
            print("  Alertas:")
            for alerta in resultado["alertas"]:
                print(f"    - {alerta}")
    except Exception as e:
        print(f"  Erro: {e}")

    print("\n=== Enriquecimento de base (lote) ===")
    cnpjs = [
        "33000167000101",  # Petrobras
        "60746948000112",  # Banco do Brasil
        "11111111111111",  # inválido
    ]
    resultados = await enriquecer_base_fornecedores(cnpjs)
    for r in resultados:
        if r["status"] == "ok":
            print(f"  {r['cnpj']}: {r['razao_social']} [{r['situacao']}]")
        else:
            print(f"  {r['cnpj']}: {r['status'].upper()} - {r.get('erro', '-')}")


if __name__ == "__main__":
    asyncio.run(main())
