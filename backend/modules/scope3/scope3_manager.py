#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scope 3 Kategorileri Yöneticisi
GHG Protocol Scope 3 kategorileri için veri yönetimi
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class Scope3Manager:
    """Scope 3 kategorileri yöneticisi - GHG Protocol uyumlu"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.create_tables()
        self.load_scope3_categories()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Scope 3 kategorileri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scope3_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_number INTEGER UNIQUE NOT NULL,
                    category_name TEXT NOT NULL,
                    description TEXT,
                    scope_type TEXT DEFAULT 'Indirect',
                    is_upstream BOOLEAN DEFAULT 1,
                    is_downstream BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Scope 3 emisyon kayıtları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scope3_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    activity_data REAL,
                    activity_unit TEXT,
                    emission_factor REAL,
                    emission_factor_unit TEXT,
                    total_emissions REAL,
                    reporting_period TEXT,
                    data_source TEXT,
                    methodology TEXT,
                    uncertainty_level TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id),
                    FOREIGN KEY(category_id) REFERENCES scope3_categories(id)
                )
            """)

            # Scope 3 hedefleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scope3_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    category_id INTEGER,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    target_year INTEGER,
                    baseline_emissions REAL,
                    target_emissions REAL,
                    reduction_percentage REAL,
                    target_description TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id),
                    FOREIGN KEY(category_id) REFERENCES scope3_categories(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Scope 3 tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] Scope 3 tablo oluşturma hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_emission_record(self, emission_data: Dict) -> bool:
        """Scope 3 emisyon kaydı ekle"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Kategori ID'sini bul
            category_name = emission_data['category']
            cursor.execute("SELECT id FROM scope3_categories WHERE category_name = ?", (category_name,))
            category_row = cursor.fetchone()

            if not category_row:
                # Kategori yoksa ekle
                category_number = category_name.split('.')[0] if '.' in category_name else '1'
                cursor.execute("""
                    INSERT INTO scope3_categories (category_number, category_name, description)
                    VALUES (?, ?, ?)
                """, (int(category_number), category_name, f"Scope 3 Kategori {category_number}"))
                category_id = cursor.lastrowid
            else:
                category_id = category_row[0]

            # Emisyon kaydını ekle
            cursor.execute("""
                INSERT INTO scope3_emissions (
                    company_id, category_id, activity_data, activity_unit,
                    emission_factor, total_emissions, reporting_period,
                    data_source, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emission_data['company_id'],
                category_id,
                emission_data['activity_data'],
                emission_data['unit'],
                emission_data['emission_factor'],
                emission_data['total_emission'],
                emission_data['period'],
                emission_data['source'],
                emission_data['notes'],
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Scope 3 emisyon kaydı ekleme hatası: {e}")
            return False

    def add_target_record(self, target_data: Dict) -> bool:
        """Scope 3 hedef kaydı ekle"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Kategori ID'sini bul
            category_name = target_data['category']
            cursor.execute("SELECT id FROM scope3_categories WHERE category_name = ?", (category_name,))
            category_row = cursor.fetchone()

            if not category_row:
                # Kategori yoksa ekle
                category_number = category_name.split('.')[0] if '.' in category_name else '1'
                cursor.execute("""
                    INSERT INTO scope3_categories (category_number, category_name, description)
                    VALUES (?, ?, ?)
                """, (int(category_number), category_name, f"Scope 3 Kategori {category_number}"))
                category_id = cursor.lastrowid
            else:
                category_id = category_row[0]

            # Hedef kaydını ekle
            cursor.execute("""
                INSERT INTO scope3_targets (
                    company_id, category_id, target_type, baseline_year, target_year,
                    baseline_emissions, target_emissions, reduction_percentage,
                    target_description, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                target_data['company_id'],
                category_id,
                target_data['target_type'],
                target_data['baseline_year'],
                target_data['target_year'],
                target_data['baseline_emissions'],
                target_data['target_emissions'],
                target_data['reduction_percentage'],
                target_data['target_description'],
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Scope 3 hedef kaydı ekleme hatası: {e}")
            return False

    def generate_scope3_report(self, company_id: int, report_name: str, period: str,
                              format_type: str, content_options: Dict) -> str:
        """Scope 3 raporu oluştur"""
        try:
            import os
            from datetime import datetime

            import pandas as pd

            # Rapor klasörü oluştur
            report_dir = os.path.join(os.path.dirname(self.db_path), '..', 'reports', 'scope3')
            os.makedirs(report_dir, exist_ok=True)

            # Dosya adı oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}_{timestamp}.{format_type.lower()}"
            filepath = os.path.join(report_dir, filename)

            # Verileri al
            conn = self.get_connection()
            cursor = conn.cursor()

            report_data = {}

            # Emisyon verileri
            if content_options.get('include_emissions', True):
                cursor.execute("""
                    SELECT e.*, c.category_number, c.category_name, c.description
                    FROM scope3_emissions e
                    JOIN scope3_categories c ON e.category_id = c.id
                    WHERE e.company_id = ? AND e.reporting_period = ?
                    ORDER BY c.category_number
                """, (company_id, period))

                emissions_data = []
                for row in cursor.fetchall():
                    emissions_data.append({
                        'Kategori': f"{row[14]} - {row[15]}",
                        'Aktivite Verisi': row[3],
                        'Aktivite Birimi': row[4],
                        'Emisyon Faktörü': row[5],
                        'Toplam Emisyon (tCO2e)': row[7],
                        'Raporlama Dönemi': row[8],
                        'Veri Kaynağı': row[9],
                        'Notlar': row[12]
                    })
                report_data['emissions'] = emissions_data

            # Hedef verileri
            if content_options.get('include_targets', True):
                cursor.execute("""
                    SELECT t.*, c.category_number, c.category_name
                    FROM scope3_targets t
                    JOIN scope3_categories c ON t.category_id = c.id
                    WHERE t.company_id = ?
                    ORDER BY c.category_number
                """, (company_id,))

                targets_data = []
                for row in cursor.fetchall():
                    targets_data.append({
                        'Kategori': f"{row[13]} - {row[14]}",
                        'Hedef Tipi': row[3],
                        'Baz Yılı': row[4],
                        'Hedef Yılı': row[5],
                        'Baz Emisyon (tCO2e)': row[6],
                        'Hedef Emisyon (tCO2e)': row[7],
                        'Azaltım (%)': row[8],
                        'Açıklama': row[9]
                    })
                report_data['targets'] = targets_data

            # Özet istatistikler
            if content_options.get('include_summary', True):
                cursor.execute("""
                    SELECT 
                        COUNT(*) as toplam_kategori,
                        SUM(total_emissions) as toplam_emisyon,
                        AVG(total_emissions) as ortalama_emisyon,
                        MAX(total_emissions) as max_emisyon,
                        MIN(total_emissions) as min_emisyon
                    FROM scope3_emissions e
                    WHERE e.company_id = ? AND e.reporting_period = ?
                """, (company_id, period))

                summary_row = cursor.fetchone()
                report_data['summary'] = {
                    'Toplam Kategori': summary_row[0],
                    'Toplam Emisyon (tCO2e)': summary_row[1] or 0,
                    'Ortalama Emisyon (tCO2e)': summary_row[2] or 0,
                    'Maksimum Emisyon (tCO2e)': summary_row[3] or 0,
                    'Minimum Emisyon (tCO2e)': summary_row[4] or 0
                }

            conn.close()

            # Rapor oluştur
            if format_type.lower() == 'excel':
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    if 'emissions' in report_data:
                        df_emissions = pd.DataFrame(report_data['emissions'])
                        df_emissions.to_excel(writer, sheet_name='Emisyon Verileri', index=False)

                    if 'targets' in report_data:
                        df_targets = pd.DataFrame(report_data['targets'])
                        df_targets.to_excel(writer, sheet_name='Hedefler', index=False)

                    if 'summary' in report_data:
                        df_summary = pd.DataFrame([report_data['summary']])
                        df_summary.to_excel(writer, sheet_name='Özet', index=False)

            elif format_type.lower() == 'csv':
                if 'emissions' in report_data:
                    df_emissions = pd.DataFrame(report_data['emissions'])
                    df_emissions.to_csv(filepath, index=False, encoding='utf-8-sig')

            elif format_type.lower() == 'docx':
                from docx import Document

                doc = Document()
                doc.add_heading(f'{report_name} - {period}', 0)

                # Özet
                if 'summary' in report_data:
                    doc.add_heading('Özet İstatistikler', level=1)
                    summary = report_data['summary']
                    doc.add_paragraph(f"Toplam Kategori: {summary['Toplam Kategori']}")
                    doc.add_paragraph(f"Toplam Emisyon: {summary['Toplam Emisyon (tCO2e)']:.2f} tCO2e")
                    doc.add_paragraph(f"Ortalama Emisyon: {summary['Ortalama Emisyon (tCO2e)']:.2f} tCO2e")

                # Emisyon verileri
                if 'emissions' in report_data:
                    doc.add_heading('Emisyon Verileri', level=1)
                    table = doc.add_table(rows=1, cols=6)
                    table.style = 'Table Grid'

                    hdr_cells = table.rows[0].cells
                    hdr_cells[0].text = 'Kategori'
                    hdr_cells[1].text = 'Aktivite Verisi'
                    hdr_cells[2].text = 'Toplam Emisyon'
                    hdr_cells[3].text = 'Veri Kaynağı'
                    hdr_cells[4].text = 'Dönem'
                    hdr_cells[5].text = 'Notlar'

                    for emission in report_data['emissions']:
                        row_cells = table.add_row().cells
                        row_cells[0].text = emission['Kategori']
                        row_cells[1].text = str(emission['Aktivite Verisi'] or '')
                        row_cells[2].text = str(emission['Toplam Emisyon (tCO2e)'] or '')
                        row_cells[3].text = emission['Veri Kaynağı'] or ''
                        row_cells[4].text = emission['Raporlama Dönemi'] or ''
                        row_cells[5].text = (emission['Notlar'] or '')

                doc.save(filepath)

            return filepath

        except Exception as e:
            logging.error(f"Scope 3 rapor oluşturma hatası: {e}")
            return None

    def get_target_data(self, company_id: int) -> List[Dict]:
        """Scope 3 hedef verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT t.*, c.category_number, c.category_name
                FROM scope3_targets t
                JOIN scope3_categories c ON t.category_id = c.id
                WHERE t.company_id = ?
                ORDER BY c.category_number
            """, (company_id,))

            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'id': row[0],
                    'company_id': row[1],
                    'category_id': row[2],
                    'target_type': row[3],
                    'baseline_year': row[4],
                    'target_year': row[5],
                    'baseline_emissions': row[6],
                    'target_emissions': row[7],
                    'reduction_percentage': row[8],
                    'target_description': row[9],
                    'status': row[10],
                    'created_at': row[11],
                    'category_number': row[12],
                    'category_name': row[13]
                })

            return targets

        except Exception as e:
            logging.error(f"Scope 3 hedef verileri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def load_scope3_categories(self) -> None:
        """Scope 3 kategorilerini yükle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Kategorilerin zaten var olup olmadığını kontrol et
            cursor.execute("SELECT COUNT(*) FROM scope3_categories")
            count = cursor.fetchone()[0]

            if count == 0:
                # Scope 3 kategorilerini ekle
                categories = [
                    (1, "Satın Alınan Mallar ve Hizmetler", "Üretim için satın alınan tüm mallar ve hizmetler", "Indirect", 1, 0),
                    (2, "Sermaye Malları", "Üretim tesisleri, ekipman ve altyapı yatırımları", "Indirect", 1, 0),
                    (3, "Yakıt ve Enerji Faaliyetleri", "Üretim dışı yakıt kullanımı", "Indirect", 1, 0),
                    (4, "Upstream Taşıma ve Dağıtım", "Satın alınan malların taşınması", "Indirect", 1, 0),
                    (5, "Operasyonlarda Oluşan Atık", "Üretim sürecinde oluşan atıkların bertarafı", "Indirect", 1, 0),
                    (6, "İş Seyahatleri", "Çalışanların iş amaçlı seyahatleri", "Indirect", 1, 0),
                    (7, "Çalışan İşe Gidiş-Geliş", "Çalışanların ev-iş arası ulaşımı", "Indirect", 1, 0),
                    (8, "Kiralanan Varlıklar", "Kiralık ofis, depo ve diğer varlıklar", "Indirect", 1, 0),
                    (9, "Downstream Taşıma ve Dağıtım", "Ürünlerin müşterilere ulaştırılması", "Indirect", 0, 1),
                    (10, "Satılan Ürünlerin İşlenmesi", "Müşterilerin ürünleri kullanımı", "Indirect", 0, 1),
                    (11, "Satılan Ürünlerin Kullanımı", "Ürünlerin müşteri tarafından kullanımı", "Indirect", 0, 1),
                    (12, "Satılan Ürünlerin Bertarafı", "Ürünlerin son kullanım sonrası bertarafı", "Indirect", 0, 1),
                    (13, "Kiralanan Varlıklar (Downstream)", "Müşterilere kiralanan varlıklar", "Indirect", 0, 1),
                    (14, "Franchise", "Franchise operasyonları", "Indirect", 0, 1),
                    (15, "Yatırımlar", "Finansal yatırımlar", "Indirect", 1, 0)
                ]

                cursor.executemany("""
                    INSERT INTO scope3_categories 
                    (category_number, category_name, description, scope_type, is_upstream, is_downstream)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, categories)

                conn.commit()
                logging.info(f"[OK] {len(categories)} Scope 3 kategorisi eklendi")

        except Exception as e:
            logging.error(f"[HATA] Scope 3 kategorileri yükleme hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_categories(self) -> List[Dict]:
        """Tüm Scope 3 kategorilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, category_number, category_name, description, 
                       scope_type, is_upstream, is_downstream, is_active
                FROM scope3_categories 
                WHERE is_active = 1
                ORDER BY category_number
            """)

            categories = []
            for row in cursor.fetchall():
                categories.append({
                    'id': row[0],
                    'category_number': row[1],
                    'category_name': row[2],
                    'description': row[3],
                    'scope_type': row[4],
                    'is_upstream': bool(row[5]),
                    'is_downstream': bool(row[6]),
                    'is_active': bool(row[7])
                })

            return categories

        except Exception as e:
            logging.error(f"[HATA] Kategoriler getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def save_emission_data(self, company_id: int, category_id: int,
                          activity_data: float, activity_unit: str,
                          emission_factor: float, emission_factor_unit: str,
                          total_emissions: float, reporting_period: str,
                          data_source: str = "", methodology: str = "",
                          uncertainty_level: str = "", notes: str = "") -> bool:
        """Scope 3 emisyon verisi kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO scope3_emissions 
                (company_id, category_id, activity_data, activity_unit,
                 emission_factor, emission_factor_unit, total_emissions,
                 reporting_period, data_source, methodology, uncertainty_level, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, category_id, activity_data, activity_unit,
                  emission_factor, emission_factor_unit, total_emissions,
                  reporting_period, data_source, methodology, uncertainty_level, notes))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[HATA] Emisyon verisi kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_emission_data(self, company_id: int, reporting_period: str = None) -> List[Dict]:
        """Scope 3 emisyon verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if reporting_period:
                cursor.execute("""
                    SELECT e.*, c.category_number, c.category_name, c.description
                    FROM scope3_emissions e
                    JOIN scope3_categories c ON e.category_id = c.id
                    WHERE e.company_id = ? AND e.reporting_period = ?
                    ORDER BY c.category_number
                """, (company_id, reporting_period))
            else:
                cursor.execute("""
                    SELECT e.*, c.category_number, c.category_name, c.description
                    FROM scope3_emissions e
                    JOIN scope3_categories c ON e.category_id = c.id
                    WHERE e.company_id = ?
                    ORDER BY c.category_number, e.reporting_period DESC
                """, (company_id,))

            emissions = []
            for row in cursor.fetchall():
                emissions.append({
                    'id': row[0],
                    'company_id': row[1],
                    'category_id': row[2],
                    'activity_data': row[3],
                    'activity_unit': row[4],
                    'emission_factor': row[5],
                    'emission_factor_unit': row[6],
                    'total_emissions': row[7],
                    'reporting_period': row[8],
                    'data_source': row[9],
                    'methodology': row[10],
                    'uncertainty_level': row[11],
                    'notes': row[12],
                    'created_at': row[13],
                    'updated_at': row[14],
                    'category_number': row[15],
                    'category_name': row[16],
                    'description': row[17]
                })

            return emissions

        except Exception as e:
            logging.error(f"[HATA] Emisyon verileri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_emissions_summary(self, company_id: int, reporting_period: str = None) -> Dict:
        """Scope 3 emisyon özetini getir"""
        emissions = self.get_emission_data(company_id, reporting_period)

        summary = {
            'total_emissions': 0,
            'upstream_emissions': 0,
            'downstream_emissions': 0,
            'category_breakdown': {},
            'data_quality': {
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }

        for emission in emissions:
            total = emission.get('total_emissions', 0) or 0
            summary['total_emissions'] += total

            category_name = emission.get('category_name', '')
            if category_name in summary['category_breakdown']:
                summary['category_breakdown'][category_name] += total
            else:
                summary['category_breakdown'][category_name] = total

            # Upstream/Downstream ayrımı
            if emission.get('category_number', 0) <= 8:
                summary['upstream_emissions'] += total
            else:
                summary['downstream_emissions'] += total

            # Veri kalitesi
            uncertainty = emission.get('uncertainty_level', '') or ''
            uncertainty = uncertainty.lower() if uncertainty else ''
            if uncertainty in ['high', 'düşük']:
                summary['data_quality']['low'] += 1
            elif uncertainty in ['medium', 'orta']:
                summary['data_quality']['medium'] += 1
            else:
                summary['data_quality']['high'] += 1

        return summary
