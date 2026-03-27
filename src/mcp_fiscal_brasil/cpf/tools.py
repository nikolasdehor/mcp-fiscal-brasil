"""Ferramentas MCP para CPF."""

from ..shared.validators import format_cpf, validate_cpf
from .schemas import CPFValidacaoResponse


async def validar_cpf_tool(cpf: str) -> CPFValidacaoResponse:
    """
    Valida o digito verificador de um CPF brasileiro.

    Nao consulta APIs externas - apenas verifica o calculo matematico.
    A Receita Federal nao disponibiliza API publica para consulta de dados de CPF.

    Args:
        cpf: Numero do CPF com ou sem formatacao (ex: '123.456.789-09' ou '12345678909')

    Returns:
        CPFValidacaoResponse indicando se o CPF e matematicamente valido.
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
            motivo = f"CPF deve ter 11 digitos, recebeu {len(digitos)}"
        elif len(set(digitos)) == 1:
            motivo = "CPF com todos os digitos iguais e invalido"
        else:
            motivo = "Digito verificador invalido"

    return CPFValidacaoResponse(
        cpf_informado=cpf,
        cpf_formatado=cpf_formatado,
        valido=valido,
        motivo=motivo,
    )
