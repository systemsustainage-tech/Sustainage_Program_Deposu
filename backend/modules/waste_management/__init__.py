#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATIK YÖNETİMİ MODÜLÜ
Sürdürülebilir atık yönetimi ve döngüsel ekonomi modülü
"""

__version__ = "1.0.0"
__author__ = "SUSTAINAGE SDG Team"
__description__ = "Atık Yönetimi ve Döngüsel Ekonomi Modülü"

# Modül bileşenleri
from .waste_calculator import WasteCalculator
from .waste_factors import WasteFactors
from .waste_manager import WasteManager
from .waste_reporting import WasteReporting

__all__ = [
    'WasteManager',
    'WasteCalculator',
    'WasteFactors',
    'WasteReporting'
]
