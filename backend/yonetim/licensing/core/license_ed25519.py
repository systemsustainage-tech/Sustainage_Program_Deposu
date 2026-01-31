#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
"""
Lisanslama Core - Ed25519 License Modülü
SUSTAINAGE-SDG'den adapte edilmiş Ed25519 lisans sistemi
"""

import base64
import json
import os
import sys
import time
import hashlib
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from yonetim.security.core.audit import audit_license_change
from yonetim.security.core.crypto import protect_str, unprotect_str
from yonetim.security.core.hw import hwid_full_core

# Uygulamaya gömülü genel anahtar (public key)
# Bu anahtarı license_generator.py ile oluşturulan public key ile değiştirin
EMBEDDED_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAd+IHPrONBCWibzEuurm+G1A7lggl78EdT24zRlLZI+o=
-----END PUBLIC KEY-----
"""

SETTINGS_KEY = "license_key_enc"
SETTINGS_TOL = "tolerance_mac_ok"
SETTINGS_LAST_CHECK = "license_last_check"
SETTINGS_USE_COUNT = "license_use_count"
SETTINGS_REQUIRE_FULL = "license_require_full"
SETTINGS_INTEGRITY_PATHS = "license_integrity_paths"
SETTINGS_INTEGRITY_HASHES = "license_integrity_hashes"
SETTINGS_ONLINE_REQUIRED = "license_online_required"
SETTINGS_SERVER_URL = "license_server_url"

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

def _inc_usage(conn) -> None:
    try:
        cur = conn.cursor()
        cur.execute("SELECT value FROM system_settings WHERE key=?", (SETTINGS_USE_COUNT,))
        r = cur.fetchone()
        n = int((r[0] or "0")) if r else 0
        n += 1
        _set_setting(conn, SETTINGS_USE_COUNT, str(n))
        _set_setting(conn, SETTINGS_LAST_CHECK, str(int(time.time())))
    except Exception as e:
        logging.error(f'Silent error in license_ed25519.py: {str(e)}')

def _hash_file(path: str) -> str:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                b = f.read(8192)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return ""

def verify_integrity(conn) -> bool:
    try:
        paths_json = _get_setting(conn, SETTINGS_INTEGRITY_PATHS, "[]")
        hashes_json = _get_setting(conn, SETTINGS_INTEGRITY_HASHES, "{}")
        paths = []
        hashes = {}
        try:
            paths = json.loads(paths_json)
        except Exception:
            paths = []
        try:
            hashes = json.loads(hashes_json)
        except Exception:
            hashes = {}
        if not paths or not hashes:
            return True
        for p in paths:
            expected = hashes.get(p)
            if not expected:
                continue
            actual = _hash_file(p)
            if not actual or actual != expected:
                return False
        return True
    except Exception:
        return True

def online_validate(conn, license_key: str, hw_core: str, hw_full: str) -> bool:
    try:
        url = _get_setting(conn, SETTINGS_SERVER_URL, "")
        if not url:
            return True
        data = json.dumps({
            "license": hashlib.sha256((license_key or "").encode()).hexdigest(),
            "hw_core": hw_core or "",
            "hw_full": hw_full or "",
            "ts": int(time.time())
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=3) as resp:
            code = resp.getcode()
            if code != 200:
                return False
            body = resp.read()
            try:
                obj = json.loads(body.decode("utf-8"))
                return bool(obj.get("ok", False))
            except Exception:
                return False
    except urllib.error.URLError:
        return False
    except Exception:
        return False

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
        logging.error(f'Silent error in license_ed25519.py: {str(e)}')
    enc = protect_str(new_plain or "")
    _set_setting(conn, SETTINGS_KEY, enc)
    audit_license_change(conn, actor, old_plain, new_plain)

def _is_valid_license_format(license_key: str) -> bool:
    """Lisans anahtarının formatını kontrol eder."""
    parts = (license_key or "").split(".")
    if len(parts) != 2:  # payload.signature formatı
        return False
    try:
        # Base64URL formatını kontrol et
        for part in parts:
            # Padding ekleyerek decode et
            padding = "=" * ((4 - len(part) % 4) % 4)
            base64.urlsafe_b64decode(part + padding)
        return True
    except Exception:
        return False

def _decode_payload(license_key: str) -> Optional[Dict[str, Any]]:
    """Lisans anahtarından payload kısmını çıkarır ve decode eder."""
    try:
        parts = license_key.split(".")
        if len(parts) != 2:
            return None

        # Base64URL decode
        payload_b64 = parts[0]
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)

        # JSON parse
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

def _verify_signature(license_key: str) -> bool:
    """Ed25519 imzasını doğrular."""
    try:
        parts = license_key.split(".")
        if len(parts) != 2:
            return False

        payload_b64, signature_b64 = parts

        # Payload'ı decode et
        padding_payload = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding_payload)

        # İmzayı decode et
        padding_sig = "=" * ((4 - len(signature_b64) % 4) % 4)
        signature = base64.urlsafe_b64decode(signature_b64 + padding_sig)

        # Genel anahtarı yükle
        from cryptography.hazmat.primitives import serialization
        public_key = serialization.load_pem_public_key(EMBEDDED_PUBLIC_KEY.encode())

        # İmzayı doğrula
        public_key.verify(signature, payload_bytes)
        return True
    except Exception:
        return False

def verify_token(token: str, tolerance_mac_ok: bool) -> Dict:
    """
    Lisans anahtarını doğrular.
    
    Dönen state: valid / tolerated / expired / invalid / none
    Ek alanlar: reason, exp, bound, now
    """
    if not token:
        return {"state": "none"}

    if not _is_valid_license_format(token):
        return {"state": "invalid", "reason": "format"}

    # İmzayı doğrula
    if not _verify_signature(token):
        return {"state": "invalid", "reason": "signature"}

    # Payload'ı decode et
    payload = _decode_payload(token)
    if not payload:
        return {"state": "invalid", "reason": "payload"}

    # HW bilgisi
    hw, hw_full, hw_core = hwid_full_core()

    # Geçerlilik süresini kontrol et
    exp = int(payload.get("exp", 0))
    now = int(time.time())
    if exp and exp < now:
        return {"state": "expired", "reason": "exp", "exp": exp, "now": now}

    # Donanım kimliğini kontrol et
    token_core = payload.get("hwid_core", "")
    token_full = payload.get("hwid_full", "")

    def _eq(a: str, b: str) -> bool:
        return (a or "").strip().lower() == (b or "").strip().lower()

    # Tam donanım kimliği kontrolü
    if token_full and _eq(token_full, hw_full):
        return {
            "state": "valid",
            "exp": exp,
            "bound": "full",
            "edition": payload.get("edition", "CORE"),
            "max_users": payload.get("max_users", 0),
            "note": payload.get("note", ""),
            "mode": payload.get("mode", "")
        }

    # Temel donanım kimliği kontrolü
    if token_core and _eq(token_core, hw_core):
        # MAC toleransı etkinse veya tam kimlik kontrolü yoksa
        if tolerance_mac_ok or not token_full:
            return {
                "state": "tolerated" if token_full else "valid",
                "exp": exp,
                "bound": "core",
                "edition": payload.get("edition", "CORE"),
                "max_users": payload.get("max_users", 0),
                "note": payload.get("note", ""),
                "mode": payload.get("mode", "")
            }

    return {"state": "invalid", "reason": "hwid"}

def apply_hardening(conn) -> Dict:
    """Test lisansı doğrulanınca gerçek güvenlik sertleştirmesini uygula"""
    changed = {}
    try:
        # Integrity baseline: kritik dosyalar
        base = os.path.abspath(os.getcwd())
        critical = [
            os.path.join(base, 'main.py'),
            os.path.join(base, 'yonetim', 'licensing', 'core', 'license_ed25519.py'),
        ]
        hashes = {}
        for p in critical:
            h = _hash_file(p)
            if h:
                hashes[p] = h
        if hashes:
            _set_setting(conn, SETTINGS_INTEGRITY_PATHS, json.dumps(critical))
            _set_setting(conn, SETTINGS_INTEGRITY_HASHES, json.dumps(hashes))
            changed['integrity'] = True
        # Require full binding
        _set_setting(conn, SETTINGS_REQUIRE_FULL, '1')
        changed['require_full'] = True
        # Online required only if server URL configured
        url = _get_setting(conn, SETTINGS_SERVER_URL, '')
        if url:
            _set_setting(conn, SETTINGS_ONLINE_REQUIRED, '1')
            changed['online_required'] = True
        else:
            changed['online_required'] = False
    except Exception as e:
        logging.error(f'Silent error in license_ed25519.py: {str(e)}')
    return changed

def get_license_info(conn) -> Dict:
    """Lisans bilgilerini getir (Ed25519)"""
    license_key = load_license_key(conn)
    tolerance_mac_ok = _get_setting(conn, SETTINGS_TOL, "0") == "1"
    require_full = _get_setting(conn, SETTINGS_REQUIRE_FULL, "0") == "1"

    if not license_key:
        return {"state": "none", "message": "Lisans anahtarı bulunamadı"}

    verification = verify_token(license_key, tolerance_mac_ok)
    if verification.get("state") in ("valid", "tolerated"):
        if require_full and verification.get("bound") == "core":
            verification = {"state": "invalid", "reason": "policy_full_required"}
        else:
            _inc_usage(conn)
            ok_integrity = verify_integrity(conn)
            if not ok_integrity:
                verification = {"state": "invalid", "reason": "integrity"}
            else:
                must_online = _get_setting(conn, SETTINGS_ONLINE_REQUIRED, "0") == "1"
                if must_online:
                    hw = hwid_full_core()
                    if not online_validate(conn, license_key, hw[2], hw[1]):
                        verification = {"state": "invalid", "reason": "online"}

    # Hardware bilgilerini ekle
    hw_info = hwid_full_core()
    verification.update({
        "hwid_core": hw_info[2],
        "hwid_full": hw_info[1],
        "tolerance_enabled": tolerance_mac_ok
    })

    return verification

def activate_license(conn, license_key: str, actor: str = "system") -> Dict:
    """Lisans anahtarını aktifleştir (Ed25519)"""
    try:
        # Lisans anahtarını doğrula
        verification = verify_token(license_key, False)
        require_full = _get_setting(conn, SETTINGS_REQUIRE_FULL, "0") == "1"

        if verification["state"] in ["valid", "tolerated"]:
            if require_full and verification.get("bound") == "core":
                return {
                    "ok": False,
                    "message": "Tam donanım bağlama gerekli",
                    "verification": verification
                }
            # Lisans anahtarını kaydet
            save_license_key(conn, actor, license_key)

            # Tolerans ayarını güncelle
            if verification["state"] == "tolerated":
                _set_setting(conn, SETTINGS_TOL, "1")
            _inc_usage(conn)
            # Test lisansı ise sertleştirme uygula
            if (verification.get('mode') or '').lower() == 'test':
                changes = apply_hardening(conn)
                return {
                    "ok": True,
                    "message": "Lisans aktifleştirildi ve güvenlik sertleştirmesi uygulandı",
                    "license_info": get_license_info(conn),
                    "hardening": changes
                }
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