#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lisanslama Core - License Modülü
SUSTAINAGE-SDG'den adapte edilmiş lisans sistemi
"""
from __future__ import annotations

import logging
import base64
import os
import sys
import time
from typing import Dict

import jwt  # PyJWT

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from yonetim.security.core.audit import audit_license_change
from yonetim.security.core.crypto import protect_str, unprotect_str
from yonetim.security.core.hw import hwid_full_core

# Basit bir örnek gizli anahtar — prod'da dışa alınmalı
APP_JWT_SECRET = "SUSTAINAGE_APP_SECRET_HS256"
JWT_ALGOS = ["HS256"]

SETTINGS_KEY = "license_key_enc"
SETTINGS_TOL = "tolerance_mac_ok"

def _get_setting(conn, key, default="") -> None:
    cur = conn.cursor()
    cur.execute("SELECT value FROM system_settings WHERE key=?", (key,))
    r = cur.fetchone()
    return r[0] if r else default

def _set_setting(conn, key, value) -> None:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO system_settings(key, value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value)
    )
    conn.commit()

def load_license_key(conn) -> str:
    enc = _get_setting(conn, SETTINGS_KEY, "")
    try:
        return unprotect_str(enc) if enc else ""
    except Exception:
        return ""

def save_license_key(conn, actor: str, new_plain: str) -> None:
    old_plain = ""
    try:
        old_plain = load_license_key(conn)
    except Exception as e:
        logging.error(f'Silent error in license.py: {str(e)}')
    enc = protect_str(new_plain or "")
    _set_setting(conn, SETTINGS_KEY, enc)
    audit_license_change(conn, actor, old_plain, new_plain)

def _base64url_like(s: str) -> bool:
    # JWT 3 parça olmalı: header.payload.signature
    parts = (s or "").split(".")
    if len(parts) != 3:
        return False
    try:
        for p in parts[:2]:
            base64.urlsafe_b64decode(p + "===")  # padding tolere
        return True
    except Exception:
        return False

def verify_token(token: str, tolerance_mac_ok: bool) -> Dict:
    """
    Dönen state: valid / tolerated / expired / invalid / none
    Ek alanlar: reason, exp, bound, now
    """
    if not token:
        return {"state": "none"}

    if not _base64url_like(token):
        return {"state": "invalid", "reason": "format"}

    # HW bilgisi
    hw, hw_full, hw_core = hwid_full_core()

    # Token decode ve imza/doğrulama
    try:
        payload = jwt.decode(token, APP_JWT_SECRET, algorithms=JWT_ALGOS)
    except jwt.ExpiredSignatureError:
        return {"state": "expired", "reason": "exp"}
    except Exception:
        return {"state": "invalid", "reason": "signature"}

    # Beklenen alanlar: exp, hw_full veya hw_core, max_users (opsiyonel)
    exp = int(payload.get("exp", 0))
    now = int(time.time())
    if exp and exp < now:
        return {"state": "expired", "reason": "exp", "exp": exp, "now": now}

    bound = payload.get("hw_bind", "core")  # "full" / "core"
    token_full = payload.get("hw_full", "")
    token_core = payload.get("hw_core", "")

    def _eq(a: str, b: str) -> bool:
        return (a or "").strip().lower() == (b or "").strip().lower()

    # Tam bağ veya core bağ kıyası
    if bound == "full":
        if _eq(token_full, hw_full):
            return {"state": "valid", "exp": exp, "bound": "full"}
        # tolerans MAC: MAC değişimi dışında disk+cpu tutuyorsa core kabulü
        if tolerance_mac_ok and _eq(token_core, hw_core):
            return {"state": "tolerated", "exp": exp, "bound": "core"}
        return {"state": "invalid", "reason": "hw_mismatch", "bound": "full"}

    # core bağı
    if _eq(token_core, hw_core):
        return {"state": "valid", "exp": exp, "bound": "core"}

    return {"state": "invalid", "reason": "hw_mismatch", "bound": "core"}

def get_license_info(conn) -> Dict:
    """Lisans bilgilerini getir"""
    license_key = load_license_key(conn)
    tolerance_mac_ok = _get_setting(conn, SETTINGS_TOL, "0") == "1"

    if not license_key:
        return {"state": "none", "message": "Lisans anahtarı bulunamadı"}

    verification = verify_token(license_key, tolerance_mac_ok)

    # Hardware bilgilerini ekle
    hw_info = hwid_full_core()
    verification.update({
        "hwid_core": hw_info[2],
        "hwid_full": hw_info[1],
        "tolerance_enabled": tolerance_mac_ok
    })

    return verification

def activate_license(conn, license_key: str, actor: str = "system") -> Dict:
    """Lisans anahtarını aktifleştir"""
    try:
        # Lisans anahtarını doğrula
        verification = verify_token(license_key, False)

        if verification["state"] in ["valid", "tolerated"]:
            # Lisans anahtarını kaydet
            save_license_key(conn, actor, license_key)

            # Tolerans ayarını güncelle
            if verification["state"] == "tolerated":
                _set_setting(conn, SETTINGS_TOL, "1")

            return {
                "ok": True,
                "message": "Lisans başarıyla aktifleştirildi",
                "license_info": get_license_info(conn)
            }
        else:
            return {
                "ok": False,
                "message": f"Lisans anahtarı geçersiz: {verification.get('reason', 'bilinmeyen hata')}",
                "verification": verification
            }

    except Exception as e:
        return {
            "ok": False,
            "message": f"Lisans aktifleştirme hatası: {str(e)}"
        }

def deactivate_license(conn, actor: str = "system") -> Dict:
    """Lisans anahtarını deaktifleştir"""
    try:
        load_license_key(conn)
        save_license_key(conn, actor, "")
        _set_setting(conn, SETTINGS_TOL, "0")

        return {
            "ok": True,
            "message": "Lisans başarıyla deaktifleştirildi"
        }
    except Exception as e:
        return {
            "ok": False,
            "message": f"Lisans deaktifleştirme hatası: {str(e)}"
        }
