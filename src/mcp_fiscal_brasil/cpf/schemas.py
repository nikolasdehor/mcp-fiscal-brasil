from pydantic import BaseModel


class CPFValidation(BaseModel):
    cpf_formatado: str
    válido: bool
    digitos_verificadores_ok: bool
