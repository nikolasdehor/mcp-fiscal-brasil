"""Modulo compartilhado: utilitarios, clientes HTTP, validadores e schemas base."""

from .exceptions import (
    MCPFiscalError,
    APIError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    TimeoutError,
    XMLParseError,
)
from .validators import validate_cpf, validate_cnpj, validate_chave_nfe, format_cpf, format_cnpj
from .schemas import BaseResponse, ErrorResponse

__all__ = [
    "MCPFiscalError",
    "APIError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "TimeoutError",
    "XMLParseError",
    "validate_cpf",
    "validate_cnpj",
    "validate_chave_nfe",
    "format_cpf",
    "format_cnpj",
    "BaseResponse",
    "ErrorResponse",
]
