#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESRS (European Sustainability Reporting Standards) Manager
Web arayüzü için ESRS değerlendirmelerini ve özet istatistikleri yönetir.
"""

import logging
import os
import sqlite3
from typing import Dict

from config.database import DB_PATH


class ESRSManager:
    """ESRS modülü yöneticisi (web tarafı)"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise repo köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            db_path = os.path.join(repo_root, db_path)
        self.db_path = db_path

    def init_assessments_table(self) -> None:
        """ESRS değerlendirme ve önemlilik tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Mevcut esrs_assessments tablosu
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS esrs_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    standard_code TEXT NOT NULL,
                    status TEXT DEFAULT 'not_started',
                    notes TEXT,
                    governance_notes TEXT,
                    strategy_notes TEXT,
                    impact_risk_notes TEXT,
                    metrics_notes TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """
            )
            
            # Yeni esrs_materiality tablosu (Çifte Önemlilik)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS esrs_materiality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    impact_score INTEGER, -- 1-5 arası etki puanı
                    likelihood INTEGER, -- 1-5 arası olasılık
                    financial_effect TEXT, -- Finansal etki açıklaması veya değeri
                    environmental_effect TEXT, -- Çevresel/Sosyal etki açıklaması
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """
            )
            
            # Sütun kontrolü ve ekleme (Migration)
            cursor.execute("PRAGMA table_info(esrs_assessments)")
            columns = [info[1] for info in cursor.fetchall()]
            
            new_columns = ['governance_notes', 'strategy_notes', 'impact_risk_notes', 'metrics_notes']
            for col in new_columns:
                if col not in columns:
                    try:
                        cursor.execute(f"ALTER TABLE esrs_assessments ADD COLUMN {col} TEXT")
                        logging.info(f"Added missing column: {col}")
                    except Exception as e:
                        logging.error(f"Error adding column {col}: {e}")

            conn.commit()
        except Exception as e:
            logging.error(f"ESRS table init error: {e}")
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """ESRS dashboard istatistiklerini getir"""
        self.init_assessments_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {"covered_standards": 0, "completion_rate": 0}

        # Standart sayısı: ESRS 1, 2, E1-E5, S1-S4, G1 (toplam 12)
        total_standards = 12

        try:
            cursor.execute(
                "SELECT standard_code, status FROM esrs_assessments WHERE company_id = ?",
                (company_id,),
            )
            rows = cursor.fetchall()
            status_map = {r[0]: r[1] for r in rows}

            completed_count = sum(1 for status in status_map.values() if status == "completed")

            stats["covered_standards"] = len(status_map)
            if total_standards > 0:
                stats["completion_rate"] = int((completed_count / total_standards) * 100)

        except Exception as e:
            logging.error(f"ESRS stats error: {e}")
        finally:
            conn.close()

        return stats

    def get_assessment_status(self, company_id: int) -> Dict[str, str]:
        """Tüm standartlar için durum haritasını getir"""
        self.init_assessments_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        status_map: Dict[str, str] = {}
        try:
            cursor.execute(
                "SELECT standard_code, status FROM esrs_assessments WHERE company_id = ?",
                (company_id,),
            )
            rows = cursor.fetchall()
            status_map = {r[0]: r[1] for r in rows}
        except Exception as e:
            logging.error(f"ESRS status load error: {e}")
        finally:
            conn.close()
        return status_map

    def get_assessment_details(self, company_id: int, standard_code: str) -> Dict[str, str]:
        """Belirli bir standardın detaylarını getir"""
        self.init_assessments_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        details = {}
        try:
            cursor.execute(
                """
                SELECT status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes 
                FROM esrs_assessments 
                WHERE company_id = ? AND standard_code = ?
                """,
                (company_id, standard_code),
            )
            row = cursor.fetchone()
            if row:
                details = {
                    "status": row[0],
                    "notes": row[1] or "",
                    "governance_notes": row[2] or "",
                    "strategy_notes": row[3] or "",
                    "impact_risk_notes": row[4] or "",
                    "metrics_notes": row[5] or ""
                }
        except Exception as e:
            logging.error(f"ESRS details load error: {e}")
        finally:
            conn.close()
        return details

    def update_assessment(
        self, 
        company_id: int, 
        standard_code: str, 
        status: str, 
        notes: str,
        governance_notes: str = None,
        strategy_notes: str = None,
        impact_risk_notes: str = None,
        metrics_notes: str = None
    ) -> bool:
        """Belirli bir ESRS standardı için durumu güncelle"""
        self.init_assessments_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM esrs_assessments WHERE company_id = ? AND standard_code = ?",
                (company_id, standard_code),
            )
            exists = cursor.fetchone()

            if exists:
                cursor.execute(
                    """
                    UPDATE esrs_assessments 
                    SET status = ?, notes = ?, governance_notes = ?, strategy_notes = ?, impact_risk_notes = ?, metrics_notes = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE company_id = ? AND standard_code = ?
                """,
                    (status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes, company_id, standard_code),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO esrs_assessments (company_id, standard_code, status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (company_id, standard_code, status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes),
                )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"ESRS update error: {e}")
            return False
        finally:
            conn.close()

    def get_materiality_analysis(self, company_id: int) -> list:
        """Çifte önemlilik analizi verilerini getir"""
        self.init_assessments_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        items = []
        try:
            cursor.execute(
                """
                SELECT id, topic, impact_score, likelihood, financial_effect, environmental_effect, created_at
                FROM esrs_materiality
                WHERE company_id = ?
                ORDER BY created_at DESC
                """,
                (company_id,)
            )
            columns = [col[0] for col in cursor.description]
            items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"ESRS materiality fetch error: {e}")
        finally:
            conn.close()
        return items

    def add_materiality_item(self, company_id: int, topic: str, impact_score: int, likelihood: int, financial_effect: str, environmental_effect: str) -> bool:
        """Yeni önemlilik maddesi ekle"""
        self.init_assessments_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO esrs_materiality (company_id, topic, impact_score, likelihood, financial_effect, environmental_effect)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (company_id, topic, impact_score, likelihood, financial_effect, environmental_effect)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"ESRS materiality add error: {e}")
            return False
        finally:
            conn.close()

    def delete_materiality_item(self, item_id: int, company_id: int) -> bool:
        """Önemlilik maddesini sil"""
        self.init_assessments_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM esrs_materiality WHERE id = ? AND company_id = ?",
                (item_id, company_id)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"ESRS materiality delete error: {e}")
            return False
        finally:
            conn.close()
