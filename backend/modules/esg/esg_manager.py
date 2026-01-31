import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
from config.database import DB_PATH


class ESGManager:
    """
    ESG skor yöneticisi.
    - E/S/G sütunları için skorları gerçek verilerden hesaplar
    - Kaynaklar: SDG soru yanıtları, GRI yanıtları, TSRS yanıtları ve materyalite,
      varsa anket ve ERP sinyalleri (bonus)
    - Salt okunur; veritabanına yazmaz.
    """

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, 'config', 'esg_config.json')
        self.config = self._load_config()
        self.db_path = os.path.join(base_dir, self.config['sources']['db_path'])
        self._init_db()

    def _init_db(self) -> None:
        """ESG skor tablosunu oluştur"""
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS esg_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    score_date DATE DEFAULT CURRENT_DATE,
                    e_score REAL,
                    s_score REAL,
                    g_score REAL,
                    overall_score REAL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # Check if columns exist and add them if not (migration)
            cursor.execute("PRAGMA table_info(esg_scores)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'score_date' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN score_date DATE")
                cursor.execute("UPDATE esg_scores SET score_date = DATE('now') WHERE score_date IS NULL")
            
            if 'e_score' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN e_score REAL")
            
            if 's_score' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN s_score REAL")
            
            if 'g_score' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN g_score REAL")
            
            if 'overall_score' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN overall_score REAL")
            
            if 'details' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN details TEXT")
                
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN created_at TIMESTAMP")
                cursor.execute("UPDATE esg_scores SET created_at = DATETIME('now') WHERE created_at IS NULL")
            
            if 'year' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN year INTEGER")
                cursor.execute("UPDATE esg_scores SET year = CAST(strftime('%Y', score_date) AS INTEGER) WHERE year IS NULL")

            if 'quarter' not in columns:
                cursor.execute("ALTER TABLE esg_scores ADD COLUMN quarter INTEGER")
                cursor.execute("UPDATE esg_scores SET quarter = ((CAST(strftime('%m', score_date) AS INTEGER) - 1) / 3) + 1 WHERE quarter IS NULL")
                
            conn.commit()
        except Exception as e:
            logging.error(f"ESG tablo olusturma hatasi: {e}")
        finally:
            conn.close()

    def _load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # Minimal varsayılanlar
            return {
                'weights': {'E': 0.4, 'S': 0.3, 'G': 0.3},
                'sources': {'db_path': DB_PATH},
                'scoring': {
                    'min_completeness_to_count': 0.5,
                    'evidence_bonus': 0.05,
                    'materiality_bonus': 0.1,
                    'normalize_method': 'ratio_answered_to_total'
                },
                'mappings': {
                    'E': {'gri_categories': ['Environmental'], 'tsrs_sections': ['TSRS-E1','TSRS-E2','TSRS-E3','TSRS-E4','TSRS-E5']},
                    'S': {'gri_categories': ['Social'], 'tsrs_sections': ['TSRS-S1','TSRS-S2','TSRS-S3','TSRS-S4']},
                    'G': {'gri_standards': ['GRI 2'], 'tsrs_sections': ['TSRS-G1']}
                }
            }

    def update_weights(self, new_weights: Dict[str, float]) -> bool:
        """Ağırlık katsayılarını güncelle ve kaydet"""
        try:
            # Doğrulama: Toplam 1.0 olmalı (yaklaşık)
            total = sum(new_weights.values())
            if not (0.99 <= total <= 1.01):
                logging.warning(f"Ağırlık toplamı 1.0 değil: {total}")
                # Yine de kaydetmeye izin verelim, belki kullanıcı ayarlıyordur
            
            # Mevcut configi güncelle
            self.config['weights'] = new_weights
            
            # Dosyaya yaz
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
                
            logging.info(f"ESG ağırlıkları güncellendi: {new_weights}")
            return True
        except Exception as e:
            logging.error(f"Ağırlık güncelleme hatası: {e}")
            return False

    def _connect(self) -> None:
        return sqlite3.connect(self.db_path)

    def _safe_count(self, cursor, table: str, where: str = None, params: Tuple = ()) -> int:
        try:
            allowed_tables = {
                'gri_indicators i JOIN gri_standards s ON i.standard_id = s.id',
                'gri_responses r JOIN gri_indicators i ON r.indicator_id=i.id JOIN gri_standards s ON i.standard_id=s.id',
                'tsrs_indicators i JOIN tsrs_standards s ON i.standard_id=s.id',
                'tsrs_responses r JOIN tsrs_indicators i ON r.indicator_id=i.id JOIN tsrs_standards s ON i.standard_id=s.id',
                'sdg_question_responses',
                'tsrs_materiality_assessment',
                'erp_metrics',
                'supplier_assessments',
                'survey_responses',
            }
            allowed_wheres = {
                's.category = ?',
                'r.company_id=? AND s.category=? AND r.response_value IS NOT NULL',
                's.code = ?',
                'r.company_id=? AND s.code=? AND r.response_value IS NOT NULL',
                'company_id=? AND (answer_text IS NOT NULL OR answer_value IS NOT NULL)',
                'company_id=? AND is_material=1',
            }
            if table not in allowed_tables:
                return 0
            q = 'SELECT COUNT(*) FROM ' + table
            if where:
                if where not in allowed_wheres:
                    return 0
                q += ' WHERE ' + where
            cursor.execute(q, params)
            return cursor.fetchone()[0] or 0
        except Exception:
            return 0

    def compute_scores(self, company_id: int, period: str = None) -> Dict:
        """E, S, G skorlarını hesaplar ve genel ESG skorunu döner."""
        conn = self._connect()
        cur = conn.cursor()
        cfg = self.config
        sc = cfg['scoring']

        # GRI yanıtları: kategoriye göre cevaplanan gösterge oranı
        gri_e_total = self._safe_count(cur, 'gri_indicators i JOIN gri_standards s ON i.standard_id = s.id', "s.category = ?", ("Environmental",))
        gri_e_answered = self._safe_count(cur, 'gri_responses r JOIN gri_indicators i ON r.indicator_id=i.id JOIN gri_standards s ON i.standard_id=s.id', "r.company_id=? AND s.category=? AND r.response_value IS NOT NULL", (company_id, "Environmental"))

        gri_s_total = self._safe_count(cur, 'gri_indicators i JOIN gri_standards s ON i.standard_id = s.id', "s.category = ?", ("Social",))
        gri_s_answered = self._safe_count(cur, 'gri_responses r JOIN gri_indicators i ON r.indicator_id=i.id JOIN gri_standards s ON i.standard_id=s.id', "r.company_id=? AND s.category=? AND r.response_value IS NOT NULL", (company_id, "Social"))

        # Governance: GRI 2 ve TSRS-G1 ağırlıklı
        gri_g_total = self._safe_count(cur, 'gri_indicators i JOIN gri_standards s ON i.standard_id = s.id', "s.code = ?", ("GRI 2",))
        gri_g_answered = self._safe_count(cur, 'gri_responses r JOIN gri_indicators i ON r.indicator_id=i.id JOIN gri_standards s ON i.standard_id=s.id', "r.company_id=? AND s.code=? AND r.response_value IS NOT NULL", (company_id, "GRI 2"))

        # TSRS yanıtları: kategoriye göre cevaplanan gösterge oranı
        tsrs_e_total = self._safe_count(cur, 'tsrs_indicators i JOIN tsrs_standards s ON i.standard_id=s.id', "s.category = ?", ("Environmental",))
        tsrs_e_answered = self._safe_count(cur, 'tsrs_responses r JOIN tsrs_indicators i ON r.indicator_id=i.id JOIN tsrs_standards s ON i.standard_id=s.id', "r.company_id=? AND s.category=? AND r.response_value IS NOT NULL", (company_id, "Environmental"))

        tsrs_s_total = self._safe_count(cur, 'tsrs_indicators i JOIN tsrs_standards s ON i.standard_id=s.id', "s.category = ?", ("Social",))
        tsrs_s_answered = self._safe_count(cur, 'tsrs_responses r JOIN tsrs_indicators i ON r.indicator_id=i.id JOIN tsrs_standards s ON i.standard_id=s.id', "r.company_id=? AND s.category=? AND r.response_value IS NOT NULL", (company_id, "Social"))

        tsrs_g_total = self._safe_count(cur, 'tsrs_indicators i JOIN tsrs_standards s ON i.standard_id=s.id', "s.category = ?", ("Governance",))
        tsrs_g_answered = self._safe_count(cur, 'tsrs_responses r JOIN tsrs_indicators i ON r.indicator_id=i.id JOIN tsrs_standards s ON i.standard_id=s.id', "r.company_id=? AND s.category=? AND r.response_value IS NOT NULL", (company_id, "Governance"))

        # SDG katkısı: soru yanıtları kanıt olarak bonus
        sdg_any_answers = self._safe_count(cur, 'sdg_question_responses', "company_id=? AND (answer_text IS NOT NULL OR answer_value IS NOT NULL)", (company_id,))

        # Kanıt / materyalite bonusları
        evidence_bonus = 0.0
        materiality_bonus = 0.0
        try:
            # ERP/supplier/survey mevcutsa minimal bonus
            erp_rows = self._safe_count(cur, cfg['sources'].get('erp_metrics_table', 'erp_metrics'))
            supp_rows = self._safe_count(cur, cfg['sources'].get('supplier_assessments_table', 'supplier_assessments'))
            survey_rows = self._safe_count(cur, cfg['sources'].get('survey_responses_table', 'survey_responses'))
            if erp_rows or supp_rows or survey_rows or sdg_any_answers:
                evidence_bonus = sc.get('evidence_bonus', 0.05)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        try:
            # TSRS materyalite değerlendirmeleri varsa bonus
            mat_rows = self._safe_count(cur, cfg['sources'].get('tsrs_materiality_table', 'tsrs_materiality_assessment'), "company_id=? AND is_material=1", (company_id,))
            if mat_rows:
                materiality_bonus = sc.get('materiality_bonus', 0.1)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Oranlar (cevaplanan/toplam), 0 bölme güvenliği
        def ratio(ans: int, tot: int) -> float:
            return float(ans) / float(tot) if tot > 0 else 0.0

        e_ratio = max(ratio(gri_e_answered + tsrs_e_answered, gri_e_total + tsrs_e_total), 0.0)
        s_ratio = max(ratio(gri_s_answered + tsrs_s_answered, gri_s_total + tsrs_s_total), 0.0)
        g_ratio = max(ratio(gri_g_answered + tsrs_g_answered, gri_g_total + tsrs_g_total), 0.0)

        # Bonusları uygula, 1.0 ile sınırla
        E = min(e_ratio + evidence_bonus, 1.0)
        S = min(s_ratio + evidence_bonus, 1.0)
        G = min(g_ratio + materiality_bonus, 1.0)

        weights = cfg['weights']
        overall = E * weights['E'] + S * weights['S'] + G * weights['G']

        conn.close()
        return {
            'E': round(E * 100, 1),
            'S': round(S * 100, 1),
            'G': round(G * 100, 1),
            'overall': round(overall * 100, 1),
            'details': {
                'gri': {
                    'environmental': {'answered': gri_e_answered, 'total': gri_e_total},
                    'social': {'answered': gri_s_answered, 'total': gri_s_total},
                    'governance': {'answered': gri_g_answered, 'total': gri_g_total}
                },
                'tsrs': {
                    'environmental': {'answered': tsrs_e_answered, 'total': tsrs_e_total},
                    'social': {'answered': tsrs_s_answered, 'total': tsrs_s_total},
                    'governance': {'answered': tsrs_g_answered, 'total': tsrs_g_total}
                },
                'bonuses': {
                    'evidence_bonus': evidence_bonus,
                    'materiality_bonus': materiality_bonus,
                    'sdg_answers': sdg_any_answers
                }
            }
        }

    def calculate_and_save_score(self, company_id: int) -> Dict:
        """Skoru hesapla ve veritabanına kaydet"""
        scores = self.compute_scores(company_id)
        
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO esg_scores 
                (company_id, score_date, e_score, s_score, g_score, overall_score, details)
                VALUES (?, DATE('now'), ?, ?, ?, ?, ?)
            """, (
                company_id, 
                scores['E'], scores['S'], scores['G'], scores['overall'],
                json.dumps(scores['details'])
            ))
            conn.commit()
            logging.info(f"ESG skoru kaydedildi: {company_id} -> {scores['overall']}")
            return scores
        except Exception as e:
            logging.error(f"Skor kaydetme hatasi: {e}")
            return scores
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        # En son hesaplanan skoru getir, yoksa hesapla
        history = self.get_history(company_id)
        if history:
            latest = history[0]
            # Format uyumluluğu için
            return {
                'E': latest['E'],
                'S': latest['S'],
                'G': latest['G'],
                'overall': latest['overall'],
                'environmental': latest['E'],
                'social': latest['S'],
                'governance': latest['G'],
                'details': latest['details']
            }
        else:
            # Varsayılan değerler
            return {
                'E': 0, 'S': 0, 'G': 0, 'overall': 0,
                'environmental': 0, 'social': 0, 'governance': 0,
                'details': {}
            }
        return self.compute_scores(company_id)

    def get_history(self, company_id: int) -> List[Dict]:
        """Geçmiş skorları getir"""
        conn = self._connect()
        cursor = conn.cursor()
        try:
            # Sütun kontrolü (eski veritabanları için)
            cursor.execute("PRAGMA table_info(esg_scores)")
            cols = [info[1] for info in cursor.fetchall()]
            has_yq = 'year' in cols and 'quarter' in cols
            
            if has_yq:
                query = """
                    SELECT score_date, e_score, s_score, g_score, overall_score, details, year, quarter, created_at
                    FROM esg_scores
                    WHERE company_id = ?
                    ORDER BY score_date DESC
                """
            else:
                query = """
                    SELECT score_date, e_score, s_score, g_score, overall_score, details, created_at
                    FROM esg_scores
                    WHERE company_id = ?
                    ORDER BY score_date DESC
                """
            
            cursor.execute(query, (company_id,))
            
            history = []
            for row in cursor.fetchall():
                item = {
                    'date': row[0],
                    'E': row[1],
                    'S': row[2],
                    'G': row[3],
                    'overall': row[4],
                    'environmental_score': row[1],
                    'social_score': row[2],
                    'governance_score': row[3],
                    'total_score': row[4],
                    'details': json.loads(row[5]) if row[5] else {}
                }
                
                if has_yq:
                    item['year'] = row[6]
                    item['quarter'] = row[7]
                    item['created_at'] = row[8]
                else:
                    # Fallback date parsing
                    try:
                        dt = row[0] # YYYY-MM-DD
                        item['year'] = int(dt[:4])
                        item['quarter'] = ((int(dt[5:7]) - 1) // 3) + 1
                    except:
                        item['year'] = datetime.now().year
                        item['quarter'] = 1
                    
                    if len(row) > 6:
                         item['created_at'] = row[6]
                    else:
                         item['created_at'] = row[0]

                history.append(item)
            return history
        except Exception as e:
            logging.error(f"Gecmis getirme hatasi: {e}")
            return []
        finally:
            conn.close()

