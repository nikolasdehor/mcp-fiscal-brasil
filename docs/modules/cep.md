# Modulo CEP

Lookup de endereços por CEP.

## Uso

```python
from mcp_fiscal_brasil.cep.client import CEPClient

client = CEPClient()
endereço = await client.get_address("74000000")
print(f"{endereço.logradouro}, {endereço.bairro} - {endereço.municipio}/{endereço.uf}")
```

## Fontes

- **BrasilAPI** (preferencial)
- **ViaCEP** (fallback)

Ambas são publicas e gratuitas, sem rate limit estrito.
