"""Tests for shared fiscal error types."""

from typing import Any

from mcp_fiscal_brasil._core.errors import (
    FiscalError,
    FiscalHTTPError,
    FiscalNotFoundError,
    FiscalRateLimitError,
    FiscalValidationError,
)


def test_fiscal_error_has_message_detail_str_and_repr() -> None:
    error = FiscalError("Falha fiscal", detail={"source": "test"})

    assert str(error) == "Falha fiscal"
    assert repr(error) == "FiscalError(message='Falha fiscal', detail={'source': 'test'})"
    assert error.message == "Falha fiscal"
    assert error.detail == {"source": "test"}


def test_http_error_inherits_fiscal_error_and_exposes_status_url() -> None:
    error = FiscalHTTPError(
        "Serviço indisponível",
        status_code=503,
        url="https://example.test/api",
        detail={"attempts": 3},
    )

    assert isinstance(error, FiscalError)
    assert str(error) == "Serviço indisponível"
    assert error.status_code == 503
    assert error.url == "https://example.test/api"
    assert "status_code=503" in repr(error)
    assert "https://example.test/api" in repr(error)


def test_rate_limit_error_exposes_retry_after() -> None:
    error = FiscalRateLimitError("Limite excedido", retry_after=1.5)

    assert isinstance(error, FiscalError)
    assert error.retry_after == 1.5
    assert "retry_after=1.5" in repr(error)


def test_validation_error_exposes_field_and_value() -> None:
    value: Any = "00"
    error = FiscalValidationError("CNPJ inválido", field="cnpj", value=value)

    assert isinstance(error, FiscalError)
    assert error.field == "cnpj"
    assert error.value == value
    assert "field='cnpj'" in repr(error)


def test_not_found_error_exposes_resource_type_and_identifier() -> None:
    error = FiscalNotFoundError(
        "Empresa não encontrada",
        resource_type="cnpj",
        identifier="00000000000000",
    )

    assert isinstance(error, FiscalError)
    assert error.resource_type == "cnpj"
    assert error.identifier == "00000000000000"
    assert "resource_type='cnpj'" in repr(error)
