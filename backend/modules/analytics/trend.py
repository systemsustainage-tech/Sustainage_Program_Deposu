#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trend ve Tahmin Modelleri
- Hareketli ortalama
- Basit üstel düzeltme
- Naif tahmin ve what-if analiz fonksiyonları
"""

from typing import List


def moving_average(series: List[float], window: int = 3) -> List[float]:
    if window <= 0:
        raise ValueError('window must be > 0')
    out: List[float] = []
    for i in range(len(series)):
        start = max(0, i - window + 1)
        chunk = series[start:i+1]
        out.append(sum(chunk) / len(chunk))
    return out


def exponential_smoothing(series: List[float], alpha: float = 0.3) -> List[float]:
    if not 0 < alpha <= 1:
        raise ValueError('alpha must be in (0,1]')
    out: List[float] = []
    prev = series[0] if series else 0.0
    for x in series:
        smoothed = alpha * x + (1 - alpha) * prev
        out.append(smoothed)
        prev = smoothed
    return out


def forecast_naive(series: List[float], periods: int = 3) -> List[float]:
    if not series:
        return [0.0] * periods
    return [series[-1]] * periods


def what_if_scale(series: List[float], factor: float) -> List[float]:
    return [x * factor for x in series]
