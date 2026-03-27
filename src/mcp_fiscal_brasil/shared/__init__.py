"""Modulo compartilhado: utilitarios, clientes HTTP, validadores e schemas base."""

from .exceptions import (
    APIError,
    MCPFiscalError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    XMLParseError,
)
from .schemas import BaseResponse, ErrorResponse
from .validators import format_cnpj, format_cpf, validate_chave_nfe, validate_cnpj, validate_cpf

__all__ = [
    "APIError",
    "BaseResponse",
    "ErrorResponse",
    "MCPFiscalError",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    "XMLParseError",
    "format_cnpj",
    "format_cpf",
    "validate_chave_nfe",
    "validate_cnpj",
    "validate_cpf",
]
