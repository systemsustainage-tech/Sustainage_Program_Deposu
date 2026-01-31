#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalite Validasyon ve Anomali Skoru Modülü
- Modüller arası tutarlılık kontrolleri
- Basit anomali tespiti (z-skor benzeri yaklaşım)
"""

from typing import Dict, List


def check_consistency(company_id: int, year: int, managers: Dict[str, object]) -> Dict[str, List[str]]:
    """
    Basit tutarlılık kontrolleri:
    - TCFD metrics ile ESG/ISSB metriklerinin bulunurluğu
    - Governance verisinin varlığı
    Returns: { module: [warnings] }
    """
    warnings: Dict[str, List[str]] = {}
    # TCFD
    tcfd = managers.get('tcfd')
    if tcfd:
        m = tcfd.get_metrics(company_id, year)
        g = tcfd.get_governance(company_id, year)
        if not m:
            warnings.setdefault('tcfd', []).append('Metrics bulunamadı.')
        if not g:
            warnings.setdefault('tcfd', []).append('Governance bulunamadı.')
    # Diğer modüller için yer tutucu
    return warnings


def zscore(values: List[float]) -> List[float]:
    if not values:
        return []
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = var ** 0.5
    if std == 0:
        return [0.0 for _ in values]
    return [(v - mean) / std for v in values]


def detect_anomalies(series: List[float], threshold: float = 2.5) -> List[int]:
    """Basit z-skor tabanlı anomali tespiti: eşik üstü indeksleri döner"""
    zs = zscore(series)
    return [i for i, z in enumerate(zs) if abs(z) >= threshold]
