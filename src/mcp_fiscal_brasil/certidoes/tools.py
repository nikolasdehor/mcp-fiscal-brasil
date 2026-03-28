"""Ferramentas MCP para certidões negativas de débito."""

from ..shared.exceptions import ValidationError
from ..shared.validators import validate_cnpj, validate_cpf


async def consultar_certidao_federal(cnpj_cpf: str) -> dict[str, str]:
    """
    Orienta sobre como consultar a Certidão Negativa de Débitos (CND) na Receita Federal.

    IMPORTANTE: A Receita Federal não disponibiliza API pública para emissão automática de CND.
    A emissão requer resolução de CAPTCHA ou certificado digital A1/A3.

    Args:
        cnpj_cpf: CNPJ ou CPF do contribuinte (com ou sem formatação)

    Returns:
        Dicionário com orientações sobre como obter a certidão.

    Raises:
        ValidationError: Se o CNPJ/CPF for inválido.
    """
    digitos = "".join(c for c in cnpj_cpf if c.isdigit())

    if len(digitos) == 14:
        if not validate_cnpj(cnpj_cpf):
            raise ValidationError("cnpj", cnpj_cpf, "CNPJ inválido")
        tipo_doc = "CNPJ"
        url_emissao = "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir"
        url_verificacao = (
            "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Verificar"
        )
    elif len(digitos) == 11:
        if not validate_cpf(cnpj_cpf):
            raise ValidationError("cpf", cnpj_cpf, "CPF inválido")
        tipo_doc = "CPF"
        url_emissao = "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PF/Emitir"
        url_verificacao = (
            "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PF/Verificar"
        )
    else:
        raise ValidationError(
            "cnpj_cpf", cnpj_cpf, "Informe um CPF (11 dígitos) ou CNPJ (14 dígitos)"
        )

    return {
        "tipo_documento": tipo_doc,
        "documento": cnpj_cpf,
        "status": "consulta_manual_necessaria",
        "motivo": (
            "A Receita Federal não disponibiliza API pública para emissão automática de CND. "
            "A emissão online requer resolução de CAPTCHA."
        ),
        "url_emissao": url_emissao,
        "url_verificacao": url_verificacao,
        "alternativas": (
            "Para automação, utilize: "
            "(1) Certificado digital A1/A3 com procuração no e-CAC; "
            "(2) Serviços como Serasa Experian, Boa Vista ou APIs de terceiros; "
            "(3) Procuração eletrônica no e-CAC para acesso via sistema."
        ),
        "e_cac": "https://cav.receita.fazenda.gov.br/autenticacao/login",
    }


async def consultar_certidao_fgts(cnpj: str) -> dict[str, str]:
    """
    Orienta sobre como consultar a Certidão de Regularidade do FGTS (CRF).

    O FGTS disponibiliza consulta via portal do FGTS (conectividade social).

    Args:
        cnpj: CNPJ do empregador (com ou sem formatação)

    Returns:
        Dicionário com orientações e URL de consulta.

    Raises:
        ValidationError: Se o CNPJ for inválido.
    """
    if not validate_cnpj(cnpj):
        raise ValidationError("cnpj", cnpj, "CNPJ inválido")

    return {
        "documento": cnpj,
        "orgao": "Caixa Econômica Federal - FGTS",
        "status": "consulta_manual_necessaria",
        "url_consulta": "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf",
        "url_conectividade_social": "https://conectividade.caixa.gov.br/",
        "motivo": (
            "A consulta de CRF do FGTS requer autenticação no portal da Caixa "
            "ou uso do Conectividade Social (certificado digital)."
        ),
        "para_automacao": (
            "Utilize o kit Conectividade Social da Caixa com certificado digital A1/A3 "
            "para integração automatizada via SFTP."
        ),
    }
