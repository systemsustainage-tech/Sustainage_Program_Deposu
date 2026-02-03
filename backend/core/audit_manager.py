import sqlite3
import logging
from datetime import datetime
from typing import Optional
from config.database import DB_PATH

class AuditManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def log_action(self, user_id: Optional[int], action: str, resource: str, details: str = "", ip_address: str = "", company_id: Optional[int] = None, resource_id: Optional[int] = None):
        """
        Kullanıcı eylemini veritabanına kaydeder.
        
        Args:
            user_id: Eylemi yapan kullanıcı ID (varsa)
            action: Eylem türü (örn: "CREATE", "UPDATE", "LOGIN")
            resource: Etkilenen kaynak tipi (örn: "company_targets", "user") - resource_type sütununa yazılır
            details: JSON formatında detay veya açıklama
            ip_address: Kullanıcı IP adresi
            company_id: Şirket ID (varsa) - Multi-tenant izolasyon için
            resource_id: Etkilenen kaynağın ID'si (varsa)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Check schema columns
            cursor.execute("PRAGMA table_info(audit_logs)")
            cols = [c[1] for c in cursor.fetchall()]
            
            has_company_id = 'company_id' in cols
            has_resource_type = 'resource_type' in cols
            has_resource_id = 'resource_id' in cols
            
            # Construct query based on available columns
            columns = ['user_id', 'action', 'details', 'ip_address']
            values = [user_id, action, details, ip_address]
            
            if has_company_id:
                columns.append('company_id')
                values.append(company_id)
                
            if has_resource_type:
                columns.append('resource_type')
                values.append(resource)
            elif 'resource' in cols:
                columns.append('resource')
                values.append(resource)
                
            if has_resource_id:
                columns.append('resource_id')
                values.append(resource_id)
                
            placeholders = ', '.join(['?'] * len(columns))
            sql = f"INSERT INTO audit_logs ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor.execute(sql, values)
                
            conn.commit()
            self.logger.info(f"Audit Log: User={user_id} Action={action} Resource={resource} ID={resource_id} Company={company_id}")
        except Exception as e:
            self.logger.error(f"Audit log error: {e}")
        finally:
            conn.close()

    def get_logs(self, limit: int = 50, offset: int = 0, company_id: Optional[int] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Check available columns for selection
            cursor.execute("PRAGMA table_info(audit_logs)")
            cols = [c[1] for c in cursor.fetchall()]
            
            select_cols = ['id', 'user_id', 'action', 'details', 'ip_address', 'created_at']
            if 'resource_type' in cols:
                select_cols.append('resource_type as resource') # Alias for compatibility
            elif 'resource' in cols:
                select_cols.append('resource')
                
            if 'resource_id' in cols:
                select_cols.append('resource_id')
            
            if 'company_id' in cols:
                select_cols.append('company_id')

            query = f"""
                SELECT {', '.join(select_cols)}
                FROM audit_logs
                WHERE 1=1
            """
            params = []
            
            if company_id is not None:
                query += " AND company_id = ?"
                params.append(company_id)
                
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_logs_count(self, company_id: Optional[int] = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
            params = []
            
            if company_id is not None:
                query += " AND company_id = ?"
                params.append(company_id)
                
            cursor.execute(query, params)
            return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Get logs count error: {e}")
            return 0
        finally:
            conn.close()
