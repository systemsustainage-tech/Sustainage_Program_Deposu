# -*- coding: utf-8 -*-
"""
TSRS Modülü
Türkiye Sürdürülebilirlik Raporlama Standartları
"""

from modules.tsrs.tsrs_manager import TSRSManager

try:
    from modules.tsrs.tsrs_gui import TSRSGUI
except ImportError:
    TSRSGUI = None

__all__ = ['TSRSManager', 'TSRSGUI']
