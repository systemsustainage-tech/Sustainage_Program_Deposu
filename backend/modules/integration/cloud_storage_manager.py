#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Storage Yönetimi - TAM ALTYAPI
Google Drive, OneDrive, Dropbox entegrasyonu (Simüle Edilmiş)
"""

import logging
import os
import shutil
from typing import Dict, Optional

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
    except ImportError:
        import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager

class CloudStorageManager(BaseTenantManager):
    """Cloud storage yönetimi"""

    SUPPORTED_PROVIDERS = {
        "local_cloud": {
            "name": "Local Cloud Simulation",
            "icon": "☁️",
            "auth_type": "None"
        },
        "google_drive": {
            "name": "Google Drive",
            "icon": "▶️",
            "auth_type": "OAuth2"
        },
        "onedrive": {
            "name": "Microsoft OneDrive",
            "icon": "☁️",
            "auth_type": "OAuth2"
        },
        "dropbox": {
            "name": "Dropbox",
            "icon": "📦",
            "auth_type": "OAuth2"
        }
    }

    def __init__(self, db_path: str = None, cloud_root: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self.connections = {}
        self.enabled = True 
        
        if cloud_root:
            self.cloud_root = cloud_root
        else:
            # Varsayılan olarak backend/data/cloud_storage altında
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.cloud_root = os.path.join(base_dir, '..', '..', 'data', 'cloud_storage')
        
        # Ensure directory exists
        os.makedirs(self.cloud_root, exist_ok=True)
