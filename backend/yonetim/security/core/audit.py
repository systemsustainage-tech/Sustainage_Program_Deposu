#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güvenlik Core - Audit Modülü
SUSTAINAGE-SDG'den adapte edilmiş audit sistemi
"""

from __future__ import annotations

import hashlib
import json
import time


def _ensure_table(conn) -> None:
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS security_audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER NOT NULL,
        actor TEXT,
        action TEXT,
        details TEXT
    )
    """)
    conn.commit()

def write_audit(conn, actor: str, action: str, details: dict) -> None:
    _ensure_table(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO security_audit_log(ts, actor, action, details) VALUES(?,?,?,?)",
        (int(time.time()), actor or "-", action, json.dumps(details, ensure_ascii=False))
    )
    conn.commit()

def sha256_hex(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

def audit_license_change(conn, actor: str, old_plain: str, new_plain: str) -> None:
    write_audit(conn, actor, "license_change", {
        "old_hash": sha256_hex(old_plain),
        "new_hash": sha256_hex(new_plain),
    })

def audit_user_action(conn, actor: str, action: str, target_user: str = None, details: dict = None) -> None:
    """Kullanıcı işlemlerini audit et"""
    audit_details = details or {}
    if target_user:
        audit_details["target_user"] = target_user

    write_audit(conn, actor, f"user_{action}", audit_details)

def audit_security_event(conn, actor: str, event: str, details: dict = None) -> None:
    """Güvenlik olaylarını audit et"""
    write_audit(conn, actor, f"security_{event}", details or {})

def get_audit_logs(conn, limit: int = 100, actor: str = None, action: str = None) -> list:
    """Audit loglarını getir"""
    cur = conn.cursor()

    query = "SELECT ts, actor, action, details FROM security_audit_log"
    params = []
    conditions = []

    if actor:
        conditions.append("actor = ?")
        params.append(actor)

    if action:
        conditions.append("action LIKE ?")
        params.append(f"%{action}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY ts DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)

    logs = []
    for row in cur.fetchall():
        try:
            details = json.loads(row[3]) if row[3] else {}
        except Exception:
            details = {}

        logs.append({
            'timestamp': row[0],
            'actor': row[1],
            'action': row[2],
            'details': details
        })

    return logs
