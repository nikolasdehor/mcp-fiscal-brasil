"""
Servidor MCP Fiscal Brasil.

Registra todas as ferramentas fiscais e expoe via protocolo MCP (Model Context Protocol).
"""

import logging
from typing import Any

from fastmcp import FastMCP

from . import __version__
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
        "Consulte CNPJ, NFe, NFSe, SPED, eSocial e certidoes via linguagem natural. "
        "Dados obtidos de fontes publicas: BrasilAPI, ReceitaWS, SEFAZ."
    ),
)

# ---------------------------------------------------------------------------
# CNPJ
# ---------------------------------------------------------------------------


@app.tool(
    name="consultar_cnpj",
    description=(
        "Consulta os dados cadastrais completos de uma empresa pelo CNPJ. "
        "Retorna razao social, endereco, atividades economicas (CNAE), "
        "socios (QSA), situacao cadastral e porte da empresa. "
        "Aceita CNPJ com ou sem formatacao (pontos, barra, traco)."
    ),
)
async def tool_consultar_cnpj(cnpj: str) -> dict[str, Any]:
    """Consulta dados de empresa pelo CNPJ."""
    resultado = await consultar_cnpj(cnpj)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="listar_cnpjs_por_nome",
    description=(
        "Busca empresas pelo nome ou razao social. "
        "Nota: esta funcionalidade tem disponibilidade limitada em APIs publicas."
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
        "Valida o digito verificador de um CPF brasileiro. "
        "Verificacao matematica offline - nao consulta APIs externas. "
        "A Receita Federal nao disponibiliza API publica para dados de CPF."
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
        "Consulta os dados de uma Nota Fiscal Eletronica (NFe) pela chave de acesso de 44 digitos. "
        "A chave pode ser encontrada no DANFE (documento impresso da nota). "
        "Retorna emitente, destinatario, itens, valores e protocolo de autorizacao."
    ),
)
async def tool_consultar_nfe(chave_acesso: str) -> dict[str, Any]:
    """Consulta NFe pela chave de acesso."""
    resultado = await consultar_nfe(chave_acesso)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="validar_chave_nfe",
    description=(
        "Valida o formato e o digito verificador de uma chave de acesso de NFe. "
        "Nao consulta APIs - apenas verifica o calculo matematico (modulo 11). "
        "Tambem extrai informacoes da chave: UF, data de emissao, CNPJ emitente e numero da nota."
    ),
)
async def tool_validar_chave_nfe(chave_acesso: str) -> dict[str, Any]:
    """Valida chave de acesso de NFe."""
    return await validar_chave_nfe(chave_acesso)


@app.tool(
    name="consultar_status_sefaz",
    description=(
        "Consulta o status atual do servico SEFAZ de um estado brasileiro. "
        "Verifica se o webservice da SEFAZ para emissao de NFe esta operacional. "
        "Util para diagnosticar falhas de transmissao de notas fiscais."
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
        "Consulta dados de uma NFSe (Nota Fiscal de Servico Eletronica). "
        "ATENCAO: NFSe nao possui padrao nacional - cada municipio tem seu proprio sistema. "
        "Esta ferramenta orienta sobre como acessar o portal correto do municipio."
    ),
)
async def tool_consultar_nfse(
    numero: str,
    municipio: str,
    uf: str,
    cnpj_prestador: str | None = None,
) -> dict[str, str]:
    """Consulta NFSe com orientacoes por municipio."""
    return await consultar_nfse(numero, municipio, uf, cnpj_prestador)


# ---------------------------------------------------------------------------
# Simples Nacional
# ---------------------------------------------------------------------------


@app.tool(
    name="consultar_simples_nacional",
    description=(
        "Consulta se uma empresa e optante do Simples Nacional ou MEI. "
        "Retorna situacao atual, datas de opcao e exclusao do regime simplificado."
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
        "Analisa um arquivo SPED (EFD-ICMS/IPI, EFD-Contribuicoes, ECD ou ECF) "
        "e extrai informacoes sobre periodo, empresa, tipos de registros e possiveis erros. "
        "Recebe o conteudo do arquivo como texto (formato pipe-delimitado)."
    ),
)
async def tool_analisar_sped(conteudo: str, nome_arquivo: str | None = None) -> dict[str, Any]:
    """Analisa arquivo SPED."""
    resultado = await analisar_sped(conteudo, nome_arquivo)
    return resultado.model_dump(mode="json", exclude_none=True)


@app.tool(
    name="listar_registros_sped",
    description=(
        "Lista todas as ocorrencias de um tipo de registro especifico em um arquivo SPED. "
        "Exemplo: buscar todos os registros C100 (documentos fiscais) ou E110 (apuracao ICMS)."
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
        "Lista os eventos do eSocial com nome, grupo e descricao. "
        "Pode filtrar por grupo: 'Tabelas', 'Nao Periodicos', 'Periodicos' ou 'Exclusao'."
    ),
)
async def tool_listar_eventos_esocial(grupo: str | None = None) -> list[dict[str, Any]]:
    """Lista eventos eSocial."""
    eventos = await listar_eventos_esocial(grupo)
    return [e.model_dump() for e in eventos]


@app.tool(
    name="validar_evento_esocial",
    description=(
        "Realiza validacao basica de estrutura de um XML de evento eSocial. "
        "Verifica presenca do elemento raiz correto, codigo do evento e versao do leiaute."
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
        "Orienta sobre como consultar a Certidao Negativa de Debitos (CND) "
        "da Receita Federal e PGFN para CNPJ ou CPF. "
        "Fornece URLs de emissao e verificacao e alternativas para automacao."
    ),
)
async def tool_consultar_certidao_federal(cnpj_cpf: str) -> dict[str, str]:
    """Orienta consulta de CND na Receita Federal."""
    return await consultar_certidao_federal(cnpj_cpf)


@app.tool(
    name="consultar_certidao_fgts",
    description=(
        "Orienta sobre como consultar a Certidao de Regularidade do FGTS (CRF) "
        "para um CNPJ. Fornece URL do portal da Caixa e alternativas para automacao."
    ),
)
async def tool_consultar_certidao_fgts(cnpj: str) -> dict[str, str]:
    """Orienta consulta de CRF do FGTS."""
    return await consultar_certidao_fgts(cnpj)


def main() -> None:
    """Inicia o servidor MCP.

    Modo de transporte configuravel via argumento --transport ou variavel de ambiente
    FASTMCP_TRANSPORT. Valores aceitos: stdio (padrao), sse, http, streamable-http.

    Para HTTP/SSE, a porta e configurada via variavel PORT (padrao: 8000).
    """
    import argparse
    import os

    parser = argparse.ArgumentParser(description="MCP Fiscal Brasil")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http", "streamable-http"],
        default=os.environ.get("FASTMCP_TRANSPORT", "stdio"),
        help="Protocolo de transporte (padrao: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Porta HTTP/SSE (padrao: 8000, ou valor da variavel PORT)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host para HTTP/SSE (padrao: 0.0.0.0)",
    )
    args = parser.parse_args()

    logger.info("Iniciando MCP Fiscal Brasil v%s (transport=%s)", __version__, args.transport)

    if args.transport == "stdio":
        app.run(transport="stdio")
    else:
        app.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
