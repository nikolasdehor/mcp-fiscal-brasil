"""Ferramentas MCP para NFSe."""

from .schemas import NFSeResponse


async def consultar_nfse(
    numero: str,
    municipio: str,
    uf: str,
    cnpj_prestador: str | None = None,
) -> dict[str, str]:
    """
    Consulta dados de uma NFSe (Nota Fiscal de Servico Eletronica).

    IMPORTANTE: NFSe nao possui padrao nacional. Cada municipio tem seu proprio
    sistema (ABRASF, ISS.net, Betha, Curitiba, etc.). Esta ferramenta fornece
    orientacoes sobre como consultar a NFSe no municipio informado.

    Args:
        numero: Numero da NFSe
        municipio: Nome do municipio (ex: 'Sao Paulo', 'Belo Horizonte')
        uf: Sigla do estado (ex: 'SP', 'MG')
        cnpj_prestador: CNPJ do prestador de servico (opcional)

    Returns:
        Dicionario com orientacoes de consulta para o municipio.
    """
    # Portais de consulta por municipio/sistema
    portais_conhecidos: dict[str, str] = {
        "SAO PAULO": "https://nfe.prefeitura.sp.gov.br/contribuinte/notasfiscais.aspx",
        "RIO DE JANEIRO": "https://notacarioca.rio.gov.br/",
        "BELO HORIZONTE": "https://bhiss.pbh.gov.br/nfse/",
        "CURITIBA": "https://nfse.curitiba.pr.gov.br/",
        "PORTO ALEGRE": "https://nfse.portoalegre.rs.gov.br/",
        "SALVADOR": "https://nfse.salvador.ba.gov.br/",
        "FORTALEZA": "https://www.sefin.fortaleza.ce.gov.br/",
        "BRASILIA": "https://www.nfse.df.gov.br/",
        "MANAUS": "https://nfse.manaus.am.gov.br/",
        "RECIFE": "https://nfse.recife.pe.gov.br/",
    }

    municipio_upper = municipio.upper().strip()
    portal = portais_conhecidos.get(municipio_upper)

    return {
        "numero": numero,
        "municipio": municipio,
        "uf": uf.upper(),
        "status": "consulta_manual_necessaria",
        "motivo": (
            "NFSe nao possui API publica padronizada nacional. "
            "Cada municipio gerencia seu proprio sistema de emissao e consulta."
        ),
        "portal_municipio": portal or f"Acesse o portal da prefeitura de {municipio}/{uf.upper()}",
        "alternativa": (
            "Para integracao automatizada, contrate um emissor NFSe como "
            "Omie, ContaAzul, NFe.io ou Enotas que suportam multiplos municipios."
        ),
    }
