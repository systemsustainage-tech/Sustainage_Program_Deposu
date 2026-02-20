import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from backend.core.base_manager import BaseTenantManager

class GenericDataManager(BaseTenantManager):
    """
    Basit veri girişi gerektiren modüller için genel veri yöneticisi.
    Her modül için ayrı tablo/manager yazmak yerine ortak bir yapı kullanır.
    Multi-tenant yapıya uygundur.
    """
    
    def __init__(self, db_path: str = None, company_id: Optional[int] = None):
        import os
        # db_path verilmezse varsayılanı kullan (geriye dönük uyumluluk için db_path opsiyonel olabilir ama burada zorunlu gibi duruyor, yine de default ekleyelim)
        final_db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        super().__init__(final_db_path, company_id)
        self._ensure_table()
        
    def _ensure_table(self):
        """Genel veri tablosunu oluştur"""
        try:
            # generic_module_data tablosu
            # module_type: 'eu_taxonomy', 'social_human_rights', vb.
            # data_type: 'record', 'kpi', 'target', vb.
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS generic_module_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL DEFAULT 1,
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
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_generic_company_module ON generic_module_data(company_id, module_type)")
            
        except Exception as e:
            logging.error(f"GenericDataManager table creation error: {e}")
        
    def add_record(self, company_id: Optional[int], module_type: str, data: Dict[str, Any]) -> bool:
        """Yeni kayıt ekle"""
        try:
            # company_id opsiyonel olabilir, eğer None ise context'ten alır
            cid = self._ensure_context(company_id)
            
            meta_json = json.dumps(data.get('meta', {}), ensure_ascii=False)
            
            record_data = {
                'module_type': module_type,
                'data_type': data.get('data_type', 'record'),
                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'value': data.get('value'),
                'unit': data.get('unit', ''),
                'status': data.get('status', 'active'),
                'meta_json': meta_json
            }
            
            # BaseTenantManager.insert otomatik olarak company_id ekler
            self.insert('generic_module_data', record_data, company_id=cid)
            return True
            
        except Exception as e:
            logging.error(f"GenericDataManager add_record error ({module_type}): {e}")
            return False
            
    def get_records(self, company_id: Optional[int], module_type: str, limit: int = 50) -> List[Dict]:
        """Kayıtları getir"""
        try:
            cid = self._ensure_context(company_id)
            
            # BaseTenantManager.select otomatik company_id filtresi ekler
            rows = self.select(
                'generic_module_data',
                where='module_type = ?',
                params=(module_type,),
                order_by='date DESC, created_at DESC',
                limit=limit,
                company_id=cid
            )
            
            return rows
        except Exception as e:
            logging.error(f"GenericDataManager get_records error ({module_type}): {e}")
            return []
            
    def get_stats(self, company_id: Optional[int], module_type: str) -> Dict[str, Any]:
        """Basit istatistikler"""
        stats = {
            'total_records': 0,
            'this_year_count': 0
        }
        
        try:
            cid = self._ensure_context(company_id)
            
            # Toplam kayıt
            stats['total_records'] = self.count(
                'generic_module_data',
                where='module_type = ?',
                params=(module_type,),
                company_id=cid
            )
            
            # Bu yıl
            current_year = datetime.now().year
            stats['this_year_count'] = self.count(
                'generic_module_data',
                where='module_type = ? AND date LIKE ?',
                params=(module_type, f"{current_year}%"),
                company_id=cid
            )
            
            return stats
        except Exception as e:
            logging.error(f"GenericDataManager get_stats error ({module_type}): {e}")
            return stats
