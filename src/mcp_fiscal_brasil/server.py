"""
Servidor MCP Fiscal Brasil.

Registra todas as ferramentas fiscais e expõe via protocolo MCP (Model Context Protocol).
"""

import logging
from typing import Any

from fastmcp import FastMCP

from . import __version__
from .agentic import (
    analyze_cnpj_compliance,
    compare_tax_regimes,
    risk_score_supplier,
    summarize_sped,
    validate_nfe_full,
)
from .certidoes.tools import consultar_certidao_federal, consultar_certidao_fgts

# Importa todas as ferramentas dos modulos fiscais
from .cnpj.tools import consultar_cnpj, listar_cnpjs_por_nome
from .cpf.tools import validar_cpf_tool
from .esocial.tools import listar_eventos_esocial, validar_evento_esocial
from .nfe.tools import consultar_nfe, consultar_status_sefaz, validar_chave_nfe
from .nfse.tools import consultar_nfse
from .simples.tools import consultar_simples_nacional
from .sped.tools import analisar_sped, listar_registros_sped

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastMCP(
    name="MCP Fiscal Brasil",
    version=__version__,
    instructions=(
        "Servidor MCP para integrar IAs com o sistema fiscal brasileiro. "
        "Consulte CNPJ, NFe, NFSe, SPED, eSocial e certidões via linguagem natural. "
        "Dados obtidos de fontes públicas: BrasilAPI, ReceitaWS, SEFAZ."
    ),
)

# ---------------------------------------------------------------------------
# CNPJ
# ---------------------------------------------------------------------------


@app.tool(
    name="consultar_cnpj",
    description=(
        "Consulta os dados cadastrais completos de uma empresa pelo CNPJ. "
        "Retorna razão social, endereço, atividades econômicas (CNAE), "
        "sócios (QSA), situação cadastral e porte da empresa. "
        "Aceita CNPJ com ou sem formatação (pontos, barra, traço)."
    ),
)
async def tool_consultar_cnpj(cnpj: str) -> dict[str, Any]:
    """Consulta dados de empresa pelo CNPJ."""
    resultado = await consultar_cnpj(cnpj)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="listar_cnpjs_por_nome",
    description=(
        "Busca empresas pelo nome ou razão social. "
        "Nota: esta funcionalidade tem disponibilidade limitada em APIs públicas."
    ),
)
async def tool_listar_cnpjs_por_nome(nome: str, uf: str | None = None) -> list[dict[str, str]]:
    """Busca empresas pelo nome."""
    return await listar_cnpjs_por_nome(nome, uf)


# ---------------------------------------------------------------------------
# CPF
# ---------------------------------------------------------------------------


@app.tool(
    name="validar_cpf",
    description=(
        "Valida o dígito verificador de um CPF brasileiro. "
        "Verificação matemática offline - não consulta APIs externas. "
        "A Receita Federal não disponibiliza API pública para dados de CPF."
    ),
)
async def tool_validar_cpf(cpf: str) -> dict[str, Any]:
    """Valida CPF brasileiro."""
    resultado = await validar_cpf_tool(cpf)
    return resultado.model_dump(mode="json", exclude_none=True)


# ---------------------------------------------------------------------------
# NFe
# ---------------------------------------------------------------------------


@app.tool(
    name="consultar_nfe",
    description=(
        "Consulta os dados de uma Nota Fiscal Eletrônica (NFe) pela chave de acesso de 44 dígitos. "
        "A chave pode ser encontrada no DANFE (documento impresso da nota). "
        "Retorna emitente, destinatário, itens, valores e protocolo de autorização."
    ),
)
async def tool_consultar_nfe(chave_acesso: str) -> dict[str, Any]:
    """Consulta NFe pela chave de acesso."""
    resultado = await consultar_nfe(chave_acesso)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="validar_chave_nfe",
    description=(
        "Valida o formato e o dígito verificador de uma chave de acesso de NFe. "
        "Não consulta APIs - apenas verifica o cálculo matemático (módulo 11). "
        "Também extrai informações da chave: UF, data de emissão, CNPJ emitente e número da nota."
    ),
)
async def tool_validar_chave_nfe(chave_acesso: str) -> dict[str, Any]:
    """Valida chave de acesso de NFe."""
    return await validar_chave_nfe(chave_acesso)


@app.tool(
    name="consultar_status_sefaz",
    description=(
        "Consulta o status atual do serviço SEFAZ de um estado brasileiro. "
        "Verifica se o webservice da SEFAZ para emissão de NFe está operacional. "
        "Útil para diagnosticar falhas de transmissão de notas fiscais."
    ),
)
async def tool_consultar_status_sefaz(uf: str) -> dict[str, Any]:
    """Consulta status SEFAZ de uma UF."""
    resultado = await consultar_status_sefaz(uf)
    return resultado.model_dump(mode="json", exclude_none=True)


