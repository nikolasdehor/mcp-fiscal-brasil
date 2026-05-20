# Modulo CPF

Validacao **algoritmica offline** do digito verificador do CPF.

A Receita Federal não expoe API publica para consulta de CPF (dados pessoais). Esse módulo so verifica o cálculo matematico do DV.

## Uso

```python
from mcp_fiscal_brasil.cpf.tools import validar_cpf_tool

resultado = await validar_cpf_tool("123.456.789-09")
print(resultado.válido)  # True/False
```

## Tool MCP

- `validar_cpf(cpf: str)` - validação offline do DV

## Limitacoes

Não consulta:

- Nome titular
- Situacao cadastral (regular/pendente/cancelada)
- Outras informações pessoais

Para esses dados, e necessário contrato com SERPRO Datavalid ou Caixa.
