"""Hierarquia de excecoes do MCP Fiscal Brasil."""

from typing import Any


class MCPFiscalError(Exception):
    """Excecao base para todos os erros do MCP Fiscal Brasil."""

    def __init__(
        self, message: str, code: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or "FISCAL_ERROR"
        self.details = details or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


class APIError(MCPFiscalError):
    """Erro retornado por uma API externa (SEFAZ, Receita Federal, etc.)."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        endpoint: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="API_ERROR", details=details)
        self.status_code = status_code
        self.endpoint = endpoint


class RateLimitError(MCPFiscalError):
    """Limite de requisicoes excedido para um endpoint."""

    def __init__(self, endpoint: str, retry_after: float | None = None) -> None:
        message = f"Limite de requisicoes excedido para {endpoint}"
        if retry_after is not None:
            message += f". Tente novamente em {retry_after:.1f}s"
        super().__init__(message, code="RATE_LIMIT_ERROR")
        self.endpoint = endpoint
        self.retry_after = retry_after


class ValidationError(MCPFiscalError):
    """Dado invalido fornecido pelo usuario (CPF, CNPJ, chave NFe, etc.)."""

    def __init__(self, field: str, value: str, reason: str) -> None:
        message = f"Valor invalido para '{field}': {value!r}. {reason}"
        super().__init__(message, code="VALIDATION_ERROR", details={"field": field, "value": value})
        self.field = field
        self.value = value
        self.reason = reason


class NotFoundError(MCPFiscalError):
    """Recurso nao encontrado na API ou base de dados."""

    def __init__(self, resource: str, identifier: str) -> None:
        message = f"{resource} nao encontrado: {identifier}"
        super().__init__(
            message, code="NOT_FOUND", details={"resource": resource, "identifier": identifier}
        )
        self.resource = resource
        self.identifier = identifier


class TimeoutError(MCPFiscalError):
    """Timeout ao comunicar com servico externo."""

    def __init__(self, endpoint: str, timeout_seconds: float) -> None:
        message = f"Timeout de {timeout_seconds}s ao acessar {endpoint}"
        super().__init__(message, code="TIMEOUT_ERROR", details={"endpoint": endpoint})
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds


class XMLParseError(MCPFiscalError):
    """Erro ao parsear XML de NFe, NFSe ou SPED."""

    def __init__(self, message: str, raw_content: str | None = None) -> None:
        super().__init__(message, code="XML_PARSE_ERROR")
        self.raw_content = raw_content


class AuthError(MCPFiscalError):
    """Erro de autenticacao com servico externo (certificado digital, token, etc.)."""

    def __init__(self, service: str, reason: str) -> None:
        message = f"Falha de autenticacao com {service}: {reason}"
        super().__init__(message, code="AUTH_ERROR", details={"service": service})
        self.service = service
        self.reason = reason
