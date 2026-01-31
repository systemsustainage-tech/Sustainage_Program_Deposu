#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Sektörel Standartları Modülü
GRI 11, 12, 13, 14 ve diğer sektörel standartlar için yönetim
"""

import logging
import os
import sqlite3
from typing import Dict, List
from config.database import DB_PATH


class GRISectoralStandardsManager:
    """GRI Sektörel Standartları yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_sectoral_tables()
        self._populate_sectoral_standards()

    def _init_sectoral_tables(self) -> None:
        """GRI sektörel standartları tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # GRI 11 - Oil and Gas Sector
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_11_oil_gas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 12 - Coal Sector
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_12_coal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 13 - Agriculture, Aquaculture & Fishing
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_13_agriculture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 14 - Mining Sector
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_14_mining (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 101 - Biodiversity 2024
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_101_biodiversity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 102 - Climate Change 2025
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_102_climate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 103 - Energy 2025
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_103_energy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Sektörel standartlar indeksi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_sectoral_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    standard_code TEXT UNIQUE NOT NULL,
                    standard_name TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    description TEXT,
                    applicable_sectors TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] GRI sektörel standartları tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"[ERROR] GRI sektörel tabloları oluşturulurken hata: {e}")
        finally:
            conn.close()

    def _populate_sectoral_standards(self) -> None:
        """GRI sektörel standartları verilerini doldur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Sektörel standartlar tanımları
            sectoral_standards = [
                # GRI 11 - Oil and Gas Sector
                ("GRI 11", "Oil and Gas Sector", "Oil and Gas", 2021,
                 "Petrol ve doğal gaz sektörü için özel standartlar",
                 "Oil, Gas, Petroleum, Energy"),

                # GRI 12 - Coal Sector
                ("GRI 12", "Coal Sector", "Coal", 2022,
                 "Kömür sektörü için özel standartlar",
                 "Coal, Mining, Energy"),

                # GRI 13 - Agriculture, Aquaculture & Fishing
                ("GRI 13", "Agriculture, Aquaculture & Fishing", "Agriculture", 2022,
                 "Tarım, su ürünleri ve balıkçılık sektörleri için standartlar",
                 "Agriculture, Aquaculture, Fishing, Food"),

                # GRI 14 - Mining Sector
                ("GRI 14", "Mining Sector", "Mining", 2024,
                 "Madencilik sektörü için özel standartlar",
                 "Mining, Metals, Minerals, Extraction"),

                # GRI 101 - Biodiversity 2024
                ("GRI 101", "Biodiversity 2024", "Biodiversity", 2024,
                 "Biyoçeşitlilik konuları için güncellenmiş standartlar",
                 "All Sectors"),

                # GRI 102 - Climate Change 2025
                ("GRI 102", "Climate Change 2025", "Climate", 2025,
                 "İklim değişikliği konuları için güncellenmiş standartlar",
                 "All Sectors"),

                # GRI 103 - Energy 2025
                ("GRI 103", "Energy 2025", "Energy", 2025,
                 "Enerji konuları için güncellenmiş standartlar",
                 "All Sectors"),
            ]

            for standard_code, standard_name, sector, year, description, applicable_sectors in sectoral_standards:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_sectoral_index 
                    (standard_code, standard_name, sector, year, description, applicable_sectors)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (standard_code, standard_name, sector, year, description, applicable_sectors))

            # GRI 11 - Oil and Gas Sector konuları
            gri_11_topics = [
                ("GRI 11-1", "Oil and Gas Reserves", "Petrol ve Doğal Gaz Rezervleri",
                 "Şirketin petrol ve doğal gaz rezervlerinin açıklanması",
                 "Rezerv miktarları, rezerv değişimleri, rezerv kategorileri",
                 "Rezerv yönetim politikaları ve prosedürleri"),

                ("GRI 11-2", "Oil and Gas Production", "Petrol ve Doğal Gaz Üretimi",
                 "Petrol ve doğal gaz üretim verilerinin açıklanması",
                 "Üretim miktarları, üretim türleri, üretim lokasyonları",
                 "Üretim yönetim sistemleri ve performans göstergeleri"),

                ("GRI 11-3", "Oil and Gas Exploration", "Petrol ve Doğal Gaz Arama",
                 "Arama faaliyetlerinin çevresel ve sosyal etkilerinin açıklanması",
                 "Arama alanları, arama yöntemleri, etki değerlendirmeleri",
                 "Arama süreçlerinde sürdürülebilirlik yaklaşımı"),
            ]

            for standard_id, topic_name, topic_description, disclosure_requirements, metrics, management_approach in gri_11_topics:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_11_oil_gas 
                    (company_id, reporting_period, standard_id, topic_name, topic_description, 
                     disclosure_requirements, management_approach, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (0, "2024", standard_id, topic_name, topic_description,
                      disclosure_requirements, management_approach, metrics))

            # GRI 12 - Coal Sector konuları
            gri_12_topics = [
                ("GRI 12-1", "Coal Reserves", "Kömür Rezervleri",
                 "Kömür rezervlerinin açıklanması",
                 "Rezerv miktarları, rezerv kalitesi, rezerv değişimleri",
                 "Rezerv yönetim politikaları"),

                ("GRI 12-2", "Coal Production", "Kömür Üretimi",
                 "Kömür üretim verilerinin açıklanması",
                 "Üretim miktarları, üretim türleri, üretim yöntemleri",
                 "Üretim süreçlerinde sürdürülebilirlik"),
            ]

            for standard_id, topic_name, topic_description, disclosure_requirements, metrics, management_approach in gri_12_topics:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_12_coal 
                    (company_id, reporting_period, standard_id, topic_name, topic_description, 
                     disclosure_requirements, management_approach, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (0, "2024", standard_id, topic_name, topic_description,
                      disclosure_requirements, management_approach, metrics))

            # GRI 13 - Agriculture konuları
            gri_13_topics = [
                ("GRI 13-1", "Agricultural Land Use", "Tarımsal Arazi Kullanımı",
                 "Tarımsal arazi kullanımının açıklanması",
                 "Arazi kullanım miktarları, arazi türleri, arazi değişimleri",
                 "Arazi yönetim politikaları"),

                ("GRI 13-2", "Water Use in Agriculture", "Tarımda Su Kullanımı",
                 "Tarımsal faaliyetlerde su kullanımının açıklanması",
                 "Su kullanım miktarları, su kaynakları, su verimliliği",
                 "Su yönetim sistemleri"),
            ]

            for standard_id, topic_name, topic_description, disclosure_requirements, metrics, management_approach in gri_13_topics:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_13_agriculture 
                    (company_id, reporting_period, standard_id, topic_name, topic_description, 
                     disclosure_requirements, management_approach, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (0, "2024", standard_id, topic_name, topic_description,
                      disclosure_requirements, management_approach, metrics))

            # GRI 14 - Mining konuları
            gri_14_topics = [
                ("GRI 14-1", "Mining Operations", "Madencilik Operasyonları",
                 "Madencilik operasyonlarının açıklanması",
                 "Operasyon türleri, üretim miktarları, operasyon lokasyonları",
                 "Operasyon yönetim sistemleri"),

                ("GRI 14-2", "Mine Closure", "Maden Kapatma",
                 "Maden kapatma planlarının açıklanması",
                 "Kapatma planları, rehabilitasyon çalışmaları, maliyetler",
                 "Kapatma yönetim politikaları"),
            ]

            for standard_id, topic_name, topic_description, disclosure_requirements, metrics, management_approach in gri_14_topics:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_14_mining 
                    (company_id, reporting_period, standard_id, topic_name, topic_description, 
                     disclosure_requirements, management_approach, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (0, "2024", standard_id, topic_name, topic_description,
                      disclosure_requirements, management_approach, metrics))

            # GRI 101 - Biodiversity konuları
            gri_101_topics = [
                ("GRI 101-1", "Biodiversity Impact Assessment", "Biyoçeşitlilik Etki Değerlendirmesi",
                 "Biyoçeşitlilik etkilerinin değerlendirilmesi",
                 "Etki değerlendirme raporları, etki türleri, etki büyüklükleri",
                 "Biyoçeşitlilik yönetim politikaları"),

                ("GRI 101-2", "Biodiversity Conservation", "Biyoçeşitlilik Koruma",
                 "Biyoçeşitlilik koruma çalışmalarının açıklanması",
                 "Koruma alanları, koruma türleri, koruma başarıları",
                 "Koruma yönetim sistemleri"),
            ]

            for standard_id, topic_name, topic_description, disclosure_requirements, metrics, management_approach in gri_101_topics:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_101_biodiversity 
                    (company_id, reporting_period, standard_id, topic_name, topic_description, 
                     disclosure_requirements, management_approach, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (0, "2024", standard_id, topic_name, topic_description,
                      disclosure_requirements, management_approach, metrics))

            # GRI 102 - Climate Change konuları
            gri_102_topics = [
                ("GRI 102-1", "Climate Risk Assessment", "İklim Risk Değerlendirmesi",
                 "İklim risklerinin değerlendirilmesi",
                 "Risk türleri, risk büyüklükleri, risk yönetimi",
                 "İklim risk yönetim politikaları"),

                ("GRI 102-2", "Climate Targets", "İklim Hedefleri",
                 "İklim hedeflerinin açıklanması",
                 "Hedef türleri, hedef değerleri, hedef zamanlamaları",
                 "Hedef yönetim sistemleri"),
            ]

            for standard_id, topic_name, topic_description, disclosure_requirements, metrics, management_approach in gri_102_topics:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_102_climate 
                    (company_id, reporting_period, standard_id, topic_name, topic_description, 
                     disclosure_requirements, management_approach, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (0, "2024", standard_id, topic_name, topic_description,
                      disclosure_requirements, management_approach, metrics))

            # GRI 103 - Energy konuları
            gri_103_topics = [
                ("GRI 103-1", "Energy Consumption", "Enerji Tüketimi",
                 "Enerji tüketiminin açıklanması",
                 "Tüketim miktarları, enerji türleri, tüketim lokasyonları",
                 "Enerji yönetim politikaları"),

                ("GRI 103-2", "Renewable Energy", "Yenilenebilir Enerji",
                 "Yenilenebilir enerji kullanımının açıklanması",
                 "Yenilenebilir enerji miktarları, enerji türleri, paylar",
                 "Yenilenebilir enerji stratejileri"),
            ]

            for standard_id, topic_name, topic_description, disclosure_requirements, metrics, management_approach in gri_103_topics:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_103_energy 
                    (company_id, reporting_period, standard_id, topic_name, topic_description, 
                     disclosure_requirements, management_approach, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (0, "2024", standard_id, topic_name, topic_description,
                      disclosure_requirements, management_approach, metrics))

            conn.commit()
            logging.info("[OK] GRI sektörel standartları verileri dolduruldu")

        except Exception as e:
            logging.error(f"[ERROR] GRI sektörel veriler doldurulurken hata: {e}")
        finally:
            conn.close()

    def get_sectoral_standards(self) -> List[Dict]:
        """Tüm sektörel standartları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT standard_code, standard_name, sector, year, description, applicable_sectors
                FROM gri_sectoral_index
                WHERE is_active = 1
                ORDER BY year DESC, standard_code
            """)

            columns = [col[0] for col in cursor.description]
            standards = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return standards

        except Exception as e:
            logging.error(f"Sektörel standartlar getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_standard_topics(self, standard_code: str, company_id: int = 0) -> List[Dict]:
        """Belirli bir standart için konuları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Standart koduna göre tablo adını belirle
            table_mapping = {
                "GRI 11": "gri_11_oil_gas",
                "GRI 12": "gri_12_coal",
                "GRI 13": "gri_13_agriculture",
                "GRI 14": "gri_14_mining",
                "GRI 101": "gri_101_biodiversity",
                "GRI 102": "gri_102_climate",
                "GRI 103": "gri_103_energy"
            }

            table_name = table_mapping.get(standard_code)
            if not table_name:
                return []

            cursor.execute(f"""
                SELECT * FROM {table_name}
                WHERE company_id = ? OR company_id = 0
                ORDER BY standard_id
            """, (company_id,))

            columns = [col[0] for col in cursor.description]
            topics = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return topics

        except Exception as e:
            logging.error(f"Standart konuları getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def update_topic_compliance(self, standard_code: str, topic_id: int,
                               compliance_status: str, notes: str = "") -> bool:
        """Konu uyumluluk durumunu güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            table_mapping = {
                "GRI 11": "gri_11_oil_gas",
                "GRI 12": "gri_12_coal",
                "GRI 13": "gri_13_agriculture",
                "GRI 14": "gri_14_mining",
                "GRI 101": "gri_101_biodiversity",
                "GRI 102": "gri_102_climate",
                "GRI 103": "gri_103_energy"
            }

            table_name = table_mapping.get(standard_code)
            if not table_name:
                return False

            cursor.execute(f"""
                UPDATE {table_name}
                SET compliance_status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (compliance_status, notes, topic_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Uyumluluk durumu güncellenirken hata: {e}")
            return False
        finally:
            conn.close()

    def get_company_sectoral_summary(self, company_id: int) -> Dict:
        """Şirket için sektörel standartlar özeti"""
        summary = {
            "total_standards": 0,
            "applicable_standards": 0,
            "compliant_topics": 0,
            "total_topics": 0,
            "standards_breakdown": {}
        }

        try:
            standards = self.get_sectoral_standards()
            summary["total_standards"] = len(standards)

            for standard in standards:
                standard_code = standard["standard_code"]
                topics = self.get_standard_topics(standard_code, company_id)

                if topics:
                    summary["applicable_standards"] += 1
                    summary["total_topics"] += len(topics)

                    compliant_count = sum(1 for topic in topics
                                        if topic.get("compliance_status") == "Compliant")
                    summary["compliant_topics"] += compliant_count

                    summary["standards_breakdown"][standard_code] = {
                        "name": standard["standard_name"],
                        "total_topics": len(topics),
                        "compliant_topics": compliant_count,
                        "compliance_rate": (compliant_count / len(topics) * 100) if topics else 0
                    }

            return summary

        except Exception as e:
            logging.error(f"Sektörel özet getirilirken hata: {e}")
            return summary
