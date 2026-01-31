#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gizli Saklama Katmanı (Secret Store)
- Windows'ta DPAPI ile şifrelenmiş içerik
- Varsayılan yol: %APPDATA%/SDG/secrets.json (Windows) veya ~/.sdg/secrets.json (diğer)

Not: İçerik base64-url ile kodlanmış DPAPI çıktısı olarak saklanır.
"""
from __future__ import annotations

import logging
import json
import os
from typing import Any, Dict, Optional

try:
    # Yerel DPAPI yardımcıları
    from .crypto import protect_str, unprotect_str
except Exception:
    # Modül konumu farklıysa üst seviyeden içe aktar
    from yonetim.security.core.crypto import protect_str, unprotect_str


def _default_secrets_path() -> str:
    if os.name == 'nt':
        appdata = os.getenv('APPDATA') or os.path.expanduser('~')
        base = os.path.join(appdata, 'SDG')
    else:
        base = os.path.join(os.path.expanduser('~'), '.sdg')
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, 'secrets.json')


class SecretStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or _default_secrets_path()
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            else:
                self._data = {"service_accounts": {}}
        except Exception:
            self._data = {"service_accounts": {}}

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            # Sessiz geç; üst katman isterse raporlar
            logging.error(f'Silent error in secret_store.py: {str(e)}')

    # ---- Servis Hesabı JSON ----
    def store_service_account_json(self, identifier: str, json_content: str) -> bool:
        try:
            enc = protect_str(json_content)
            self._data.setdefault('service_accounts', {})[identifier] = enc
            self._save()
            return True
        except Exception:
            return False

    def import_service_account_file(self, identifier: str, file_path: str) -> bool:
        try:
            if not file_path or not os.path.exists(file_path):
                return False
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.store_service_account_json(identifier, content)
        except Exception:
            return False

    def load_service_account_info(self, identifier: str) -> Optional[Dict[str, Any]]:
        try:
            enc = self._data.get('service_accounts', {}).get(identifier)
            if not enc:
                return None
            plain = unprotect_str(enc)
            return json.loads(plain)
        except Exception:
            return None


# Kolay erişim yardımcıları
_store: Optional[SecretStore] = None

def get_store() -> SecretStore:
    global _store
    if _store is None:
        _store = SecretStore()
    return _store

def save_service_account(identifier: str, json_path: str) -> bool:
    return get_store().import_service_account_file(identifier, json_path)

def load_service_account(identifier: str) -> Optional[Dict[str, Any]]:
    return get_store().load_service_account_info(identifier)
