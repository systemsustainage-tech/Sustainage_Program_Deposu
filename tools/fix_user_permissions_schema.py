import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı Yetkilendirme Şeması Düzeltme Aracı
Eksik sütunları ekler ve veritabanını düzeltir
"""

import os
import sqlite3
from datetime import datetime
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fix_user_permissions_schema(db_path: str) -> None:
    """Kullanıcı yetkilendirme şemasını düzelt"""
    
    if not os.path.exists(db_path):
        logging.error(f"Hata: Veritabanı bulunamadı: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logging.info("Kullanıcı yetkilendirme şeması düzeltiliyor...")
        
        # 1. Users tablosunu kontrol et ve eksik sütunları ekle
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        
        if 'tour_completed' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN tour_completed INTEGER DEFAULT 0")
            logging.info("+ users.tour_completed sutunu eklendi")
        
        if 'role_name' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role_name TEXT DEFAULT 'User'")
            logging.info("+ users.role_name sutunu eklendi")
        
        # 2. User permissions tablosunu kontrol et
        cursor.execute("PRAGMA table_info(user_permissions)")
        perm_columns = [row[1] for row in cursor.fetchall()]
        
        if not perm_columns:
            # Tablo yoksa oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    granted_by INTEGER,
                    granted_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (permission_id) REFERENCES permissions(id)
                )
            """)
            logging.info("+ user_permissions tablosu olusturuldu")
        
        # 3. Permissions tablosunu kontrol et
        cursor.execute("PRAGMA table_info(permissions)")
        perm_def_columns = [row[1] for row in cursor.fetchall()]
        
        if not perm_def_columns:
            # Permissions tablosunu oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    permission_name TEXT UNIQUE NOT NULL,
                    permission_category TEXT,
                    description TEXT,
                    created_at TEXT
                )
            """)
            logging.info("+ permissions tablosu olusturuldu")
            
            # Varsayılan izinleri ekle
            default_permissions = [
                ('export', 'Genel İzinler', 'Dışa Aktarma'),
                ('import', 'Genel İzinler', 'İçe Aktarma'),
                ('admin', 'Genel İzinler', 'Yönetici'),
                ('view_digital_security', 'Dijital Güvenlik', 'Görüntüleme'),
                ('edit_digital_security', 'Dijital Güvenlik', 'Düzenleme'),
                ('view_environmental', 'Çevresel', 'Görüntüleme'),
                ('edit_environmental', 'Çevresel', 'Düzenleme'),
                ('view_social', 'Sosyal', 'Görüntüleme'),
                ('edit_social', 'Sosyal', 'Düzenleme'),
                ('view_economic', 'Ekonomik', 'Görüntüleme'),
                ('edit_economic', 'Ekonomik', 'Düzenleme'),
                ('view_gri', 'GRI', 'Görüntüleme'),
                ('edit_gri', 'GRI', 'Düzenleme'),
                ('view_tsrs', 'TSRS', 'Görüntüleme'),
                ('edit_tsrs', 'TSRS', 'Düzenleme'),
                ('view_reports', 'Raporlama', 'Görüntüleme'),
                ('create_reports', 'Raporlama', 'Oluşturma'),
                ('view_analytics', 'Analiz', 'Görüntüleme'),
                ('edit_analytics', 'Analiz', 'Düzenleme')
            ]
            
            for perm_name, category, description in default_permissions:
                cursor.execute("""
                    INSERT OR IGNORE INTO permissions 
                    (permission_name, permission_category, description, created_at)
                    VALUES (?, ?, ?, ?)
                """, (perm_name, category, description, datetime.now().isoformat()))
            
            logging.info(f"+ {len(default_permissions)} varsayilan izin eklendi")
        
        # 4. Roles tablosunu kontrol et
        cursor.execute("PRAGMA table_info(roles)")
        role_columns = [row[1] for row in cursor.fetchall()]
        
        if not role_columns:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_name TEXT UNIQUE NOT NULL,
                    role_description TEXT,
                    is_system_role INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            logging.info("+ roles tablosu olusturuldu")
            
            # Varsayılan roller
            default_roles = [
                ('Admin', 'Sistem Yöneticisi', 1),
                ('User', 'Standart Kullanıcı', 1),
                ('Viewer', 'Sadece Görüntüleme', 1),
                ('Editor', 'Düzenleme Yetkisi', 1)
            ]
            
            for role_name, description, is_system in default_roles:
                cursor.execute("""
                    INSERT OR IGNORE INTO roles 
                    (role_name, role_description, is_system_role, created_at)
                    VALUES (?, ?, ?, ?)
                """, (role_name, description, is_system, datetime.now().isoformat()))
            
            logging.info(f"+ {len(default_roles)} varsayilan rol eklendi")
        
        # 5. Role permissions tablosunu kontrol et
        cursor.execute("PRAGMA table_info(role_permissions)")
        role_perm_columns = [row[1] for row in cursor.fetchall()]
        
        if not role_perm_columns:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    created_at TEXT,
                    FOREIGN KEY (role_id) REFERENCES roles(id),
                    FOREIGN KEY (permission_id) REFERENCES permissions(id)
                )
            """)
            logging.info("+ role_permissions tablosu olusturuldu")
        
        # 6. User roles tablosunu kontrol et
        cursor.execute("PRAGMA table_info(user_roles)")
        user_role_columns = [row[1] for row in cursor.fetchall()]
        
        if not user_role_columns:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    assigned_by INTEGER,
                    assigned_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (role_id) REFERENCES roles(id)
                )
            """)
            logging.info("+ user_roles tablosu olusturuldu")
        
        # 7. Varsayılan Admin rolüne tüm izinleri ver
        try:
            cursor.execute("SELECT id FROM roles WHERE role_name = 'Admin'")
            admin_role = cursor.fetchone()
        except Exception:
            admin_role = None
        
        if admin_role:
            admin_role_id = admin_role[0]
            
            # Tüm izinleri al
            cursor.execute("SELECT id FROM permissions")
            all_permissions = cursor.fetchall()
            
            # Admin rolüne tüm izinleri ata
            for perm in all_permissions:
                cursor.execute("""
                    INSERT OR IGNORE INTO role_permissions 
                    (role_id, permission_id, created_at)
                    VALUES (?, ?, ?)
                """, (admin_role_id, perm[0], datetime.now().isoformat()))
            
            logging.info(f"+ Admin rolune {len(all_permissions)} izin atandi")
        
        # 8. Mevcut kullanıcıları User rolüne ata
        cursor.execute("SELECT id FROM users")
        all_users = cursor.fetchall()
        
        try:
            cursor.execute("SELECT id FROM roles WHERE role_name = 'User'")
            user_role = cursor.fetchone()
        except Exception:
            user_role = None
        
        if user_role and all_users:
            user_role_id = user_role[0]
            
            for user in all_users:
                cursor.execute("""
                    INSERT OR IGNORE INTO user_roles 
                    (user_id, role_id, assigned_at)
                    VALUES (?, ?, ?)
                """, (user[0], user_role_id, datetime.now().isoformat()))
            
            logging.info(f"+ {len(all_users)} kullanici User rolune atandi")
        
        # 9. Mevcut kullanıcıların role_name sütununu güncelle
        try:
            cursor.execute("UPDATE users SET role_name = 'User' WHERE role_name IS NULL OR role_name = ''")
            logging.info("+ Mevcut kullanıcıların rol isimleri güncellendi")
        except Exception as e:
            logging.info(f"+ Rol ismi güncelleme atlandı: {e}")
        
        # İndeksleri ekle
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_permissions_user ON user_permissions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_permissions_perm ON user_permissions(permission_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_role_permissions_perm ON role_permissions(permission_id)")
            logging.info("+ Indeksler eklendi")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        
        conn.commit()
        conn.close()
        
        logging.info("\n+ Kullanici yetkilendirme semasi basariyla duzeltildi!")
        return True
        
    except Exception as e:
        logging.error(f"- Hata: {e}")
        return False


def main() -> None:
    """Ana fonksiyon"""
    logging.info("Kullanıcı Yetkilendirme Şeması Düzeltme Aracı")
    logging.info("=" * 50)
    
    # Veritabanı yolunu bul
    possible_paths = [
        DB_PATH,
        "sdg.db",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sdg_desktop.sqlite")
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        logging.info("Veritabanı dosyası bulunamadı!")
        logging.info("Lütfen aşağıdaki konumlardan birinde olduğundan emin olun:")
        for path in possible_paths:
            logging.info(f"  - {path}")
        return
    
    logging.info(f"Veritabanı bulundu: {db_path}")
    
    if fix_user_permissions_schema(db_path):
        logging.info("\n+ Islem tamamlandi! Artik kullanici yetkilendirme sistemi calisacak.")
    else:
        logging.info("\n- Islem basarisiz!")


if __name__ == "__main__":
    main()
