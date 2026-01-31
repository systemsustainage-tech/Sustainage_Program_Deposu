#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güvenlik Core - Destek Oturumu (Break-Glass)
- Vendor imzalı, süreli ve tek kullanımlık token doğrulama (Ed25519)
- Zorunlu 2FA doğrulaması
- Başlat/Sonlandır API’leri ve audit kayıtları
"""
from __future__ import annotations

import logging
import base64
import json
import time
from typing import Any, Dict, Optional

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import \
        Ed25519PublicKey
except Exception:
    Ed25519PublicKey = None

# Vendor genel anahtar (örnek). Üretimde dışa ayırın.
VENDOR_PUBLIC_KEY_PEM = """
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA9dSwIPfI3DukbUtCuQ9wl2+dnOxdjY0tSYluXWMYjdw=
-----END PUBLIC KEY-----
"""

SETTINGS_SESSION_KEY = "support_session_state"
SETTINGS_USED_JTI = "support_used_jtis"

def _load_public_key() -> Optional[Ed25519PublicKey]:
    try:
        return serialization.load_pem_public_key(VENDOR_PUBLIC_KEY_PEM.encode())
    except Exception:
        return None

def _is_ed25519_token(token: str) -> bool:
    parts = (token or "").split(".")
    return len(parts) == 2

def _b64url_decode(s: str) -> bytes:
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + padding)

def _verify_signature(token: str) -> bool:
    try:
        parts = token.split(".")
        payload_b64, signature_b64 = parts[0], parts[1]
        payload = _b64url_decode(payload_b64)
        signature = _b64url_decode(signature_b64)
        pk = _load_public_key()
        if pk is None:
            return False
        pk.verify(signature, payload)
        return True
    except Exception:
        return False

def _decode_payload(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload_b64 = token.split(".")[0]
        payload_bytes = _b64url_decode(payload_b64)
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

def _get_setting(conn, key: str, default: str="") -> str:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS system_settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    cur.execute("SELECT value FROM system_settings WHERE key=?", (key,))
    r = cur.fetchone()
    return r[0] if r else default

def _set_setting(conn, key: str, value: str) -> None:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS system_settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    cur.execute(
        "INSERT INTO system_settings(key, value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value)
    )
    conn.commit()

def verify_support_token(token: str) -> Dict:
    """Vendor imzalı destek tokenını doğrula.
    Beklenen payload alanları: exp (epoch), jti (benzersiz), scope (örn. admin_full)
    """
    if not token:
        return {"ok": False, "reason": "empty"}
    if not _is_ed25519_token(token):
        return {"ok": False, "reason": "format"}
    if not _verify_signature(token):
        return {"ok": False, "reason": "signature"}
    payload = _decode_payload(token)
    if not payload:
        return {"ok": False, "reason": "payload"}
    exp = int(payload.get("exp", 0) or 0)
    now = int(time.time())
    if exp and exp < now:
        return {"ok": False, "reason": "expired", "exp": exp}
    jti = (payload.get("jti") or "").strip()
    scope = (payload.get("scope") or "").strip()
    if not jti or not scope:
        return {"ok": False, "reason": "claims"}
    return {"ok": True, "claims": {"exp": exp, "jti": jti, "scope": scope}}

def _get_user(conn, username: str) -> None:
    cur = conn.cursor()
    cur.execute("SELECT id, is_admin, is_superadmin, is_active, totp_secret, totp_enabled FROM users WHERE username=?", (username,))
    return cur.fetchone()

def _verify_totp(secret: str, code: str) -> bool:
    try:
        import pyotp
        return pyotp.TOTP(secret).verify(code)
    except Exception:
        return False

def start_support_session(conn, actor_username: str, token: str, totp_code: str) -> Dict:
    """Destek oturumunu başlat.
    - Actor admin/super olmalı ve aktif olmalı
    - Actor için 2FA etkin olmalı ve kod doğrulanmalı
    - Token imzası ve exp/jti/scope doğrulanmalı
    - jti tek kullanımlık olarak işaretlenmeli
    - Durum system_settings içinde kaydedilmeli
    - Audit kaydı yazılmalı
    """
    # Actor kontrol
    row = _get_user(conn, actor_username)
    if not row:
        return {"ok": False, "reason": "actor_not_found"}
    user_id, is_admin, is_super, is_active, totp_secret, totp_enabled = row
    if int(is_active) != 1:
        return {"ok": False, "reason": "inactive"}
    if not (int(is_admin) == 1 or int(is_super) == 1):
        return {"ok": False, "reason": "forbidden"}
    if int(totp_enabled) != 1 or not totp_secret:
        return {"ok": False, "reason": "2fa_required"}
    if not totp_code or not _verify_totp(totp_secret, totp_code):
        return {"ok": False, "reason": "2fa_invalid"}

    # Token doğrulama
    if not _is_ed25519_token(token) or not _verify_signature(token):
        return {"ok": False, "reason": "token_invalid"}
    claims = _decode_payload(token) or {}
    exp = int(claims.get("exp", 0) or 0)
    now = int(time.time())
    if exp and exp < now:
        return {"ok": False, "reason": "token_expired"}
    jti = (claims.get("jti") or "").strip()
    scope = (claims.get("scope") or "").strip()
    if not jti or not scope:
        return {"ok": False, "reason": "token_claims"}

    # Tek kullanımlık jti kontrolü
    used_raw = _get_setting(conn, SETTINGS_USED_JTI, "")
    try:
        used = json.loads(used_raw) if used_raw else []
    except Exception:
        used = []
    if jti in used:
        return {"ok": False, "reason": "token_used"}

    # Durum ve jti kaydı
    state = {
        "active": True,
        "actor": actor_username,
        "started_at": now,
        "exp": exp,
        "jti": jti,
        "scope": scope
    }
    _set_setting(conn, SETTINGS_SESSION_KEY, json.dumps(state))
    used.append(jti)
    _set_setting(conn, SETTINGS_USED_JTI, json.dumps(used))

    # Audit
    try:
        from .audit import audit_security_event
        audit_security_event(conn, actor_username, "support_session_start", {"jti": jti, "scope": scope, "exp": exp})
    except Exception as e:
        logging.error(f'Silent error in support_session.py: {str(e)}')
    return {"ok": True, "state": state}

def stop_support_session(conn, actor_username: str) -> Dict:
    """Aktif destek oturumunu sonlandır ve audit kaydı yaz."""
    raw = _get_setting(conn, SETTINGS_SESSION_KEY, "")
    try:
        curr = json.loads(raw) if raw else {}
    except Exception:
        curr = {}
    _set_setting(conn, SETTINGS_SESSION_KEY, json.dumps({"active": False}))
    try:
        from .audit import audit_security_event
        audit_security_event(conn, actor_username, "support_session_stop", {"prev": curr})
    except Exception as e:
        logging.error(f'Silent error in support_session.py: {str(e)}')
    return {"ok": True}

def get_support_session_state(conn) -> Dict:
    raw = _get_setting(conn, SETTINGS_SESSION_KEY, "")
    try:
        state = json.loads(raw) if raw else {}
    except Exception:
        state = {}
    now = int(time.time())
    if state.get("active") and state.get("exp") and int(state["exp"]) < now:
        # Süre dolmuşsa otomatik kapat
        _set_setting(conn, SETTINGS_SESSION_KEY, json.dumps({"active": False}))
        state["active"] = False
    return state or {"active": False}
