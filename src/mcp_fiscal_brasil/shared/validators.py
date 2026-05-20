"""Validadores de documentos fiscais brasileiros (CPF, CNPJ, chave NFe)."""

import re


def _somente_digitos(valor: str) -> str:
    """Remove qualquer caractere não numerico."""
    return re.sub(r"\D", "", valor)


def validate_cpf(cpf: str) -> bool:
    """
    Valida um CPF brasileiro.

    Aceita formatos com ou sem mascara (XXX.XXX.XXX-XX ou XXXXXXXXXXX).
    Retorna False para CPFs com todos os digitos iguais (ex: 111.111.111-11).
    """
    números = _somente_digitos(cpf)

    if len(números) != 11:
        return False

    # Rejeita sequencias repetidas (ex: 00000000000)
    if len(set(números)) == 1:
        return False

    # Valida primeiro digito verificador
    soma = sum(int(números[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(números[9]):
        return False

    # Valida segundo digito verificador
    soma = sum(int(números[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(números[10]):
        return False

    return True


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida um CNPJ brasileiro.

    Aceita formatos com ou sem mascara (XX.XXX.XXX/XXXX-XX ou XXXXXXXXXXXXXX).
    """
    números = _somente_digitos(cnpj)

    if len(números) != 14:
        return False

    # Rejeita sequencias repetidas
    if len(set(números)) == 1:
        return False

    # Valida primeiro digito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(números[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    if digito1 != int(números[12]):
        return False

    # Valida segundo digito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(números[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    if digito2 != int(números[13]):
        return False

    return True


def validate_chave_nfe(chave: str) -> bool:
    """
    Valida uma chave de acesso de NFe/NFCe (44 digitos).

    A chave e composta por: cUF(2) + AAMM(4) + CNPJ(14) + mod(2) + serie(3)
    + nNF(9) + tpEmis(1) + cNF(8) + cDV(1) = 44 digitos.

    Verifica apenas o digito verificador (modulo 11).
    """
    números = _somente_digitos(chave)

    if len(números) != 44:
        return False

    # Calcula digito verificador pelo modulo 11
    # Pesos ciclo de 2 a 9 aplicados da direita para a esquerda (conforme NT SEFAZ 2011.002)
    pesos_ciclo = list(range(2, 10))  # [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    for i, digito in enumerate(reversed(números[:43])):
        soma += int(digito) * pesos_ciclo[i % len(pesos_ciclo)]

    resto = soma % 11
    if resto == 0 or resto == 1:
        dv_esperado = 0
    else:
        dv_esperado = 11 - resto

    return dv_esperado == int(números[43])


def format_cpf(cpf: str, remover_mascara: bool = False) -> str:
    """
    Formata um CPF com ou sem mascara.

    Se remover_mascara=True, retorna apenas os 11 digitos numericos.
    Caso contrario, retorna no formato XXX.XXX.XXX-XX.
    """
    números = _somente_digitos(cpf)
    if len(números) != 11:
        raise ValueError(f"CPF deve ter 11 digitos, recebeu {len(números)}")

    if remover_mascara:
        return números
    return f"{números[:3]}.{números[3:6]}.{números[6:9]}-{números[9:]}"


def format_cnpj(cnpj: str, remover_mascara: bool = False) -> str:
    """
    Formata um CNPJ com ou sem mascara.

    Se remover_mascara=True, retorna apenas os 14 digitos numericos.
    Caso contrario, retorna no formato XX.XXX.XXX/XXXX-XX.
    """
    números = _somente_digitos(cnpj)
    if len(números) != 14:
        raise ValueError(f"CNPJ deve ter 14 digitos, recebeu {len(números)}")

    if remover_mascara:
        return números
    return f"{números[:2]}.{números[2:5]}.{números[5:8]}/{números[8:12]}-{números[12:]}"


def format_chave_nfe(chave: str) -> str:
    """Formata uma chave NFe em grupos de 4 digitos para legibilidade."""
    números = _somente_digitos(chave)
    if len(números) != 44:
        raise ValueError(f"Chave NFe deve ter 44 digitos, recebeu {len(números)}")
    return " ".join(números[i : i + 4] for i in range(0, 44, 4))
