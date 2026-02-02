import sqlite3
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class GenericDataManager:
    """
    Basit veri girişi gerektiren modüller için genel veri yöneticisi.
    Her modül için ayrı tablo/manager yazmak yerine ortak bir yapı kullanır.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_table()
        
    def _ensure_table(self):
        """Genel veri tablosunu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # generic_module_data tablosu
        # module_type: 'eu_taxonomy', 'social_human_rights', vb.
        # data_type: 'record', 'kpi', 'target', vb.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generic_module_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                module_type TEXT NOT NULL,
                data_type TEXT DEFAULT 'record',
                date TEXT,
                title TEXT,
                description TEXT,
                value REAL,
                unit TEXT,
                status TEXT,
                meta_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # İndeksler
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generic_company_module ON generic_module_data(company_id, module_type)")
        
        conn.commit()
        conn.close()
        
    def add_record(self, company_id: int, module_type: str, data: Dict[str, Any]) -> bool:
        """Yeni kayıt ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            meta_json = json.dumps(data.get('meta', {}), ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO generic_module_data 
                (company_id, module_type, data_type, date, title, description, value, unit, status, meta_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                module_type,
                data.get('data_type', 'record'),
                data.get('date', datetime.now().strftime('%Y-%m-%d')),
                data.get('title', ''),
                data.get('description', ''),
                data.get('value'),
                data.get('unit', ''),
                data.get('status', 'active'),
                meta_json
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"GenericDataManager add_record error ({module_type}): {e}")
            return False
        finally:
            conn.close()
            
    def get_records(self, company_id: int, module_type: str, limit: int = 50) -> List[Dict]:
        """Kayıtları getir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM generic_module_data 
                WHERE company_id = ? AND module_type = ? 
                ORDER BY date DESC, created_at DESC 
                LIMIT ?
            """, (company_id, module_type, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"GenericDataManager get_records error ({module_type}): {e}")
            return []
        finally:
            conn.close()
            
    def get_stats(self, company_id: int, module_type: str) -> Dict[str, Any]:
        """Basit istatistikler"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            'total_records': 0,
            'this_year_count': 0
        }
        
        try:
            # Toplam kayıt
            cursor.execute("SELECT COUNT(*) FROM generic_module_data WHERE company_id = ? AND module_type = ?", (company_id, module_type))
            stats['total_records'] = cursor.fetchone()[0]
            
            # Bu yıl
            current_year = datetime.now().year
            cursor.execute("SELECT COUNT(*) FROM generic_module_data WHERE company_id = ? AND module_type = ? AND date LIKE ?", (company_id, module_type, f"{current_year}%"))
            stats['this_year_count'] = cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            logging.error(f"GenericDataManager get_stats error ({module_type}): {e}")
            return stats
        finally:
            conn.close()
