import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Library Manager
Kurumsal Sürdürülebilirlik Politika Kütüphanesi
Politika şablonları ve modül eşleştirme sistemi
"""

import os
import sqlite3
from typing import Dict, List
from config.icons import Icons
from config.database import DB_PATH


class PolicyLibraryManager:
    """Politika kütüphanesi yöneticisi"""

    def __init__(self, db_path: str, templates_dir: str = 'data/policy_templates') -> None:
        self.db_path = db_path
        self.templates_dir = templates_dir
        self._ensure_schema()
        self._ensure_templates_dir()

    def _ensure_schema(self) -> None:
        """Veritabanı şemasını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Politika kategorileri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policy_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_code VARCHAR(50) UNIQUE NOT NULL,
                    category_name VARCHAR(255) NOT NULL,
                    category_name_tr VARCHAR(255),
                    description TEXT,
                    icon VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Politika şablonları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policy_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_code VARCHAR(50) UNIQUE NOT NULL,
                    template_name VARCHAR(255) NOT NULL,
                    template_name_tr VARCHAR(255),
                    category_id INTEGER,
                    description TEXT,
                    content TEXT,
                    version VARCHAR(20),
                    language VARCHAR(10) DEFAULT 'tr',
                    file_path VARCHAR(500),
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES policy_categories(id)
                )
            """)

            # Şirket politikaları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    template_id INTEGER,
                    policy_name VARCHAR(255) NOT NULL,
                    policy_code VARCHAR(50),
                    category_id INTEGER,
                    content TEXT,
                    version VARCHAR(20),
                    status VARCHAR(50) DEFAULT 'Draft',
                    approval_date DATE,
                    approved_by VARCHAR(100),
                    review_date DATE,
                    file_path VARCHAR(500),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (template_id) REFERENCES policy_templates(id),
                    FOREIGN KEY (category_id) REFERENCES policy_categories(id)
                )
            """)

            # Politika-Modül eşleştirme tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policy_module_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    policy_id INTEGER NOT NULL,
                    module_name VARCHAR(100) NOT NULL,
                    metric_name VARCHAR(255),
                    target_value VARCHAR(100),
                    mapping_type VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (policy_id) REFERENCES company_policies(id)
                )
            """)

            # Politika-Framework eşleştirme tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policy_framework_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    policy_id INTEGER NOT NULL,
                    framework_type VARCHAR(50) NOT NULL,
                    framework_code VARCHAR(100),
                    alignment_level VARCHAR(50),
                    notes TEXT,
                    FOREIGN KEY (policy_id) REFERENCES company_policies(id)
                )
            """)

            # Uyum matrisi tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_matrix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    policy_id INTEGER NOT NULL,
                    requirement VARCHAR(255) NOT NULL,
                    module_name VARCHAR(100),
                    metric_name VARCHAR(255),
                    target_value VARCHAR(100),
                    current_value VARCHAR(100),
                    compliance_status VARCHAR(50),
                    gap_analysis TEXT,
                    action_plan TEXT,
                    responsible_person VARCHAR(100),
                    due_date DATE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (policy_id) REFERENCES company_policies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Politika kütüphanesi tabloları oluşturuldu")

            # Varsayılan kategorileri ekle
            self._seed_default_categories(cursor)
            conn.commit()

        except Exception as e:
            logging.error(f"[HATA] Politika kütüphanesi şema oluşturma hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _seed_default_categories(self, cursor) -> None:
        """Varsayılan kategorileri ekle"""
        categories = [
            ('ENV', 'Environmental Policy', 'Çevre Politikası', 'Çevresel sürdürülebilirlik politikaları', ''),
            ('SOC', 'Social Policy', 'Sosyal Politika', 'Sosyal sorumluluk politikaları', ''),
            ('GOV', 'Governance Policy', 'Yönetişim Politikası', 'Kurumsal yönetim politikaları', '️'),
            ('ETH', 'Ethics & Compliance', 'Etik ve Uyum', 'Etik kurallar ve uyum politikaları', ''),
            ('HR', 'Human Resources', 'İnsan Kaynakları', 'İK ve İSG politikaları', ''),
            ('SUP', 'Supply Chain', 'Tedarik Zinciri', 'Tedarik zinciri politikaları', ''),
            ('QUA', 'Quality', 'Kalite', 'Kalite yönetimi politikaları', Icons.STAR),
            ('RIS', 'Risk Management', 'Risk Yönetimi', 'Risk yönetimi politikaları', '️')
        ]

        for cat in categories:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO policy_categories 
                    (category_code, category_name, category_name_tr, description, icon)
                    VALUES (?, ?, ?, ?, ?)
                """, cat)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

    def _ensure_templates_dir(self) -> None:
        """Şablon dizinini oluştur"""
        os.makedirs(self.templates_dir, exist_ok=True)

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def get_categories(self) -> List[Dict]:
        """Kategorileri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, category_code, category_name, category_name_tr, 
                       description, icon
                FROM policy_categories
                ORDER BY category_name_tr
            """)

            columns = [desc[0] for desc in cursor.description]
            categories = []

            for row in cursor.fetchall():
                category = dict(zip(columns, row))
                categories.append(category)

            return categories

        except Exception as e:
            logging.error(f"[HATA] Kategoriler getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_templates(self, category_id: int = None) -> List[Dict]:
        """Şablonları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT t.id, t.template_code, t.template_name, t.template_name_tr,
                       t.category_id, c.category_name_tr, t.description, t.version,
                       t.language, t.is_active
                FROM policy_templates t
                LEFT JOIN policy_categories c ON t.category_id = c.id
                WHERE t.is_active = 1
            """

            params = []
            if category_id:
                query += " AND t.category_id = ?"
                params.append(category_id)

            query += " ORDER BY t.template_name_tr"

            cursor.execute(query, params)

            columns = [desc[0] for desc in cursor.description]
            templates = []

            for row in cursor.fetchall():
                template = dict(zip(columns, row))
                templates.append(template)

            return templates

        except Exception as e:
            logging.error(f"[HATA] Şablonlar getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def add_template(self, template_data: Dict) -> bool:
        """Şablon ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO policy_templates 
                (template_code, template_name, template_name_tr, category_id,
                 description, content, version, language, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_data.get('template_code'),
                template_data.get('template_name'),
                template_data.get('template_name_tr'),
                template_data.get('category_id'),
                template_data.get('description'),
                template_data.get('content'),
                template_data.get('version', '1.0'),
                template_data.get('language', 'tr'),
                template_data.get('file_path')
            ))

            conn.commit()
            logging.info(f"[OK] Şablon eklendi: {template_data.get('template_code')}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Şablon ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_company_policy(self, company_id: int, policy_data: Dict) -> bool:
        """Şirket politikası oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO company_policies 
                (company_id, template_id, policy_name, policy_code, category_id,
                 content, version, status, file_path, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                policy_data.get('template_id'),
                policy_data.get('policy_name'),
                policy_data.get('policy_code'),
                policy_data.get('category_id'),
                policy_data.get('content'),
                policy_data.get('version', '1.0'),
                policy_data.get('status', 'Draft'),
                policy_data.get('file_path'),
                policy_data.get('notes')
            ))

            policy_id = cursor.lastrowid
            conn.commit()
            logging.info(f"[OK] Şirket politikası oluşturuldu: {policy_id}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Şirket politikası oluşturma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_company_policies(self, company_id: int, category_id: int = None) -> List[Dict]:
        """Şirket politikalarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT p.id, p.policy_name, p.policy_code, p.category_id,
                       c.category_name_tr, p.version, p.status, p.approval_date,
                       p.review_date, p.created_at, p.updated_at
                FROM company_policies p
                LEFT JOIN policy_categories c ON p.category_id = c.id
                WHERE p.company_id = ?
            """

            params = [company_id]
            if category_id:
                query += " AND p.category_id = ?"
                params.append(category_id)

            query += " ORDER BY p.updated_at DESC"

            cursor.execute(query, params)

            columns = [desc[0] for desc in cursor.description]
            policies = []

            for row in cursor.fetchall():
                policy = dict(zip(columns, row))
                policies.append(policy)

            return policies

        except Exception as e:
            logging.error(f"[HATA] Şirket politikaları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def map_policy_to_module(self, policy_id: int, mapping_data: Dict) -> bool:
        """Politikayı modüle eşleştir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO policy_module_mapping 
                (policy_id, module_name, metric_name, target_value, 
                 mapping_type, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                policy_id,
                mapping_data.get('module_name'),
                mapping_data.get('metric_name'),
                mapping_data.get('target_value'),
                mapping_data.get('mapping_type', 'metric'),
                mapping_data.get('description')
            ))

            conn.commit()
            logging.info("[OK] Politika-modül eşleştirmesi eklendi")
            return True

        except Exception as e:
            logging.error(f"[HATA] Politika-modül eşleştirme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_compliance_matrix(self, company_id: int, policy_id: int = None) -> List[Dict]:
        """Uyum matrisini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT cm.id, cm.policy_id, p.policy_name, cm.requirement,
                       cm.module_name, cm.metric_name, cm.target_value,
                       cm.current_value, cm.compliance_status, cm.gap_analysis,
                       cm.action_plan, cm.responsible_person, cm.due_date
                FROM compliance_matrix cm
                JOIN company_policies p ON cm.policy_id = p.id
                WHERE cm.company_id = ?
            """

            params = [company_id]
            if policy_id:
                query += " AND cm.policy_id = ?"
                params.append(policy_id)

            query += " ORDER BY cm.compliance_status, cm.due_date"

            cursor.execute(query, params)

            columns = [desc[0] for desc in cursor.description]
            matrix = []

            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                matrix.append(item)

            return matrix

        except Exception as e:
            logging.error(f"[HATA] Uyum matrisi getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def update_compliance_status(self, matrix_id: int, status_data: Dict) -> bool:
        """Uyum durumunu güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE compliance_matrix 
                SET current_value = ?, compliance_status = ?, 
                    gap_analysis = ?, action_plan = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                status_data.get('current_value'),
                status_data.get('compliance_status'),
                status_data.get('gap_analysis'),
                status_data.get('action_plan'),
                matrix_id
            ))

            conn.commit()
            logging.info("[OK] Uyum durumu güncellendi")
            return True

        except Exception as e:
            logging.error(f"[HATA] Uyum durumu güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_company_policy(self, policy_data: Dict) -> bool:
        """Şirket politikası ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Şirket politikaları tablosu yoksa oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    policy_name VARCHAR(255) NOT NULL,
                    policy_code VARCHAR(50) NOT NULL,
                    category VARCHAR(100),
                    version VARCHAR(20),
                    status VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Politikayı ekle
            cursor.execute("""
                INSERT INTO company_policies 
                (company_id, policy_name, policy_code, version, status, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                policy_data['company_id'],
                policy_data['name'],
                policy_data['code'],
                policy_data.get('version', '1.0'),
                policy_data.get('status', 'Draft'),
                policy_data.get('description', '')
            ))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Şirket politikası ekleme hatası: {e}")
            return False
        finally:
            conn.close()

    def add_compliance_requirement(self, requirement_data: Dict) -> bool:
        """Uyum gereksinimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Uyum matrisi tablosu yoksa oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_matrix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    policy_id INTEGER,
                    policy_name VARCHAR(255),
                    requirement VARCHAR(255) NOT NULL,
                    module VARCHAR(100),
                    metric VARCHAR(255),
                    target_value VARCHAR(255),
                    current_value VARCHAR(255),
                    compliance_status VARCHAR(50),
                    responsible VARCHAR(255),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Gereksinimi ekle
            cursor.execute("""
                INSERT INTO compliance_matrix 
                (company_id, policy_id, requirement, module_name, metric_name, target_value, 
                 current_value, compliance_status, responsible_person, gap_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                requirement_data['company_id'],
                1,  # Varsayılan policy_id
                requirement_data['requirement'],
                requirement_data.get('module', ''),
                requirement_data.get('metric', ''),
                requirement_data.get('target', ''),
                requirement_data.get('current', ''),
                requirement_data.get('status', 'Uyumlu'),
                requirement_data.get('responsible', ''),
                requirement_data.get('description', '')
            ))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Uyum gereksinimi ekleme hatası: {e}")
            return False
        finally:
            conn.close()

    # get_company_policies(company_id, category_id=None) yukarıda tanımlı ve kullanılmaktadır

    def get_compliance_requirements(self, company_id: int) -> List[Dict]:
        """Uyum gereksinimlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM compliance_matrix 
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (company_id,))

            columns = [description[0] for description in cursor.description]
            requirements = []
            for row in cursor.fetchall():
                requirements.append(dict(zip(columns, row)))

            return requirements

        except Exception as e:
            logging.error(f"Uyum gereksinimleri getirme hatası: {e}")
            return []
        finally:
            conn.close()


# Test fonksiyonu
if __name__ == '__main__':
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    manager = PolicyLibraryManager(db_path)

    # Test kategorileri getir
    categories = manager.get_categories()
    logging.info(f"Kategoriler: {len(categories)}")
    for cat in categories:
        logging.info(f"  - {cat['category_name_tr']} ({cat['category_code']})")
