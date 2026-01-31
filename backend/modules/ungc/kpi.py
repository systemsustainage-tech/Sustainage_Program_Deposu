#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC KPI Modulü
- İlke bazlı KPI tanımı
- Basit KPI skoru hesaplama
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UNGCKPI:
    """Bir UNGC KPI kaydı"""
    name: str
    principle: str  # Human Rights, Labour, Environment, Anti-Corruption
    metric_id: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    weight: float = 1.0


def compute_kpi_score(kpi: UNGCKPI) -> float:
    """
    Basit KPI skoru (0-100):
    - Hedef ve mevcut değere göre oranlama
    - Boş veriler için 0
    """
    try:
        if kpi.target_value is None or kpi.current_value is None:
            return 0.0
        if kpi.target_value == 0:
            return 0.0
        ratio = kpi.current_value / kpi.target_value
        # Oranı 0-1 arasında sınırla ve 0-100'e ölçekle
        ratio = max(0.0, min(1.0, ratio))
        return round(ratio * 100.0, 2)
    except Exception:
        return 0.0


def weighted_average(scores_with_weights: list[tuple[float, float]]) -> float:
    """Ağırlıklı ortalama hesapla (scores_with_weights: [(score, weight), ...])"""
    total_w = sum(w for _, w in scores_with_weights) or 0.0
    if total_w == 0:
        return 0.0
    total_s = sum(s * w for s, w in scores_with_weights)
    return round(total_s / total_w, 2)
