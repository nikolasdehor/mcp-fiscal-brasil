# Planejamento tributário

Como usar o `mcp-fiscal` para sugerir regime tributário a clientes ou para decisões internas de planejamento.

## Cenario

Cliente / equipe pergunta: "Qual o melhor regime para meu cenário?". Tradicionalmente: pegar planilhas, calcular para cada regime, comparar. Tempo: 30-60 minutos.

Com `compare_tax_regimes`:

```python
plano = compare_tax_regimes(
    faturamento_anual=500_000,
    setor="serviços",
    folha_pagamento_anual=180_000,
)
```

Resposta em milissegundos com alíquota efetiva e imposto estimado por regime.

## Exemplo: assistente de planejamento

```python
from mcp_fiscal_brasil.agentic import compare_tax_regimes

def sugerir_regime(cenário: dict) -> dict:
    """Sugere regime tributário com base no cenário do cliente."""
    plano = compare_tax_regimes(
        faturamento_anual=cenário["faturamento"],
        setor=cenário["setor"],
        folha_pagamento_anual=cenário.get("folha"),
    )

    return {
        "recomendacao": plano.melhor_opcao,
        "economia_anual": plano.economia_anual_vs_pior,
        "ranking": [
            {
                "regime": o.regime,
                "imposto_anual": o.imposto_anual_estimado,
                "aplicável": o.aplicável,
            }
            for o in plano.opções
        ],
        "observações": plano.observações,
    }
```

## Cenarios comuns

### MEI vs Simples (microempresa de serviços)

```bash
mcp-fiscal regimes --faturamento 60000 --setor serviços --json
mcp-fiscal regimes --faturamento 100000 --setor serviços --json
```

Esperado: para faturamento <= R$ 81 mil, MEI tende a ser melhor (se a atividade for permitida). Acima disso, Simples.

### Fator R em serviços

```bash
# Folha alta -> Anexo III
mcp-fiscal regimes --faturamento 500000 --setor serviços --folha 200000

# Folha baixa -> Anexo V (mais caro)
mcp-fiscal regimes --faturamento 500000 --setor serviços --folha 30000
```

A diferenca de alíquota pode passar de 5pp.

### Industria grande (sem Simples)

```bash
mcp-fiscal regimes --faturamento 10000000 --setor indústria --json
```

Simples saira como `aplicável=false`. Comparativo entre Lucro Presumido e Lucro Real.

## Integracao com SaaS contabil

```python
from fastapi import FastAPI
from mcp_fiscal_brasil.agentic import compare_tax_regimes

app = FastAPI()

@app.post("/api/planejamento-tributário")
async def planejamento(payload: dict) -> dict:
    plano = compare_tax_regimes(
        faturamento_anual=payload["faturamento"],
        setor=payload["setor"],
        folha_pagamento_anual=payload.get("folha"),
    )
    return plano.model_dump(mode="json", exclude_none=True)
```

## Limitacoes

- Calculo simplificado, **NAO substitui parecer contabil**
- Não considera benefícios estaduais (ProEmprego, regimes especiais)
- ICMS usado e média nacional (12%) - na prática varia 4-25% por UF
- ISS usado e média (5%) - varia 2-5% por municipio
- Aliquotas atualizadas em 2025; revisar a cada reforma tributária
