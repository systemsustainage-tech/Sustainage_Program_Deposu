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

class CloudStorageManager:
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

    def __init__(self, cloud_root: str = None) -> None:
        self.connections = {}
        # Gerçek cloud aktif değilse yerel simülasyon kullan
        self.enabled = True 
        if cloud_root:
            self.cloud_root = cloud_root
        else:
            # Varsayılan olarak backend/data/cloud_storage altında
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.cloud_root = os.path.join(base_dir, '..', '..', 'data', 'cloud_storage')
        
        os.makedirs(self.cloud_root, exist_ok=True)

    def upload_file(self, file_path: str, provider: str = "local_cloud", 
                   remote_folder: str = "Backups") -> bool:
        """
        Dosyayı cloud'a (veya simülasyonuna) yükle
        
        Args:
            file_path: Yüklenecek dosya yolu
            provider: Sağlayıcı (local_cloud, google_drive, etc.)
            remote_folder: Hedef klasör
        """
        if not os.path.exists(file_path):
            logging.error(f"[HATA] Dosya bulunamadı: {file_path}")
            return False

        if provider == "local_cloud":
            return self._upload_local(file_path, remote_folder)
        else:
            logging.warning(f"[INFO] {provider} henüz aktif değil, local_cloud kullanılıyor.")
            return self._upload_local(file_path, remote_folder)

    def _upload_local(self, file_path: str, remote_folder: str) -> bool:
        """Yerel bulut simülasyonuna yükleme"""
        try:
            target_dir = os.path.join(self.cloud_root, remote_folder)
            os.makedirs(target_dir, exist_ok=True)
            
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_dir, filename)
            
            shutil.copy2(file_path, target_path)
            logging.info(f"[OK] Cloud Upload (Local): {target_path}")
            return True
        except Exception as e:
            logging.error(f"[HATA] Cloud Upload (Local) hatası: {e}")
            return False

    def list_files(self, provider: str = "local_cloud", remote_folder: str = "Backups") -> list:
        """Cloud dosyalarını listele"""
        if provider == "local_cloud":
            target_dir = os.path.join(self.cloud_root, remote_folder)
            if os.path.exists(target_dir):
                return os.listdir(target_dir)
            return []
        return []

    # Geriye uyumluluk için alias
    def upload_report_to_cloud(self, provider: str, report_path: str,
                               folder_name: str = "SUSTAINAGE_Reports") -> bool:
        return self.upload_file(report_path, provider, folder_name)
