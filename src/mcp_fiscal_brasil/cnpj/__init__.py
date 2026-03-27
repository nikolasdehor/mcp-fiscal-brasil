"""Modulo CNPJ: consulta e validacao de empresas na Receita Federal."""

from .schemas import CNPJResponse, QSASocio
from .tools import consultar_cnpj, listar_cnpjs_por_nome

__all__ = ["CNPJResponse", "QSASocio", "consultar_cnpj", "listar_cnpjs_por_nome"]
