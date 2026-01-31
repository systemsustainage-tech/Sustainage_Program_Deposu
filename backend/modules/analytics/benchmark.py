#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sector Benchmark Dataset
- CSV veri yükleme ve metrik standardizasyonu
- Basit sektör bazlı özet istatistikler
"""

import csv
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class BenchmarkRow:
    company: str
    sector: str
    metrics: Dict[str, Any]


class BenchmarkDataset:
    def __init__(self):
        self.rows: List[BenchmarkRow] = []

    def load_csv(self, path: str) -> int:
        count = 0
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                company = r.get('company', 'unknown')
                sector = r.get('sector', 'unknown')
                metrics = {k: _to_number(r.get(k)) for k in r.keys() if k not in ['company', 'sector']}
                self.rows.append(BenchmarkRow(company=company, sector=sector, metrics=metrics))
                count += 1
        return count

    def standardize_metrics(self, mapping: Dict[str, str]) -> None:
        """Örn: {'renewable_pct': 'renewable_energy_pct'}"""
        for row in self.rows:
            for src, dst in mapping.items():
                if src in row.metrics and dst not in row.metrics:
                    row.metrics[dst] = row.metrics[src]

    def sector_stats(self, metric: str) -> Dict[str, Dict[str, float]]:
        """Sektör bazlı min/avg/max döner"""
        buckets: Dict[str, List[float]] = {}
        for row in self.rows:
            val = row.metrics.get(metric)
            if isinstance(val, (int, float)):
                buckets.setdefault(row.sector, []).append(float(val))
        stats: Dict[str, Dict[str, float]] = {}
        for sec, values in buckets.items():
            if not values:
                continue
            avg = sum(values) / len(values)
            stats[sec] = {
                'min': min(values),
                'avg': round(avg, 3),
                'max': max(values),
                'count': float(len(values)),
            }
        return stats


def _to_number(x: Any) -> Any:
    try:
        if x is None:
            return None
        s = str(x).strip()
        if s == '':
            return None
        return float(s)
    except Exception:
        return None
