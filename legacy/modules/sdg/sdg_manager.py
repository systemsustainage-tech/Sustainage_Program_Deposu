import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SDGManager:
    """SDG modülü yöneticisi - 17 hedef, 169 alt hedef, 232 gösterge"""

    def __init__(self, db_path: Optional[str] = None) -> None:
        # CALISAN DB kullan
        if db_path is None:
            try:
                from config.settings import get_db_path
                self.db_path = get_db_path()
            except Exception:
                # Fallback: her zaman ana veritabanına yönlendir
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                self.db_path = os.path.join(project_root, "data", "sdg_desktop.sqlite")
        else:
            # db_path göreli ise proje köküne göre mutlak hale getir
            if not os.path.isabs(db_path):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                self.db_path = os.path.join(project_root, db_path)
            else:
                self.db_path = db_path
        # DB klasörünü garanti et
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        try:
            self._init_sdg_tables()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        # Klasörü garanti etmeden bağlan
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _init_sdg_tables(self) -> None:
        try:
            from tools.create_master_tables import SDGMasterTableCreator
            creator = SDGMasterTableCreator(self.db_path)
            creator.create_tables()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sdg_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                goal_id INTEGER NOT NULL,
                selected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (goal_id) REFERENCES sdg_goals(id) ON DELETE CASCADE,
                UNIQUE(company_id, goal_id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS selections (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                goal_id INTEGER,
                target_id INTEGER,
                indicator_id INTEGER,
                selected INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY(goal_id) REFERENCES sdg_goals(id),
                FOREIGN KEY(target_id) REFERENCES sdg_targets(id),
                FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                indicator_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                answer_json TEXT,
                value_num REAL,
                progress_pct INTEGER DEFAULT 0,
                request_status TEXT DEFAULT 'Gönderilmedi',
                policy_flag TEXT DEFAULT 'Hayır',
                evidence_url TEXT,
                approved_by_owner TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id) ON DELETE CASCADE,
                UNIQUE(company_id, indicator_id, period)
            )
            """
        )
        conn.commit()
        conn.close()

    def save_selected_goals(self, company_id: int, selected_goal_ids: List[int]) -> bool:
        """Seçilen SDG hedeflerini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Önce mevcut seçimleri sil
            cursor.execute("""
                DELETE FROM user_sdg_selections 
                WHERE company_id = ?
            """, (company_id,))

            # Yeni seçimleri ekle
            for goal_id in selected_goal_ids:
                cursor.execute("""
                    INSERT INTO user_sdg_selections (company_id, goal_id, selected_at)
                    VALUES (?, ?, ?)
                """, (company_id, goal_id, datetime.now().isoformat()))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"SDG seçimleri kaydedilirken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_selected_goals(self, company_id: int) -> List[int]:
        """Şirket için seçilen SDG hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT goal_id 
                FROM user_sdg_selections 
                WHERE company_id = ?
                ORDER BY goal_id
            """, (company_id,))

            selected_ids = [row[0] for row in cursor.fetchall()]
            return selected_ids
        except Exception as e:
            logging.error(f"SDG seçimleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_sdg_goals(self) -> List[Tuple]:
        """Tüm SDG hedeflerini getir (GUI için tuple formatında)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # created_at sütunu bazı eski veritabanlarında olmayabilir; geriye dönük uyumluluk
        try:
            cursor.execute(
                """
                SELECT id, code, title_tr, created_at 
                FROM sdg_goals 
                ORDER BY code
                """
            )
            goals = cursor.fetchall()
        except sqlite3.OperationalError:
            # Fallback: created_at olmadan seç
            cursor.execute(
                """
                SELECT id, code, title_tr 
                FROM sdg_goals 
                ORDER BY code
                """
            )
            rows = cursor.fetchall()
            # Dördüncü alanı None olarak dolduralım ki üst katman beklerse boş gelsin
            goals = [(row[0], row[1], row[2], None) for row in rows]
        finally:
            conn.close()
        return goals

    def get_all_goals(self) -> List[Dict]:
        """Tüm SDG hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # created_at ve description sütunu bazı şemalarda olmayabilir; uyumlu sorgu
        has_created_at = False
        has_description = False
        try:
            cursor.execute("PRAGMA table_info(sdg_goals)")
            cols = [c[1] for c in cursor.fetchall()]
            has_created_at = 'created_at' in cols
            has_description = 'description' in cols
        except Exception:
            has_created_at = False
            has_description = False

        query = "SELECT id, code, title_tr"
        if has_description:
            query += ", description"
        else:
            query += ", '' as description"
            
        if has_created_at:
            query += ", created_at"
        else:
            query += ", NULL as created_at"
            
        query += " FROM sdg_goals ORDER BY id"
        
        cursor.execute(query)

        goals = []
        for row in cursor.fetchall():
            goals.append({
                'id': row[0],
                'code': row[1],
                'title': row[2],
                'description': row[3],
                'created_at': row[4]
            })

        conn.close()
        return goals

    def get_goal_targets(self, goal_id: int) -> List[Dict]:
        """Belirli bir hedefin alt hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, code, title_tr 
            FROM sdg_targets 
            WHERE goal_id = ? 
            ORDER BY code
            """,
            (goal_id,)
        )

        targets = []
        for row in cursor.fetchall():
            targets.append({
                'id': row[0],
                'code': row[1],
                'title': row[2]
            })

        conn.close()
        return targets

    def get_target_indicators(self, target_id: int) -> List[Dict]:
        """Belirli bir alt hedefin göstergelerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, code, title_tr, unit, measurement_frequency as frequency, topic 
            FROM sdg_indicators 
            WHERE target_id = ? 
            ORDER BY code
            """,
            (target_id,)
        )

        indicators = []
        for row in cursor.fetchall():
            indicators.append({
                'id': row[0],
                'code': row[1],
                'title': row[2],
                'unit': row[3],
                'frequency': row[4],
                'topic': row[5]
            })

        conn.close()
        return indicators

    def get_indicator_questions(self, indicator_code: str) -> Dict:
        """Gösterge için soru bankasından soruları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT q1, q2, q3, default_unit, default_frequency, default_owner, default_source
            FROM question_bank 
            WHERE indicator_code = ?
            """,
            (indicator_code,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'q1': row[0],
                'q2': row[1],
                'q3': row[2],
                'unit': row[3],
                'frequency': row[4],
                'owner': row[5],
                'source': row[6]
            }
        return {}

    def get_company_selections(self, company_id: int) -> List[Dict]:
        """Şirketin seçtiği göstergeleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT us.id, us.goal_id, NULL as target_id, NULL as indicator_id, 1 as selected,
                   g.code as goal_code, g.title_tr as goal_title,
                   NULL as target_code, NULL as target_title,
                   NULL as indicator_code, NULL as indicator_title
            FROM user_sdg_selections us
            LEFT JOIN sdg_goals g ON us.goal_id = g.id
            WHERE us.company_id = ?
            ORDER BY g.id
            """,
            (company_id,)
        )

        selections = []
        for row in cursor.fetchall():
            selections.append({
                'id': row[0],
                'goal_id': row[1],
                'target_id': row[2],
                'indicator_id': row[3],
                'selected': bool(row[4]),
                'goal_code': row[5],
                'goal_title': row[6],
                'target_code': row[7],
                'target_title': row[8],
                'indicator_code': row[9],
                'indicator_title': row[10]
            })

        conn.close()
        return selections

    def select_indicator(self, company_id: int, indicator_id: int, selected: bool = True) -> bool:
        """Gösterge seçimi/seçimini kaldırma"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Önce mevcut seçimi kontrol et
            cursor.execute(
                """
                SELECT id FROM selections 
                WHERE company_id = ? AND indicator_id = ?
                """,
                (company_id, indicator_id)
            )

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute(
                    """
                    UPDATE selections SET selected = ? WHERE id = ?
                    """,
                    (1 if selected else 0, existing[0])
                )
            else:
                # Yeni seçim ekle
                # Önce gösterge bilgilerini al
                cursor.execute(
                    """
                    SELECT i.target_id, t.goal_id 
                    FROM sdg_indicators i
                    JOIN sdg_targets t ON i.target_id = t.id
                    WHERE i.id = ?
                    """,
                    (indicator_id,)
                )

                target_goal = cursor.fetchone()
                if target_goal:
                    cursor.execute(
                        """
                        INSERT INTO selections (company_id, goal_id, target_id, indicator_id, selected)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (company_id, target_goal[1], target_goal[0], indicator_id, 1 if selected else 0)
                    )

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Seçim hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def save_response(self, company_id: int, indicator_id: int, period: str,
                     answer_json: str, value_num: Optional[float] = None,
                     progress_pct: int = 0, policy_flag: str = "Hayır",
                     evidence_url: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """Gösterge cevabını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO responses 
                (company_id, indicator_id, period, answer_json, value_num, 
                 progress_pct, request_status, policy_flag, evidence_url, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (company_id, indicator_id, period, answer_json, value_num,
                 progress_pct, "Gönderilmedi", policy_flag, evidence_url, notes)
            )

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Cevap kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_responses(self, company_id: int, period: Optional[str] = None) -> List[Dict]:
        """Şirketin cevaplarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if period:
            cursor.execute(
                """
                SELECT r.id, r.indicator_id, r.period, r.answer_json, r.value_num,
                       r.progress_pct, r.request_status, r.policy_flag, r.evidence_url, r.notes,
                       i.code as indicator_code, i.title_tr as indicator_title,
                       g.code as goal_code, g.title_tr as goal_title
                FROM responses r
                JOIN sdg_indicators i ON r.indicator_id = i.id
                JOIN sdg_targets t ON i.target_id = t.id
                JOIN sdg_goals g ON t.goal_id = g.id
                WHERE r.company_id = ? AND r.period = ?
                ORDER BY g.code, i.code
                """,
                (company_id, period)
            )
        else:
            cursor.execute(
                """
                SELECT r.id, r.indicator_id, r.period, r.answer_json, r.value_num,
                       r.progress_pct, r.request_status, r.policy_flag, r.evidence_url, r.notes,
                       i.code as indicator_code, i.title_tr as indicator_title,
                       g.code as goal_code, g.title_tr as goal_title
                FROM responses r
                JOIN sdg_indicators i ON r.indicator_id = i.id
                JOIN sdg_targets t ON i.target_id = t.id
                JOIN sdg_goals g ON t.goal_id = g.id
                WHERE r.company_id = ?
                ORDER BY r.period DESC, g.code, i.code
                """,
                (company_id,)
            )

        responses = []
        for row in cursor.fetchall():
            responses.append({
                'id': row[0],
                'indicator_id': row[1],
                'period': row[2],
                'answer_json': row[3],
                'value_num': row[4],
                'progress_pct': row[5],
                'request_status': row[6],
                'policy_flag': row[7],
                'evidence_url': row[8],
                'notes': row[9],
                'indicator_code': row[10],
                'indicator_title': row[11],
                'goal_code': row[12],
                'goal_title': row[13]
            })

        conn.close()
        return responses

    def get_statistics(self, company_id: int) -> Dict:
        """SDG istatistiklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Toplam hedef sayısı
        cursor.execute("SELECT COUNT(*) FROM sdg_goals")
        total_goals = cursor.fetchone()[0]

        # Seçilen hedef sayısı
        cursor.execute(
            """
            SELECT COUNT(DISTINCT goal_id) FROM user_sdg_selections 
            WHERE company_id = ?
            """,
            (company_id,)
        )
        selected_goals = cursor.fetchone()[0]

        # Seçilen hedeflerin ID'lerini al
        cursor.execute(
            """
            SELECT goal_id FROM user_sdg_selections 
            WHERE company_id = ?
            """
        , (company_id,))
        selected_goal_ids = [row[0] for row in cursor.fetchall()]

        # Eşleştirme modülünden soru sayılarını al
        try:
            try:
                from mapping.sdg_gri_mapping import SDGGRIMapping
            except ImportError:
                # Modül yolu çakışması durumunda manuel import
                import importlib.util
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                mapping_path = os.path.join(project_root, 'mapping', 'sdg_gri_mapping.py')
                if os.path.exists(mapping_path):
                    spec = importlib.util.spec_from_file_location("sdg_gri_mapping_manual", mapping_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    SDGGRIMapping = mod.SDGGRIMapping
                else:
                    raise ImportError("Mapping file not found")

            mapping = SDGGRIMapping()
            total_questions = mapping.get_total_questions_count(selected_goal_ids)
            answered_questions = mapping.get_answered_questions_count(company_id, selected_goal_ids)
        except Exception as e:
            # print(f"Eşleştirme modülü hatası: {e}") 
            total_questions = 0
            answered_questions = 0

        # Hedef bazında seçim sayıları
        cursor.execute(
            """
            SELECT g.code, g.title_tr, COUNT(us.id) as selected_count
            FROM sdg_goals g
            LEFT JOIN user_sdg_selections us ON g.id = us.goal_id AND us.company_id = ?
            GROUP BY g.id, g.code, g.title_tr
            ORDER BY g.code
            """,
            (company_id,)
        )

        goal_stats = []
        for row in cursor.fetchall():
            goal_stats.append({
                'code': row[0],
                'title': row[1],
                'selected_count': row[2]
            })

        conn.close()

        return {
            'total_goals': total_goals,
            'selected_goals': selected_goals,
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'answered_indicators': answered_questions,  # Uyumluluk için
            'selection_percentage': (selected_goals / total_goals * 100) if total_goals > 0 else 0,
            'answer_percentage': (answered_questions / total_questions * 100) if total_questions > 0 else 0,
            'goal_stats': goal_stats
        }
