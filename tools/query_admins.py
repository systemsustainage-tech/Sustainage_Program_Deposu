import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Her iki veritabanında (sdg.db ve data/sdg_desktop.sqlite) 'admin' kullanıcısını
inceleyip durum raporu çıkarır.
"""

import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def query_admin(db_path: str) -> None:
    """Belirtilen veritabanında admin kullanıcısını incele"""
    exists = os.path.exists(db_path)
    logging.info(f"\n DB: {db_path} | exists={exists}")
    if not exists:
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # users kolonları
        cur.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in cur.fetchall()]
        logging.info(f"   users kolonları: {cols}")

        # admin satırı
        cur.execute(
            "SELECT id, username, email, password_hash, is_active FROM users WHERE LOWER(username) = LOWER('admin')"
        )
        row = cur.fetchone()
        if not row:
            logging.info("    admin kullanıcı bulunamadı")
            conn.close()
            return

        user_id, username, email, pwd_hash, is_active = row
        logging.info(f"    admin bulundu: id={user_id}, email={email}, active={is_active}")
        logging.info(f"    hash prefix: {pwd_hash[:20] if pwd_hash else None}")

        # roller
        role_names = []
        if "role" in cols:
            cur.execute("SELECT role FROM users WHERE id=?", (user_id,))
            r = cur.fetchone()
            role_names = [r[0]] if r and r[0] else []
        else:
            try:
                cur.execute("SELECT name FROM roles LIMIT 1")
                _ = cur.fetchone()
                cur.execute(
                    """
                    SELECT r.name
                    FROM user_roles ur
                    JOIN roles r ON r.id = ur.role_id
                    WHERE ur.user_id = ? AND ur.is_active = 1
                    """,
                    (user_id,),
                )
                role_names = [r[0] for r in cur.fetchall()]
            except Exception:
                role_names = []
        logging.info(f"    roller: {', '.join(role_names) if role_names else '—'}")

        # örnek izinler
        perm_names = []
        try:
            cur.execute("SELECT name FROM permissions LIMIT 1")
            _ = cur.fetchone()
            cur.execute(
                """
                SELECT p.name
                FROM role_permissions rp
                JOIN permissions p ON p.id = rp.permission_id
                JOIN user_roles ur ON ur.role_id = rp.role_id AND ur.user_id = ?
                WHERE rp.is_granted = 1 AND ur.is_active = 1
                LIMIT 10
                """,
                (user_id,),
            )
            perm_names = [r[0] for r in cur.fetchall()]
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        logging.info(f"   ️ örnek izinler (ilk 10): {', '.join(perm_names) if perm_names else '—'}")

        # ek alanlar
        extra = {}
        present = [
            c for c in [
                "failed_attempts",
                "locked_until",
                "must_change_password",
                "pw_hash_version",
                "twofa_failed_attempts",
                "twofa_locked_until",
            ]
            if c in cols
        ]
        if present:
            row_all = cur.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            for c in present:
                try:
                    idx = cols.index(c)
                    extra[c] = row_all[idx] if row_all else None
                except Exception:
                    extra[c] = None
        if extra:
            logging.info("    ek alanlar: " + ", ".join([f"{k}={v}" for k, v in extra.items()]))

        conn.close()
    except Exception as e:
        logging.error(f"    hata: {e}")


def main() -> None:
    logging.info("Admin kullanıcı durumu incelemesi\n" + "=" * 70)
    base = os.getcwd()
    dbs = [
        os.path.join(base, "sdg.db"),
        os.path.join(base, "data", "sdg_desktop.sqlite"),
    ]
    for db_path in dbs:
        query_admin(db_path)
    logging.info("\nİnceleme tamamlandı.")


if __name__ == "__main__":
    main()