# ---------------------------------------------------------------------------
# NFSe
# ---------------------------------------------------------------------------


@app.tool(
    name="consultar_nfse",
    description=(
        "Consulta dados de uma NFSe (Nota Fiscal de Serviço Eletrônica). "
        "ATENÇÃO: NFSe não possui padrão nacional - cada município tem seu próprio sistema. "
        "Esta ferramenta orienta sobre como acessar o portal correto do município."
    ),
)
async def tool_consultar_nfse(
    número: str,
    municipio: str,
    uf: str,
    cnpj_prestador: str | None = None,
) -> dict[str, str]:
    """Consulta NFSe com orientacoes por municipio."""
    return await consultar_nfse(número, municipio, uf, cnpj_prestador)


# ---------------------------------------------------------------------------
# Simples Nacional
# ---------------------------------------------------------------------------


@app.tool(
    name="consultar_simples_nacional",
    description=(
        "Consulta se uma empresa é optante do Simples Nacional ou MEI. "
        "Retorna situação atual, datas de opção e exclusão do regime simplificado."
    ),
)
async def tool_consultar_simples_nacional(cnpj: str) -> dict[str, Any]:
    """Consulta situacao no Simples Nacional."""
    resultado = await consultar_simples_nacional(cnpj)
    return resultado.model_dump(mode="json", exclude_none=True)


# ---------------------------------------------------------------------------
# SPED
# ---------------------------------------------------------------------------


@app.tool(
    name="analisar_sped",
    description=(
        "Analisa um arquivo SPED (EFD-ICMS/IPI, EFD-Contribuições, ECD ou ECF) "
        "e extrai informações sobre período, empresa, tipos de registros e possíveis erros. "
        "Recebe o conteúdo do arquivo como texto (formato pipe-delimitado)."
    ),
)
async def tool_analisar_sped(conteudo: str, nome_arquivo: str | None = None) -> dict[str, Any]:
    """Analisa arquivo SPED."""
    resultado = await analisar_sped(conteudo, nome_arquivo)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="listar_registros_sped",
    description=(
        "Lista todas as ocorrências de um tipo de registro específico em um arquivo SPED. "
        "Exemplo: buscar todos os registros C100 (documentos fiscais) ou E110 (apuração ICMS)."
    ),
)
async def tool_listar_registros_sped(conteudo: str, tipo_registro: str) -> list[dict[str, str]]:
    """Lista registros de um tipo especifico no SPED."""
    return await listar_registros_sped(conteudo, tipo_registro)


# ---------------------------------------------------------------------------
# eSocial
# ---------------------------------------------------------------------------


@app.tool(
    name="listar_eventos_esocial",
    description=(
        "Lista os eventos do eSocial com nome, grupo e descrição. "
        "Pode filtrar por grupo: 'Tabelas', 'Não Periodicos', 'Periodicos' ou 'Exclusao'."
    ),
)
async def tool_listar_eventos_esocial(grupo: str | None = None) -> list[dict[str, Any]]:
    """Lista eventos eSocial."""
    eventos = await listar_eventos_esocial(grupo)
    return [e.model_dump() for e in eventos]


@app.tool(
    name="validar_evento_esocial",
    description=(
        "Realiza validação básica de estrutura de um XML de evento eSocial. "
        "Verifica presença do elemento raiz correto, código do evento e versão do leiaute."
    ),
)
async def tool_validar_evento_esocial(xml_conteudo: str) -> dict[str, Any]:
    """Valida XML de evento eSocial."""
    resultado = await validar_evento_esocial(xml_conteudo)
    return resultado.model_dump(mode="json", exclude_none=True)


# ---------------------------------------------------------------------------
# Certidoes
# ---------------------------------------------------------------------------


@app.tool(
    name="consultar_certidao_federal",
    description=(
        "Orienta sobre como consultar a Certidão Negativa de Débitos (CND) "
        "da Receita Federal e PGFN para CNPJ ou CPF. "
        "Fornece URLs de emissão e verificação e alternativas para automação."
    ),
)
async def tool_consultar_certidao_federal(cnpj_cpf: str) -> dict[str, str]:
    """Orienta consulta de CND na Receita Federal."""
    return await consultar_certidao_federal(cnpj_cpf)


@app.tool(
    name="consultar_certidao_fgts",
    description=(
        "Orienta sobre como consultar a Certidão de Regularidade do FGTS (CRF) "
        "para um CNPJ. Fornece URL do portal da Caixa e alternativas para automação."
    ),
)
async def tool_consultar_certidao_fgts(cnpj: str) -> dict[str, str]:
    """Orienta consulta de CRF do FGTS."""
    return await consultar_certidao_fgts(cnpj)


