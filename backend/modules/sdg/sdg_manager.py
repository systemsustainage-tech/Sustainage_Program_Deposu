import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from backend.core.base_manager import BaseTenantManager

class SDGManager(BaseTenantManager):
    """SDG modülü yöneticisi - 17 hedef, 169 alt hedef, 232 gösterge"""

    def __init__(self, db_path: Optional[str] = None, company_id: Optional[int] = None) -> None:
        if db_path is None:
            try:
                from config.settings import get_db_path
                db_path = get_db_path()
            except Exception:
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                db_path = os.path.join(project_root, "data", "sdg_desktop.sqlite")
        else:
            if not os.path.isabs(db_path):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                db_path = os.path.join(project_root, db_path)
        
        super().__init__(db_path, company_id)
            
        try:
            os.makedirs(os.path.dirname(self.db.db_path), exist_ok=True)
            self._create_tables()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _create_tables(self):
        """Gerekli tabloları oluştur"""
        try:
            # sdg_responses tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS sdg_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    indicator_id INTEGER,
                    period TEXT,
                    value TEXT,
                    unit TEXT,
                    evidence TEXT,
                    status TEXT DEFAULT 'pending',
                    progress_pct INTEGER DEFAULT 0,
                    action TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # user_sdg_selections tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS user_sdg_selections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    goal_id INTEGER,
                    selected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, goal_id)
                )
            """)
        except Exception as e:
            logging.error(f"Error creating tables: {e}")

    def get_all_goals(self) -> List[Dict]:
        """Tüm SDG hedeflerini getir"""
        goals = []
        try:
            rows = self.db.execute_query("SELECT * FROM sdg_goals ORDER BY CAST(code AS INTEGER)")
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
        return goals

    def get_goal_details(self, goal_id: int) -> Dict:
        """Hedef detaylarını getir"""
        try:
            rows = self.db.execute_query("SELECT * FROM sdg_goals WHERE id = ?", (goal_id,))
            if rows:
                return dict(rows[0])
        except Exception as e:
            logging.error(f"Error fetching goal details: {e}")
        return {}

    def get_goal_targets(self, goal_id: int) -> List[Dict]:
        """Belirli bir hedefin alt hedeflerini getir"""
        targets = []
        try:
            rows = self.db.execute_query("""
                SELECT * FROM sdg_targets 
                WHERE parent_id = ? 
                ORDER BY code
            """, (goal_id,))
            for row in rows:
                targets.append({
                    'id': row['id'],
                    'code': row['code'],
                    'title': row['name_tr'],
                    'name_tr': row['name_tr'],
                    'name_en': row['name_en']
                })
        except Exception as e:
            logging.error(f"Error fetching targets: {e}")
        return targets

    def get_target_indicators(self, target_id: int) -> List[Dict]:
        """Belirli bir alt hedefin göstergelerini getir"""
        indicators = []
        try:
            rows = self.db.execute_query("""
                SELECT * FROM sdg_indicators 
                WHERE parent_id = ? 
                ORDER BY code
            """, (target_id,))
            for row in rows:
                indicators.append({
                    'id': row['id'],
                    'code': row['code'],
                    'title': row['name_tr'],
                    'name_tr': row['name_tr'],
                    'gri_mapping': row['gri_mapping'],
                    'tsrs_mapping': row['tsrs_mapping']
                })
        except Exception as e:
            logging.error(f"Error fetching indicators: {e}")
        return indicators

    def save_response(self, company_id: int, indicator_id: int, period: str, 
                      value: any, unit: Optional[str] = None, 
                      evidence: Optional[str] = None,
                      status: Optional[str] = 'pending',
                      progress_pct: Optional[int] = 0,
                      action: Optional[str] = None,
                      **kwargs) -> bool:
        """SDG yanıtını kaydet"""
        try:
            # Ensure schema has new columns (using raw connection for PRAGMA/ALTER if needed, 
            # or just assume ensure_multitenancy_schema handled basics, but here we have specific columns)
            # We can use self.db.execute_query for PRAGMA
            
            # Note: For simple schema checks, we can skip or use try-catch on insert/update.
            # But let's keep the logic using the new manager methods where possible.
            
            # Check existing
            existing = self.select_one('sdg_responses', company_id=company_id, 
                                       where="indicator_id = ? AND period = ?", 
                                       params=(indicator_id, period))
            
            val_str = str(value) if value is not None else ""
            
            data = {
                'indicator_id': indicator_id,
                'period': period,
                'value': val_str,
                'unit': unit,
                'evidence': evidence,
                'status': status,
                'progress_pct': progress_pct,
                'action': action,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if existing:
                self.update('sdg_responses', data, company_id=company_id,
                            where="id = ?", params=(existing['id'],))
            else:
                data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.insert('sdg_responses', data, company_id=company_id)
            
            return True
        except Exception as e:
            logging.error(f"Error saving response: {e}")
            return False

    def get_response(self, company_id: int, indicator_id: int, period: str) -> Dict:
        """Yanıtı getir"""
        try:
            return self.select_one('sdg_responses', company_id=company_id,
                                   where="indicator_id = ? AND period = ?",
                                   params=(indicator_id, period)) or {}
        except Exception as e:
            logging.error(f"Error getting response: {e}")
            return {}

    def get_company_responses(self, company_id: int) -> List[Dict]:
        """Şirketin tüm yanıtlarını getir"""
        try:
            # Complex query with joins - use execute_query but ensure company_id
            rows = self.db.execute_query("""
                SELECT r.*, i.code as indicator_code, i.name_tr as indicator_name,
                       g.name_tr as goal_title
                FROM sdg_responses r
                JOIN sdg_indicators i ON r.indicator_id = i.id
                LEFT JOIN sdg_targets t ON i.parent_id = t.id
                LEFT JOIN sdg_goals g ON t.parent_id = g.id
                WHERE r.company_id = ?
                ORDER BY r.created_at DESC
            """, (company_id,))
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error getting company responses: {e}")
            return []

    def get_responses(self, company_id: int) -> List[Dict]:
        """get_company_responses alias"""
        return self.get_company_responses(company_id)

    def get_statistics(self, company_id: int) -> Dict:
        """İstatistikler"""
        stats = {
            'total_goals': 17,
            'completed_actions': 0,
            'avg_progress': 0
        }
        try:
            stats['completed_actions'] = self.count('sdg_responses', company_id=company_id)
            
            # Avg progress - custom query
            rows = self.db.execute_query("SELECT AVG(progress_pct) FROM sdg_responses WHERE company_id = ?", (company_id,))
            if rows and rows[0][0]:
                stats['avg_progress'] = int(rows[0][0])
                
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
        return stats

    def get_selected_goals(self, company_id: int) -> List[int]:
        """Seçili hedefleri getir (IDs)"""
        selected_ids = []
        try:
            rows = self.select('user_sdg_selections', company_id=company_id, columns="goal_id")
            selected_ids = [row['goal_id'] for row in rows]
        except Exception as e:
            logging.error(f"Error getting selected goals: {e}")
        return selected_ids

    def save_selected_goals(self, company_id: int, goal_ids: List[int]) -> bool:
        """Seçili hedefleri kaydet"""
        try:
            # Ensure table exists handled in init
            
            # Transaction handled by db_manager if we used batch, but here we do delete then insert
            # We can use explicit transaction or just sequential calls
            
            self.delete('user_sdg_selections', company_id=company_id)
            
            for gid in goal_ids:
                self.insert('user_sdg_selections', {'goal_id': gid}, company_id=company_id)
                
            return True
        except Exception as e:
            logging.error(f"Error saving selected goals: {e}")
            return False

    def get_recent_responses(self, company_id: int, limit: int = 5) -> List[Dict]:
        """Son aktiviteleri getir"""
        try:
            rows = self.db.execute_query("""
                SELECT r.*, i.name_tr as indicator_name 
                FROM sdg_responses r
                JOIN sdg_indicators i ON r.indicator_id = i.id
                WHERE r.company_id = ?
                ORDER BY r.updated_at DESC
                LIMIT ?
            """, (company_id, limit))
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error getting recent responses: {e}")
            return []

