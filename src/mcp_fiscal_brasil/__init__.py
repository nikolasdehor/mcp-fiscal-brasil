"""MCP Fiscal Brasil - Servidor MCP e SDK Python para o sistema fiscal brasileiro."""

__version__ = "0.1.0"
__author__ = "Nikolas DeHor"
__description__ = (
    "Servidor MCP para integrar IAs com o sistema fiscal brasileiro. "
    "Consulte CNPJ, NFe, NFSe, SPED, eSocial e mais via linguagem natural."
)

# SDK publica - disponivel como `from mcp_fiscal_brasil import FiscalBrasil`
from .sdk import FiscalBrasil

# Validadores offline - disponivel como `from mcp_fiscal_brasil import validate_cpf`
from .shared.validators import (
    format_chave_nfe,
    format_cnpj,
    format_cpf,
    validate_chave_nfe,
    validate_cnpj,
    validate_cpf,
)

__all__ = [
    "FiscalBrasil",
    "format_chave_nfe",
    "format_cnpj",
    "format_cpf",
    "validate_chave_nfe",
    "validate_cnpj",
    "validate_cpf",
]