# ---------------------------------------------------------------------------
# Agentic (tools de alto nivel orientadas a IA)
# ---------------------------------------------------------------------------


@app.tool(
    name="analyze_cnpj_compliance",
    description=(
        "Analise consolidada de compliance fiscal de um CNPJ. "
        "Combina dados cadastrais (Receita), regime tributário (Simples Nacional), "
        "status MEI e CNAE em um relatório unico com score 0-100, risco classificado "
        "(baixo/medio/alto/critico) e achados acionaveis. "
        "Use para decisão de contratar/recusar/investigar uma empresa em uma chamada."
    ),
)
async def tool_analyze_cnpj_compliance(cnpj: str) -> dict[str, Any]:
    """Analise consolidada de compliance fiscal."""
    resultado = await analyze_cnpj_compliance(cnpj)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="compare_tax_regimes",
    description=(
        "Compara regimes tributarios brasileiros (MEI, Simples Nacional, Lucro Presumido, "
        "Lucro Real) para um cenário de faturamento e setor. Retorna estimativa de alíquota "
        "efetiva, imposto anual e melhor opção. Util para planejamento tributário rápido. "
        "Setor: comércio, serviços ou indústria. Folha opcional impacta Fator R no Simples."
    ),
)
async def tool_compare_tax_regimes(
    faturamento_anual: float,
    setor: str,
    folha_pagamento_anual: float | None = None,
) -> dict[str, Any]:
    """Compara regimes tributarios para um cenário."""
    if setor not in ("comércio", "serviços", "indústria"):
        raise ValueError("setor deve ser: comércio, serviços ou indústria")
    resultado = compare_tax_regimes(
        faturamento_anual=faturamento_anual,
        setor=setor,  # type: ignore[arg-type]
        folha_pagamento_anual=folha_pagamento_anual,
    )
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="risk_score_supplier",
    description=(
        "Calcula score de risco (0-100) para due diligence de fornecedor. "
        "Combina ComplianceReport com ajustes conservadores para contratacao. "
        "Retorna recomendacao binaria (aprovar/aprovar_com_ressalvas/investigar/recusar). "
        "Opcao criterios_estritos=true reduz score em 10 para politicas anti-corrupcao."
    ),
)
async def tool_risk_score_supplier(cnpj: str, criterios_estritos: bool = False) -> dict[str, Any]:
    """Score de risco para due diligence de fornecedor."""
    resultado = await risk_score_supplier(cnpj, criterios_estritos)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="validate_nfe_full",
    description=(
        "Validacao consolidada de uma NFe a partir do XML: parse estrutural, validação "
        "do digito verificador da chave, verificacao de situacao do CNPJ emissor. "
        "Recebe caminho de arquivo XML local. Retorna relatório com chave, validade, "
        "issues e resumo."
    ),
)
async def tool_validate_nfe_full(xml_path: str) -> dict[str, Any]:
    """Validacao consolidada de NFe."""
    resultado = await validate_nfe_full(xml_path)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="summarize_sped",
    description=(
        "Sumarizacao executiva de um arquivo SPED (Fiscal, Contribuicoes, ECF ou ECD). "
        "Identifica tipo, extrai período, empresa, total de registros, blocos e produz "
        "resumo em pt-BR. Recebe caminho de arquivo .txt local."
    ),
)
async def tool_summarize_sped(file_path: str) -> dict[str, Any]:
    """Sumarizacao executiva de arquivo SPED."""
    resultado = await summarize_sped(file_path)
    return resultado.model_dump(mode="json", exclude_none=True)


def main() -> None:
    """Inicia o servidor MCP.

    Modo de transporte configurável via argumento --transport ou variável de ambiente
    FASTMCP_TRANSPORT. Valores aceitos: stdio (padrão), sse, http, streamable-http.

    Para HTTP/SSE, a porta é configurada via variável PORT (padrão: 8000).
    """
    import argparse
    import os

    parser = argparse.ArgumentParser(description="MCP Fiscal Brasil")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http", "streamable-http"],
        default=os.environ.get("FASTMCP_TRANSPORT", "stdio"),
        help="Protocolo de transporte (padrão: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Porta HTTP/SSE (padrão: 8000, ou valor da variável PORT)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host para HTTP/SSE (padrão: 0.0.0.0)",
    )
    args = parser.parse_args()

    logger.info("Iniciando MCP Fiscal Brasil v%s (transport=%s)", __version__, args.transport)

    if args.transport == "stdio":
        app.run(transport="stdio")
    else:
        app.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
