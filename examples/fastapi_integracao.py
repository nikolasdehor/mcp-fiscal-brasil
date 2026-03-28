"""
Exemplo: API REST fiscal usando mcp-fiscal-brasil + FastAPI.

Demonstra como integrar o SDK em uma aplicação FastAPI, aproveitando
o ciclo de vida do framework para gerenciar a instância do FiscalBrasil.

Instalar dependências extras:
    pip install fastapi uvicorn

Executar:
    uvicorn examples.fastapi_integracao:app --reload

Endpoints disponíveis:
    GET /cnpj/{cnpj}              - Dados completos do CNPJ
    GET /nfe/status/{uf}          - Status SEFAZ de uma UF
    GET /nfe/chave/{chave}        - Consultar NFe por chave de acesso
    GET /validar/cpf/{cpf}        - Validar CPF (offline)
    GET /validar/cnpj/{cnpj}      - Validar CNPJ (offline)
    GET /simples/{cnpj}           - Situação no Simples Nacional
    GET /esocial/eventos          - Listar eventos eSocial
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query

from mcp_fiscal_brasil import FiscalBrasil


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Gerencia o ciclo de vida do FiscalBrasil junto com a aplicação FastAPI."""
    app.state.fiscal = FiscalBrasil()
    yield
    await app.state.fiscal.fechar()


app = FastAPI(
    title="API Fiscal Brasil",
    description="API REST para consultas fiscais brasileiras. Alimentada pelo mcp-fiscal-brasil.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_fiscal(request: Any) -> FiscalBrasil:
    return request.app.state.fiscal


@app.get(
    "/cnpj/{cnpj}",
    summary="Consultar CNPJ",
    description="Retorna os dados completos de um CNPJ via BrasilAPI ou ReceitaWS.",
)
async def consultar_cnpj(cnpj: str, request: Any = None) -> Any:
    fiscal: FiscalBrasil = request.app.state.fiscal if request else FiscalBrasil()
    try:
        empresa = await fiscal.consultar_cnpj(cnpj)
        return empresa.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Serviço externo indisponível: {e}") from e


@app.get(
    "/nfe/status/{uf}",
    summary="Status SEFAZ",
    description="Consulta o status do serviço SEFAZ de uma UF.",
)
async def status_sefaz(uf: str, request: Any = None) -> Any:
    fiscal: FiscalBrasil = request.app.state.fiscal if request else FiscalBrasil()
    status = await fiscal.status_sefaz(uf.upper())
    return status.model_dump()


@app.get(
    "/nfe/chave/{chave}",
    summary="Consultar NFe",
    description="Consulta os dados de uma NFe pela chave de acesso de 44 dígitos.",
)
async def consultar_nfe(chave: str, request: Any = None) -> Any:
    fiscal: FiscalBrasil = request.app.state.fiscal if request else FiscalBrasil()
    try:
        nfe = await fiscal.consultar_nfe(chave)
        return nfe.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Serviço externo indisponível: {e}") from e


@app.get(
    "/validar/cpf/{cpf}",
    summary="Validar CPF",
    description="Valida o dígito verificador de um CPF (sem chamada de API).",
)
def validar_cpf(cpf: str) -> dict[str, Any]:
    fiscal = FiscalBrasil()
    return {"cpf": cpf, "valido": fiscal.validar_cpf(cpf)}


@app.get(
    "/validar/cnpj/{cnpj}",
    summary="Validar CNPJ",
    description="Valida o dígito verificador de um CNPJ (sem chamada de API).",
)
def validar_cnpj(cnpj: str) -> dict[str, Any]:
    fiscal = FiscalBrasil()
    return {"cnpj": cnpj, "valido": fiscal.validar_cnpj(cnpj)}


@app.get(
    "/validar/chave-nfe/{chave}",
    summary="Validar e decodificar chave NFe",
    description="Valida o dígito verificador e extrai os campos da chave de acesso.",
)
def validar_chave_nfe(chave: str) -> dict[str, Any]:
    fiscal = FiscalBrasil()
    return fiscal.validar_chave_nfe(chave)


@app.get(
    "/simples/{cnpj}",
    summary="Consultar Simples Nacional",
    description="Retorna a situação de um CNPJ no Simples Nacional e MEI.",
)
async def consultar_simples(cnpj: str, request: Any = None) -> Any:
    fiscal: FiscalBrasil = request.app.state.fiscal if request else FiscalBrasil()
    try:
        resultado = await fiscal.consultar_simples(cnpj)
        return resultado.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Serviço externo indisponível: {e}") from e


@app.get(
    "/esocial/eventos",
    summary="Listar eventos eSocial",
    description="Lista os eventos do eSocial com opção de filtro por grupo.",
)
async def listar_eventos_esocial(
    grupo: str | None = Query(
        default=None,
        description="Filtrar por grupo: Tabelas, Nao Periodicos, Periodicos, Exclusao, Totalizadores",
    ),
) -> list[dict[str, Any]]:
    fiscal = FiscalBrasil()
    return await fiscal.listar_eventos_esocial(grupo)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
