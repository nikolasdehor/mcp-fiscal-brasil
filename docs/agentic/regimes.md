# compare_tax_regimes

Comparativo entre regimes tributários brasileiros (MEI, Simples, Lucro Presumido, Lucro Real).

## Assinatura

```python
def compare_tax_regimes(
    faturamento_anual: float,
    setor: Literal["comércio", "serviços", "indústria"],
    folha_pagamento_anual: float | None = None,
) -> TaxRegimeComparison
```

## O que faz

Calcula **alíquota efetiva estimada** e **imposto anual estimado** para cada regime tributário aplicável ao cenário, baseado em tabelas publicas vigentes (2025).

Retorna o regime **mais econômico** e a **economia anual vs pior opção**.

!!! warning "Estimativa, não planejamento contabil"

    Calculo simplificado baseado em premissas publicas. NAO substitui parecer de contador. Use para direcionamento em decisões de planejamento, não para apuração final.

## Heuristicas

### MEI
- Limite: R$ 81.000/ano
- Aplicavel apenas a algumas atividades
- Tributacao fixa mensal (~R$ 75-80)

### Simples Nacional
- Limite: R$ 4,8 milhoes/ano
- Anexo conforme setor (comércio I, indústria II, serviços III ou V)
- **Fator R** (serviços): folha/faturamento >= 28% -> Anexo III (mais barato)

### Lucro Presumido
- Limite: R$ 78 milhoes/ano
- Presuncao 8% (comércio/indústria) ou 32% (serviços)
- PIS/COFINS cumulativos (3,65%)

### Lucro Real
- Sem teto
- IRPJ 15% + adicional 10% sobre lucro liquido
- PIS/COFINS não-cumulativos com creditos
- Burocracia maior

## Schema de saida

```python
class TaxRegimeComparison(BaseModel):
    cenario_faturamento_anual: float
    cenario_setor: Literal["comércio", "serviços", "indústria"]
    folha_pagamento_anual: float | None
    opções: list[TaxRegimeOption]  # ordenadas: aplicáveis primeiro, do mais barato
    melhor_opcao: str
    economia_anual_vs_pior: float
    observações: str

class TaxRegimeOption(BaseModel):
    regime: Literal["mei", "simples_nacional", "lucro_presumido", "lucro_real"]
    aplicável: bool
    motivo_inaplicavel: str | None
    aliquota_efetiva_estimada: float | None
    imposto_anual_estimado: float | None
    pros: list[str]
    contras: list[str]
```

## Exemplos

### Empresa de serviços pequena

```bash
mcp-fiscal regimes --faturamento 300000 --setor serviços --folha 120000 --json
```

Esperado: melhor opção = `simples_nacional` (Anexo III pelo Fator R).

### Industria de medio porte

```bash
mcp-fiscal regimes --faturamento 5000000 --setor indústria --folha 1500000 --json
```

Esperado: Simples Nacional **não aplicável** (faturamento > R$ 4,8 mi). Melhor opção tipicamente `lucro_presumido`.

### Via REST API

```bash
curl "http://localhost:8000/v1/agentic/regimes?faturamento_anual=500000&setor=serviços&folha_pagamento_anual=180000"
```

### Via agente IA

> "Sou prestador de serviços com faturamento de R$ 500 mil e folha de R$ 180 mil. Qual o melhor regime?"
