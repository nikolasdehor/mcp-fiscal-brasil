"""Comparativo entre regimes tributarios brasileiros.

Calculo simplificado, baseado em premissas publicas e tabelas vigentes em 2025.
Nao substitui parecer de contador. Util para estimativa rapida e direcionamento.
"""

from __future__ import annotations

from typing import Literal

from .schemas import TaxRegimeComparison, TaxRegimeOption

_LIMITE_MEI = 81_000.0
_LIMITE_SIMPLES = 4_800_000.0
_LIMITE_LUCRO_PRESUMIDO = 78_000_000.0


def _calc_simples(
    faturamento: float,
    setor: Literal["comercio", "servicos", "industria"],
    folha: float | None,
) -> tuple[bool, float | None, float | None, str | None]:
    if faturamento > _LIMITE_SIMPLES:
        return (
            False,
            None,
            None,
            "Faturamento excede o limite anual do Simples Nacional (R$ 4,8 milhoes).",
        )

    # Aliquotas efetivas simplificadas por anexo (medias por faixa)
    if setor == "comercio":
        # Anexo I - aliquota efetiva media
        if faturamento <= 180_000:
            aliquota = 4.0
        elif faturamento <= 360_000:
            aliquota = 7.3
        elif faturamento <= 720_000:
            aliquota = 9.5
        elif faturamento <= 1_800_000:
            aliquota = 10.7
        elif faturamento <= 3_600_000:
            aliquota = 14.3
        else:
            aliquota = 19.0
    elif setor == "industria":
        # Anexo II - 0.5pp acima do comercio em geral
        if faturamento <= 180_000:
            aliquota = 4.5
        elif faturamento <= 360_000:
            aliquota = 7.8
        elif faturamento <= 720_000:
            aliquota = 10.0
        elif faturamento <= 1_800_000:
            aliquota = 11.2
        elif faturamento <= 3_600_000:
            aliquota = 14.7
        else:
            aliquota = 30.0
    else:  # servicos
        # Anexo III ou V conforme Fator R (folha / faturamento >= 0.28)
        fator_r = (folha or 0) / faturamento if faturamento > 0 else 0
        if fator_r >= 0.28:
            # Anexo III
            if faturamento <= 180_000:
                aliquota = 6.0
            elif faturamento <= 360_000:
                aliquota = 11.2
            elif faturamento <= 720_000:
                aliquota = 13.5
            elif faturamento <= 1_800_000:
                aliquota = 16.0
            elif faturamento <= 3_600_000:
                aliquota = 21.0
            else:
                aliquota = 33.0
        else:
            # Anexo V (servicos sem folha relevante)
            if faturamento <= 180_000:
                aliquota = 15.5
            elif faturamento <= 360_000:
                aliquota = 18.0
            elif faturamento <= 720_000:
                aliquota = 19.5
            elif faturamento <= 1_800_000:
                aliquota = 20.5
            elif faturamento <= 3_600_000:
                aliquota = 23.0
            else:
                aliquota = 30.5

    imposto = faturamento * aliquota / 100
    return True, aliquota, imposto, None


def _calc_lucro_presumido(
    faturamento: float, setor: Literal["comercio", "servicos", "industria"]
) -> tuple[bool, float | None, float | None, str | None]:
    if faturamento > _LIMITE_LUCRO_PRESUMIDO:
        return (
            False,
            None,
            None,
            "Faturamento excede o limite anual do Lucro Presumido (R$ 78 milhoes).",
        )
    # Presuncao de lucro
    if setor == "servicos":
        presuncao = 0.32
    else:
        presuncao = 0.08
    base_irpj = faturamento * presuncao
    irpj = base_irpj * 0.15
    csll = base_irpj * 0.09
    # PIS+COFINS regime cumulativo
    pis_cofins = faturamento * 0.0365
    # ISS estimado (servicos) ou ICMS estimado (comercio/industria)
    if setor == "servicos":
        outros = faturamento * 0.05  # ISS medio
    else:
        outros = faturamento * 0.12  # ICMS medio com beneficios
    total = irpj + csll + pis_cofins + outros
    aliquota_efetiva = total / faturamento * 100
    return True, aliquota_efetiva, total, None


def _calc_lucro_real_simplificado(
    faturamento: float, setor: Literal["comercio", "servicos", "industria"]
) -> tuple[bool, float | None, float | None, str | None]:
    # Estimativa muito grosseira: margem operacional 15% (lucro liquido)
    margem = 0.15
    lucro = faturamento * margem
    irpj = lucro * 0.15
    adicional = max(0.0, lucro - 240_000) * 0.10
    csll = lucro * 0.09
    pis_cofins = faturamento * 0.0925  # nao-cumulativo
    if setor == "servicos":
        outros = faturamento * 0.05
    else:
        outros = faturamento * 0.12
    total = irpj + adicional + csll + pis_cofins + outros
    aliquota_efetiva = total / faturamento * 100
    return True, aliquota_efetiva, total, None


