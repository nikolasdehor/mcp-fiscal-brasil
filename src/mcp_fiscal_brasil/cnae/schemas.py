from pydantic import BaseModel


class CNAEActivity(BaseModel):
    código: str
    descrição: str


class CNAEClass(BaseModel):
    código: str
    descrição: str
    grupo: str | None = None
    divisao: str | None = None
