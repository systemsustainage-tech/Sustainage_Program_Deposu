#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı Yönetimi Manager
Kullanıcı, rol, yetki ve audit trail yönetimi
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from utils.language_manager import LanguageManager
from services.email_service import EmailService
from yonetim.security.core.crypto import hash_password as secure_hash_password
from yonetim.security.core.crypto import verify_password_compat as secure_verify_password
from config.database import DB_PATH


class UserManager:
    """Kullanıcı Yönetimi Manager"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.lm = LanguageManager()
        self._ensure_schema()
        # Email servisini örnek olarak tut (testlerde patch edilebilsin)
        self.email_service = EmailService()

    def get_user_company(self, user_id: int) -> Optional[int]:
        """Kullanıcının birincil şirket ID'sini döndür"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Önce birincil şirketi ara
            cursor.execute("""
                SELECT company_id FROM user_companies 
                WHERE user_id = ? AND is_primary = 1
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            
            # Birincil yoksa ilk şirketi döndür
            cursor.execute("""
                SELECT company_id FROM user_companies 
                WHERE user_id = ?
                ORDER BY id ASC LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
                
            return None
        except Exception as e:
            logging.error(f"Error getting user company: {e}")
            return None
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        """Kullanıcı yönetimi şemasını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Şema dosyasını oku ve çalıştır
            schema_file = os.path.join(os.path.dirname(__file__), 'user_schema.sql')
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # SQL komutlarını çalıştır
            cursor.executescript(schema_sql)
            conn.commit()

            # Varsayılan verileri oluştur
            self._create_default_data(cursor)
            conn.commit()

            logging.info(self.lm.tr("log_schema_created", "Kullanıcı yönetimi şeması başarıyla oluşturuldu"))
        
        except Exception as e:
            logging.error(self.lm.tr("log_schema_creation_error", "Kullanıcı yönetimi şeması oluşturulurken hata: {}").format(e))
            conn.rollback()
        finally:
            conn.close()

    def _create_default_data(self, cursor) -> None:
        """Varsayılan verileri oluştur"""
        # Varsayılan roller
        default_roles = [
            ('super_admin', 'Süper Yönetici', 'Sistemin tam kontrolüne sahip kullanıcı', 1),
            ('admin', 'Yönetici', 'Sistem yönetimi yetkilerine sahip kullanıcı', 0),
            ('manager', 'Müdür', 'Departman yönetimi yetkilerine sahip kullanıcı', 0),
            ('analyst', 'Analist', 'Veri analizi ve raporlama yetkilerine sahip kullanıcı', 0),
            ('user', 'Kullanıcı', 'Temel kullanıcı yetkileri', 0),
            ('viewer', 'Görüntüleyici', 'Sadece okuma yetkisi olan kullanıcı', 0)
        ]

        for role in default_roles:
            cursor.execute("""
                INSERT OR IGNORE INTO roles (name, display_name, description, is_system_role)
                VALUES (?, ?, ?, ?)
            """, role)

        # Varsayılan yetkiler
        default_permissions = [
            # Kullanıcı Yönetimi
            ('user.create', 'Kullanıcı Oluştur', 'Yeni kullanıcı oluşturma yetkisi', 'user_management', 'create', 'user'),
            ('user.read', 'Kullanıcı Görüntüle', 'Kullanıcı bilgilerini görüntüleme yetkisi', 'user_management', 'read', 'user'),
            ('user.update', 'Kullanıcı Güncelle', 'Kullanıcı bilgilerini güncelleme yetkisi', 'user_management', 'update', 'user'),
            ('user.delete', 'Kullanıcı Sil', 'Kullanıcı silme yetkisi', 'user_management', 'delete', 'user'),

            # Rol Yönetimi
            ('role.create', 'Rol Oluştur', 'Yeni rol oluşturma yetkisi', 'user_management', 'create', 'role'),
            ('role.read', 'Rol Görüntüle', 'Rol bilgilerini görüntüleme yetkisi', 'user_management', 'read', 'role'),
            ('role.update', 'Rol Güncelle', 'Rol bilgilerini güncelleme yetkisi', 'user_management', 'update', 'role'),
            ('role.delete', 'Rol Sil', 'Rol silme yetkisi', 'user_management', 'delete', 'role'),

            # SDG Modülü
            ('sdg.read', 'SDG Görüntüle', 'SDG modülünü görüntüleme yetkisi', 'sdg', 'read', 'sdg'),
            ('sdg.update', 'SDG Güncelle', 'SDG verilerini güncelleme yetkisi', 'sdg', 'update', 'sdg'),

            # GRI Modülü
            ('gri.read', 'GRI Görüntüle', 'GRI modülünü görüntüleme yetkisi', 'gri', 'read', 'gri'),
            ('gri.update', 'GRI Güncelle', 'GRI verilerini güncelleme yetkisi', 'gri', 'update', 'gri'),

            # TSRS Modülü
            ('tsrs.read', 'TSRS Görüntüle', 'TSRS modülünü görüntüleme yetkisi', 'tsrs', 'read', 'tsrs'),
            ('tsrs.update', 'TSRS Güncelle', 'TSRS verilerini güncelleme yetkisi', 'tsrs', 'update', 'tsrs'),

            # ESG Modülü
            ('esg.read', 'ESG Görüntüle', 'ESG modülünü görüntüleme yetkisi', 'esg', 'read', 'esg'),
            ('esg.update', 'ESG Güncelle', 'ESG verilerini güncelleme yetkisi', 'esg', 'update', 'esg'),

            # Raporlama
            ('report.create', 'Rapor Oluştur', 'Rapor oluşturma yetkisi', 'reporting', 'create', 'report'),
            ('report.read', 'Rapor Görüntüle', 'Rapor görüntüleme yetkisi', 'reporting', 'read', 'report'),
            ('report.download', 'Rapor İndir', 'Rapor indirme yetkisi', 'reporting', 'download', 'report'),

            # Sistem Yönetimi
            ('system.settings', 'Sistem Ayarları', 'Sistem ayarlarını yönetme yetkisi', 'system', 'manage', 'settings'),
            ('system.audit', 'Audit Görüntüle', 'Audit loglarını görüntüleme yetkisi', 'system', 'read', 'audit'),

            # Dashboard ve şirket bilgileri
            ('dashboard.read', 'Dashboard Görüntüle', 'Dashboard erişimi', 'dashboard', 'read', 'dashboard'),
            ('dashboard.advanced', 'Gelişmiş Dashboard', 'Gelişmiş dashboard erişimi', 'dashboard', 'read', 'advanced'),
            ('company.read', 'Firma Bilgileri', 'Firma bilgilerini görüntüleme', 'company', 'read', 'info'),

            # Stratejik ve veri toplama
            ('strategic.read', 'Stratejik Yönetim', 'Stratejik modülüne erişim', 'strategic', 'read', 'strategic'),
            ('data.import', 'Veri İçe Aktarım', 'Veri içe aktarımına erişim', 'data', 'import', 'import'),
            ('forms.manage', 'Form Yönetimi', 'Form yönetimine erişim', 'forms', 'manage', 'forms'),

            # Görev ve dosya yönetimi
            ('tasks.read', 'Görevlerim', 'Görev listesini görüntüleme', 'tasks', 'read', 'tasks'),
            ('tasks.auto_create', 'Otomatik Görevler', 'Otomatik görev oluşturma', 'tasks', 'auto_create', 'tasks'),
            ('files.manage', 'Dosya Yönetimi', 'Gelişmiş dosya yönetimi erişimi', 'files', 'manage', 'files'),

            # Sosyal ve politika
            ('hr.read', 'İK Metrikleri', 'İK metrikleri modülüne erişim', 'hr', 'read', 'metrics'),
            ('policy.read', 'Politika Kütüphanesi', 'Politika kütüphanesine erişim', 'policy', 'read', 'library'),
            ('surveys.read', 'Anketler', 'Anketler modülüne erişim', 'surveys', 'read', 'surveys'),

            # SKDM ve diğer modüller
            ('skdm.read', 'SKDM Modülü', 'SKDM modülüne erişim', 'skdm', 'read', 'skdm'),
            ('mapping.read', 'Eşleştirme', 'Haritalama modülüne erişim', 'mapping', 'read', 'mapping'),
            ('prioritization.read', 'Önceliklendirme', 'Önceliklendirme modülüne erişim', 'prioritization', 'read', 'prioritization'),
            ('waste.read', 'Atık Yönetimi', 'Atık yönetimi modülüne erişim', 'waste', 'read', 'waste'),
            ('water.read', 'Su Yönetimi', 'Su yönetimi modülüne erişim', 'water', 'read', 'water'),
            ('supply_chain.read', 'Tedarik Zinciri', 'Tedarik zinciri modülüne erişim', 'supply_chain', 'read', 'supply_chain'),
            ('product_tech.read', 'Ürün & Teknoloji', 'Ürün ve teknoloji modülüne erişim', 'product_tech', 'read', 'product_technology'),
        ]

        # Tablo şemasını kontrol et (bazı kurulumlarda 'code' zorunlu olabilir)
        cursor.execute("PRAGMA table_info(permissions)")
        cols = [row[1] for row in cursor.fetchall()]
        has_code_col = 'code' in cols

        for permission in default_permissions:
            if has_code_col:
                # code sütununu doldur: name'i güvenli bir koda dönüştür
                name = permission[0]
                code = name.replace('.', '_')
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO permissions 
                    (code, name, display_name, description, module, action, resource, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (code, permission[0], permission[1], permission[2], permission[3], permission[4], permission[5])
                )
            else:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO permissions 
                    (name, display_name, description, module, action, resource)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    permission
                )

        # Varsayılan departmanlar
        default_departments = [
            ('Genel Müdürlük', 'GM', 'Genel müdürlük departmanı'),
            ('İnsan Kaynakları', 'IK', 'İnsan kaynakları departmanı'),
            ('Bilgi İşlem', 'IT', 'Bilgi işlem departmanı'),
            ('Finans', 'FN', 'Finans departmanı'),
            ('Sürdürülebilirlik', 'SB', 'Sürdürülebilirlik departmanı'),
            ('Kalite', 'KL', 'Kalite departmanı')
        ]

        for dept in default_departments:
            cursor.execute("""
                INSERT OR IGNORE INTO departments (name, code, description)
                VALUES (?, ?, ?)
            """, dept)

        # role_permissions tablosunda 'granted_by' sütunu var mı kontrol et
        try:
            cursor.execute("PRAGMA table_info(role_permissions)")
            _rp_cols = [row[1] for row in cursor.fetchall()]
        except Exception:
            _rp_cols = []
        _rp_has_granted_by = 'granted_by' in _rp_cols

        # Admin kullanıcısı oluştur (eğer yoksa)
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password = self._hash_password('admin')
            cursor.execute("""
                INSERT INTO users 
                (username, email, password_hash, first_name, last_name, is_active, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@sustainage.com', admin_password, 'Sistem', 'Yöneticisi', 1, 1))

            # Admin rolünü ata
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_user_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
            admin_role_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO user_roles (user_id, role_id, assigned_by)
                VALUES (?, ?, ?)
            """, (admin_user_id, admin_role_id, admin_user_id))

            # Tüm yetkileri süper admin rolüne ata
            cursor.execute("SELECT id FROM permissions")
            permissions = cursor.fetchall()

            cursor.execute("SELECT id FROM roles WHERE name = 'super_admin'")
            super_admin_role_id = cursor.fetchone()[0]
            for permission in permissions:
                if _rp_has_granted_by:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id, granted_by)
                        VALUES (?, ?, ?)
                        """,
                        (super_admin_role_id, permission[0], admin_user_id)
                    )
                else:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                        """,
                        (super_admin_role_id, permission[0])
                    )

            # Admin rolü için gerekli yetkileri ata (Super Admin hariç tüm modüller)
            admin_permission_names = [
                'dashboard.read', 'dashboard.advanced', 'company.read',
                'sdg.read', 'gri.read', 'tsrs.read', 'esg.read',
                'strategic.read', 'data.import', 'forms.manage',
                'tasks.read', 'tasks.auto_create', 'files.manage', 'hr.read', 'policy.read', 'surveys.read',
                'skdm.read', 'mapping.read', 'prioritization.read',
                'waste.read', 'water.read', 'supply_chain.read',
                'product_tech.read', 'report.read', 'system.settings'
            ]
            cursor.execute(
                f"SELECT id FROM permissions WHERE name IN ({','.join(['?']*len(admin_permission_names))})",
                admin_permission_names
            )
            admin_permissions = cursor.fetchall()
            for perm in admin_permissions:
                if _rp_has_granted_by:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id, granted_by)
                        VALUES (?, ?, ?)
                        """,
                        (admin_role_id, perm[0], admin_user_id)
                    )
                else:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                        """,
                        (admin_role_id, perm[0])
                    )

        # --- GARANTİ BLOĞU: Admin/Süper Admin rol izinlerini her başlangıçta güvenceye al ---
        # Admin kullanıcı ID'sini al (varsa)
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        row = cursor.fetchone()
        admin_user_id = row[0] if row else None

        # Süper Admin ve Admin rol ID'lerini al
        cursor.execute("SELECT id FROM roles WHERE name = 'super_admin'")
        row = cursor.fetchone()
        super_admin_role_id = row[0] if row else None

        cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
        row = cursor.fetchone()
        admin_role_id = row[0] if row else None

        # Süper Admin: tüm aktif izinleri ekle (INSERT OR IGNORE)
        if super_admin_role_id:
            cursor.execute("SELECT id FROM permissions WHERE is_active = 1")
            for (perm_id,) in cursor.fetchall():
                if _rp_has_granted_by:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id, granted_by)
                        VALUES (?, ?, ?)
                        """,
                        (super_admin_role_id, perm_id, admin_user_id)
                    )
                else:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                        """,
                        (super_admin_role_id, perm_id)
                    )

        # Admin: temel izin setini ekle (INSERT OR IGNORE)
        if admin_role_id:
            admin_basic_permissions = [
                'dashboard.read', 'dashboard.advanced', 'company.read',
                'sdg.read', 'gri.read', 'tsrs.read', 'esg.read',
                'strategic.read', 'data.import', 'forms.manage',
                'tasks.read', 'tasks.auto_create', 'files.manage', 'hr.read', 'policy.read', 'surveys.read',
                'skdm.read', 'mapping.read', 'prioritization.read',
                'waste.read', 'water.read', 'supply_chain.read',
                'product_tech.read', 'report.read', 'system.settings'
            ]
            cursor.execute(
                f"SELECT id FROM permissions WHERE name IN ({','.join(['?']*len(admin_basic_permissions))})",
                admin_basic_permissions
            )
            for (perm_id,) in cursor.fetchall():
                if _rp_has_granted_by:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id, granted_by)
                        VALUES (?, ?, ?)
                        """,
                        (admin_role_id, perm_id, admin_user_id)
                    )
                else:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                        """,
                        (admin_role_id, perm_id)
                    )

        # Varsayılan Şirket Oluşturma ve Admin Atama
        try:
            # Şirket tablosu var mı kontrol et
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
            if cursor.fetchone():
                # Varsayılan şirket
                cursor.execute("SELECT id FROM companies WHERE id = 1")
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO companies (id, name, sector, country)
                        VALUES (1, 'SustainAge Demo A.Ş.', 'Teknoloji', 'Türkiye')
                    """)
                
                # Admin kullanıcısına şirketi ata
                if admin_user_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO user_companies (user_id, company_id, is_primary, assigned_by)
                        VALUES (?, 1, 1, ?)
                    """, (admin_user_id, admin_user_id))
        except Exception as e:
            logging.error(f"Varsayılan şirket oluşturulurken hata: {e}")

    def _hash_password(self, password: str) -> str:
        """Şifreyi hash'le (Argon2, merkezi güvenlik modülü)"""
        return secure_hash_password(password)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Şifreyi doğrula (geri uyumlu Argon2/PBKDF2/SHA256)"""
        try:
            return secure_verify_password(password_hash, password)
        except Exception:
            return False

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def authenticate(self, username, password) -> Optional[Dict]:
        """Kullanıcı girişi doğrula"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, password_hash, first_name, last_name, email, is_active 
                FROM users 
                WHERE username = ?
            """, (username,))
            
            user = cursor.fetchone()
            
            if user and self._verify_password(password, user[2]):
                if not user[6]: # is_active check
                    logging.warning(f"Inactive user login attempt: {username}")
                    return None
                    
                return {
                    'id': user[0],
                    'username': user[1],
                    'first_name': user[3],
                    'last_name': user[4],
                    'email': user[5],
                    'display_name': f"{user[3]} {user[4]}"
                }
            return None
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return None
        finally:
            conn.close()

    # Kullanıcı İşlemleri
    def create_user(self, user_data: Dict, created_by: Optional[int] = None) -> int:
        """Yeni kullanıcı oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Şifreyi hash'le
            password_hash = self._hash_password(user_data['password'])

            cursor.execute("""
                INSERT INTO users 
                (username, email, password_hash, first_name, last_name, phone, 
                 department, position, is_active, is_verified, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['first_name'],
                user_data['last_name'],
                user_data.get('phone'),
                user_data.get('department'),
                user_data.get('position'),
                user_data.get('is_active', True),
                user_data.get('is_verified', False),
                created_by,
                created_by
            ))

            user_id = cursor.lastrowid

            # Kullanıcı profilini oluştur
            cursor.execute("""
                INSERT INTO user_profiles (user_id)
                VALUES (?)
            """, (user_id,))

            # Varsayılan rolü ata (eğer belirtilmişse)
            if 'role_ids' in user_data and user_data['role_ids']:
                for role_id in user_data['role_ids']:
                    cursor.execute(
                        """
                        INSERT INTO user_roles (user_id, role_id, assigned_by)
                        VALUES (?, ?, ?)
                        """,
                        (user_id, role_id, created_by),
                    )
            else:
                # Hiç rol verilmemişse varsayılan 'user' rolünü ata
                try:
                    cursor.execute("SELECT id FROM roles WHERE name = 'user' AND is_active = 1")
                    row = cursor.fetchone()
                    if row and row[0]:
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO user_roles (user_id, role_id, assigned_by)
                            VALUES (?, ?, ?)
                            """,
                            (user_id, row[0], created_by),
                        )
                except Exception:
                    # Sessiz geç; rol yoksa oluşturma akışı devam etsin
                    logging.error(f'Silent error in user_manager.py: {str(e)}')

            # Audit log
            self._log_audit(cursor, created_by, 'create', 'user', int(user_id if user_id is not None else -1),
                           None, {'username': user_data['username']})

            conn.commit()

            try:
                # display_name = (f"{(user_data.get('first_name') or '').strip()} {(user_data.get('last_name') or '').strip()}" ).strip() or user_data['username']
                self.email_service.send_new_user_welcome(user_id, password=user_data.get('password'))
            except Exception as e:
                logging.error(f'Silent error in user_manager.py: {str(e)}')

            return int(user_id if user_id is not None else -1)

        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_user_creation_error", "Kullanıcı oluşturulurken hata: {}").format(e))
            return -1
        finally:
            conn.close()

    def create_users_bulk(self, users_data: List[Dict], created_by: Optional[int] = None) -> List[int]:
        """Toplu kullanıcı oluşturma - Yüksek performans için optimize edilmiş"""
        if not users_data:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()
        created_user_ids = []

        try:
            # Varsayılan 'user' role ID'sini önceden al
            cursor.execute("SELECT id FROM roles WHERE name = 'user' AND is_active = 1")
            default_role_row = cursor.fetchone()
            default_role_id = default_role_row[0] if default_role_row else None

            # Tüm kullanıcıları tek transaction'da ekle
            user_values = []
            for user_data in users_data:
                password_hash = self._hash_password(user_data.get('password', 'defaultpass'))
                user_values.append((
                    user_data.get('username'),
                    user_data.get('email'),
                    password_hash,
                    user_data.get('first_name', ''),
                    user_data.get('last_name', ''),
                    user_data.get('phone'),
                    user_data.get('department'),
                    user_data.get('position'),
                    user_data.get('is_active', True),
                    user_data.get('is_verified', False),
                    created_by,
                    created_by
                ))

            # Toplu insert - users (tek execute ile çok daha hızlı!)
            cursor.executemany("""
                INSERT INTO users 
                (username, email, password_hash, first_name, last_name, phone, 
                 department, position, is_active, is_verified, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, user_values)

            # Son eklenen kullanıcıların ID'lerini al (bulk select ile)
            usernames = [user_data['username'] for user_data in users_data]
            placeholders = ','.join(['?' for _ in usernames])
            cursor.execute(f"""
                SELECT id, username FROM users 
                WHERE username IN ({placeholders})
                ORDER BY id
            """, usernames)

            user_id_map = {row[1]: row[0] for row in cursor.fetchall()}

            # User profiles ve roller için toplu insert hazırla
            profile_values = []
            role_values = []

            for user_data in users_data:
                user_id = user_id_map.get(user_data['username'])
                if user_id:
                    created_user_ids.append(user_id)
                    profile_values.append((user_id,))

                    if default_role_id:
                        role_values.append((user_id, default_role_id, created_by))

            # Toplu insert - profiles
            if profile_values:
                cursor.executemany("INSERT INTO user_profiles (user_id) VALUES (?)", profile_values)

            # Toplu insert - roles
            if role_values:
                cursor.executemany("""
                    INSERT OR IGNORE INTO user_roles (user_id, role_id, assigned_by)
                    VALUES (?, ?, ?)
                """, role_values)

            # Tek commit - çok daha hızlı!
            conn.commit()
            logging.info(self.lm.tr("log_bulk_user_created", "[OK] {} kullanıcı toplu olarak oluşturuldu").format(len(created_user_ids)))
            
            # Audit log (batch olarak, email gönderme yok - test performansı için)
            # Email gönderme bu metodda yok, çünkü bulk işlemlerde gereksiz yavaşlatır

            return created_user_ids

        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_bulk_user_creation_error", "[HATA] Toplu kullanıcı oluşturma hatası: {}").format(e))
            return []
        finally:
            conn.close()

    def get_users(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Kullanıcıları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT u.id, u.username, u.email, u.first_name, u.last_name, 
                       u.phone, u.department, u.position, u.is_active, u.is_verified,
                       u.last_login, u.created_at, u.updated_at,
                       GROUP_CONCAT(r.display_name, ', ') as roles,
                       GROUP_CONCAT(r.name, ',') as role_keys
                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = 1
                LEFT JOIN roles r ON ur.role_id = r.id AND r.is_active = 1
            """

            conditions = []
            params = []

            if filters:
                if filters.get('is_active') is not None:
                    conditions.append("u.is_active = ?")
                    params.append(filters['is_active'])

                if filters.get('department'):
                    conditions.append("u.department = ?")
                    params.append(filters['department'])

                if filters.get('search'):
                    conditions.append("(u.username LIKE ? OR u.email LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ?)")
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term, search_term, search_term])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " GROUP BY u.id ORDER BY u.created_at DESC"

            cursor.execute(query, params)

            columns = [description[0] for description in cursor.description]
            users = []

            for row in cursor.fetchall():
                user = dict(zip(columns, row))
                users.append(user)

            return users

        except Exception as e:
            logging.error(self.lm.tr("log_user_fetch_error", "Kullanıcılar getirilirken hata: {}").format(e))
            return []
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """ID ile kullanıcı getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            try:
                cursor.execute("""
                    SELECT u.*, up.language, up.timezone, up.theme, up.notifications_enabled,
                           GROUP_CONCAT(r.name, ', ') as roles
                    FROM users u
                    LEFT JOIN user_profiles up ON u.id = up.user_id
                    LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = 1
                    LEFT JOIN roles r ON ur.role_id = r.id AND r.is_active = 1
                    WHERE u.id = ?
                    GROUP BY u.id
                """, (user_id,))
            except sqlite3.OperationalError:
                cursor.execute("""
                    SELECT u.*, GROUP_CONCAT(r.name, ', ') as roles
                    FROM users u
                    LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = 1
                    LEFT JOIN roles r ON ur.role_id = r.id AND r.is_active = 1
                    WHERE u.id = ?
                    GROUP BY u.id
                """, (user_id,))

            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                user = dict(zip(columns, row))
                return user

            return None

        except Exception as e:
            logging.error(self.lm.tr("log_user_fetch_error_single", "Kullanıcı getirilirken hata: {}").format(e))
            return None
        finally:
            conn.close()

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Username ile kullanıcı getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            try:
                cursor.execute("""
                    SELECT u.*, up.language, up.timezone, up.theme, up.notifications_enabled,
                           GROUP_CONCAT(r.name, ', ') as roles
                    FROM users u
                    LEFT JOIN user_profiles up ON u.id = up.user_id
                    LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = 1
                    LEFT JOIN roles r ON ur.role_id = r.id AND r.is_active = 1
                    WHERE u.username = ? AND u.is_active = 1
                    GROUP BY u.id
                """, (username,))
            except sqlite3.OperationalError:
                cursor.execute("""
                    SELECT u.*, GROUP_CONCAT(r.name, ', ') as roles
                    FROM users u
                    LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = 1
                    LEFT JOIN roles r ON ur.role_id = r.id AND r.is_active = 1
                    WHERE u.username = ? AND u.is_active = 1
                    GROUP BY u.id
                """, (username,))

            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                user = dict(zip(columns, row))
                return user

            return None

        except Exception as e:
            logging.error(self.lm.tr("log_user_fetch_by_username_error", "Kullanıcı getirilirken hata: {}").format(e))
            return None
        finally:
            conn.close()

    def update_user(self, user_id: int, user_data: Dict, updated_by: Optional[int] = None) -> bool:
        """Kullanıcı güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Eski değerleri al
            old_user = self.get_user_by_id(user_id)
            if not old_user:
                return False

            # Güncellenecek alanları hazırla
            update_fields = []
            params = []

            for field in ['username', 'email', 'first_name', 'last_name', 'phone', 'department', 'position', 'is_active']:
                if field in user_data:
                    update_fields.append(f"{field} = ?")
                    params.append(user_data[field])

            if update_fields:
                update_fields.append("updated_by = ?")
                update_fields.append("updated_at = ?")
                params.extend([updated_by, datetime.now().isoformat()])
                params.append(user_id)

                cursor.execute(f"""
                    UPDATE users SET {', '.join(update_fields)}
                    WHERE id = ?
                """, params)

            # Şifre güncelleme (ayrı olarak)
            if 'password' in user_data:
                password_hash = self._hash_password(user_data['password'])
                cursor.execute("""
                    UPDATE users SET password_hash = ?, updated_by = ?, updated_at = ?
                    WHERE id = ?
                """, (password_hash, updated_by, datetime.now().isoformat(), user_id))

            # Rolleri güncelle
            if 'role_ids' in user_data:
                # Mevcut rolleri sil
                cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))

                # Yeni rolleri ekle
                for role_id in user_data['role_ids']:
                    cursor.execute("""
                        INSERT INTO user_roles (user_id, role_id, assigned_by)
                        VALUES (?, ?, ?)
                    """, (user_id, role_id, updated_by))

            # Audit log
            new_user = self.get_user_by_id(user_id)
            self._log_audit(cursor, updated_by, 'update', 'user', user_id, old_user, new_user)

            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_user_update_error", "Kullanıcı güncellenirken hata: {}").format(e))
            return False
        finally:
            conn.close()

    def delete_user(self, user_id: int, deleted_by: Optional[int] = None) -> bool:
        """Kullanıcı sil (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Super user koruması
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            if user_row:
                username = user_row[0]
                try:
                    from security.core.super_user_protection import \
                        check_delete_protection
                except (PermissionError, ImportError, OSError):
                    import importlib.util
                    import os
                    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
                    module_path = os.path.join(base_dir, 'security', 'core', 'super_user_protection.py')
                    spec = importlib.util.spec_from_file_location('security.core.super_user_protection', module_path)
                    assert spec is not None
                    _sup_mod = importlib.util.module_from_spec(spec)
                    assert spec.loader is not None
                    spec.loader.exec_module(_sup_mod)
                    check_delete_protection = _sup_mod.check_delete_protection
                can_delete, message = check_delete_protection(self.db_path, username)
                if not can_delete:
                    logging.info(f" {message}")
                    return False
            # Kullanıcıyı pasif yap
            cursor.execute("""
                UPDATE users SET is_active = 0, updated_by = ?, updated_at = ?
                WHERE id = ?
            """, (deleted_by, datetime.now().isoformat(), user_id))

            # Kullanıcı rollerini pasif yap
            cursor.execute("""
                UPDATE user_roles SET is_active = 0 WHERE user_id = ?
            """, (user_id,))

            conn.commit()

            # Audit log
            self._log_audit(cursor, deleted_by, 'delete', 'user', user_id,
                           {'is_active': True}, {'is_active': False})

            return True

        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_user_delete_error", "Kullanıcı silinirken hata: {}").format(e))
            return False
        finally:
            conn.close()

    def permanent_delete_user(self, user_id: int, deleted_by: Optional[int] = None) -> bool:
        """Kullanıcıyı kalıcı olarak sil"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Önce kullanıcı bilgilerini al (audit için)
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            # Kullanıcı rollerini sil
            cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))

            # Kullanıcı profili varsa sil
            cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))

            # Kullanıcı izinlerini sil
            cursor.execute("DELETE FROM user_permissions WHERE user_id = ?", (user_id,))

            # Kullanıcıyı kalıcı olarak sil
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

            # Audit log
            self._log_audit(cursor, deleted_by, 'permanent_delete', 'user', user_id,
                           user, {})

            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_user_permanent_delete_error", "Kullanıcı kalıcı silinirken hata: {}").format(e))
            return False
        finally:
            conn.close()

    # Rol İşlemleri
    def get_roles(self) -> List[Dict]:
        """Rolleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT r.id, r.name, r.display_name, r.description, r.is_system_role,
                       r.is_active, r.created_at, r.updated_at,
                       COUNT(DISTINCT ur.user_id) as user_count,
                       COUNT(DISTINCT rp.permission_id) as permission_count
                FROM roles r
                LEFT JOIN user_roles ur ON r.id = ur.role_id AND ur.is_active = 1
                LEFT JOIN role_permissions rp ON r.id = rp.role_id
                WHERE r.is_active = 1
                GROUP BY r.id
                ORDER BY r.name
            """)

            columns = [description[0] for description in cursor.description]
            roles = []

            for row in cursor.fetchall():
                role = dict(zip(columns, row))
                roles.append(role)

            return roles

        except Exception as e:
            logging.error(self.lm.tr("log_roles_fetch_error", "Roller getirilirken hata: {}").format(e))
            return []
        finally:
            conn.close()

    def get_permissions(self, module: Optional[str] = None) -> List[Dict]:
        """Yetkileri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT id, name, display_name, description, module, action, resource
                FROM permissions
                WHERE is_active = 1
            """

            params = []
            if module:
                query += " AND module = ?"
                params.append(module)

            query += " ORDER BY module, name"

            cursor.execute(query, params)

            columns = [description[0] for description in cursor.description]
            permissions = []

            for row in cursor.fetchall():
                permission = dict(zip(columns, row))
                permissions.append(permission)

            return permissions

        except Exception as e:
            logging.error(self.lm.tr("log_permissions_fetch_error", "Yetkiler getirilirken hata: {}").format(e))
            return []
        finally:
            conn.close()

    # --- Rol CRUD ve Yetki Atama Metodları ---
    def get_role_by_id(self, role_id: int) -> Optional[Dict]:
        """ID ile rol getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id, name, display_name, description, is_system_role,
                       is_active, created_at, updated_at
                FROM roles
                WHERE id = ?
                """,
                (role_id,),
            )
            row = cursor.fetchone()
            if row:
                columns = [d[0] for d in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logging.error(self.lm.tr("log_role_fetch_error_single", "Rol getirilirken hata: {}").format(e))
            return None
        finally:
            conn.close()

    def create_role(self, role_data: Dict, created_by: Optional[int] = None) -> int:
        """Yeni rol oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO roles (name, display_name, description, is_system_role, is_active, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    role_data["name"],
                    role_data.get("display_name") or role_data["name"],
                    role_data.get("description", ""),
                    int(bool(role_data.get("is_system_role", False))),
                    int(bool(role_data.get("is_active", True))),
                    created_by,
                    datetime.now().isoformat(),
                ),
            )
            role_id = cursor.lastrowid

            # Yetkileri ata (varsa)
            permission_ids = role_data.get("permission_ids", [])
            for pid in permission_ids:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id, granted_by)
                    VALUES (?, ?, ?)
                    """,
                    (role_id, pid, created_by),
                )

            conn.commit()

            # Audit log
            self._log_audit(
                cursor,
                created_by,
                "create",
                "role",
                int(role_id if role_id is not None else -1),
                None,
                {"name": role_data["name"], "display_name": role_data.get("display_name")},
            )

            return int(role_id if role_id is not None else -1)
        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_role_creation_error", "Rol oluşturulurken hata: {}").format(e))
            return -1
        finally:
            conn.close()

    def update_role_simple(self, role_id: int, role_data: Dict, updated_by: Optional[int] = None) -> bool:
        """Rol güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            old_role = self.get_role_by_id(role_id)
            if not old_role:
                return False

            update_fields = []
            params = []
            for field in ["name", "display_name", "description", "is_system_role", "is_active"]:
                if field in role_data:
                    update_fields.append(f"{field} = ?")
                    # booleanları int'e çevir
                    val = role_data[field]
                    if isinstance(val, bool):
                        val = int(val)
                    params.append(val)

            if update_fields:
                update_fields.append("updated_by = ?")
                update_fields.append("updated_at = ?")
                params.extend([updated_by, datetime.now().isoformat(), role_id])
                cursor.execute(
                    f"""
                    UPDATE roles SET {', '.join(update_fields)}
                    WHERE id = ?
                    """,
                    params,
                )

            # Yetkileri güncelle (permission_ids sağlanmışsa)
            if "permission_ids" in role_data:
                cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
                for pid in role_data.get("permission_ids", []):
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id, granted_by)
                        VALUES (?, ?, ?)
                        """,
                        (role_id, pid, updated_by),
                    )

            conn.commit()

            new_role = self.get_role_by_id(role_id)
            self._log_audit(cursor, updated_by, "update", "role", role_id, old_role, new_role)
            return True
        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_role_update_error", "Rol güncellenirken hata: {}").format(e))
            return False
        finally:
            conn.close()

    def delete_role(self, role_id: int, deleted_by: Optional[int] = None) -> bool:
        """Rolü sil (soft delete). Sistem rollerini silmeye izin verme."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            role = self.get_role_by_id(role_id)
            if not role:
                return False
            if role.get("is_system_role"):
                logging.error(self.lm.tr("log_system_role_delete_error", "Sistem rolü silinemez"))
                return False

            cursor.execute(
                """
                UPDATE roles SET is_active = 0, updated_by = ?, updated_at = ?
                WHERE id = ?
                """,
                (deleted_by, datetime.now().isoformat(), role_id),
            )
            conn.commit()

            self._log_audit(
                cursor,
                deleted_by,
                "delete",
                "role",
                role_id,
                {"is_active": True},
                {"is_active": False},
            )
            return True
        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_role_delete_error", "Rol silinirken hata: {}").format(e))
            return False
        finally:
            conn.close()

    def get_role_permissions(self, role_id: int) -> List[Dict]:
        """Rolün yetkilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT p.id, p.name, p.display_name, p.module, p.action, p.resource
                FROM permissions p
                INNER JOIN role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ? AND p.is_active = 1
                ORDER BY p.module, p.name
                """,
                (role_id,),
            )
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logging.error(self.lm.tr("log_role_permissions_fetch_error", "Rol yetkileri getirilirken hata: {}").format(e))
            return []
        finally:
            conn.close()

    def set_role_permissions(self, role_id: int, permission_ids: List[int], updated_by: Optional[int] = None) -> bool:
        """Rolün yetkilerini yeniden ata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
            for pid in permission_ids:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id, granted_by)
                    VALUES (?, ?, ?)
                    """,
                    (role_id, pid, updated_by),
                )
            conn.commit()
            self._log_audit(cursor, updated_by, "update_permissions", "role", role_id, None, {"count": len(permission_ids)})
            return True
        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_role_permission_assignment_error", "Rol yetkileri atanırken hata: {}").format(e))
            return False
        finally:
            conn.close()

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Kullanıcının yetkilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Önce kullanıcının rollerini kontrol et; admin/super_admin ise tüm aktif izinleri ver
            cursor.execute(
                """
                SELECT r.name
                FROM roles r
                INNER JOIN user_roles ur ON ur.role_id = r.id
                WHERE ur.user_id = ? AND ur.is_active = 1 AND r.is_active = 1
                """,
                (user_id,)
            )
            role_names = [row[0] for row in cursor.fetchall()]

            if role_names:
                if 'super_admin' in role_names or 'admin' in role_names:
                    cursor.execute("SELECT name FROM permissions WHERE is_active = 1")
                    return [row[0] for row in cursor.fetchall()]
            else:
                # Rol ataması yoksa username'e göre tam yetki ver (admin/super kullanıcılar)
                try:
                    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
                    row = cursor.fetchone()
                    uname = row[0] if row else None
                    if uname in ('admin', '_super_', '__super__'):
                        cursor.execute("SELECT name FROM permissions WHERE is_active = 1")
                        return [row[0] for row in cursor.fetchall()]
                except Exception as e:
                    logging.error(f'Silent error in user_manager.py: {str(e)}')

            cursor.execute("""
                SELECT DISTINCT p.name
                FROM permissions p
                INNER JOIN (
                    -- Rol yetkileri
                    SELECT rp.permission_id
                    FROM user_roles ur
                    INNER JOIN role_permissions rp ON ur.role_id = rp.role_id
                    WHERE ur.user_id = ? AND ur.is_active = 1
                    
                    UNION
                    
                    -- Direkt kullanıcı yetkileri
                    SELECT permission_id
                    FROM user_permissions
                    WHERE user_id = ? AND is_active = 1
                ) user_perms ON p.id = user_perms.permission_id
                WHERE p.is_active = 1
            """, (user_id, user_id))

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logging.error(self.lm.tr("log_user_permissions_fetch_error", "Kullanıcı yetkileri getirilirken hata: {}").format(e))
            return []
        finally:
            conn.close()

    def has_permission(self, user_id: int, permission_name: str) -> bool:
        """Kullanıcının belirli bir yetkiye sahip olup olmadığını kontrol et"""
        user_permissions = self.get_user_permissions(user_id)
        return permission_name in user_permissions

    def get_departments(self) -> List[Dict]:
        """Departmanları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT d.id, d.name, d.code, d.description, d.parent_id,
                       d.manager_id, d.is_active, d.created_at, d.updated_at,
                       pd.name as parent_name,
                       m.first_name || ' ' || m.last_name as manager_name,
                       COUNT(u.id) as user_count
                FROM departments d
                LEFT JOIN departments pd ON d.parent_id = pd.id
                LEFT JOIN users m ON d.manager_id = m.id
                LEFT JOIN users u ON u.department = d.name
                WHERE d.is_active = 1
                GROUP BY d.id
                ORDER BY d.name
            """)

            columns = [description[0] for description in cursor.description]
            departments = []

            for row in cursor.fetchall():
                department = dict(zip(columns, row))
                departments.append(department)

            return departments

        except Exception as e:
            logging.error(self.lm.tr("log_departments_fetch_error", "Departmanlar getirilirken hata: {}").format(e))
            return []
        finally:
            conn.close()

    def create_department(self, dept_data: Dict, created_by: Optional[int] = None) -> bool:
        """Yeni departman oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO departments (company_id, name, code, description, is_active, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                1,  # Default company_id
                dept_data['name'],
                dept_data['code'],
                dept_data.get('description', ''),
                dept_data.get('is_active', True),
                created_by,
                datetime.now().isoformat()
            ))

            conn.commit()

            # Audit log
            self._log_audit(cursor, created_by, 'create', 'department', int(cursor.lastrowid if cursor.lastrowid is not None else -1),
                           {}, dept_data)

            return True

        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_department_creation_error", "Departman oluşturulurken hata: {}").format(e))
            return False
        finally:
            conn.close()

    def update_department(self, dept_id: int, dept_data: Dict, updated_by: Optional[int] = None) -> bool:
        """Departman güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Eski değerleri al
            old_dept = self.get_department_by_id(dept_id)
            if not old_dept:
                return False

            # Güncellenecek alanları hazırla
            update_fields = []
            params = []

            for field in ['name', 'code', 'description', 'is_active']:
                if field in dept_data:
                    update_fields.append(f"{field} = ?")
                    params.append(dept_data[field])

            if update_fields:
                update_fields.append("updated_by = ?")
                update_fields.append("updated_at = ?")
                params.extend([updated_by, datetime.now().isoformat()])
                params.append(dept_id)

                cursor.execute(f"""
                    UPDATE departments SET {', '.join(update_fields)}
                    WHERE id = ?
                """, params)

            conn.commit()

            # Audit log
            self._log_audit(cursor, updated_by, 'update', 'department', dept_id,
                           old_dept, dept_data)

            return True

        except Exception as e:
            conn.rollback()
            logging.error(f"Departman güncellenirken hata: {e}")
            return False
        finally:
            conn.close()

    def delete_department(self, dept_id: int, deleted_by: Optional[int] = None) -> bool:
        """Departman sil (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Departmanı pasif yap
            cursor.execute("""
                UPDATE departments SET is_active = 0, updated_by = ?, updated_at = ?
                WHERE id = ?
            """, (deleted_by, datetime.now().isoformat(), dept_id))

            conn.commit()

            # Audit log
            self._log_audit(cursor, deleted_by, 'delete', 'department', dept_id,
                           {'is_active': True}, {'is_active': False})

            return True

        except Exception as e:
            conn.rollback()
            logging.error(f"Departman silinirken hata: {e}")
            return False
        finally:
            conn.close()

    def get_department_by_id(self, dept_id: int) -> Optional[Dict]:
        """ID ile departman getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, name, code, description, parent_id,
                       manager_id, is_active, created_at, updated_at
                FROM departments
                WHERE id = ?
            """, (dept_id,))

            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))

            return None

        except Exception as e:
            logging.error(self.lm.tr("log_department_fetch_error_single", "Departman getirilirken hata: {}").format(e))
            return None
        finally:
            conn.close()

    def update_user_password(self, username: str, new_password: str, updated_by: Optional[int] = None) -> bool:
        """Kullanıcı şifresini güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Super user koruması
            try:
                from security.core.super_user_protection import \
                    check_password_change_protection
            except (PermissionError, ImportError, OSError):
                import importlib.util
                import os
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
                module_path = os.path.join(base_dir, 'security', 'core', 'super_user_protection.py')
                spec = importlib.util.spec_from_file_location('security.core.super_user_protection', module_path)
                assert spec is not None
                _sup_mod = importlib.util.module_from_spec(spec)
                assert spec.loader is not None
                spec.loader.exec_module(_sup_mod)
                check_password_change_protection = _sup_mod.check_password_change_protection
            can_change, message = check_password_change_protection(self.db_path, username, new_password)
            if not can_change:
                logging.info(f" {message}")
                return False
            # Kullanıcıyı bul
            user = self.get_user_by_username(username)
            if not user:
                return False

            # Şifreyi hash'le
            password_hash = self._hash_password(new_password)

            # Şifreyi güncelle
            cursor.execute("""
                UPDATE users SET password_hash = ?, updated_by = ?, updated_at = ?
                WHERE username = ?
            """, (password_hash, updated_by, datetime.now().isoformat(), username))

            conn.commit()

            # Audit log
            self._log_audit(cursor, updated_by, 'update_password', 'user', user['id'],
                           {}, {'password_changed': True})

            return True

        except Exception as e:
            conn.rollback()
            logging.error(self.lm.tr("log_password_update_error", "Şifre güncellenirken hata: {}").format(e))
            return False
        finally:
            conn.close()

    def get_user_statistics(self) -> Dict:
        """Kullanıcı istatistiklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            total_users = cursor.fetchone()[0]

            # Aktif kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1 AND last_login >= date('now', '-30 days')")
            active_users = cursor.fetchone()[0]

            # Doğrulanmış kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1 AND is_verified = 1")
            verified_users = cursor.fetchone()[0]

            # Departman bazlı kullanıcı sayıları
            cursor.execute("""
                SELECT department, COUNT(*) as user_count
                FROM users
                WHERE is_active = 1 AND department IS NOT NULL
                GROUP BY department
                ORDER BY user_count DESC
            """)

            department_stats = {}
            for row in cursor.fetchall():
                department_stats[row[0]] = row[1]

            # Rol bazlı kullanıcı sayıları
            cursor.execute("""
                SELECT r.display_name, COUNT(ur.user_id) as user_count
                FROM roles r
                LEFT JOIN user_roles ur ON r.id = ur.role_id AND ur.is_active = 1
                WHERE r.is_active = 1
                GROUP BY r.id, r.display_name
                ORDER BY user_count DESC
            """)

            role_stats = {}
            for row in cursor.fetchall():
                role_stats[row[0]] = row[1]

            return {
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'department_stats': department_stats,
                'role_stats': role_stats
            }

        except Exception as e:
            logging.error(self.lm.tr("log_user_stats_fetch_error", "Kullanıcı istatistikleri getirilirken hata: {}").format(e))
            return {
                'total_users': 0,
                'active_users': 0,
                'verified_users': 0,
                'department_stats': {},
                'role_stats': {}
            }
        finally:
            conn.close()

    def _log_audit(self, cursor, user_id: Optional[int], action: str, resource_type: str,
                   resource_id: int, old_values: Optional[Dict] = None, new_values: Optional[Dict] = None) -> None:
        """Audit log kaydet - Schema uyumlu versiyon"""
        try:
            old_str = json.dumps(old_values, ensure_ascii=False) if old_values else None
            new_str = json.dumps(new_values, ensure_ascii=False) if new_values else None
            
            payload = {}
            if old_values: payload['old'] = old_values
            if new_values: payload['new'] = new_values
            payload_str = json.dumps(payload, ensure_ascii=False) if payload else None

            cursor.execute("""
                INSERT INTO audit_logs 
                (user_id, action, resource_type, resource_id, payload_json, old_values, new_values)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                action,
                resource_type,
                resource_id,
                payload_str,
                old_str,
                new_str
            ))
        except Exception as e:
            # Audit log hatası programı durdurmasın ama loglansın
            import logging
            logging.error(f"Audit log recording failed: {e}")
            pass

    def get_audit_logs(self, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
        """Audit logları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT al.id, al.user_id, al.action, al.resource_type, al.resource_id,
                       al.old_values, al.new_values, al.ip_address, al.created_at,
                       u.username, u.first_name, u.last_name
                FROM audit_logs al
                LEFT JOIN users u ON al.user_id = u.id
            """

            conditions = []
            params = []

            if filters:
                if filters.get('user_id'):
                    conditions.append("al.user_id = ?")
                    params.append(filters['user_id'])

                if filters.get('action'):
                    conditions.append("al.action = ?")
                    params.append(filters['action'])

                if filters.get('resource_type'):
                    conditions.append("al.resource_type = ?")
                    params.append(filters['resource_type'])

                if filters.get('date_from'):
                    conditions.append("al.created_at >= ?")
                    params.append(filters['date_from'])

                if filters.get('date_to'):
                    conditions.append("al.created_at <= ?")
                    params.append(filters['date_to'])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY al.created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            columns = [description[0] for description in cursor.description]
            logs = []

            for row in cursor.fetchall():
                log = dict(zip(columns, row))
                logs.append(log)

            return logs

        except Exception as e:
            import logging
            logging.error(f"Error fetching audit logs: {e}")
            return []
        finally:
            conn.close()

    def get_all_users(self) -> List[Dict]:
        """Tüm kullanıcıları getir"""
        return self.get_users()

    # removed duplicate, use typed implementation below

    def get_all_departments(self) -> List[Dict]:
        """Tüm departmanları getir"""
        return self.get_departments()

    def get_all_permissions(self) -> List[Dict]:
        """Tüm yetkileri getir"""
        return self.get_permissions()

    def add_user(self, user_data: Dict, created_by: Optional[int] = None) -> int:
        """Yeni kullanıcı ekle (create_user ile aynı)"""
        return self.create_user(user_data, created_by)

    def get_user(self, user_id: int) -> Optional[Dict]:
        """ID ile kullanıcı getir (get_user_by_id ile aynı)"""
        return self.get_user_by_id(user_id)

    # removed duplicate get_user_statistics

    # === ROL YÖNETİMİ FONKSİYONLARI ===

    def get_all_roles(self) -> List[Dict]:
        """Tüm rolleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, name, display_name, description, is_system_role, is_active, created_at, updated_at
                FROM roles 
                WHERE is_active = 1
                ORDER BY name
            """)

            columns = [description[0] for description in cursor.description]
            roles = []

            for row in cursor.fetchall():
                role = dict(zip(columns, row))
                roles.append(role)

            return roles

        except Exception as e:
            logging.error(f"Roller getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    # removed duplicate get_role_by_id (see above at 912)

    def get_role_user_count(self, role_id: int) -> int:
        """Roldeki kullanıcı sayısını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*) FROM user_roles 
                WHERE role_id = ?
            """, (role_id,))

            return cursor.fetchone()[0]

        except Exception as e:
            logging.error(f"Rol kullanıcı sayısı getirilirken hata: {e}")
            return 0
        finally:
            conn.close()

    def get_role_permission_count(self, role_id: int) -> int:
        """Roldeki yetki sayısını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*) FROM role_permissions 
                WHERE role_id = ?
            """, (role_id,))

            return cursor.fetchone()[0]

        except Exception as e:
            logging.error(f"Rol yetki sayısı getirilirken hata: {e}")
            return 0
        finally:
            conn.close()

    def get_role_users(self, role_id: int) -> List[Dict]:
        """Roldeki kullanıcıları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT u.id, u.username, u.first_name, u.last_name, u.email
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                WHERE ur.role_id = ? AND u.is_active = 1
                ORDER BY u.username
            """, (role_id,))

            columns = [description[0] for description in cursor.description]
            users = []

            for row in cursor.fetchall():
                user = dict(zip(columns, row))
                users.append(user)

            return users

        except Exception as e:
            logging.error(f"Rol kullanıcıları getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    # removed duplicate get_role_permissions (see above at 1089)

    def create_role_simple(self, role_data: Dict, created_by: Optional[int] = None) -> bool:
        """Yeni rol oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO roles (name, display_name, description, is_system_role, is_active, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                role_data['name'],
                role_data.get('display_name', role_data['name']),
                role_data.get('description', ''),
                role_data.get('is_system_role', False),
                role_data.get('is_active', True),
                created_by
            ))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Rol oluşturulurken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_role(self, role_id: int, role_data: Dict, updated_by: Optional[int] = None) -> bool:
        """Rol güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE roles 
                SET role_name = ?, description = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                role_data['role_name'],
                role_data.get('description', ''),
                role_data.get('is_active', True),
                role_id
            ))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Rol güncellenirken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_role_simple(self, role_id: int) -> bool:
        """Rol sil"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Önce rol-permission ilişkilerini sil
            cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))

            # Sonra rolü sil
            cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))

            conn.commit()
            return True

        except Exception as e:
            logging.error(self.lm.tr("log_role_permission_assignment_error", "Rol yetkileri atanırken hata: {}").format(e))
            conn.rollback()
            return False
        finally:
            conn.close()

    def assign_role_to_user(self, user_id: int, role_id: int) -> bool:
        """Kullanıcıya rol ata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Önce mevcut rolü kaldır
            cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))

            # Yeni rolü ata
            cursor.execute("""
                INSERT INTO user_roles (user_id, role_id, assigned_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, role_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Kullanıcıya rol atanırken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Kullanıcıdan rol kaldır"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM user_roles 
                WHERE user_id = ? AND role_id = ?
            """, (user_id, role_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Kullanıcıdan rol kaldırılırken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
