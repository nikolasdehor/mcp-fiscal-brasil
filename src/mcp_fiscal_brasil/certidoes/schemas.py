from pydantic import BaseModel


class CertidaoURL(BaseModel):
    tipo: str
    url: str
    descrição: str
    validade_dias_tipico: int | None = None
