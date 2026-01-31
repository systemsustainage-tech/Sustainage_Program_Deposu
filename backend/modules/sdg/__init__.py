# -*- coding: utf-8 -*-
"""
SDG Modülü
Sustainable Development Goals (Sürdürülebilir Kalkınma Amaçları)
"""

try:
    from .sdg_gui import SDGGUI
    from .sdg_manager import SDGManager
    __all__ = ['SDGManager', 'SDGGUI']
except ImportError:
    # Fallback for when running in environments where relative imports fail or GUI is not available
    try:
        from backend.modules.sdg.sdg_manager import SDGManager
        __all__ = ['SDGManager']
    except ImportError:
        pass
