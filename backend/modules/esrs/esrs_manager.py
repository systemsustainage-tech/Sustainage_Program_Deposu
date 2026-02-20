#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESRS (European Sustainability Reporting Standards) Manager
Web arayüzü için ESRS değerlendirmelerini ve özet istatistikleri yönetir.
"""

import logging
import os
from typing import Dict, List, Any, Optional

from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager

class ESRSManager(BaseTenantManager):
    """ESRS modülü yöneticisi (web tarafı)"""

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        # BaseTenantManager handles absolute path conversion if needed, 
        # but let's check if we need to do it explicitly like before.
        # BaseTenantManager's __init__ calls DatabaseManager(db_path).
        # DatabaseManager doesn't auto-convert relative paths unless they are already correct relative to CWD.
        # So we should keep the path logic.
        if not os.path.isabs(db_path):
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            db_path = os.path.join(repo_root, db_path)
        
        super().__init__(db_path, company_id)

    def init_assessments_table(self) -> None:
        """ESRS değerlendirme ve önemlilik tablolarını oluştur"""
        try:
            # Table creation doesn't need tenant filtering usually, but execute_update handles it.
            # DDL is skipped by inject_tenant_filter anyway.
            
            # Mevcut esrs_assessments tablosu
            self.execute_update("""
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
            """)
            
            # Yeni esrs_materiality tablosu (Çifte Önemlilik)
            self.execute_update("""
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
            """)
            
            # Sütun kontrolü ve ekleme (Migration)
            # We need raw connection for PRAGMA, or use a helper if available.
            # BaseTenantManager doesn't expose raw connection easily without get_connection context.
            # But we can use execute_query for PRAGMA.
            
            rows = self.execute_query("PRAGMA table_info(esrs_assessments)")
            columns = [row['name'] for row in rows]
            
            new_columns = ['governance_notes', 'strategy_notes', 'impact_risk_notes', 'metrics_notes']
            for col in new_columns:
                if col not in columns:
                    try:
                        self.execute_update(f"ALTER TABLE esrs_assessments ADD COLUMN {col} TEXT")
                        logging.info(f"Added missing column: {col}")
                    except Exception as e:
                        logging.error(f"Error adding column {col}: {e}")

        except Exception as e:
            logging.error(f"ESRS table init error: {e}")

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """ESRS dashboard istatistiklerini getir"""
        self.init_assessments_table()
        
        stats = {"covered_standards": 0, "completion_rate": 0}
        total_standards = 12

        try:
            # skip_tenant_filter=True because we handle company_id manually
            # OR we can let it inject, but we must remove manual WHERE.
            # Let's keep manual WHERE and rely on injection logic to skip if company_id is present.
            rows = self.execute_query(
                "SELECT standard_code, status FROM esrs_assessments WHERE company_id = ?",
                (company_id,)
            )
            status_map = {r['standard_code']: r['status'] for r in rows}

            completed_count = sum(1 for status in status_map.values() if status == "completed")

            stats["covered_standards"] = len(status_map)
            if total_standards > 0:
                stats["completion_rate"] = int((completed_count / total_standards) * 100)

        except Exception as e:
            logging.error(f"ESRS stats error: {e}")

        return stats

    def get_assessment_status(self, company_id: int) -> Dict[str, str]:
        """Tüm standartlar için durum haritasını getir"""
        self.init_assessments_table()
        status_map: Dict[str, str] = {}
        try:
            rows = self.execute_query(
                "SELECT standard_code, status FROM esrs_assessments WHERE company_id = ?",
                (company_id,)
            )
            status_map = {r['standard_code']: r['status'] for r in rows}
        except Exception as e:
            logging.error(f"ESRS status load error: {e}")
        return status_map

    def get_assessment_details(self, company_id: int, standard_code: str) -> Dict[str, str]:
        """Belirli bir standardın detaylarını getir"""
        self.init_assessments_table()
        details = {}
        try:
            rows = self.execute_query(
                """
                SELECT status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes 
                FROM esrs_assessments 
                WHERE company_id = ? AND standard_code = ?
                """,
                (company_id, standard_code),
            )
            if rows:
                row = rows[0]
                details = {
                    "status": row['status'],
                    "notes": row['notes'] or "",
                    "governance_notes": row['governance_notes'] or "",
                    "strategy_notes": row['strategy_notes'] or "",
                    "impact_risk_notes": row['impact_risk_notes'] or "",
                    "metrics_notes": row['metrics_notes'] or ""
                }
        except Exception as e:
            logging.error(f"ESRS details load error: {e}")
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
        try:
            exists_rows = self.execute_query(
                "SELECT 1 FROM esrs_assessments WHERE company_id = ? AND standard_code = ?",
                (company_id, standard_code),
            )

            if exists_rows:
                self.execute_update(
                    """
                    UPDATE esrs_assessments 
                    SET status = ?, notes = ?, governance_notes = ?, strategy_notes = ?, impact_risk_notes = ?, metrics_notes = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE company_id = ? AND standard_code = ?
                """,
                    (status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes, company_id, standard_code),
                )
            else:
                self.execute_update(
                    """
                    INSERT INTO esrs_assessments (company_id, standard_code, status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (company_id, standard_code, status, notes, governance_notes, strategy_notes, impact_risk_notes, metrics_notes),
                )
            return True
        except Exception as e:
            logging.error(f"ESRS update error: {e}")
            return False

    def get_materiality_analysis(self, company_id: int) -> list:
        """Çifte önemlilik analizi verilerini getir"""
        self.init_assessments_table()
        items = []
        try:
            # BaseTenantManager.execute_query returns dict-like objects
            rows = self.execute_query(
                """
                SELECT id, topic, impact_score, likelihood, financial_effect, environmental_effect, created_at
                FROM esrs_materiality
                WHERE company_id = ?
                ORDER BY created_at DESC
                """,
                (company_id,)
            )
            # No need to zip columns, execute_query already returns dict-like rows
            # But let's convert to pure dict if needed, or just return list of dicts
            items = [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"ESRS materiality fetch error: {e}")
        return items

    def add_materiality_item(self, company_id: int, topic: str, impact_score: int, likelihood: int, financial_effect: str, environmental_effect: str) -> bool:
        """Yeni önemlilik maddesi ekle"""
        self.init_assessments_table()
        try:
            self.execute_update(
                """
                INSERT INTO esrs_materiality (company_id, topic, impact_score, likelihood, financial_effect, environmental_effect)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (company_id, topic, impact_score, likelihood, financial_effect, environmental_effect)
            )
            return True
        except Exception as e:
            logging.error(f"ESRS materiality add error: {e}")
            return False

    def delete_materiality_item(self, item_id: int, company_id: int) -> bool:
        """Önemlilik maddesini sil"""
        self.init_assessments_table()
        try:
            self.execute_update(
                "DELETE FROM esrs_materiality WHERE id = ? AND company_id = ?",
                (item_id, company_id)
            )
            return True
        except Exception as e:
            logging.error(f"ESRS materiality delete error: {e}")
            return False
