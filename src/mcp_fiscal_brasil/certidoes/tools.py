"""Ferramentas MCP para certidoes negativas de debito."""

from ..shared.exceptions import ValidationError
from ..shared.validators import validate_cnpj, validate_cpf


async def consultar_certidao_federal(cnpj_cpf: str) -> dict[str, str]:
    """
    Orienta sobre como consultar a Certidao Negativa de Debitos (CND) na Receita Federal.

    IMPORTANTE: A Receita Federal nao disponibiliza API publica para emissao automatica de CND.
    A emissao requer resolucao de CAPTCHA ou certificado digital A1/A3.

    Args:
        cnpj_cpf: CNPJ ou CPF do contribuinte (com ou sem formatacao)

    Returns:
        Dicionario com orientacoes sobre como obter a certidao.

    Raises:
        ValidationError: Se o CNPJ/CPF for invalido.
    """
    digitos = "".join(c for c in cnpj_cpf if c.isdigit())

    if len(digitos) == 14:
        if not validate_cnpj(cnpj_cpf):
            raise ValidationError("cnpj", cnpj_cpf, "CNPJ invalido")
        tipo_doc = "CNPJ"
        url_emissao = "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir"
        url_verificacao = (
            "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Verificar"
        )
    elif len(digitos) == 11:
        if not validate_cpf(cnpj_cpf):
            raise ValidationError("cpf", cnpj_cpf, "CPF invalido")
        tipo_doc = "CPF"
        url_emissao = "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PF/Emitir"
        url_verificacao = (
            "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PF/Verificar"
        )
    else:
        raise ValidationError(
            "cnpj_cpf", cnpj_cpf, "Informe um CPF (11 digitos) ou CNPJ (14 digitos)"
        )

    return {
        "tipo_documento": tipo_doc,
        "documento": cnpj_cpf,
        "status": "consulta_manual_necessaria",
        "motivo": (
            "A Receita Federal nao disponibiliza API publica para emissao automatica de CND. "
            "A emissao online requer resolucao de CAPTCHA."
        ),
        "url_emissao": url_emissao,
        "url_verificacao": url_verificacao,
        "alternativas": (
            "Para automacao, utilize: "
            "(1) Certificado digital A1/A3 com procuracao no e-CAC; "
            "(2) Servicos como Serasa Experian, Boa Vista ou APIs de terceiros; "
            "(3) Procuracao eletronica no e-CAC para acesso via sistema."
        ),
        "e_cac": "https://cav.receita.fazenda.gov.br/autenticacao/login",
    }


async def consultar_certidao_fgts(cnpj: str) -> dict[str, str]:
    """
    Orienta sobre como consultar a Certidao de Regularidade do FGTS (CRF).

    O FGTS disponibiliza consulta via portal do FGTS (conectividade social).

    Args:
        cnpj: CNPJ do empregador (com ou sem formatacao)

    Returns:
        Dicionario com orientacoes e URL de consulta.

    Raises:
        ValidationError: Se o CNPJ for invalido.
    """
    if not validate_cnpj(cnpj):
        raise ValidationError("cnpj", cnpj, "CNPJ invalido")

    return {
        "documento": cnpj,
        "orgao": "Caixa Economica Federal - FGTS",
        "status": "consulta_manual_necessaria",
        "url_consulta": "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf",
        "url_conectividade_social": "https://conectividade.caixa.gov.br/",
        "motivo": (
            "A consulta de CRF do FGTS requer autenticacao no portal da Caixa "
            "ou uso do Conectividade Social (certificado digital)."
        ),
        "para_automacao": (
            "Utilize o kit Conectividade Social da Caixa com certificado digital A1/A3 "
            "para integracao automatizada via SFTP."
        ),
    }
