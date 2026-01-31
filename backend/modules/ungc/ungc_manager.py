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
import sqlite3
from typing import Dict, List, Tuple
from config.database import DB_PATH


class UNGCManager:
    def __init__(self, db_path: str, config_path: str = 'config/ungc_config.json') -> None:
        self.db_path = db_path
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

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create_ungc_tables(self) -> None:
        """UNGC tablolarını oluştur"""
        conn = self._conn()
        cursor = conn.cursor()

        try:
            # UNGC uyumluluk durumu tablosu
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("PRAGMA table_info(ungc_evidence)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'file_path' not in columns:
                cursor.execute("ALTER TABLE ungc_evidence ADD COLUMN file_path TEXT")
                logging.info("ungc_evidence tablosuna file_path kolonu eklendi")

            conn.commit()
            logging.info("UNGC tabloları başarıyla oluşturuldu")

        except Exception as e:
            logging.error(f"UNGC tablo oluşturma hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_evidence(self, company_id: int, principle_id: str, evidence_type: str, 
                     description: str, file_path: str = None) -> bool:
        """Kanıt ekle"""
        conn = self._conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ungc_evidence 
                (company_id, principle_id, evidence_type, evidence_description, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, principle_id, evidence_type, description, file_path))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Evidence add error: {e}")
            return False
        finally:
            conn.close()

    def get_evidence(self, company_id: int) -> List[Dict]:
        """Kanıt listesini getir"""
        conn = self._conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, principle_id, evidence_type, evidence_description, file_path, created_at
                FROM ungc_evidence 
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (company_id,))
            
            evidence_list = []
            for row in cursor.fetchall():
                evidence_list.append({
                    'id': row[0],
                    'principle_id': row[1],
                    'evidence_type': row[2],
                    'evidence_description': row[3],
                    'file_path': row[4],
                    'created_at': row[5]
                })
            return evidence_list
        except Exception as e:
            logging.error(f"Evidence fetch error: {e}")
            return []
        finally:
            conn.close()

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


    def _load_present_gri_disclosures(self, cur, company_id: int, period: str) -> List[str]:
        # SDG indicator codes from responses
        rows = cur.execute(
            """
            SELECT DISTINCT i.code
            FROM sdg_indicators i
            JOIN responses r ON r.indicator_id=i.id
            WHERE r.company_id=? AND r.period=?
            """,
            (company_id, period)
        ).fetchall()
        sdg_codes = [r[0] for r in rows]
        if not sdg_codes:
            return []
        placeholders = ','.join('?' * len(sdg_codes))
        gri = [row[0] for row in cur.execute(
            f"SELECT DISTINCT gri_disclosure FROM map_sdg_gri WHERE sdg_indicator_code IN ({placeholders})",
            sdg_codes
        ).fetchall()]
        return gri

    def _load_present_tsrs_metrics(self, cur, sdg_codes: List[str], gri_disclosures: List[str]) -> List[Tuple[str, str]]:
        tsrs = []
        if sdg_codes:
            placeholders = ','.join('?' * len(sdg_codes))
            tsrs += cur.execute(
                f"SELECT tsrs_section, tsrs_metric FROM map_sdg_tsrs WHERE sdg_indicator_code IN ({placeholders})",
                sdg_codes
            ).fetchall()
        if gri_disclosures:
            gri_ph = ','.join('?' * len(gri_disclosures))
            tsrs += cur.execute(
                f"SELECT tsrs_section, tsrs_metric FROM map_gri_tsrs WHERE gri_disclosure IN ({gri_ph})",
                gri_disclosures
            ).fetchall()
        return tsrs

    def _load_company_policies(self, cur, company_id: int) -> Dict[str, str]:
        out = {}
        try:
            row = cur.execute(
                "SELECT data_sources, governance_notes, assurance_statement FROM company_info WHERE company_id=?",
                (company_id,)
            ).fetchone()
            if row:
                out["data_sources"] = row[0] or ""
                out["governance_notes"] = row[1] or ""
                out["assurance_statement"] = row[2] or ""
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
        conn = self._conn()
        cursor = conn.cursor()
        stats = {
            'total_principles': 10,
            'compliant_principles': 0,
            'total_evidence': 0,
            'average_score': 0.0
        }
        try:
            cursor.execute("SELECT COUNT(*) FROM ungc_compliance WHERE company_id = ? AND compliance_level IN ('Full', 'Partial')", (company_id,))
            stats['compliant_principles'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM ungc_evidence WHERE company_id = ?", (company_id,))
            stats['total_evidence'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(score) FROM ungc_compliance WHERE company_id = ?", (company_id,))
            stats['average_score'] = round(cursor.fetchone()[0] or 0.0, 2)
            
            return stats
        except Exception as e:
            logging.error(f"UNGC istatistikleri getirme hatası: {e}")
            return stats
        finally:
            conn.close()

    def compute_principle_status(self, company_id: int, period: str) -> Dict:
        """Ten Principles uyum durumu ve skorları."""
        with self._conn() as con:
            cur = con.cursor()

            # UNGC uyumluluk verilerini al
            compliance_data = {}
            try:
                rows = cur.execute(
                    "SELECT principle_id, compliance_level, score FROM ungc_compliance WHERE company_id = ?",
                    (company_id,)
                ).fetchall()
                for row in rows:
                    compliance_data[row[0]] = {
                        'compliance_level': row[1],
                        'score': row[2]
                    }
            except Exception as e:
                logging.error(f"UNGC compliance veri okuma hatası: {e}")

        thresholds = self.config.get("thresholds", {"full": 0.6, "partial": 0.2})
        self.config.get("mappings", {})
        principles = self.config.get("principles", [])

        details = []
        cats: Dict[str, List[float]] = {"Human Rights": [], "Labour": [], "Environment": [], "Anti-Corruption": []}

        for p in principles:
            pid = p.get("id")
            cat = p.get("category") or "General"
            title = p.get("title", "")

            # Veritabanından uyumluluk verisini al
            compliance_info = compliance_data.get(pid, {})
            compliance_info.get('compliance_level', 'None')
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
        conn = self._conn()
        cursor = conn.cursor()
        
        try:
            # Check if record exists
            cursor.execute("SELECT id FROM ungc_compliance WHERE company_id = ? AND principle_id = ?", (company_id, principle_id))
            row = cursor.fetchone()
            
            # Calculate score based on level
            score = 0.0
            if compliance_level == 'Full':
                score = 1.0
            elif compliance_level == 'Partial':
                score = 0.5
            
            if row:
                # Update
                cursor.execute("""
                    UPDATE ungc_compliance 
                    SET compliance_level = ?, score = ?, notes = ?, last_assessed = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (compliance_level, score, notes, row[0]))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO ungc_compliance (company_id, principle_id, compliance_level, score, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, principle_id, compliance_level, score, notes))
                
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"UNGC veri kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

if __name__ == '__main__':
    # Basit manuel test
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    company_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    period = sys.argv[3] if len(sys.argv) > 3 else '2024'
    mgr = UNGCManager(db)
    res = mgr.compute_principle_status(company_id, period)
    logging.info(json.dumps(res, ensure_ascii=False, indent=2))
