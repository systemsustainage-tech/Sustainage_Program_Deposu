import sqlite3
import logging
from datetime import datetime
from typing import Optional
from config.database import DB_PATH

class AuditManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def log_action(self, user_id: Optional[int], action: str, resource: str, details: str = "", ip_address: str = "", company_id: Optional[int] = None):
        """
        Kullanıcı eylemini veritabanına kaydeder.
        
        Args:
            user_id: Eylemi yapan kullanıcı ID (varsa)
            action: Eylem türü (örn: "CREATE", "UPDATE", "LOGIN")
            resource: Etkilenen kaynak (örn: "company_targets", "supplier_data")
            details: JSON formatında detay veya açıklama
            ip_address: Kullanıcı IP adresi
            company_id: Şirket ID (varsa) - Multi-tenant izolasyon için
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Check if company_id column exists (backward compatibility)
            cursor.execute("PRAGMA table_info(audit_logs)")
            cols = [c[1] for c in cursor.fetchall()]
            has_company_id = 'company_id' in cols
            
            if has_company_id:
                cursor.execute("""
                    INSERT INTO audit_logs (user_id, action, resource, details, ip_address, company_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, action, resource, details, ip_address, company_id))
            else:
                # Fallback for old schema
                cursor.execute("""
                    INSERT INTO audit_logs (user_id, action, resource, details, ip_address)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, action, resource, details, ip_address))
                
            conn.commit()
            self.logger.info(f"Audit Log: User={user_id} Action={action} Resource={resource} Company={company_id}")
        except Exception as e:
            self.logger.error(f"Audit log error: {e}")
        finally:
            conn.close()

    def get_logs(self, limit: int = 50, offset: int = 0, company_id: Optional[int] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            query = """
                SELECT id, user_id, action, resource, details, ip_address, created_at, company_id
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
