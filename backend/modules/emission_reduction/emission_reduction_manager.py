#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emisyon Azaltma Projeleri Yöneticisi
"""

import logging
import sqlite3
from typing import Dict, List
from config.database import DB_PATH


class EmissionReductionManager:
    """Emisyon azaltma projeleri yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()

            # Emisyon azaltma projeleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emission_reduction_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    expected_reduction REAL DEFAULT 0.0,
                    actual_reduction REAL DEFAULT 0.0,
                    progress_percentage REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'Aktif',
                    budget REAL DEFAULT 0.0,
                    responsible_person TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies (id)
                )
            """)

            # İlerleme kayıtları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emission_reduction_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    progress_date TEXT NOT NULL,
                    progress_percentage REAL NOT NULL,
                    actual_reduction REAL DEFAULT 0.0,
                    cost REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES emission_reduction_projects (id)
                )
            """)

            # Proje kategorileri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emission_reduction_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    color TEXT DEFAULT '#28a745',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Varsayılan kategorileri ekle
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO emission_reduction_categories (name, description, color) VALUES
                    ('Enerji Verimliliği', 'Enerji tüketimini azaltan projeler', '#28a745'),
                    ('Yenilenebilir Enerji', 'Yenilenebilir enerji kaynakları projeleri', '#17a2b8'),
                    ('Atık Azaltma', 'Atık miktarını azaltan projeler', '#ffc107'),
                    ('Su Verimliliği', 'Su tüketimini azaltan projeler', '#007bff'),
                    ('Ulaşım', 'Ulaşım emisyonlarını azaltan projeler', '#6f42c1'),
                    ('Diğer', 'Diğer emisyon azaltma projeleri', '#6c757d')
                """)
            except sqlite3.OperationalError as e:
                if "no column named name" in str(e):
                    logging.info(f"[WARN] Kategori tablosu farklı yapıda, varsayılan kategoriler eklenemedi: {e}")
                else:
                    raise e

            conn.commit()
            conn.close()

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logging.info(f"[WARN] Veritabanı kilitli, tablolar oluşturulamadı: {e}")
                # Tablolar zaten mevcut olabilir, devam et
            else:
                raise e
        except Exception as e:
            logging.error(f"[WARN] Tablo oluşturma hatası: {e}")
            # Hata olsa bile devam et

    def add_project(self, company_id: int, project_name: str, category: str,
                   description: str = None, start_date: str = None, end_date: str = None,
                   expected_reduction: float = 0.0, budget: float = 0.0,
                   responsible_person: str = None) -> int:
        """Yeni emisyon azaltma projesi ekle"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO emission_reduction_projects 
                (company_id, project_name, category, description, start_date, end_date,
                 expected_reduction, budget, responsible_person)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_name, category, description, start_date, end_date,
                  expected_reduction, budget, responsible_person))

            project_id = cursor.lastrowid
            conn.commit()
            return project_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_projects(self, company_id: int) -> List[Dict]:
        """Şirketin emisyon azaltma projelerini getir"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, project_name, category, description, start_date, end_date,
                   expected_reduction, actual_reduction, progress_percentage, status,
                   budget, responsible_person, created_at
            FROM emission_reduction_projects
            WHERE company_id = ?
            ORDER BY created_at DESC
        """, (company_id,))

        columns = [desc[0] for desc in cursor.description]
        projects = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return projects

    def add_progress(self, project_id: int, progress_date: str, progress_percentage: float,
                    actual_reduction: float = 0.0, cost: float = 0.0, notes: str = None) -> int:
        """Proje ilerleme kaydı ekle"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO emission_reduction_progress
                (project_id, progress_date, progress_percentage, actual_reduction, cost, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, progress_date, progress_percentage, actual_reduction, cost, notes))

            # Proje ilerleme yüzdesini güncelle
            cursor.execute("""
                UPDATE emission_reduction_projects
                SET progress_percentage = ?, actual_reduction = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (progress_percentage, actual_reduction, project_id))

            progress_id = cursor.lastrowid
            conn.commit()
            return progress_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_progress_records(self, project_id: int = None) -> List[Dict]:
        """İlerleme kayıtlarını getir"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        if project_id:
            cursor.execute("""
                SELECT p.id, p.project_name, pr.progress_date, pr.progress_percentage,
                       pr.actual_reduction, pr.cost, pr.notes, pr.created_at
                FROM emission_reduction_progress pr
                JOIN emission_reduction_projects p ON pr.project_id = p.id
                WHERE pr.project_id = ?
                ORDER BY pr.progress_date DESC
            """, (project_id,))
        else:
            cursor.execute("""
                SELECT p.id, p.project_name, pr.progress_date, pr.progress_percentage,
                       pr.actual_reduction, pr.cost, pr.notes, pr.created_at
                FROM emission_reduction_progress pr
                JOIN emission_reduction_projects p ON pr.project_id = p.id
                ORDER BY pr.progress_date DESC
            """)

        columns = [desc[0] for desc in cursor.description]
        records = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return records

    def get_categories(self) -> List[Dict]:
        """Proje kategorilerini getir"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, color
            FROM emission_reduction_categories
            ORDER BY name
        """)

        columns = [desc[0] for desc in cursor.description]
        categories = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return categories

    def update_project(self, project_id: int, **kwargs) -> bool:
        """Proje bilgilerini güncelle"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        try:
            # Güncellenebilir alanlar
            updatable_fields = ['project_name', 'category', 'description', 'start_date',
                              'end_date', 'expected_reduction', 'actual_reduction',
                              'progress_percentage', 'status', 'budget', 'responsible_person']

            updates = []
            values = []

            for field, value in kwargs.items():
                if field in updatable_fields and value is not None:
                    updates.append(f"{field} = ?")
                    values.append(value)

            if not updates:
                return False

            values.append(project_id)
            cursor.execute(f"""
                UPDATE emission_reduction_projects
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_project(self, project_id: int) -> bool:
        """Projeyi sil"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        try:
            # Önce ilerleme kayıtlarını sil
            cursor.execute("DELETE FROM emission_reduction_progress WHERE project_id = ?", (project_id,))

            # Sonra projeyi sil
            cursor.execute("DELETE FROM emission_reduction_projects WHERE id = ?", (project_id,))

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_project_statistics(self, company_id: int) -> Dict:
        """Proje istatistiklerini getir"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        # Toplam proje sayısı
        cursor.execute("""
            SELECT COUNT(*) FROM emission_reduction_projects WHERE company_id = ?
        """, (company_id,))
        total_projects = cursor.fetchone()[0]

        # Aktif proje sayısı
        cursor.execute("""
            SELECT COUNT(*) FROM emission_reduction_projects 
            WHERE company_id = ? AND status = 'Aktif'
        """, (company_id,))
        active_projects = cursor.fetchone()[0]

        # Toplam beklenen azaltma
        cursor.execute("""
            SELECT COALESCE(SUM(expected_reduction), 0) FROM emission_reduction_projects 
            WHERE company_id = ?
        """, (company_id,))
        total_expected_reduction = cursor.fetchone()[0]

        # Toplam gerçekleşen azaltma
        cursor.execute("""
            SELECT COALESCE(SUM(actual_reduction), 0) FROM emission_reduction_projects 
            WHERE company_id = ?
        """, (company_id,))
        total_actual_reduction = cursor.fetchone()[0]

        # Kategori dağılımı
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM emission_reduction_projects
            WHERE company_id = ?
            GROUP BY category
            ORDER BY count DESC
        """, (company_id,))
        category_distribution = dict(cursor.fetchall())

        conn.close()

        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_expected_reduction': total_expected_reduction,
            'total_actual_reduction': total_actual_reduction,
            'category_distribution': category_distribution
        }
