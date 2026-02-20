import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UN Global Compact (Ten Principles) uyum yöneticisi.
- Salt-okunur: Mevcut verilerden (DB, CSV, anket, ERP) hesaplar.
- Mapping: SDG/GRI/TSRS kodlarını mevcut eşleştirmelerle tutarlı kullanır.
"""
import csv
import json
import os
from typing import Dict, List, Tuple, Optional
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager


class UNGCManager(BaseTenantManager):
    def __init__(self, db_path: str, config_path: str = 'config/ungc_config.json', company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # Minimal fallback
            return {
                "principles": [
                    {"id": "P10", "category": "Anti-Corruption", "title": "Work against corruption.", "evidence_required": ["policy", "training", "incidents"]}
                ],
                "mappings": {
                    "P10": {"sdg": ["16.5"], "gri": ["205-1", "205-2", "206"], "tsrs": ["G1"]}
                },
                "thresholds": {"full": 0.6, "partial": 0.2},
                "data_sources": {"csv_dirs": ["data/imports"]}
            }

    def create_ungc_tables(self) -> None:
        """UNGC tablolarını oluştur"""
        try:
            # UNGC uyumluluk durumu tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS ungc_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    principle_id VARCHAR(10) NOT NULL,
                    compliance_level VARCHAR(20) DEFAULT 'None',
                    evidence_count INTEGER DEFAULT 0,
                    score REAL DEFAULT 0.0,
                    last_assessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # UNGC kanıt tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS ungc_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    principle_id VARCHAR(10) NOT NULL,
                    evidence_type VARCHAR(50) NOT NULL,
                    evidence_description TEXT,
                    evidence_source VARCHAR(100),
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # Migration: file_path kontrolü
            rows = self.execute_query("PRAGMA table_info(ungc_evidence)")
            columns = [row['name'] for row in rows]
            if 'file_path' not in columns:
                self.execute_update("ALTER TABLE ungc_evidence ADD COLUMN file_path TEXT")
                logging.info("ungc_evidence tablosuna file_path kolonu eklendi")

            logging.info("UNGC tabloları başarıyla oluşturuldu")

        except Exception as e:
            logging.error(f"UNGC tablo oluşturma hatası: {e}")

    def add_evidence(self, company_id: int, principle_id: str, evidence_type: str, 
                     description: str, file_path: str = None) -> bool:
        """Kanıt ekle"""
        try:
            self.execute_update("""
                INSERT INTO ungc_evidence 
                (company_id, principle_id, evidence_type, evidence_description, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, principle_id, evidence_type, description, file_path))
            return True
        except Exception as e:
            logging.error(f"Evidence add error: {e}")
            return False

    def get_evidence(self, company_id: int) -> List[Dict]:
        """Kanıt listesini getir"""
        try:
            rows = self.execute_query("""
                SELECT id, principle_id, evidence_type, evidence_description, file_path, created_at
                FROM ungc_evidence 
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (company_id,))
            
            evidence_list = []
            for row in rows:
                evidence_list.append({
                    'id': row['id'],
                    'principle_id': row['principle_id'],
                    'evidence_type': row['evidence_type'],
                    'evidence_description': row['evidence_description'],
                    'file_path': row['file_path'],
                    'created_at': row['created_at']
                })
            return evidence_list
        except Exception as e:
            logging.error(f"Evidence fetch error: {e}")
            return []

    def get_thresholds(self) -> Dict[str, float]:
        """Eşik değerlerini getir"""
        return self.config.get('thresholds', {'full': 0.6, 'partial': 0.2})

    def update_thresholds(self, full: float, partial: float) -> bool:
        """Eşik değerlerini güncelle"""
        try:
            self.config['thresholds'] = {'full': full, 'partial': partial}
            # Config dosyasina yaz
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Threshold update error: {e}")
            return False


    def _load_present_gri_disclosures(self, company_id: int, period: str) -> List[str]:
        # SDG indicator codes from responses
        rows = self.execute_query(
            """
            SELECT DISTINCT i.code
            FROM sdg_indicators i
            JOIN responses r ON r.indicator_id=i.id
            WHERE r.company_id=? AND r.period=?
            """,
            (company_id, period)
        )
        sdg_codes = [r['code'] for r in rows]
        if not sdg_codes:
            return []
        placeholders = ','.join('?' * len(sdg_codes))
        
        gri_rows = self.execute_query(
            f"SELECT DISTINCT gri_disclosure FROM map_sdg_gri WHERE sdg_indicator_code IN ({placeholders})",
            tuple(sdg_codes)
        )
        return [row['gri_disclosure'] for row in gri_rows]

    def _load_present_tsrs_metrics(self, sdg_codes: List[str], gri_disclosures: List[str]) -> List[Dict]:
        tsrs = []
        if sdg_codes:
            placeholders = ','.join('?' * len(sdg_codes))
            tsrs += self.execute_query(
                f"SELECT tsrs_section, tsrs_metric FROM map_sdg_tsrs WHERE sdg_indicator_code IN ({placeholders})",
                tuple(sdg_codes)
            )
        if gri_disclosures:
            gri_ph = ','.join('?' * len(gri_disclosures))
            tsrs += self.execute_query(
                f"SELECT tsrs_section, tsrs_metric FROM map_gri_tsrs WHERE gri_disclosure IN ({gri_ph})",
                tuple(gri_disclosures)
            )
        return tsrs

    def _load_company_policies(self, company_id: int) -> Dict[str, str]:
        out = {}
        try:
            rows = self.execute_query(
                "SELECT data_sources, governance_notes, assurance_statement FROM company_info WHERE company_id=?",
                (company_id,)
            )
            if rows:
                row = rows[0]
                out["data_sources"] = row['data_sources'] or ""
                out["governance_notes"] = row['governance_notes'] or ""
                out["assurance_statement"] = row['assurance_statement'] or ""
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        return out

    def _load_csv_signals(self) -> Dict[str, List[Dict[str, str]]]:
        signals = {}
        dirs = self.config.get("data_sources", {}).get("csv_dirs", [])
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for name in os.listdir(d):
                if name.lower().endswith('.csv'):
                    path = os.path.join(d, name)
                    try:
                        with open(path, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            signals[name] = [row for row in reader]
                    except Exception as e:
                        logging.error(f"Silent error caught: {str(e)}")
        return signals

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        stats = {
            'total_principles': 10,
            'compliant_principles': 0,
            'total_evidence': 0,
            'average_score': 0.0
        }
        try:
            rows = self.execute_query("SELECT COUNT(*) as cnt FROM ungc_compliance WHERE company_id = ? AND compliance_level IN ('Full', 'Partial')", (company_id,))
            stats['compliant_principles'] = rows[0]['cnt'] if rows else 0
            
            rows = self.execute_query("SELECT COUNT(*) as cnt FROM ungc_evidence WHERE company_id = ?", (company_id,))
            stats['total_evidence'] = rows[0]['cnt'] if rows else 0
            
            rows = self.execute_query("SELECT AVG(score) as avg_score FROM ungc_compliance WHERE company_id = ?", (company_id,))
            stats['average_score'] = round(rows[0]['avg_score'] or 0.0, 2) if rows else 0.0
            
            return stats
        except Exception as e:
            logging.error(f"UNGC istatistikleri getirme hatası: {e}")
            return stats

    def compute_principle_status(self, company_id: int, period: str) -> Dict:
        """Ten Principles uyum durumu ve skorları."""
        # UNGC uyumluluk verilerini al
        compliance_data = {}
        try:
            rows = self.execute_query(
                "SELECT principle_id, compliance_level, score FROM ungc_compliance WHERE company_id = ?",
                (company_id,)
            )
            for row in rows:
                compliance_data[row['principle_id']] = {
                    'compliance_level': row['compliance_level'],
                    'score': row['score']
                }
        except Exception as e:
            logging.error(f"UNGC compliance veri okuma hatası: {e}")

        thresholds = self.config.get("thresholds", {"full": 0.6, "partial": 0.2})
        principles = self.config.get("principles", [])

        details = []
        cats: Dict[str, List[float]] = {"Human Rights": [], "Labour": [], "Environment": [], "Anti-Corruption": []}

        for p in principles:
            pid = p.get("id")
            cat = p.get("category") or "General"
            title = p.get("title", "")

            # Veritabanından uyumluluk verisini al
            compliance_info = compliance_data.get(pid, {})
            score = compliance_info.get('score', 0.0)

            # Durum belirleme
            if score >= thresholds["full"]:
                status = "Full"
            elif score >= thresholds["partial"]:
                status = "Partial"
            else:
                status = "None"

            det = {
                "principle_id": pid,
                "category": cat,
                "title": title,
                "status": status,
                "score": score * 100  # Yüzde olarak
            }
            details.append(det)
            cats.setdefault(cat, []).append(det["score"])

        # Category and overall scores
        def avg(arr: List[float]) -> float:
            return round(sum(arr)/max(len(arr),1), 1)
        category_scores = {k: avg(v) for k, v in cats.items()}
        overall = avg([d["score"] for d in details])

        return {
            "principles": details,
            "category_scores": category_scores,
            "overall_score": overall
        }

    def save_compliance_data(self, company_id: int, principle_id: str, compliance_level: str, notes: str = None) -> bool:
        """UNGC uyumluluk verisini kaydet"""
        try:
            # Check if record exists
            rows = self.execute_query("SELECT id FROM ungc_compliance WHERE company_id = ? AND principle_id = ?", (company_id, principle_id))
            row = rows[0] if rows else None
            
            # Calculate score based on level
            score = 0.0
            if compliance_level == 'Full':
                score = 1.0
            elif compliance_level == 'Partial':
                score = 0.5
            
            if row:
                # Update
                self.execute_update("""
                    UPDATE ungc_compliance 
                    SET compliance_level = ?, score = ?, notes = ?, last_assessed = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (compliance_level, score, notes, row['id']))
            else:
                # Insert
                self.execute_update("""
                    INSERT INTO ungc_compliance (company_id, principle_id, compliance_level, score, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, principle_id, compliance_level, score, notes))
                
            return True
        except Exception as e:
            logging.error(f"UNGC veri kaydetme hatası: {e}")
            return False

if __name__ == '__main__':
    # Basit manuel test
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    company_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    period = sys.argv[3] if len(sys.argv) > 3 else '2024'
    mgr = UNGCManager(db)
    res = mgr.compute_principle_status(company_id, period)
    logging.info(json.dumps(res, ensure_ascii=False, indent=2))
