#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güvenlik Core - Security Modülü
SUSTAINAGE-SDG'den adapte edilmiş güvenlik sistemi
"""

from __future__ import annotations

import json
import time
from typing import List, Optional


def _ensure_audit_table(conn) -> None:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS security_audit_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            username TEXT,
            event TEXT NOT NULL,
            ok INTEGER,
            meta TEXT
        )
    """ )
    conn.commit()

def audit_event(conn, event: str, username: Optional[str], ok: Optional[bool], meta: dict|None=None) -> None:
    _ensure_audit_table(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO security_audit_logs(ts, username, event, ok, meta) VALUES (?,?,?,?,?)",
        (int(time.time()), username, event, None if ok is None else (1 if ok else 0), json.dumps(meta or {}))
    )
    conn.commit()

def _count_events(conn, username: Optional[str], events: List[str], since_ts: int) -> int:
    _ensure_audit_table(conn)
    cur = conn.cursor()
    if username is None:
        cur.execute(
            f"SELECT COUNT(1) FROM security_audit_logs WHERE ts>? AND event IN ({','.join('?'*len(events))})",
            (since_ts, *events)
        )
    else:
        cur.execute(
            f"SELECT COUNT(1) FROM security_audit_logs WHERE username=? AND ts>? AND event IN ({','.join('?'*len(events))})",
            (username, since_ts, *events)
        )
    row = cur.fetchone()
    return int(row[0] if row and row[0] is not None else 0)

def check_lockout(conn, username: str, max_fail: int=5, window_sec: int=600) -> tuple[bool,int]:
    now = int(time.time())
    since = now - window_sec
    # Count recent failures
    fails = _count_events(conn, username, ["login_fail"], since)
    if fails >= max_fail:
        # last fail
        cur = conn.cursor()
        cur.execute("SELECT MAX(ts) FROM security_audit_logs WHERE username=? AND event=?", (username, "login_fail"))
        row = cur.fetchone()
        last_ts = int(row[0] or 0)
        remain = max(0, (last_ts + window_sec) - now)
        return True, remain
    return False, 0

_FAMILIES = {
    "login": ["login_success","login_fail"],
    "totp": ["totp_ok","totp_fail"],
    "backup": ["backup_ok","backup_fail"],
}

def check_rate_limit(conn, username: Optional[str], family: str, window_sec: int, max_times: int) -> tuple[bool,int]:
    now = int(time.time())
    since = now - window_sec
    events = _FAMILIES.get(family, [family])
    cnt = _count_events(conn, username, events, since)
    if cnt >= max_times:
        cur = conn.cursor()
        if username is None:
            cur.execute("SELECT MIN(ts) FROM security_audit_logs WHERE ts>? AND event IN ({})".format(",".join("?"*len(events))), (since, *events))
        else:
            cur.execute("SELECT MIN(ts) FROM security_audit_logs WHERE username=? AND ts>? AND event IN ({})".format(",".join("?"*len(events))), (username, since, *events))
        row = cur.fetchone()
        oldest = int(row[0] or now)
        retry = max(0, window_sec - (now - oldest))
        return False, retry
    return True, 0

def get_security_stats(conn) -> dict:
    """Güvenlik istatistiklerini getir"""
    cur = conn.cursor()

    # Son 24 saatteki login denemeleri
    since_24h = int(time.time()) - 86400
    cur.execute("SELECT COUNT(*) FROM security_audit_logs WHERE ts>? AND event=?", (since_24h, "login_success"))
    successful_logins = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM security_audit_logs WHERE ts>? AND event=?", (since_24h, "login_fail"))
    failed_logins = cur.fetchone()[0] or 0

    # Aktif kullanıcı sayısı
    cur.execute("SELECT COUNT(*) FROM users WHERE is_active=1 AND last_login>?", (since_24h,))
    active_users = cur.fetchone()[0] or 0

    # 2FA aktif kullanıcı sayısı
    cur.execute("SELECT COUNT(*) FROM users WHERE is_active=1 AND totp_enabled=1")
    totp_users = cur.fetchone()[0] or 0

    return {
        'successful_logins_24h': successful_logins,
        'failed_logins_24h': failed_logins,
        'active_users_24h': active_users,
        'totp_enabled_users': totp_users,
        'security_score': min(100, max(0, 100 - (failed_logins * 2)))
    }

def get_recent_security_events(conn, limit: int = 50) -> List[dict]:
    """Son güvenlik olaylarını getir"""
    cur = conn.cursor()
    cur.execute("""
        SELECT ts, username, event, ok, meta
        FROM security_audit_logs
        ORDER BY ts DESC
        LIMIT ?
    """, (limit,))

    events = []
    for row in cur.fetchall():
        try:
            meta = json.loads(row[4]) if row[4] else {}
        except Exception:
            meta = {}

        events.append({
            'timestamp': row[0],
            'username': row[1],
            'event': row[2],
            'success': bool(row[3]) if row[3] is not None else None,
            'meta': meta
        })

    return events
