#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı Yönetimi Manager
Kullanıcı, rol, yetki ve audit trail yönetimi
Refactored for Multi-tenancy using BaseTenantManager and DatabaseManager
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from backend.services.email_service import EmailService
except ImportError:
    # Fallback or mock if needed
    try:
        from services.email_service import EmailService
    except ImportError:
        EmailService = None

from yonetim.security.core.crypto import hash_password as secure_hash_password
from yonetim.security.core.crypto import verify_password_compat as secure_verify_password
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager
from backend.utils.language_manager import LanguageManager


class UserManager(BaseTenantManager):
    """Kullanıcı Yönetimi Manager"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            db_path = os.path.join(base_dir, db_path)
            
        # Initialize BaseTenantManager with no specific company context (global manager)
        # We pass company_id=None, but we will provide it explicitly for tenant-specific calls
        super().__init__(db_path, company_id=None)
        
        # DEBUG LOGGING
        logging.info(f"UserManager initialized with db_path: {self.db_path}")
        self.lm = LanguageManager()
        self._ensure_schema()
        
        # Email servisini örnek olarak tut (testlerde patch edilebilsin)
        if EmailService:
            self.email_service = EmailService(db_path=self.db_path)
        else:
            self.email_service = None

    def get_companies(self) -> List[Dict]:
        """Tüm şirketleri getir"""
        try:
            # Şirket tablosu var mı kontrol et
            # GLOBAL table, passing company_id=1 to satisfy BaseTenantManager
            try:
                self.execute_query("SELECT 1 FROM companies LIMIT 1", company_id=1)
            except Exception:
                return []

            rows = self.execute_query("""
                SELECT id, name, sector, country
                FROM companies
                ORDER BY name
            """, company_id=1)

            companies = []
            for row in rows:
                companies.append(dict(row))

            return companies

        except Exception as e:
            logging.error(f"Error fetching companies: {e}")
            return []

    def get_user_company(self, user_id: int) -> Optional[int]:
        """Kullanıcının birincil şirket ID'sini döndür"""
        try:
            # Önce birincil şirketi ara
            row = self.select_one(
                "user_companies", 
                columns="company_id", 
                where="user_id = ? AND is_primary = 1", 
                params=(user_id,),
                company_id=1 # Global table
            )
            if row:
                return row['company_id']
            
            # Birincil yoksa ilk şirketi döndür
            rows = self.execute_query("""
                SELECT company_id FROM user_companies 
                WHERE user_id = ?
                ORDER BY id ASC LIMIT 1
            """, (user_id,), company_id=1)
            
            if rows:
                return rows[0]['company_id']
                
            return None
        except Exception as e:
            logging.error(f"Error getting user company: {e}")
            return None

    def get_user_company_ids(self, user_id: int) -> List[int]:
        """Kullanıcının tüm şirket ID'lerini getir"""
        try:
            rows = self.execute_query("SELECT company_id FROM user_companies WHERE user_id = ?", (user_id,), company_id=1)
            return [row['company_id'] for row in rows]
        except Exception as e:
            logging.error(f"Error fetching user companies: {e}")
            return []

    def delete_role(self, role_id: int, deleted_by: Optional[int] = None) -> bool:
        """Rol sil (soft delete)"""
        try:
            # Sistem rolü kontrolü
            role = self.get_role_by_id(role_id)
            if role and role.get('is_system_role'):
                return False

            self.execute_update("UPDATE roles SET is_active = 0 WHERE id = ?", (role_id,), company_id=1)
            return True
        except Exception as e:
            logging.error(f"Error deleting role: {e}")
            return False

    def get_role_permissions(self, role_id: int) -> List[int]:
        """Rolün yetki ID'lerini getir"""
        try:
            rows = self.execute_query("SELECT permission_id FROM role_permissions WHERE role_id = ?", (role_id,), company_id=1)
            return [row['permission_id'] for row in rows]
        except Exception as e:
            logging.error(f"Error fetching role permissions: {e}")
            return []

    def get_role_by_id(self, role_id: int) -> Optional[Dict]:
        """Rol bilgilerini getir (Helper)"""
        try:
            row = self.select_one("roles", where="id = ?", params=(role_id,), company_id=1)
            return dict(row) if row else None
        except Exception:
            return None

    def log_audit(self, company_id: int, user_id: Optional[int], action: str, resource_type: str, resource_id: Optional[str] = None, details: Optional[str] = None, ip_address: Optional[str] = None) -> bool:
        """Denetim izi kaydı oluştur"""
        try:
            # audit_logs table usually has company_id if multi-tenant.
            # We explicitly pass company_id to execute_update.
            # If audit_logs is NOT in GLOBAL_TABLES, inject_tenant_filter will be called.
            # If we manually include company_id in INSERT, injection is skipped.
            self.execute_update("""
                INSERT INTO audit_logs (company_id, user_id, action, resource_type, resource_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, user_id, action, resource_type, resource_id, details, ip_address), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error logging audit: {e}")
            return False

    def _ensure_schema(self) -> None:
        """Kullanıcı yönetimi şemasını oluştur"""
        try:
            # Şema dosyasını oku ve çalıştır
            schema_file = os.path.join(os.path.dirname(__file__), 'user_schema.sql')
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # SQL komutlarını çalıştır via DatabaseManager
            self.db.execute_script(schema_sql)

            # Varsayılan verileri oluştur
            self._create_default_data()

            logging.info(self.lm.tr("log_schema_created", "Kullanıcı yönetimi şeması başarıyla oluşturuldu"))
        
        except Exception as e:
            logging.error(self.lm.tr("log_schema_creation_error", "Kullanıcı yönetimi şeması oluşturulurken hata: {}").format(e))

    def _create_default_data(self) -> None:
        """Varsayılan verileri oluştur"""
        # Varsayılan roller
        default_roles = [
            ('super_admin', 'Süper Yönetici', 'Sistemin tam kontrolüne sahip kullanıcı', 1),
            ('admin', 'Yönetici', 'Sistem yönetimi yetkilerine sahip kullanıcı', 0),
            ('manager', 'Müdür', 'Departman yönetimi yetkilerine sahip kullanıcı', 0),
            ('analyst', 'Analist', 'Veri analizi ve raporlama yetkilerine sahip kullanıcı', 0),
            ('user', 'Kullanıcı', 'Temel kullanıcı yetkileri', 0),
            ('viewer', 'Görüntüleyici', 'Sadece okuma yetkisi olan kullanıcı', 0),
            ('ic_paydas', 'İç Paydaş', 'Kurum içi paydaş (Çalışan vb.)', 0),
            ('dis_paydas', 'Dış Paydaş', 'Kurum dışı paydaş (Müşteri, Tedarikçi vb.)', 0)
        ]

        # Use context manager for transaction-like block (optional, but good for performance)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for role in default_roles:
                cursor.execute("""
                    INSERT OR IGNORE INTO roles (name, display_name, description, is_system_role)
                    VALUES (?, ?, ?, ?)
                """, role)

            # Varsayılan yetkiler (Dinamik oluşturulur)
            modules = [
                ('sdg', 'Sürdürülebilir Kalkınma Amaçları'),
                ('gri', 'GRI Raporlama'),
                ('tsrs', 'TSRS Raporlama'),
                ('esg', 'ESG Göstergeleri'),
                ('skdm', 'Sınırda Karbon Düzenleme'),
                ('csrd', 'Kurumsal Sürdürülebilirlik'),
                ('taxonomy', 'AB Taksonomisi'),
                ('carbon', 'Karbon Ayak İzi'),
                ('energy', 'Enerji Yönetimi'),
                ('water', 'Su Yönetimi'),
                ('waste', 'Atık Yönetimi'),
                ('social', 'Sosyal Sürdürülebilirlik'),
                ('governance', 'Kurumsal Yönetişim'),
                ('supply_chain', 'Tedarik Zinciri'),
                ('product_tech', 'Ürün ve Teknoloji'),
                ('strategic', 'Stratejik Yönetim'),
                ('provenance', 'Veri Kaynağı'),
                ('prioritization', 'Önceliklendirme'),
                ('mapping', 'Standart Eşleştirme'),
                ('reporting', 'Raporlama'),
                ('user_management', 'Kullanıcı Yönetimi'),
                ('system', 'Sistem Yönetimi'),
                ('dashboard', 'Dashboard'),
                ('company', 'Şirket Bilgileri'),
                ('data', 'Veri Yönetimi'),
                ('forms', 'Form Yönetimi'),
                ('tasks', 'Görev Yönetimi'),
                ('files', 'Dosya Yönetimi'),
                ('hr', 'İnsan Kaynakları'),
                ('policy', 'Politika Kütüphanesi'),
                ('surveys', 'Anket Yönetimi')
            ]

            actions = [
                ('read', 'Görüntüle', 'görüntüleme'),
                ('create', 'Oluştur', 'oluşturma'),
                ('update', 'Güncelle', 'güncelleme'),
                ('delete', 'Sil', 'silme')
            ]

            default_permissions = []
            
            # Dinamik yetkileri oluştur
            for mod_code, mod_name in modules:
                for act_code, act_name, act_desc in actions:
                    perm_code = f"{mod_code}.{act_code}"
                    # user_management için özel adlandırma
                    if mod_code == 'user_management' and act_code == 'create':
                        # Mevcut yapı korunuyor: user.create
                        continue
                    
                    default_permissions.append((
                        perm_code,
                        f"{mod_name} {act_name}",
                        f"{mod_name} modülü {act_desc} yetkisi",
                        mod_code,
                        act_code,
                        mod_code
                    ))

            # Özel yetkiler (Eski yapı uyumluluğu ve özel aksiyonlar)
            special_permissions = [
                # Kullanıcı ve Rol Yönetimi (Eski format)
                ('user.create', 'Kullanıcı Oluştur', 'Yeni kullanıcı oluşturma yetkisi', 'user_management', 'create', 'user'),
                ('user.read', 'Kullanıcı Görüntüle', 'Kullanıcı bilgilerini görüntüleme yetkisi', 'user_management', 'read', 'user'),
                ('user.update', 'Kullanıcı Güncelle', 'Kullanıcı bilgilerini güncelleme yetkisi', 'user_management', 'update', 'user'),
                ('user.delete', 'Kullanıcı Sil', 'Kullanıcı silme yetkisi', 'user_management', 'delete', 'user'),
                ('role.create', 'Rol Oluştur', 'Yeni rol oluşturma yetkisi', 'user_management', 'create', 'role'),
                ('role.read', 'Rol Görüntüle', 'Rol bilgilerini görüntüleme yetkisi', 'user_management', 'read', 'role'),
                ('role.update', 'Rol Güncelle', 'Rol bilgilerini güncelleme yetkisi', 'user_management', 'update', 'role'),
                ('role.delete', 'Rol Sil', 'Rol silme yetkisi', 'user_management', 'delete', 'role'),
                
                # Sistem ve Diğerleri
                ('dashboard.advanced', 'Gelişmiş Dashboard', 'Gelişmiş dashboard erişimi', 'dashboard', 'read', 'advanced'),
                ('tasks.auto_create', 'Otomatik Görevler', 'Otomatik görev oluşturma', 'tasks', 'auto_create', 'tasks'),
                ('report.download', 'Rapor İndir', 'Rapor indirme yetkisi', 'reporting', 'download', 'report'),
                ('system.audit', 'Audit Görüntüle', 'Audit loglarını görüntüleme yetkisi', 'system', 'read', 'audit'),
                ('forms.manage', 'Form Yönetimi', 'Form yönetimine erişim', 'forms', 'manage', 'forms'),
                ('system.settings', 'Sistem Ayarları', 'Sistem ayarlarını yönetme yetkisi', 'system', 'manage', 'settings'),
            ]

            # Özel yetkileri ekle (Varsa üzerine yaz, yoksa ekle)
            existing_codes = {p[0] for p in default_permissions}
            for sp in special_permissions:
                if sp[0] not in existing_codes:
                    default_permissions.append(sp)


            # Tablo şemasını kontrol et (bazı kurulumlarda 'code' zorunlu olabilir)
            cursor.execute("PRAGMA table_info(permissions)")
            cols = [row['name'] for row in cursor.fetchall()]
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
                _rp_cols = [row['name'] for row in cursor.fetchall()]
            except Exception:
                _rp_cols = []
            _rp_has_granted_by = 'granted_by' in _rp_cols

            # Admin kullanıcısı oluştur (eğer yoksa)
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
            row = cursor.fetchone()
            if row['count'] == 0:
                admin_password = self._hash_password('admin')
                cursor.execute("""
                    INSERT INTO users 
                    (username, email, password_hash, first_name, last_name, is_active, is_verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ('admin', 'admin@sustainage.com', admin_password, 'Sistem', 'Yöneticisi', 1, 1))

                # Admin rolünü ata
                cursor.execute("SELECT id FROM users WHERE username = 'admin'")
                admin_user_id = cursor.fetchone()['id']

                cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
                admin_role_id = cursor.fetchone()['id']

                cursor.execute("""
                    INSERT INTO user_roles (user_id, role_id, assigned_by)
                    VALUES (?, ?, ?)
                """, (admin_user_id, admin_role_id, admin_user_id))

                # Tüm yetkileri süper admin rolüne ata
                cursor.execute("SELECT id FROM permissions")
                permissions = cursor.fetchall()

                cursor.execute("SELECT id FROM roles WHERE name = 'super_admin'")
                super_admin_role_id = cursor.fetchone()['id']
                for permission in permissions:
                    perm_id = permission['id']
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
                    perm_id = perm['id']
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

            # --- GARANTİ BLOĞU: Admin/Süper Admin rol izinlerini her başlangıçta güvenceye al ---
            # Admin kullanıcı ID'sini al (varsa)
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            row = cursor.fetchone()
            admin_user_id = row['id'] if row else None

            # Süper Admin ve Admin rol ID'lerini al
            cursor.execute("SELECT id FROM roles WHERE name = 'super_admin'")
            row = cursor.fetchone()
            super_admin_role_id = row['id'] if row else None

            cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
            row = cursor.fetchone()
            admin_role_id = row['id'] if row else None

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
            
            # Commit handled by context manager on exit? 
            # DatabaseManager's get_connection context manager handles commit/rollback if exception occurs?
            # Actually get_connection yields conn. user has to commit?
            # No, DatabaseManager context manager:
            # yield conn
            # finally: put back to pool.
            # It DOES NOT auto-commit unless we used execute_update.
            # So I must commit manually here since I used cursor directly.
            conn.commit()

    def _hash_password(self, password: str) -> str:
        """Şifreyi hash'le (Argon2, merkezi güvenlik modülü)"""
        return secure_hash_password(password)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Şifreyi doğrula (geri uyumlu Argon2/PBKDF2/SHA256)"""
        try:
            return secure_verify_password(password_hash, password)
        except Exception:
            return False

    def authenticate(self, username, password) -> Optional[Dict]:
        """Kullanıcı girişi doğrula"""
        try:
            # Users is GLOBAL table. Pass company_id=1.
            rows = self.execute_query("""
                SELECT id, username, password_hash, first_name, last_name, email, is_active 
                FROM users 
                WHERE username = ?
            """, (username,), company_id=1)
            
            if not rows:
                logging.error(f"Auth failed: User {username} not found")
                return None
            
            user = rows[0]
            
            # DEBUG LOG
            stored_hash = user['password_hash']
            # print(f"DEBUG: Auth attempt for {username}. Hash prefix: {stored_hash[:30] if stored_hash else 'None'}", flush=True)
            
            if self._verify_password(password, stored_hash):
                if not user['is_active']: # is_active check
                    logging.error(f"Inactive user login attempt: {username}")
                    return None
                    
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'display_name': f"{user['first_name']} {user['last_name']}"
                }
            else:
                logging.error(f"Auth failed: Password mismatch for {username}")
                return None
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return None

    # Kullanıcı İşlemleri
    def create_user(self, user_data: Dict, created_by: Optional[int] = None) -> int:
        """Yeni kullanıcı oluştur"""
        try:
            # Şifreyi hash'le
            password_hash = self._hash_password(user_data['password'])

            # Ensure company_id context
            if self.company_id is None:
                # Fallback to user_data if available
                if 'company_id' in user_data:
                    self.company_id = user_data['company_id']
                else:
                    raise ValueError("Company ID context missing for create_user")

            cid = self.company_id

            # Since create_user needs lastrowid and multiple inserts, best to use connection.
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users 
                    (company_id, username, email, password_hash, first_name, last_name, phone, 
                     department, position, is_active, is_verified, created_by, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cid,
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
                    INSERT INTO user_profiles (company_id, user_id)
                    VALUES (?, ?)
                """, (cid, user_id,))
                
                # Varsayılan rolü ata (eğer belirtilmişse)
                if 'role_ids' in user_data and user_data['role_ids']:
                    for role_id in user_data['role_ids']:
                        cursor.execute(
                            """
                            INSERT INTO user_roles (company_id, user_id, role_id, assigned_by)
                            VALUES (?, ?, ?, ?)
                            """,
                            (cid, user_id, role_id, created_by),
                        )
                else:
                    # Hiç rol verilmemişse varsayılan 'user' rolünü ata
                    try:
                        # Roles are often global or per-company. Assuming per-company or global with company_id=0/1
                        # But for safety, filter by company_id OR global
                        # Here we assume roles table has company_id
                        cursor.execute("SELECT id FROM roles WHERE name = 'user' AND is_active = 1")
                        row = cursor.fetchone()
                        if row and row[0]:
                            cursor.execute(
                                """
                                INSERT OR IGNORE INTO user_roles (company_id, user_id, role_id, assigned_by)
                                VALUES (?, ?, ?, ?)
                                """,
                                (cid, user_id, row[0], created_by)
                            )
                    except Exception as e:
                        logging.error(f"Error assigning default role: {e}")
                
                conn.commit()
                return user_id
                
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return 0

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """ID ile kullanıcı getir"""
        try:
            row = self.select_one("users", where="id = ?", params=(user_id,), company_id=1)
            if not row:
                return None
            
            user = dict(row)
            
            # Profil bilgilerini de getir
            profile = self.select_one("user_profiles", where="user_id = ?", params=(user_id,), company_id=1)
            if profile:
                user.update(dict(profile))
                
            return user
        except Exception as e:
            logging.error(f"Error getting user by id: {e}")
            return None

    def update_user(self, user_id: int, data: Dict, updated_by: Optional[int] = None) -> bool:
        """Kullanıcı bilgilerini güncelle"""
        try:
            # Users tablosunu güncelle
            user_fields = ['first_name', 'last_name', 'email', 'phone', 'department', 'position', 'is_active']
            update_data = {k: v for k, v in data.items() if k in user_fields}
            
            if updated_by:
                update_data['updated_by'] = updated_by
            update_data['updated_at'] = datetime.now()
            
            if update_data:
                set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
                params = list(update_data.values()) + [user_id]
                self.execute_update(f"UPDATE users SET {set_clause} WHERE id = ?", tuple(params), company_id=1)
            
            # Profil tablosunu güncelle (eğer varsa)
            profile_fields = ['bio', 'address', 'city', 'country', 'postal_code', 'website', 'linkedin', 'twitter']
            profile_data = {k: v for k, v in data.items() if k in profile_fields}
            
            if profile_data:
                # Profil var mı kontrol et
                exists = self.select_one("user_profiles", where="user_id = ?", params=(user_id,), company_id=1)
                if exists:
                    set_clause = ", ".join([f"{k} = ?" for k in profile_data.keys()])
                    params = list(profile_data.values()) + [user_id]
                    self.execute_update(f"UPDATE user_profiles SET {set_clause} WHERE user_id = ?", tuple(params), company_id=1)
                else:
                    cols = ", ".join(['user_id'] + list(profile_data.keys()))
                    placeholders = ", ".join(['?'] * (len(profile_data) + 1))
                    params = [user_id] + list(profile_data.values())
                    self.execute_update(f"INSERT INTO user_profiles ({cols}) VALUES ({placeholders})", tuple(params), company_id=1)
                    
            return True
        except Exception as e:
            logging.error(f"Error updating user: {e}")
            return False

    def delete_user(self, user_id: int, deleted_by: Optional[int] = None) -> bool:
        """Kullanıcıyı sil (Soft delete)"""
        try:
            # is_active = 0 yap
            self.execute_update("UPDATE users SET is_active = 0, updated_by = ?, updated_at = ? WHERE id = ?", 
                               (deleted_by, datetime.now(), user_id), company_id=1)
            return True
        except Exception as e:
            logging.error(f"Error deleting user: {e}")
            return False

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Kullanıcı şifresini değiştir"""
        try:
            password_hash = self._hash_password(new_password)
            self.execute_update("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                               (password_hash, datetime.now(), user_id), company_id=1)
            return True
        except Exception as e:
            logging.error(f"Error changing password: {e}")
            return False

    def assign_role(self, user_id: int, role_id: int, assigned_by: Optional[int] = None) -> bool:
        """Kullanıcıya rol ata"""
        try:
            self.execute_update("""
                INSERT OR IGNORE INTO user_roles (user_id, role_id, assigned_by)
                VALUES (?, ?, ?)
            """, (user_id, role_id, assigned_by), company_id=1)
            return True
        except Exception as e:
            logging.error(f"Error assigning role: {e}")
            return False

    def remove_role(self, user_id: int, role_id: int) -> bool:
        """Kullanıcıdan rolü al"""
        try:
            self.execute_update("DELETE FROM user_roles WHERE user_id = ? AND role_id = ?",
                               (user_id, role_id), company_id=1)
            return True
        except Exception as e:
            logging.error(f"Error removing role: {e}")
            return False

    def get_user_roles(self, user_id: int) -> List[Dict]:
        """Kullanıcının rollerini getir"""
        try:
            rows = self.execute_query("""
                SELECT r.id, r.name, r.display_name, r.description
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ? AND r.is_active = 1
            """, (user_id,), company_id=1)
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error getting user roles: {e}")
            return []

    def get_all_users(self, active_only: bool = True) -> List[Dict]:
        """Tüm kullanıcıları getir"""
        try:
            where = "is_active = 1" if active_only else None
            rows = self.select("users", where=where, order_by="first_name, last_name", company_id=1)
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []
