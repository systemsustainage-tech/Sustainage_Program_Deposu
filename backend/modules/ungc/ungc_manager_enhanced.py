import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UN Global Compact - Enhanced Manager
- KPI-based scoring system
- Level classification (Learner/Active/Advanced)
- Progress tracking
- COP data generation
"""
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional
from config.database import DB_PATH


class UNGCManagerEnhanced:
    """Enhanced UNGC Manager with full KPI and scoring system"""

    def __init__(self, db_path: str, config_path: str = 'config/ungc_config.json') -> None:
        self.db_path = db_path
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load UNGC configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Config load error: {e}")
            return {
                "principles": [],
                "kpis": [],
                "mappings": {},
                "levels": {},
                "thresholds": {"full": 0.7, "partial": 0.4}
            }

    def _conn(self) -> sqlite3.Connection:
        """Database connection"""
        return sqlite3.connect(self.db_path)

    def get_principle_info(self, principle_id: str, lang: str = 'tr') -> Optional[Dict]:
        """Get principle information"""
        for p in self.config.get('principles', []):
            if p['id'] == principle_id:
                return {
                    'id': p['id'],
                    'number': p['number'],
                    'category': p['category'],
                    'title': p.get(f'title_{lang}', p.get('title_en', '')),
                    'description': p.get(f'description_{lang}', p.get('description_en', '')),
                    'evidence_required': p.get('evidence_required', [])
                }
        return None

    def get_principle_kpis(self, principle_id: str) -> List[Dict]:
        """Get all KPIs for a principle"""
        kpis = []
        for kpi in self.config.get('kpis', []):
            if kpi.get('principle_id') == principle_id:
                kpis.append(kpi)
        return kpis

    def get_kpi_data(self, company_id: int, kpi_id: str, period: Optional[str] = None) -> Optional[float]:
        """
        Get KPI data from database
        Returns the current value or None
        """
        if period is None:
            period = str(datetime.now().year)

        conn = self._conn()
        try:
            # KPI verisini ungc_kpi_data tablosundan çek
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT value FROM ungc_kpi_data
                WHERE company_id = ? AND kpi_id = ? AND period = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (company_id, kpi_id, period)).fetchone()

            if result:
                return float(result[0])
            return None
        except Exception:
            # Tablo yoksa None dön
            return None
        finally:
            conn.close()

    def calculate_kpi_score(self, kpi: Dict, current_value: Optional[float]) -> float:
        """
        Calculate score for a single KPI
        Returns: 0-100 score
        """
        if current_value is None:
            return 0.0

        kpi_type = kpi.get('type', 'number')
        target = kpi.get('target', 100)
        inverse = kpi.get('inverse', False)

        if kpi_type == 'boolean':
            # Boolean: 100 if True, 0 if False
            score = 100.0 if current_value > 0 else 0.0

        elif kpi_type == 'percentage':
            # Percentage: value is the score (0-100)
            score = min(100.0, max(0.0, current_value))

        elif kpi_type == 'number':
            # Number: normalize against target
            if target > 0:
                score = min(100.0, (current_value / target) * 100.0)
            else:
                score = current_value if current_value <= 100 else 100.0

        else:
            score = 0.0

        # Apply inverse if needed (for negative KPIs like violations)
        if inverse:
            score = 100.0 - score

        return score

    def calculate_principle_score(self, company_id: int, principle_id: str, period: Optional[str] = None) -> Dict:
        """
        Calculate compliance score for a principle
        Returns: {
            'principle_id': str,
            'kpis': List[Dict],
            'total_score': float (0-100),
            'weighted_score': float (0-100)
        }
        """
        if period is None:
            period = str(datetime.now().year)

        kpis = self.get_principle_kpis(principle_id)
        if not kpis:
            return {
                'principle_id': principle_id,
                'kpis': [],
                'total_score': 0.0,
                'weighted_score': 0.0
            }

        kpi_results = []
        total_weight = 0.0
        weighted_sum = 0.0

        for kpi in kpis:
            kpi_id = kpi['kpi_id']
            weight = kpi.get('weight', 1.0)

            # Get current value from DB
            current_value = self.get_kpi_data(company_id, kpi_id, period)

            # Calculate KPI score
            kpi_score = self.calculate_kpi_score(kpi, current_value)

            # Weighted contribution
            weighted_contribution = kpi_score * weight
            weighted_sum += weighted_contribution
            total_weight += weight

            kpi_results.append({
                'kpi_id': kpi_id,
                'name': kpi.get('name_tr', kpi.get('name_en', '')),
                'type': kpi.get('type'),
                'weight': weight,
                'current_value': current_value,
                'target': kpi.get('target'),
                'score': round(kpi_score, 2),
                'weighted_contribution': round(weighted_contribution, 2)
            })

        # Calculate final scores
        total_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0

        return {
            'principle_id': principle_id,
            'kpis': kpi_results,
            'total_score': round(total_score, 2),
            'weighted_score': round(total_score, 2)  # Same for now
        }

    def _get_principle_evidence_types(self, company_id: int, principle_id: str) -> List[str]:
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ungc_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    principle_id VARCHAR(10) NOT NULL,
                    evidence_type TEXT,
                    file_path TEXT,
                    url TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            rows = cursor.execute(
                """
                SELECT DISTINCT COALESCE(evidence_type, '') FROM ungc_evidence
                WHERE company_id=? AND principle_id=?
                """,
                (company_id, principle_id)
            ).fetchall()
            return [r[0] for r in rows if r and r[0]]
        finally:
            conn.close()

    def compute_principle_gaps(self, company_id: int, principle_id: str, period: Optional[str] = None) -> Dict:
        if period is None:
            period = str(datetime.now().year)
        info = self.get_principle_info(principle_id)
        required = info.get('evidence_required', []) if info else []
        present = self._get_principle_evidence_types(company_id, principle_id)
        missing_evidence = [e for e in required if e not in present]
        kpis = self.get_principle_kpis(principle_id)
        missing_kpi_data = []
        below_target_kpis = []
        for kpi in kpis:
            kpi_id_val = kpi.get('kpi_id')
            if not isinstance(kpi_id_val, str):
                continue
            current_value = self.get_kpi_data(company_id, kpi_id_val, period)
            if current_value is None:
                missing_kpi_data.append({
                    'kpi_id': kpi_id_val,
                    'name': kpi.get('name_tr', kpi.get('name_en', ''))
                })
                continue
            score = self.calculate_kpi_score(kpi, current_value)
            thresholds_cfg = self.config.get('thresholds', {})
            kpi_threshold = float(thresholds_cfg.get('kpi_below_target_pct', 60.0))
            if score < kpi_threshold:
                below_target_kpis.append({
                    'kpi_id': kpi_id_val,
                    'name': kpi.get('name_tr', kpi.get('name_en', '')),
                    'score': round(score, 2)
                })
        return {
            'missing_evidence': missing_evidence,
            'missing_kpi_data': missing_kpi_data,
            'below_target_kpis': below_target_kpis
        }

    def calculate_category_scores(self, company_id: int, period: Optional[str] = None) -> Dict[str, float]:
        """Calculate scores for each category (Human Rights, Labour, Environment, Anti-Corruption)"""
        categories: Dict[str, List[float]] = {
            'Human Rights': [],
            'Labour': [],
            'Environment': [],
            'Anti-Corruption': []
        }

        # Group principles by category
        for principle in self.config.get('principles', []):
            category = principle.get('category', 'General')
            principle_id = principle['id']

            # Calculate principle score
            result = self.calculate_principle_score(company_id, principle_id, period)
            score = result['total_score']

            if category in categories:
                categories[category].append(score)

        # Calculate average for each category
        category_scores = {}
        for cat, scores in categories.items():
            if scores:
                category_scores[cat] = round(sum(scores) / len(scores), 2)
            else:
                category_scores[cat] = 0.0

        return category_scores

    def calculate_overall_score(self, company_id: int, period: Optional[str] = None) -> Dict:
        """
        Calculate overall UNGC compliance score
        Returns: {
            'overall_score': float (0-100),
            'level': str (Learner/Active/Advanced),
            'category_scores': Dict,
            'principle_scores': List[Dict]
        }
        """
        principle_scores = []
        all_scores = []

        # Calculate score for each principle
        for principle in self.config.get('principles', []):
            principle_id = principle['id']
            result = self.calculate_principle_score(company_id, principle_id, period)

            principle_scores.append({
                'principle_id': principle_id,
                'principle_number': principle.get('number'),
                'category': principle.get('category'),
                'title': principle.get('title_tr', principle.get('title_en', '')),
                'score': result['total_score']
            })

            all_scores.append(result['total_score'])

        # Calculate overall score
        overall_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0

        # Get category scores
        category_scores = self.calculate_category_scores(company_id, period)

        # Determine level
        level_info = self.get_level_classification(overall_score)

        return {
            'overall_score': overall_score,
            'level': level_info['level'],
            'level_info': level_info,
            'category_scores': category_scores,
            'principle_scores': principle_scores
        }

    def get_level_classification(self, score: float) -> Dict:
        """
        Classify UNGC level based on score
        Returns: {
            'level': str,
            'badge': str,
            'color': str,
            'description': str
        }
        """
        levels = self.config.get('levels', {})

        # Find matching level
        for level_key, level_data in levels.items():
            min_score = level_data.get('min_score', 0)
            max_score = level_data.get('max_score', 100)

            if min_score <= score <= max_score:
                return {
                    'level': level_data.get('name', level_key.capitalize()),
                    'level_key': level_key,
                    'badge': level_data.get('badge', ''),
                    'color': level_data.get('color', '#808080'),
                    'description': level_data.get('description_tr', level_data.get('description_en', '')),
                    'min_score': min_score,
                    'max_score': max_score,
                    'requirements': level_data.get('requirements', [])
                }

        # Default to learner
        return {
            'level': 'Learner',
            'level_key': 'learner',
            'badge': '',
            'color': '#CD7F32',
            'description': 'Başlangıç seviyesi',
            'min_score': 0,
            'max_score': 40,
            'requirements': []
        }

    def generate_cop_data(self, company_id: int, period: Optional[str] = None, ceo_statement: str = "") -> Dict:
        """
        Generate Communication on Progress (COP) report data
        """
        if period is None:
            period = str(datetime.now().year)

        # Calculate overall compliance
        overall_data = self.calculate_overall_score(company_id, period)

        # COP template
        cop_template = self.config.get('cop_template', {})

        # Organize data by COP sections
        sections: List[Dict[str, Any]] = []
        cop_data: Dict[str, Any] = {
            'meta': {
                'company_id': company_id,
                'period': period,
                'generated_at': datetime.now().isoformat(),
                'overall_score': overall_data['overall_score'],
                'level': overall_data['level']
            },
            'ceo_statement': ceo_statement,
            'sections': sections
        }

        # Build sections
        for section in cop_template.get('sections', []):
            section_id = section.get('id')

            if section_id == 'ceo_statement':
                continue  # Already handled

            section_principles = section.get('principles', [])
            section_data = {
                'id': section_id,
                'title': section.get('name_tr', section.get('name_en', '')),
                'principles': []
            }

            # Add principle data
            for principle_id in section_principles:
                principle_score = self.calculate_principle_score(company_id, principle_id, period)
                principle_info = self.get_principle_info(principle_id)
                gaps = self.compute_principle_gaps(company_id, principle_id, period)
                if principle_info:
                    section_data['principles'].append({
                        'id': principle_id,
                        'title': principle_info['title'],
                        'score': principle_score['total_score'],
                        'kpis': principle_score['kpis'],
                        'gaps': gaps
                    })

            cop_data['sections'].append(section_data)

        return cop_data

    def track_progress(self, company_id: int, start_period: str, end_period: str) -> Dict:
        """
        Track progress between two periods
        Returns comparison data
        """
        start_data = self.calculate_overall_score(company_id, start_period)
        end_data = self.calculate_overall_score(company_id, end_period)

        # Calculate improvements
        overall_improvement = end_data['overall_score'] - start_data['overall_score']

        # Category improvements
        category_improvements = {}
        for category in start_data['category_scores'].keys():
            start_score = start_data['category_scores'].get(category, 0)
            end_score = end_data['category_scores'].get(category, 0)
            category_improvements[category] = end_score - start_score

        # Principle improvements
        principle_improvements = []
        for i, start_p in enumerate(start_data['principle_scores']):
            end_p = end_data['principle_scores'][i]
            improvement = end_p['score'] - start_p['score']

            principle_improvements.append({
                'principle_id': start_p['principle_id'],
                'title': start_p['title'],
                'start_score': start_p['score'],
                'end_score': end_p['score'],
                'improvement': round(improvement, 2)
            })

        return {
            'start_period': start_period,
            'end_period': end_period,
            'start_score': start_data['overall_score'],
            'end_score': end_data['overall_score'],
            'overall_improvement': round(overall_improvement, 2),
            'start_level': start_data['level'],
            'end_level': end_data['level'],
            'category_improvements': category_improvements,
            'principle_improvements': principle_improvements
        }

    def save_kpi_data(self, company_id: int, kpi_id: str, value: float,
                      period: Optional[str] = None, evidence_id: Optional[int] = None) -> bool:
        """Save KPI data to database"""
        if period is None:
            period = str(datetime.now().year)

        conn = self._conn()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ungc_kpi_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    kpi_id VARCHAR(20) NOT NULL,
                    value REAL NOT NULL,
                    period VARCHAR(10) NOT NULL,
                    evidence_id INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    UNIQUE(company_id, kpi_id, period)
                )
            """)

            # Insert or update
            cursor.execute("""
                INSERT OR REPLACE INTO ungc_kpi_data 
                (company_id, kpi_id, value, period, evidence_id, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, kpi_id, value, period, evidence_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"KPI save error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def seed_company_kpis(self, company_id: int, period: Optional[str] = None) -> int:
        if period is None:
            period = str(datetime.now().year)
        seeded = 0
        for kpi in self.config.get('kpis', []):
            kpi_id = kpi.get('kpi_id')
            kpi_type = kpi.get('type', 'number')
            target = kpi.get('target')
            inverse = bool(kpi.get('inverse', False))
            if kpi_type == 'boolean':
                value = 1.0
            elif kpi_type == 'percentage':
                base = target if isinstance(target, (int, float)) else 60.0
                value = max(0.0, min(100.0, float(base)))
            else:
                if isinstance(target, (int, float)):
                    value = float(target) * (0.8 if not inverse else 0.2)
                else:
                    value = 10.0 if not inverse else 0.0
            ok = self.save_kpi_data(company_id, kpi_id, float(value), period)
            if ok:
                seeded += 1
        return seeded

    def update_compliance_from_kpis(self, company_id: int, period: Optional[str] = None) -> Dict:
        if period is None:
            period = str(datetime.now().year)
        thresholds = self.config.get('thresholds', {'full': 0.7, 'partial': 0.4, 'none': 0})
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
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
                """
            )
            for principle in self.config.get('principles', []):
                pid = principle.get('id')
                result = self.calculate_principle_score(company_id, pid, period)
                score_pct = result.get('total_score', 0.0)
                normalized = round(float(score_pct) / 100.0, 4)
                if normalized >= thresholds.get('full', 0.7):
                    level = 'Full'
                elif normalized >= thresholds.get('partial', 0.4):
                    level = 'Partial'
                else:
                    level = 'None'
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO ungc_compliance
                    (id, company_id, principle_id, compliance_level, evidence_count, score, last_assessed, notes)
                    VALUES (
                        COALESCE((SELECT id FROM ungc_compliance WHERE company_id=? AND principle_id=?), NULL),
                        ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, NULL
                    )
                    """,
                    (company_id, pid, company_id, pid, level, 0, normalized)
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        return self.calculate_overall_score(company_id, period)

    def save_compliance_edit(self, company_id: int, principle_id: str, compliance_level: str, notes: Optional[str] = None) -> bool:
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
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
                """
            )
            cursor.execute(
                """
                INSERT OR REPLACE INTO ungc_compliance
                (id, company_id, principle_id, compliance_level, evidence_count, score, last_assessed, notes)
                VALUES (
                    COALESCE((SELECT id FROM ungc_compliance WHERE company_id=? AND principle_id=?), NULL),
                    ?, ?, ?, COALESCE((SELECT evidence_count FROM ungc_compliance WHERE company_id=? AND principle_id=?), 0),
                    COALESCE((SELECT score FROM ungc_compliance WHERE company_id=? AND principle_id=?), 0.0),
                    CURRENT_TIMESTAMP,
                    ?
                )
                """,
                (company_id, principle_id, company_id, principle_id, compliance_level, company_id, principle_id, company_id, principle_id, notes)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Evidence save error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_evidence(self, company_id: int, principle_id: str, evidence_type: str = 'file', file_path: Optional[str] = None, url: Optional[str] = None, notes: Optional[str] = None) -> bool:
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ungc_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    principle_id VARCHAR(10) NOT NULL,
                    evidence_type TEXT,
                    file_path TEXT,
                    url TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cols = [row[1] for row in cursor.execute("PRAGMA table_info(ungc_evidence)").fetchall()]
            if 'url' not in cols:
                cursor.execute("ALTER TABLE ungc_evidence ADD COLUMN url TEXT")
            if 'file_path' not in cols:
                cursor.execute("ALTER TABLE ungc_evidence ADD COLUMN file_path TEXT")
            cursor.execute(
                """
                INSERT INTO ungc_evidence(company_id, principle_id, evidence_type, file_path, url, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (company_id, principle_id, evidence_type, file_path, url, notes)
            )
            try:
                cursor.execute(
                    """
                    UPDATE ungc_compliance
                    SET evidence_count = COALESCE(evidence_count,0) + 1, last_assessed = CURRENT_TIMESTAMP
                    WHERE company_id=? AND principle_id=?
                    """,
                    (company_id, principle_id)
                )
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating compliance evidence: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_tables(self) -> None:
        """Create necessary UNGC tables"""
        conn = self._conn()
        try:
            cursor = conn.cursor()

            # KPI data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ungc_kpi_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    kpi_id VARCHAR(20) NOT NULL,
                    value REAL NOT NULL,
                    period VARCHAR(10) NOT NULL,
                    evidence_id INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    UNIQUE(company_id, kpi_id, period)
                )
            """)

            # Compliance table
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

            # Evidence table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ungc_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    principle_id VARCHAR(10) NOT NULL,
                    evidence_type VARCHAR(50) NOT NULL,
                    evidence_description TEXT,
                    evidence_source VARCHAR(100),
                    file_path VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("UNGC tables created successfully")

        except Exception as e:
            logging.error(f"Table creation error: {e}")
            conn.rollback()
        finally:
            conn.close()


if __name__ == '__main__':
    # Test
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else DB_PATH

    manager = UNGCManagerEnhanced(db)
    manager.create_tables()

    # Test overall score
    result = manager.calculate_overall_score(company_id=1)
    logging.info("\n=== UNGC Overall Compliance ===")
    logging.info(f"Overall Score: {result['overall_score']}%")
    logging.info(f"Level: {result['level']} {result['level_info']['badge']}")
    logging.info("\nCategory Scores:")
    for cat, score in result['category_scores'].items():
        logging.info(f"  {cat}: {score}%")

