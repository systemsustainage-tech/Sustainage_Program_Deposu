#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI 201-1 Ekonomik Değer Dağılımı Otomatik Hesaplama
Direct Economic Value Generated and Distributed
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from utils.language_manager import LanguageManager
from config.database import DB_PATH


class GRI201Calculator:
    """GRI 201-1 otomatik hesaplama sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.lm = LanguageManager()
        self._init_tables()

    def _init_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Ekonomik değer verileri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS economic_value_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'TRY',
                    notes TEXT,
                    data_source TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 201-1 hesaplanmış değerler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_201_calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_generated REAL,
                    total_distributed REAL,
                    retained_value REAL,
                    calculation_date TEXT,
                    breakdown_json TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] GRI 201-1 tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] GRI 201-1 tablo oluşturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_economic_data(self, company_id: int, year: int, category: str,
                         subcategory: str, amount: float, currency: str = 'TRY',
                         notes: str = None, data_source: str = None) -> bool:
        """
        Ekonomik veri ekle
        
        Categories:
        - Generated: revenues
        - Distributed_Operating: operating_costs, employee_wages, payments_capital_providers, payments_government, community_investments
        - Retained: retained_earnings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO economic_value_data 
                (company_id, year, category, subcategory, amount, currency, notes, data_source, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, category, subcategory, amount, currency, notes, data_source,
                  datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Ekonomik veri ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def calculate_gri_201(self, company_id: int, year: int) -> Dict:
        """
        GRI 201-1 otomatik hesaplama
        
        Returns:
            Dict: {
                'generated': {...},
                'distributed': {...},
                'retained': float,
                'total_generated': float,
                'total_distributed': float
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Üretilen Ekonomik Değer (Generated)
            cursor.execute("""
                SELECT subcategory, SUM(amount)
                FROM economic_value_data
                WHERE company_id = ? AND year = ? AND category = 'Generated'
                GROUP BY subcategory
            """, (company_id, year))

            generated = {}
            total_generated = 0
            for subcategory, amount in cursor.fetchall():
                generated[subcategory] = amount
                total_generated += amount

            # Varsayılan değerler
            if not generated:
                generated = {'revenues': 0}

            # Dağıtılan Ekonomik Değer (Distributed)
            cursor.execute("""
                SELECT subcategory, SUM(amount)
                FROM economic_value_data
                WHERE company_id = ? AND year = ? AND category = 'Distributed_Operating'
                GROUP BY subcategory
            """, (company_id, year))

            distributed = {}
            total_distributed = 0
            for subcategory, amount in cursor.fetchall():
                distributed[subcategory] = amount
                total_distributed += amount

            # Varsayılan kategoriler
            default_categories = [
                'operating_costs',
                'employee_wages',
                'payments_capital_providers',
                'payments_government',
                'community_investments'
            ]

            for cat in default_categories:
                if cat not in distributed:
                    distributed[cat] = 0

            # İşletmede Tutulan Değer (Retained)
            retained_value = total_generated - total_distributed

            # Sonuçları kaydet
            import json
            breakdown = {
                'generated': generated,
                'distributed': distributed,
                'retained': retained_value
            }

            cursor.execute("""
                INSERT OR REPLACE INTO gri_201_calculations
                (company_id, year, total_generated, total_distributed, retained_value,
                 calculation_date, breakdown_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, total_generated, total_distributed, retained_value,
                  datetime.now().isoformat(), json.dumps(breakdown, ensure_ascii=False)))

            conn.commit()

            return {
                'generated': generated,
                'distributed': distributed,
                'retained': retained_value,
                'total_generated': total_generated,
                'total_distributed': total_distributed
            }

        except Exception as e:
            logging.error(f"GRI 201-1 hesaplama hatası: {e}")
            return None
        finally:
            conn.close()

    def get_economic_data(self, company_id: int, year: int) -> List[Dict]:
        """Tüm ekonomik verileri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, category, subcategory, amount, currency, notes, data_source, created_at
                FROM economic_value_data
                WHERE company_id = ? AND year = ?
                ORDER BY category, subcategory
            """, (company_id, year))

            data = []
            for row in cursor.fetchall():
                data.append({
                    'id': row[0],
                    'category': row[1],
                    'subcategory': row[2],
                    'amount': row[3],
                    'currency': row[4],
                    'notes': row[5],
                    'data_source': row[6],
                    'created_at': row[7]
                })

            return data

        except Exception as e:
            logging.error(f"Veri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_latest_calculation(self, company_id: int, year: int) -> Optional[Dict]:
        """Son hesaplanmış değerleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT total_generated, total_distributed, retained_value, 
                       calculation_date, breakdown_json
                FROM gri_201_calculations
                WHERE company_id = ? AND year = ?
                ORDER BY id DESC
                LIMIT 1
            """, (company_id, year))

            row = cursor.fetchone()
            if not row:
                return None

            import json
            return {
                'total_generated': row[0],
                'total_distributed': row[1],
                'retained_value': row[2],
                'calculation_date': row[3],
                'breakdown': json.loads(row[4]) if row[4] else {}
            }

        except Exception as e:
            logging.error(f"Hesaplama getirme hatası: {e}")
            return None
        finally:
            conn.close()

    def update_economic_data(self, data_id: int, amount: float,
                            notes: str = None) -> bool:
        """Ekonomik veriyi güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE economic_value_data
                SET amount = ?, notes = ?, updated_at = ?
                WHERE id = ?
            """, (amount, notes, datetime.now().isoformat(), data_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Veri güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_economic_data(self, data_id: int) -> bool:
        """Ekonomik veriyi sil"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM economic_value_data WHERE id = ?", (data_id,))
            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Veri silme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def generate_report(self, company_id: int, year: int) -> str:
        """GRI 201-1 rapor metni oluştur"""
        calc = self.calculate_gri_201(company_id, year)

        if not calc:
            return "Hesaplama yapılamadı - veri yok"

        report = f"""
# GRI 201-1: Direct Economic Value Generated and Distributed

## Rapor Yılı: {year}

### Üretilen Ekonomik Değer (Economic Value Generated)
"""

        for key, value in calc['generated'].items():
            report += f"- {key.replace('_', ' ').title()}: {value:,.2f} TRY\n"

        report += f"\n**Toplam Üretilen Değer: {calc['total_generated']:,.2f} TRY**\n"

        report += "\n### Dağıtılan Ekonomik Değer (Economic Value Distributed)\n"

        distributed_labels = {
            'operating_costs': 'İşletme Maliyetleri',
            'employee_wages': 'Çalışan Ücretleri ve Yan Haklar',
            'payments_capital_providers': 'Sermaye Sağlayıcılara Ödemeler',
            'payments_government': 'Devlete Ödemeler (Vergi)',
            'community_investments': 'Topluma Yatırımlar'
        }

        for key, value in calc['distributed'].items():
            label = distributed_labels.get(key, key.replace('_', ' ').title())
            report += f"- {label}: {value:,.2f} TRY\n"

        report += f"\n**Toplam Dağıtılan Değer: {calc['total_distributed']:,.2f} TRY**\n"

        report += "\n### İşletmede Tutulan Ekonomik Değer (Economic Value Retained)\n"
        report += f"**{calc['retained']:,.2f} TRY**\n"

        # Yüzdeler
        if calc['total_generated'] > 0:
            report += "\n### Dağıtım Oranları\n"
            for key, value in calc['distributed'].items():
                percentage = (value / calc['total_generated']) * 100
                label = distributed_labels.get(key, key.replace('_', ' ').title())
                report += f"- {label}: %{percentage:.2f}\n"

            retained_pct = (calc['retained'] / calc['total_generated']) * 100
            report += f"- Tutulan Değer: %{retained_pct:.2f}\n"

        return report

    def create_sample_data(self, company_id: int, year: int = 2024) -> None:
        """Örnek veri oluştur (test için)"""
        # Üretilen Değer
        self.add_economic_data(company_id, year, 'Generated', 'revenues',
                              50000000, notes='Net satış gelirleri')

        # Dağıtılan Değerler
        self.add_economic_data(company_id, year, 'Distributed_Operating', 'operating_costs',
                              30000000, notes='İşletme giderleri, hammadde, enerji')

        self.add_economic_data(company_id, year, 'Distributed_Operating', 'employee_wages',
                              8000000, notes='Maaş, ikramiye, yan haklar')

        self.add_economic_data(company_id, year, 'Distributed_Operating', 'payments_capital_providers',
                              2000000, notes='Faiz, temettü')

        self.add_economic_data(company_id, year, 'Distributed_Operating', 'payments_government',
                              3500000, notes='Kurumlar vergisi, KDV, damga vergisi')

        self.add_economic_data(company_id, year, 'Distributed_Operating', 'community_investments',
                              500000, notes='Sosyal sorumluluk projeleri')

        logging.info(f"[OK] {company_id} numaralı şirket için {year} yılı örnek veri oluşturuldu")

