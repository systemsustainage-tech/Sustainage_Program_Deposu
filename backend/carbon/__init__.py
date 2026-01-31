#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARBON HESAPLAMA MODÜLÜ
GHG Protocol uyumlu Scope 1, 2, 3 emisyon hesaplama ve raporlama
+ Karbon Offset/Kredilendirme Sistemi (v1.1.0)
+ ISO 14064-1:2018 Uyumluluk (v1.2.0)
"""

from .carbon_calculator import CarbonCalculator
from .carbon_manager import CarbonManager
from .emission_factors import EmissionFactors
from .iso14064_compliance import ISO14064Compliance
from .iso14064_reporting import ISO14064Reporter
from .offset_calculator import OffsetCalculator
from .offset_manager import OffsetManager

__version__ = "1.2.0"
__all__ = [
    "CarbonManager",
    "CarbonCalculator",
    "EmissionFactors",
    "OffsetManager",           # v1.1: Offset yönetimi
    "OffsetCalculator",        # v1.1: Net emisyon hesaplama
    "ISO14064Compliance",      # v1.2: ISO uyumluluk
    "ISO14064Reporter"         # v1.2: ISO rapor oluşturucu
]

