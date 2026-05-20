# validate_nfe_full

Validacao consolidada de NFe (XML + chave + situação do emissor).

## Assinatura

```python
async def validate_nfe_full(xml_path: str | Path) -> NFeValidationReport
```

## O que faz

1. **Parse estrutural** do XML (lxml)
2. **Validacao do digito verificador** da chave de acesso (módulo 11)
3. **Consulta do CNPJ emissor** para confirmar situação ativa

Retorna relatório com chave, validade, issues e resumo.

## Schema de saida

```python
class NFeValidationReport(BaseModel):
    chave_acesso: str
    valida_estruturalmente: bool
    chave_consistente: bool
    emissor_ativo: bool | None  # None se não foi possivel verificar
    issues: list[NFeValidationIssue]
    cnpj_emissor: str | None
    cnpj_destinatario: str | None
    valor_total: float | None
    data_emissao: date | None
    resumo: str
```

## Codigos de issue

| Codigo | Severidade | Significado |
|--------|------------|-------------|
| `XML_PARSE_ERROR` | critico | XML mal-formado ou schema invalido |
| `CHAVE_INVALIDA` | alto | DV da chave não confere com conteudo |
| `EMISSOR_INATIVO` | alto | CNPJ emissor não esta `ativa` na Receita |
| `CHAVE_VALIDACAO_FALHOU` | medio | Falha técnica ao validar chave (rede etc) |

## Exemplos

### Via REST API

```bash
curl -X POST http://localhost:8000/v1/nfe/validate \
  -H "Content-Type: application/json" \
  -d '{"xml_path": "/var/notas/35240300623904000197550010000012341234567890.xml"}'
```

### Python

```python
from mcp_fiscal_brasil.agentic import validate_nfe_full

report = await validate_nfe_full("/var/notas/nota.xml")
if not report.valida_estruturalmente:
    raise ValueError(f"NFe invalida: {report.resumo}")
for issue in report.issues:
    print(f"[{issue.severidade}] {issue.código}: {issue.descrição}")
```

### Via agente IA

> "Valide a NFe em /var/notas/35240300623904000197550010000012341234567890.xml e me da o relatório"
