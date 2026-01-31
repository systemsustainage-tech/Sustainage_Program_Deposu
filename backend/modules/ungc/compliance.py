#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC Uyum Skoru
- İlke bazlı KPI skorlarını birleştirerek uyum skoru üretir
- Toplam uyum skoru ve ilke bazlı detay döner
"""

from typing import Dict, List

from .kpi import UNGCKPI, compute_kpi_score, weighted_average

PRINCIPLES = [
    "Human Rights",
    "Labour",
    "Environment",
    "Anti-Corruption",
]


def compute_principle_compliance(kpis: List[UNGCKPI]) -> Dict[str, Dict]:
    """
    KPI listesine göre ilke bazlı uyum skorlarını üretir.

    Returns:
        { principle: {"score": float, "kpi_count": int} }
    """
    result: Dict[str, Dict] = {}
    for p in PRINCIPLES:
        pkpis = [k for k in kpis if k.principle == p]
        sw = [(compute_kpi_score(k), k.weight) for k in pkpis]
        score = weighted_average(sw) if sw else 0.0
        result[p] = {"score": score, "kpi_count": len(pkpis)}
    return result


def compute_overall_compliance(kpis: List[UNGCKPI]) -> Dict[str, float]:
    """Toplam uyum skoru ve ilke skorlarını döner"""
    by_p = compute_principle_compliance(kpis)
    sw = [(v["score"], 1.0) for v in by_p.values()]  # ilke başına eşit ağırlık
    overall = weighted_average(sw) if sw else 0.0
    scores = {f"{p}_score": v["score"] for p, v in by_p.items()}
    scores["overall_score"] = overall
    return scores
