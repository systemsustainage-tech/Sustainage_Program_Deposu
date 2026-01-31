import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class SDGManager:
    """SDG modülü yöneticisi - 17 hedef, 169 alt hedef, 232 gösterge"""

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            try:
                from config.settings import get_db_path
                self.db_path = get_db_path()
            except Exception:
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                self.db_path = os.path.join(project_root, "data", "sdg_desktop.sqlite")
        else:
            if not os.path.isabs(db_path):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                db_path = os.path.join(project_root, db_path)
            self.db_path = db_path
            
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Use Row factory for name access
        return conn

    def get_all_goals(self) -> List[Dict]:
        """Tüm SDG hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        goals = []
        try:
            cursor.execute("SELECT * FROM sdg_goals ORDER BY CAST(code AS INTEGER)")
            rows = cursor.fetchall()
            for row in rows:
                goals.append({
                    'id': row['id'],
                    'code': row['code'],
                    'title': row['name_tr'], # Legacy compat
                    'name_tr': row['name_tr'],
                    'name_en': row['name_en'],
                    'description': row['description_tr'],
                    'icon': row['icon']
                })
        except Exception as e:
            logging.error(f"Error fetching goals: {e}")
        finally:
            conn.close()
        return goals

    def get_goal_details(self, goal_id: int) -> Dict:
        """Hedef detaylarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM sdg_goals WHERE id = ?", (goal_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        finally:
            conn.close()
        return {}

    def get_goal_targets(self, goal_id: int) -> List[Dict]:
        """Belirli bir hedefin alt hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        targets = []
        try:
            # Using parent_id which links to sdg_goals.id
            cursor.execute("""
                SELECT * FROM sdg_targets 
                WHERE parent_id = ? 
                ORDER BY code
            """, (goal_id,))
            rows = cursor.fetchall()
            for row in rows:
                targets.append({
                    'id': row['id'],
                    'code': row['code'],
                    'title': row['name_tr'],
                    'name_tr': row['name_tr'],
                    'name_en': row['name_en']
                })
        finally:
            conn.close()
        return targets

    def get_target_indicators(self, target_id: int) -> List[Dict]:
        """Belirli bir alt hedefin göstergelerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        indicators = []
        try:
            cursor.execute("""
                SELECT * FROM sdg_indicators 
                WHERE parent_id = ? 
                ORDER BY code
            """, (target_id,))
            rows = cursor.fetchall()
            for row in rows:
                indicators.append({
                    'id': row['id'],
                    'code': row['code'],
                    'title': row['name_tr'],
                    'name_tr': row['name_tr'],
                    'gri_mapping': row['gri_mapping'],
                    'tsrs_mapping': row['tsrs_mapping']
                })
        finally:
            conn.close()
        return indicators

    def save_response(self, company_id: int, indicator_id: int, period: str, 
                      value: any, unit: Optional[str] = None, 
                      evidence: Optional[str] = None,
                      status: Optional[str] = 'pending',
                      progress_pct: Optional[int] = 0,
                      action: Optional[str] = None,
                      **kwargs) -> bool:
        """SDG yanıtını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Ensure schema has new columns
            cursor.execute("PRAGMA table_info(sdg_responses)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'progress_pct' not in columns:
                cursor.execute("ALTER TABLE sdg_responses ADD COLUMN progress_pct INTEGER DEFAULT 0")
            if 'action' not in columns:
                cursor.execute("ALTER TABLE sdg_responses ADD COLUMN action TEXT")
            if 'status' not in columns:
                cursor.execute("ALTER TABLE sdg_responses ADD COLUMN status TEXT DEFAULT 'pending'")
                
            # Check if exists
            cursor.execute("""
                SELECT id FROM sdg_responses 
                WHERE company_id = ? AND indicator_id = ? AND period = ?
            """, (company_id, indicator_id, period))
            row = cursor.fetchone()
            
            # Handle value (convert to string if needed)
            val_str = str(value) if value is not None else ""
            
            if row:
                cursor.execute("""
                    UPDATE sdg_responses 
                    SET value = ?, unit = ?, evidence = ?, status = ?, progress_pct = ?, action = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (val_str, unit, evidence, status, progress_pct, action, row[0]))
            else:
                cursor.execute("""
                    INSERT INTO sdg_responses (company_id, indicator_id, period, value, unit, evidence, status, progress_pct, action)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, indicator_id, period, val_str, unit, evidence, status, progress_pct, action))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving response: {e}")
            return False
        finally:
            conn.close()

    def get_response(self, company_id: int, indicator_id: int, period: str) -> Dict:
        """Yanıtı getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM sdg_responses 
                WHERE company_id = ? AND indicator_id = ? AND period = ?
            """, (company_id, indicator_id, period))
            row = cursor.fetchone()
            if row:
                return dict(row)
        finally:
            conn.close()
        return {}

    def get_company_responses(self, company_id: int) -> List[Dict]:
        """Şirketin tüm yanıtlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.*, i.code as indicator_code, i.name_tr as indicator_name,
                       g.name_tr as goal_title
                FROM sdg_responses r
                JOIN sdg_indicators i ON r.indicator_id = i.id
                LEFT JOIN sdg_targets t ON i.parent_id = t.id
                LEFT JOIN sdg_goals g ON t.parent_id = g.id
                WHERE r.company_id = ?
                ORDER BY r.created_at DESC
            """, (company_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_responses(self, company_id: int) -> List[Dict]:
        """get_company_responses alias"""
        return self.get_company_responses(company_id)

    def get_statistics(self, company_id: int) -> Dict:
        """İstatistikler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {
            'total_goals': 17,
            'completed_actions': 0,
            'avg_progress': 0
        }
        try:
            # Completed actions (count of responses)
            cursor.execute("SELECT COUNT(*) FROM sdg_responses WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            stats['completed_actions'] = row[0] if row else 0
            
            # Avg progress
            try:
                cursor.execute("SELECT AVG(progress_pct) FROM sdg_responses WHERE company_id = ?", (company_id,))
                avg = cursor.fetchone()[0]
                stats['avg_progress'] = int(avg) if avg else 0
            except Exception:
                stats['avg_progress'] = 0
                
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
        finally:
            conn.close()
        return stats

    def get_selected_goals(self, company_id: int) -> List[int]:
        """Seçili hedefleri getir (IDs)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        selected_ids = []
        try:
            # Check if table exists first to avoid error if dropped
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sdg_selections'")
            if cursor.fetchone():
                cursor.execute("SELECT goal_id FROM user_sdg_selections WHERE company_id = ?", (company_id,))
                rows = cursor.fetchall()
                selected_ids = [row[0] for row in rows]
        except Exception as e:
            logging.error(f"Error getting selected goals: {e}")
        finally:
            conn.close()
        return selected_ids

    def save_selected_goals(self, company_id: int, goal_ids: List[int]) -> bool:
        """Seçili hedefleri kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check/Create table if not exists (legacy support)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sdg_selections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    goal_id INTEGER,
                    selected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, goal_id)
                )
            """)
            
            cursor.execute("DELETE FROM user_sdg_selections WHERE company_id = ?", (company_id,))
            
            for gid in goal_ids:
                cursor.execute("INSERT INTO user_sdg_selections (company_id, goal_id) VALUES (?, ?)", (company_id, gid))
                
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving selected goals: {e}")
            return False
        finally:
            conn.close()

    def get_recent_responses(self, company_id: int, limit: int = 5) -> List[Dict]:
        """Son aktiviteleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.*, i.name_tr as indicator_name 
                FROM sdg_responses r
                JOIN sdg_indicators i ON r.indicator_id = i.id
                WHERE r.company_id = ?
                ORDER BY r.updated_at DESC
                LIMIT ?
            """, (company_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error getting recent responses: {e}")
            return []
        finally:
            conn.close()
