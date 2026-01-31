#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESRS (European Sustainability Reporting Standards) Module"""

import logging
__version__ = "1.0.0"
__author__ = "SUSTAINAGE SDG Team"

try:
    from .esrs_gui import ESRSGUI
    from .esrs_module import ESRSModule
    __all__ = ['ESRSModule', 'ESRSGUI']
except ImportError as e:
    logging.error(f"[UYARI] ESRS modulu yukleme hatasi: {e}")
    ESRSModule = None
    ESRSGUI = None
    __all__ = []