def _calc_mei(
    faturamento: float, setor: Literal["comercio", "servicos", "industria"]
) -> tuple[bool, float | None, float | None, str | None]:
    if faturamento > _LIMITE_MEI:
        return False, None, None, "Faturamento excede o limite anual do MEI (R$ 81 mil)."
    # Valor mensal MEI 2025 ~ R$ 75 comercio/industria, R$ 80 servicos
    mensal = 80 if setor == "servicos" else 75
    total = mensal * 12
    aliquota_efetiva = total / faturamento * 100 if faturamento else 0
    return True, aliquota_efetiva, total, None


def compare_tax_regimes(
    faturamento_anual: float,
    setor: Literal["comercio", "servicos", "industria"],
    folha_pagamento_anual: float | None = None,
) -> TaxRegimeComparison:
    """
    Compara regimes tributarios brasileiros (MEI, Simples, Lucro Presumido, Lucro Real).

    Estimativa rapida baseada em tabelas publicas vigentes. NAO substitui parecer
    de contador. Util para direcionamento em decisoes de planejamento tributario.

    Args:
        faturamento_anual: Receita bruta anual em reais.
        setor: Setor da empresa (impacta anexo do Simples e presuncoes do LP).
        folha_pagamento_anual: Folha anual em reais. Importante para Fator R no Simples
            (servicos): se folha/faturamento >= 28%, usa Anexo III (mais barato).

    Returns:
        TaxRegimeComparison com opcoes avaliadas, melhor regime e economia estimada.

    Exemplo:
        resultado = compare_tax_regimes(
            faturamento_anual=500_000,
            setor="servicos",
            folha_pagamento_anual=180_000,
        )
        print(resultado.melhor_opcao)  # "simples_nacional"
        print(resultado.economia_anual_vs_pior)  # economia vs pior opcao
    """
    if faturamento_anual <= 0:
        raise ValueError("faturamento_anual deve ser positivo")

    opcoes_calc = [
        ("mei", _calc_mei(faturamento_anual, setor)),
        ("simples_nacional", _calc_simples(faturamento_anual, setor, folha_pagamento_anual)),
        ("lucro_presumido", _calc_lucro_presumido(faturamento_anual, setor)),
        ("lucro_real", _calc_lucro_real_simplificado(faturamento_anual, setor)),
    ]

    opcoes: list[TaxRegimeOption] = []
    for regime, (aplicavel, aliquota, imposto, motivo) in opcoes_calc:
        pros: list[str] = []
        contras: list[str] = []
        if regime == "mei":
            pros = ["Tributacao fixa mensal", "Burocracia minima"]
            contras = ["Limite baixo de faturamento", "Restrito a algumas atividades"]
        elif regime == "simples_nacional":
            pros = ["Recolhimento unificado (DAS)", "Aliquotas progressivas"]
            contras = ["Limite de R$ 4,8 mi anual", "Limitacoes em servicos especificos"]
        elif regime == "lucro_presumido":
            pros = ["Calculo simples", "Aproveitamento de margens altas"]
            contras = ["PIS/COFINS cumulativos", "Pode pagar imposto sobre lucro inexistente"]
        else:
            pros = [
                "Sem teto de faturamento",
                "PIS/COFINS nao-cumulativos com creditos",
                "Imposto sobre lucro real",
            ]
            contras = [
                "Burocracia alta (escrituracao completa)",
                "Custo contabil maior",
                "Antecipacoes mensais",
            ]
        opcoes.append(
            TaxRegimeOption(
                regime=regime,
                aplicavel=aplicavel,
                motivo_inaplicavel=motivo,
                aliquota_efetiva_estimada=aliquota,
                imposto_anual_estimado=imposto,
                pros=pros,
                contras=contras,
            )
        )

    aplicaveis = [o for o in opcoes if o.aplicavel and o.imposto_anual_estimado is not None]
    if not aplicaveis:
        raise RuntimeError("Nenhum regime aplicavel ao cenario fornecido")

    aplicaveis.sort(key=lambda o: o.imposto_anual_estimado or float("inf"))
    melhor = aplicaveis[0]
    pior_aplicavel = aplicaveis[-1]
    economia = (pior_aplicavel.imposto_anual_estimado or 0) - (melhor.imposto_anual_estimado or 0)

    obs = (
        "Estimativa simplificada usando tabelas publicas vigentes em 2025. "
        "Considera presuncoes medias de ICMS/ISS. Nao inclui beneficios estaduais nem "
        "regimes especiais. Consulte contador para decisao final."
    )

    return TaxRegimeComparison(
        cenario_faturamento_anual=faturamento_anual,
        cenario_setor=setor,
        folha_pagamento_anual=folha_pagamento_anual,
        opcoes=[*aplicaveis, *(o for o in opcoes if not o.aplicavel)],
        melhor_opcao=melhor.regime,
        economia_anual_vs_pior=economia,
        observacoes=obs,
    )
