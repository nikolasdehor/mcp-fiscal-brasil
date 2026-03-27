"""Schemas para dados de NFe."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..shared.schemas import BaseResponse, Endereco


class EnderecoNFe(Endereco):
    """Endereco especifico do modelo NFe (com CNPJ/CPF)."""

    cnpj: str | None = None
    cpf: str | None = None
    ie: str | None = None
    nome: str | None = None


class ItemNFe(BaseModel):
    """Item (produto ou servico) de uma NFe."""

    numero: int
    codigo_produto: str
    descricao: str
    ncm: str | None = None
    cfop: str
    unidade: str
    quantidade: float
    valor_unitario: float
    valor_total: float
    cst_icms: str | None = None
    aliquota_icms: float | None = None
    valor_icms: float | None = None
    aliquota_ipi: float | None = None
    valor_ipi: float | None = None
    aliquota_pis: float | None = None
    valor_pis: float | None = None
    aliquota_cofins: float | None = None
    valor_cofins: float | None = None


class TotaisNFe(BaseModel):
    """Totais da NFe."""

    valor_produtos: float | None = None
    valor_desconto: float | None = None
    valor_frete: float | None = None
    valor_seguro: float | None = None
    valor_outras_despesas: float | None = None
    base_calculo_icms: float | None = None
    valor_icms: float | None = None
    valor_icms_desonerado: float | None = None
    base_calculo_icms_st: float | None = None
    valor_icms_st: float | None = None
    valor_ipi: float | None = None
    valor_pis: float | None = None
    valor_cofins: float | None = None
    valor_nota: float | None = None


class NFeResponse(BaseResponse):
    """Dados de uma NFe consultada."""

    chave_acesso: str
    numero: str | None = None
    serie: str | None = None
    modelo: str = "55"
    emitente: EnderecoNFe | None = None
    destinatario: EnderecoNFe | None = None
    data_emissao: datetime | None = None
    data_saida_entrada: datetime | None = None
    natureza_operacao: str | None = None
    tipo_operacao: str | None = None  # "0" saida, "1" entrada
    finalidade: str | None = None
    itens: list[ItemNFe] = Field(default_factory=list)
    totais: TotaisNFe | None = None
    protocolo_autorizacao: str | None = None
    data_autorizacao: datetime | None = None
    situacao: str | None = None
    informacoes_adicionais: str | None = None


class StatusSEFAZResponse(BaseResponse):
    """Status do servico SEFAZ de uma UF."""

    uf: str
    status: str
    descricao: str
    codigo: int | None = None
    ambiente: str = "producao"
    versao: str | None = None
