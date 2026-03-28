"""
Servidor MCP Fiscal Brasil.

Registra todas as ferramentas fiscais e expõe via protocolo MCP (Model Context Protocol).
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
