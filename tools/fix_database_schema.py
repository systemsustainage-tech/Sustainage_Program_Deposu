#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı Şema Düzeltmeleri
"""

import logging
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fix_database_schema(db_path="sdg.db") -> None:
    """Eksik kolonları ekle"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Veritabanı Şema Düzeltmeleri")
    logging.info("="*50)
    
    try:
        # 1. user_roles tablosuna assigned_by kolonu ekle
        logging.info("\n1️⃣ user_roles tablosu düzeltiliyor...")
        try:
            cur.execute("ALTER TABLE user_roles ADD COLUMN assigned_by INTEGER")
            logging.info("    assigned_by kolonu eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("    assigned_by kolonu zaten mevcut")
            else:
                logging.error(f"    Hata: {e}")
        
        # 2. user_roles tablosuna diğer eksik kolonları ekle
        try:
            cur.execute("ALTER TABLE user_roles ADD COLUMN assigned_at TEXT DEFAULT CURRENT_TIMESTAMP")
            logging.info("    assigned_at kolonu eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("    assigned_at kolonu zaten mevcut")
        
        try:
            cur.execute("ALTER TABLE user_roles ADD COLUMN is_active INTEGER DEFAULT 1")
            logging.info("    is_active kolonu eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("    is_active kolonu zaten mevcut")
        
        # 3. users tablosunda eksik kolonları kontrol et
        logging.info("\n2️⃣ users tablosu kontrol ediliyor...")
        cur.execute("PRAGMA table_info(users)")
        user_cols = [row[1] for row in cur.fetchall()]
        
        required_user_cols = ['failed_attempts', 'locked_until', 'pw_hash_version']
        for col in required_user_cols:
            if col not in user_cols:
                try:
                    if col == 'failed_attempts':
                        cur.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0")
                    elif col == 'locked_until':
                        cur.execute("ALTER TABLE users ADD COLUMN locked_until TEXT")
                    elif col == 'pw_hash_version':
                        cur.execute("ALTER TABLE users ADD COLUMN pw_hash_version TEXT DEFAULT 'argon2'")
                    logging.info(f"    {col} kolonu eklendi")
                except sqlite3.OperationalError as e:
                    logging.info(f"    {col} kolonu eklenemedi: {e}")
            else:
                logging.info(f"    {col} kolonu mevcut")
        
        # 4. modules tablosunu kontrol et
        logging.info("\n3️⃣ modules tablosu kontrol ediliyor...")
        cur.execute("PRAGMA table_info(modules)")
        module_cols = [row[1] for row in cur.fetchall()]
        
        if 'is_core' in module_cols:
            logging.info("    is_core kolonu mevcut")
        else:
            try:
                cur.execute("ALTER TABLE modules ADD COLUMN is_core INTEGER DEFAULT 0")
                logging.info("    is_core kolonu eklendi")
            except sqlite3.OperationalError as e:
                logging.info(f"    is_core kolonu eklenemedi: {e}")
        
        # 5. company_modules tablosunu kontrol et ve modül_id tabanlı şemaya migrate et
        logging.info("\n4️⃣ company_modules tablosu kontrol ediliyor...")
        try:
            # Tablo mevcut mu ve kolonlar nedir?
            cur.execute("PRAGMA table_info(company_modules)")
            cols_info = cur.fetchall()
            cols = [c[1] for c in cols_info]

            if not cols_info:
                # Tablo yoksa doğru şemayla oluştur
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS company_modules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        module_id INTEGER NOT NULL,
                        is_enabled INTEGER DEFAULT 1,
                        enabled_at TEXT,
                        disabled_at TEXT,
                        enabled_by_user_id INTEGER,
                        license_expires_at TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT (datetime('now')),
                        updated_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                        FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE,
                        FOREIGN KEY(enabled_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
                        UNIQUE(company_id, module_id)
                    )
                    """
                )
                # İndeksler
                cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_company ON company_modules(company_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_module ON company_modules(module_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_enabled ON company_modules(is_enabled)")
                logging.info("    company_modules tablosu oluşturuldu")
            elif 'module_code' in cols and 'module_id' not in cols:
                # Eski şema: module_code içeriyor, migrate et
                logging.info("   ️  Eski şema tespit edildi (module_code). Migrasyon başlatılıyor...")
                # Yeni tabloyu oluştur
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS company_modules_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        module_id INTEGER NOT NULL,
                        is_enabled INTEGER DEFAULT 1,
                        enabled_at TEXT,
                        disabled_at TEXT,
                        enabled_by_user_id INTEGER,
                        license_expires_at TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT (datetime('now')),
                        updated_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                        FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE,
                        FOREIGN KEY(enabled_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
                        UNIQUE(company_id, module_id)
                    )
                    """
                )

                # Verileri taşı: module_code'dan module_id'ye map et
                cur.execute(
                    """
                    INSERT INTO company_modules_new (
                        company_id, module_id, is_enabled, enabled_at, disabled_at, enabled_by_user_id,
                        license_expires_at, notes
                    )
                    SELECT 
                        cm.company_id,
                        (SELECT m.id FROM modules m WHERE m.module_code = cm.module_code),
                        cm.is_enabled,
                        cm.enabled_at,
                        cm.disabled_at,
                        cm.enabled_by,
                        NULL AS license_expires_at,
                        NULL AS notes
                    FROM company_modules cm
                    """
                )

                # Eski tabloyu sil ve yeni tabloyu yeniden adlandır
                cur.execute("DROP TABLE company_modules")
                cur.execute("ALTER TABLE company_modules_new RENAME TO company_modules")

                # İndeksler
                cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_company ON company_modules(company_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_module ON company_modules(module_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_company_modules_enabled ON company_modules(is_enabled)")
                logging.info("    company_modules migrasyonu tamamlandı")
            else:
                logging.info("    company_modules şeması uyumlu")
        except sqlite3.OperationalError as e:
            logging.error(f"    company_modules hatası: {e}")
        
        # 6. reset_tokens tablosunu kontrol et
        logging.info("\n5️⃣ reset_tokens tablosu kontrol ediliyor...")
        try:
            cur.execute("CREATE TABLE IF NOT EXISTS reset_tokens ("
                       "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "user_id INTEGER NOT NULL,"
                       "code_hash TEXT NOT NULL,"
                       "requested_at TEXT NOT NULL,"
                       "expires_at TEXT NOT NULL,"
                       "attempts_left INTEGER NOT NULL DEFAULT 5,"
                       "used_at TEXT,"
                       "request_ip TEXT,"
                       "sent_via TEXT DEFAULT 'email',"
                       "FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,"
                       "UNIQUE(user_id)"
                       ")")
            logging.info("    reset_tokens tablosu oluşturuldu/kontrol edildi")
        except sqlite3.OperationalError as e:
            logging.error(f"    reset_tokens hatası: {e}")
        
        conn.commit()
        
        logging.info("\n" + "="*50)
        logging.info(" VERİTABANI ŞEMA DÜZELTMELERİ TAMAMLANDI!")
        logging.info("="*50)
        
        return True
        
    except Exception as e:
        logging.error(f"\n HATA: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "sdg.db"
    logging.info(f" Veritabanı: {db_path}\n")
    
    success = fix_database_schema(db_path)
    sys.exit(0 if success else 1)
