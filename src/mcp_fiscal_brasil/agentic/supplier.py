"""Score de risco de fornecedor combinando compliance + heuristica."""

from __future__ import annotations

from typing import Literal

from .compliance import analyze_cnpj_compliance
from .schemas import SupplierRiskScore


def _recomendacao(
    score: int,
) -> Literal["aprovar", "aprovar_com_ressalvas", "investigar", "recusar"]:
    if score >= 80:
        return "aprovar"
    if score >= 60:
        return "aprovar_com_ressalvas"
    if score >= 30:
        return "investigar"
    return "recusar"


async def risk_score_supplier(cnpj: str, criterios_estritos: bool = False) -> SupplierRiskScore:
    """
    Calcula score de risco para due diligence de fornecedor.

    Baseia-se em ComplianceReport e aplica ajustes para o contexto de
    contratacao de fornecedor (mais conservador que compliance geral).

    Args:
        cnpj: CNPJ do fornecedor (com ou sem formatacao).
        criterios_estritos: Se True, reduz tolerancia (subtrai 10 pontos do score).
            Usar quando contratante tem politica anti-corrupcao agressiva.

    Returns:
        SupplierRiskScore com recomendacao acionavel.

    Exemplo:
        score = await risk_score_supplier("12.345.678/0001-90", criterios_estritos=True)
        if score.recomendacao == "recusar":
            # bloquear cadastro
            ...
    """
    compliance = await analyze_cnpj_compliance(cnpj)

    score = compliance.score
    fatores: list[str] = []

    if compliance.risco_geral == "baixo":
        fatores.append("Situacao cadastral regular")
    if compliance.razao_social:
        fatores.append(f"Empresa identificada: {compliance.razao_social}")

    for achado in compliance.achados:
        if achado.severidade in ("alto", "critico"):
            score -= 15
            fatores.append(f"NEGATIVO: {achado.titulo}")
        elif achado.severidade == "medio":
            score -= 5
            fatores.append(f"Atencao: {achado.titulo}")

    if criterios_estritos:
        score -= 10
        fatores.append("Criterios estritos aplicados (-10)")

    score = max(0, min(100, score))

    if score >= 80:
        risco = "baixo"
    elif score >= 60:
        risco = "medio"
    elif score >= 30:
        risco = "alto"
    else:
        risco = "critico"

    return SupplierRiskScore(
        cnpj=compliance.cnpj,
        razao_social=compliance.razao_social,
        risco=risco,
        score=score,
        fatores=fatores,
        recomendacao=_recomendacao(score),
    )
