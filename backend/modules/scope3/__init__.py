#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scope 3 Kategorileri Modülü
GHG Protocol Scope 3 kategorileri için kapsamlı yönetim sistemi
"""

from .scope3_gui import Scope3GUI
from .scope3_manager import Scope3Manager

__all__ = ['Scope3Manager', 'Scope3GUI']
