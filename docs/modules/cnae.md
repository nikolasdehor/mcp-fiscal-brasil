# Modulo CNAE

Classificacao Nacional de Atividades Economicas.

## Uso

```python
from mcp_fiscal_brasil.cnae.client import CNAEClient

client = CNAEClient()
atividades = await client.search("desenvolvimento de software")
for a in atividades:
    print(a.código, a.descrição)
```

## Schema

```python
class CNAEActivity(BaseModel):
    código: str
    descrição: str

class CNAEClass(BaseModel):
    classe: str
    descrição: str
    atividades: list[CNAEActivity]
```

## Casos de uso

- Validar compatibilidade entre atividade economica e operação
- Sugerir CNAE para novos cadastros
- Mapear empresa -> setor para analise de carteira
