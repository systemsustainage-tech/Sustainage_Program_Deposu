#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SU YÖNETİMİ MODÜLÜ
ISO 14046 ve Water Footprint Network standartlarına uygun su ayak izi yönetimi
"""

__version__ = "1.0.0"
__author__ = "SUSTAINAGE Team"
__description__ = "Su yönetimi modülü - Su ayak izi, tüketim takibi ve verimlilik analizi"

from .water_calculator import WaterCalculator
from .water_factors import WaterFactors
from .water_gui import WaterGUI
from .water_manager import WaterManager
from .water_reporting import WaterReporting

__all__ = [
    'WaterManager',
    'WaterCalculator',
    'WaterFactors',
    'WaterReporting',
    'WaterGUI'
]
