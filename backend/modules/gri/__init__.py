# -*- coding: utf-8 -*-
"""
GRI Modülü
Global Reporting Initiative Standards
"""

from modules.gri.gri_manager import GRIManager

try:
    from modules.gri.gri_gui import GRIGUI
except ImportError:
    GRIGUI = None

__all__ = ['GRIManager', 'GRIGUI']
