"""Ferramentas MCP para CPF."""

from ..shared.validators import format_cpf, validate_cpf
from .schemas import CPFValidacaoResponse


async def validar_cpf_tool(cpf: str) -> CPFValidacaoResponse:
    """
    Valida o dígito verificador de um CPF brasileiro.

    Não consulta APIs externas - apenas verifica o cálculo matemático.
    A Receita Federal não disponibiliza API pública para consulta de dados de CPF.

    Args:
        cpf: Número do CPF com ou sem formatação (ex: '123.456.789-09' ou '12345678909')

    Returns:
        CPFValidacaoResponse indicando se o CPF é matematicamente válido.
    """
    valido = validate_cpf(cpf)

    cpf_formatado = None
    if valido:
        try:
            cpf_formatado = format_cpf(cpf)
        except ValueError:
            pass

    motivo = None
    if not valido:
        digitos = "".join(c for c in cpf if c.isdigit())
        if len(digitos) != 11:
            motivo = f"CPF deve ter 11 dígitos, recebeu {len(digitos)}"
        elif len(set(digitos)) == 1:
            motivo = "CPF com todos os dígitos iguais é inválido"
        else:
            motivo = "Dígito verificador inválido"

    return CPFValidacaoResponse(
        cpf_informado=cpf,
        cpf_formatado=cpf_formatado,
        valido=valido,
        motivo=motivo,
    )
