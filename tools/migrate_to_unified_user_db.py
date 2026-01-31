#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Login kullanıcı ve ilgili RBAC verilerini sdg.db'den data/sdg_desktop.sqlite'e taşır.

Özellikler:
- users tablolarını kullanıcı adına göre birleştirir (case-insensitive)
- mevcut alanları dinamik olarak eşler (login_attempts/failed_attempts, last_login/last_login_at, totp_* vb.)
- roller (roles), kullanıcı-rol eşleşmeleri (user_roles) ve yetkiler (permissions) için upsert yapar

Çalıştırma:
  python tools/migrate_to_unified_user_db.py
"""

import logging
import os
import re
import sqlite3
from datetime import datetime
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.getcwd()
SRC_DB = os.path.join(BASE_DIR, 'sdg.db')
DEST_DB = os.path.join(BASE_DIR, 'data', 'sdg_desktop.sqlite')


def fetch_cols(cur, table: str) -> None:
    import re
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table or ""):
        return []
    cur.execute("PRAGMA table_info(" + table + ")")
    return [row[1] for row in cur.fetchall()]


def row_to_dict(cols, row) -> None:
    return {c: row[i] for i, c in enumerate(cols)}


def get_user_by_username(cur, username: str) -> None:
    cur.execute("SELECT id, username FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    return cur.fetchone()


def upsert_user(src_user: dict, dest_cur, dest_cols: list) -> None:
    username = src_user.get('username')
    if not username:
        return False, 'skip_no_username'

    # Mevcut kullanıcı var mı?
    existing = get_user_by_username(dest_cur, username)

    # Kolon eşlemeleri ve dönüştürmeler
    def pick(name) -> None:
        return src_user.get(name)

    attempts_val = None
    if 'failed_attempts' in src_user:
        attempts_val = src_user.get('failed_attempts')
    elif 'login_attempts' in src_user:
        attempts_val = src_user.get('login_attempts')

    last_login_val = None
    if 'last_login' in src_user:
        last_login_val = src_user.get('last_login')
    elif 'last_login_at' in src_user:
        last_login_val = src_user.get('last_login_at')

    fields = {
        'username': pick('username'),
        'email': pick('email'),
        'password_hash': pick('password_hash'),
        'display_name': pick('display_name'),
        'first_name': pick('first_name'),
        'last_name': pick('last_name'),
        'is_active': pick('is_active'),
        'must_change_password': pick('must_change_password'),
        'locked_until': pick('locked_until'),
        'totp_enabled': pick('totp_enabled'),
        'totp_secret': pick('totp_secret'),
        'backup_codes': pick('backup_codes'),
        'is_superadmin': pick('is_superadmin'),
        'role': pick('role') or pick('role_name'),
        'role_name': pick('role_name') or pick('role'),
    }

    # Dinamik kolon isimleri için ekler
    if 'login_attempts' in dest_cols:
        fields['login_attempts'] = attempts_val
    elif 'failed_attempts' in dest_cols:
        fields['failed_attempts'] = attempts_val

    if 'last_login' in dest_cols:
        fields['last_login'] = last_login_val
    elif 'last_login_at' in dest_cols:
        fields['last_login_at'] = last_login_val

    # Insert/Update sütun setlerini hazırla (None olmayan ve tabloda var olanlar)
    valid_items = {
        k: v for k, v in fields.items() if k in dest_cols and v is not None and is_valid_identifier(k)
    }

    if existing:
        # Güncelleme
        if not valid_items:
            return False, 'skip_no_fields'
        safe_cols = [k for k in valid_items.keys() if is_valid_identifier(k)]
        set_clause = ', '.join([c + " = ?" for c in safe_cols])
        params = list(valid_items.values()) + [username]
        dest_cur.execute(
            "UPDATE users SET " + set_clause + " WHERE LOWER(username) = LOWER(?)",
            params
        )
        return True, 'updated'
    else:
        # Ekleme
        if 'created_at' in dest_cols and 'created_at' not in valid_items:
            valid_items['created_at'] = datetime.now().isoformat()
        safe_cols = [k for k in valid_items.keys() if is_valid_identifier(k)]
        cols_str = ', '.join(safe_cols)
        placeholders = ', '.join(['?'] * len(valid_items))
        dest_cur.execute(
            "INSERT INTO users (" + cols_str + ") VALUES (" + placeholders + ")",
            list(valid_items.values())
        )
        return True, 'inserted'


def upsert_role(src_role: dict, dest_cur, dest_cols: list) -> None:
    name = src_role.get('name') or src_role.get('role_name') or src_role.get('display_name')
    if not name:
        return False
    dest_cur.execute("SELECT id FROM roles WHERE LOWER(name) = LOWER(?)", (name,))
    row = dest_cur.fetchone()
    if row:
        return False
    fields = {
        'name': name,
        'display_name': src_role.get('display_name') or name,
        'description': src_role.get('description'),
        'is_system_role': src_role.get('is_system_role'),
        'is_active': src_role.get('is_active', 1),
    }
    valid_items = {
        k: v for k, v in fields.items() if k in dest_cols and v is not None and is_valid_identifier(k)
    }
    if 'created_at' in dest_cols and 'created_at' not in valid_items:
        valid_items['created_at'] = datetime.now().isoformat()
    safe_cols = [k for k in valid_items.keys() if is_valid_identifier(k)]
    cols_str = ', '.join(safe_cols)
    placeholders = ', '.join(['?'] * len(valid_items))
    dest_cur.execute(
        "INSERT INTO roles (" + cols_str + ") VALUES (" + placeholders + ")",
        list(valid_items.values())
    )
    return True


def ensure_user_role(dest_cur, username: str, role_name: str) -> None:
    if not username or not role_name:
        return False
    # Kullanıcı id
    dest_cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    u = dest_cur.fetchone()
    if not u:
        return False
    user_id = u[0]
    # Rol id
    dest_cur.execute("SELECT id FROM roles WHERE LOWER(name) = LOWER(?)", (role_name,))
    r = dest_cur.fetchone()
    if not r:
        return False
    role_id = r[0]
    # Var mı?
    dest_cur.execute("SELECT 1 FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
    if dest_cur.fetchone():
        return False
    # Ekle
    dest_cur.execute(
        "INSERT INTO user_roles (user_id, role_id, assigned_at) VALUES (?, ?, ?)",
        (user_id, role_id, datetime.now().isoformat())
    )
    return True


def migrate() -> None:
    logging.info(" Kullanıcı verilerinin birleşik DB'ye migrasyonu başlıyor")
    if not os.path.exists(SRC_DB):
        logging.info(f"️ Kaynak DB yok: {SRC_DB}")
        return
    if not os.path.exists(DEST_DB):
        logging.info(f"️ Hedef DB yok: {DEST_DB}")
        return

    src = sqlite3.connect(SRC_DB)
    dest = sqlite3.connect(DEST_DB)
    src_cur = src.cursor()
    dest_cur = dest.cursor()

    try:
        # Kolon listeleri
        src_user_cols = fetch_cols(src_cur, 'users')
        dest_user_cols = fetch_cols(dest_cur, 'users')
        logging.info(f"Kaynak users kolonları: {src_user_cols}")
        logging.info(f"Hedef users kolonları: {dest_user_cols}")

        # 1) Users
        src_cur.execute("SELECT * FROM users")
        users_rows = src_cur.fetchall()
        inserted = updated = skipped = 0
        for row in users_rows:
            src_user = row_to_dict(src_user_cols, row)
            ok, status = upsert_user(src_user, dest_cur, dest_user_cols)
            if ok and status == 'inserted':
                inserted += 1
            elif ok and status == 'updated':
                updated += 1
            else:
                skipped += 1

        logging.info(f" Users: inserted={inserted}, updated={updated}, skipped={skipped}")

        # 2) Roles
        created_roles = 0
        try:
            src_role_cols = fetch_cols(src_cur, 'roles')
            dest_role_cols = fetch_cols(dest_cur, 'roles')
            src_cur.execute("SELECT * FROM roles")
            for r in src_cur.fetchall():
                src_role = row_to_dict(src_role_cols, r)
                if upsert_role(src_role, dest_cur, dest_role_cols):
                    created_roles += 1
        except Exception as e:
            logging.info(f"️ roles migrasyonu atlandı: {e}")
        logging.info(f" Roles: created={created_roles}")

        # 3) User-Roles
        linked = 0
        try:
            src_cur.execute("SELECT u.username, r.name FROM user_roles ur JOIN users u ON ur.user_id = u.id JOIN roles r ON ur.role_id = r.id")
            for username, role_name in src_cur.fetchall():
                if ensure_user_role(dest_cur, username, role_name):
                    linked += 1
        except Exception as e:
            logging.info(f"️ user_roles migrasyonu atlandı: {e}")
        logging.info(f" User-Roles: linked={linked}")

        # 4) Permissions (opsiyonel, sadece olmayanları ekle)
        added_perms = added_role_perms = added_user_perms = 0
        try:
            src_perm_cols = fetch_cols(src_cur, 'permissions')
            dest_perm_cols = fetch_cols(dest_cur, 'permissions')
            # Kaynak izin ad kolonu (name vs permission_name)
            src_perm_name_col = 'name' if 'name' in src_perm_cols else ('permission_name' if 'permission_name' in src_perm_cols else None)
            # izinler
            src_cur.execute("SELECT * FROM permissions")
            for p in src_cur.fetchall():
                sp = row_to_dict(src_perm_cols, p)
                perm_name = sp.get(src_perm_name_col) if src_perm_name_col else None
                if not perm_name:
                    # bazı kaynaklarda name alanı farklı olabilir; bulamazsak atla
                    continue
                dest_cur.execute("SELECT id FROM permissions WHERE LOWER(name) = LOWER(?)", (perm_name,))
                if dest_cur.fetchone():
                    continue
                fields = {}
                # Temel alanlar
                if 'name' in dest_perm_cols:
                    fields['name'] = perm_name
                if 'display_name' in dest_perm_cols:
                    fields['display_name'] = sp.get('display_name') or perm_name
                if 'description' in dest_perm_cols and sp.get('description') is not None:
                    fields['description'] = sp.get('description')
                # Opsiyonel alanlar
                for opt in ['module','action','resource','is_active']:
                    if opt in dest_perm_cols and opt in src_perm_cols and sp.get(opt) is not None:
                        fields[opt] = sp.get(opt)
                # code alanı varsa kopyala
                if 'code' in dest_perm_cols and 'code' in src_perm_cols and sp.get('code') is not None:
                    fields['code'] = sp.get('code')
                if 'created_at' in dest_perm_cols and 'created_at' not in fields:
                    fields['created_at'] = datetime.now().isoformat()
                cols_str = ', '.join(fields.keys())
                placeholders = ', '.join(['?'] * len(fields))
                safe_cols = [k for k in fields.keys() if is_valid_identifier(k)]
                cols_str = ', '.join(safe_cols)
                dest_cur.execute(
                    "INSERT INTO permissions (" + cols_str + ") VALUES (" + placeholders + ")",
                    list(fields.values()),
                )
                added_perms += 1

            # rol-izin eşleşmeleri
            try:
                # İzin adı: name/permission_name sütunlarından birini kullan (dinamik sütun yerine COALESCE)
                src_cur.execute(
                    """
                    SELECT r.name, COALESCE(p.name, p.permission_name) AS perm_name
                    FROM role_permissions rp
                    JOIN roles r ON rp.role_id = r.id
                    JOIN permissions p ON rp.permission_id = p.id
                    """
                )
                for role_name, perm_name in src_cur.fetchall():
                        dest_cur.execute("SELECT id FROM roles WHERE LOWER(name) = LOWER(?)", (role_name,))
                        r = dest_cur.fetchone()
                        dest_cur.execute("SELECT id FROM permissions WHERE LOWER(name) = LOWER(?)", (perm_name,))
                        p = dest_cur.fetchone()
                        if not r or not p:
                            continue
                        role_id, perm_id = r[0], p[0]
                        dest_cur.execute("SELECT 1 FROM role_permissions WHERE role_id = ? AND permission_id = ?", (role_id, perm_id))
                        if dest_cur.fetchone():
                            continue
                        dest_cur.execute("INSERT INTO role_permissions (role_id, permission_id, granted_at) VALUES (?, ?, ?)", (role_id, perm_id, datetime.now().isoformat()))
                        added_role_perms += 1
                else:
                    logging.info("️ Kaynak permissions tablosunda name/permission_name kolonu bulunamadı; role_permissions atlandı")
            except Exception as e:
                logging.info(f"️ role_permissions atlandı: {e}")

            # kullanıcı özel izinleri
            try:
                # Kaynakta user_permissions tablosu varsa çalıştır
                src_user_perm_cols = []
                try:
                    src_user_perm_cols = fetch_cols(src_cur, 'user_permissions')
                except Exception:
                    src_user_perm_cols = []
                if src_user_perm_cols:
                    src_cur.execute(
                        """
                        SELECT u.username, COALESCE(p.name, p.permission_name) AS perm_name
                        FROM user_permissions up
                        JOIN users u ON up.user_id = u.id
                        JOIN permissions p ON up.permission_id = p.id
                        """
                    )
                    for username, perm_name in src_cur.fetchall():
                            dest_cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
                            u = dest_cur.fetchone()
                            dest_cur.execute("SELECT id FROM permissions WHERE LOWER(name) = LOWER(?)", (perm_name,))
                            p = dest_cur.fetchone()
                            if not u or not p:
                                continue
                            user_id, perm_id = u[0], p[0]
                            dest_cur.execute("SELECT 1 FROM user_permissions WHERE user_id = ? AND permission_id = ?", (user_id, perm_id))
                            if dest_cur.fetchone():
                                continue
                            dest_cur.execute("INSERT INTO user_permissions (user_id, permission_id, granted_at) VALUES (?, ?, ?)", (user_id, perm_id, datetime.now().isoformat()))
                            added_user_perms += 1
                    else:
                        logging.info("️ Kaynak permissions tablosunda name/permission_name yok; user_permissions atlandı")
                else:
                    logging.info(f"{Icons.INFO} Kaynak DB’de user_permissions tablosu yok; atlandı")
            except Exception as e:
                logging.info(f"️ user_permissions atlandı: {e}")
        except Exception as e:
            logging.info(f"️ permissions migrasyonu atlandı: {e}")

        logging.info(f" Permissions: added={added_perms}, role_links={added_role_perms}, user_links={added_user_perms}")

        # Son: commit
        dest.commit()
        logging.info(" Migrasyon tamamlandı.")
    finally:
        src.close()
        dest.close()


if __name__ == '__main__':
    migrate()
def is_valid_identifier(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name or ""))
