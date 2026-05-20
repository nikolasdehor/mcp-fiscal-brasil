from unittest.mock import patch

import pytest

from mcp_fiscal_brasil._core.errors import FiscalHTTPError, FiscalNotFoundError
from mcp_fiscal_brasil.cnae.client import CNAEClient


@pytest.fixture
def client():
    return CNAEClient()


@pytest.mark.asyncio
async def test_get_activities_success(client):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get_list") as mock_get:
        mock_get.return_value = [{"id": "0111301", "descrição": "Cultivo de arroz"}]
        result = await client.get_activities()
        assert len(result) == 1
        assert result[0].código == "0111301"


@pytest.mark.asyncio
async def test_get_activity_not_found(client):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get_list") as mock_get:
        mock_get.side_effect = FiscalHTTPError("Not found", 404, "http://test")
        with pytest.raises(FiscalNotFoundError):
            await client.get_activity("9999999")


@pytest.mark.asyncio
async def test_get_classes_success(client):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get_list") as mock_get:
        mock_get.return_value = [
            {
                "id": "01113",
                "descrição": "Cultivo de cereais",
                "grupo": {"descrição": "Grupo 1", "divisao": {"descrição": "Divisao 1"}},
            }
        ]
        result = await client.get_classes()
        assert len(result) == 1
        assert result[0].código == "01113"
        assert result[0].grupo == "Grupo 1"
        assert result[0].divisao == "Divisao 1"


@pytest.mark.asyncio
async def test_get_class_success(client):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get_list") as mock_get:
        mock_get.return_value = [{"id": "01113", "descrição": "Cultivo de cereais"}]
        result = await client.get_class("01113")
        assert result.código == "01113"
