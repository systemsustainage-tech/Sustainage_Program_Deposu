import logging
import sqlite3
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

# Configuration (should be in env vars in production)
JWT_SECRET = "SUSTAINAGE_SDG_LICENSE_SECRET_KEY_2025"
JWT_ALGORITHM = "HS256"

class LicenseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def generate_license(self, company_id: int, duration_days: int = 365, max_users: int = 5) -> Dict[str, Any]:
        """
        Generates a new license key for a company.
        """
        issued_at = datetime.now()
        expires_at = issued_at + timedelta(days=duration_days)
        
        # Create JWT payload
        payload = {
            'company_id': company_id,
            'max_users': max_users,
            'iat': int(issued_at.timestamp()),
            'exp': int(expires_at.timestamp()),
            'jti': str(uuid.uuid4()) # Unique identifier for the token
        }
        
        license_key = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO licenses (company_id, license_key, issued_at, expires_at, max_users, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            """, (company_id, license_key, issued_at, expires_at, max_users))
            conn.commit()
            
            return {
                'success': True,
                'license_key': license_key,
                'expires_at': expires_at,
                'max_users': max_users
            }
        except Exception as e:
            logging.error(f"Error generating license: {e}")
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    def verify_license_key(self, license_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Verifies a license key.
        Returns: (is_valid, message, payload)
        """
        if not license_key:
            return False, "License key is missing", {}

        try:
            # 1. Decode and verify signature/expiry
            payload = jwt.decode(license_key, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # 2. Check against database (revocation check)
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT status, company_id FROM licenses WHERE license_key = ?", (license_key,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return False, "License not found in database", {}
            
            status, db_company_id = row
            
            if status != 'active':
                return False, f"License is {status}", {}
            
            if payload.get('company_id') != db_company_id:
                return False, "License company mismatch", {}

            return True, "Valid license", payload
            
        except jwt.ExpiredSignatureError:
            return False, "License has expired", {}
        except jwt.InvalidTokenError:
            return False, "Invalid license key", {}
        except Exception as e:
            logging.error(f"License verification error: {e}")
            return False, f"Verification error: {str(e)}", {}

    def get_active_license(self, company_id: int) -> Optional[str]:
        """Retrieves the active license key for a company."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT license_key FROM licenses 
            WHERE company_id = ? AND status = 'active' 
            ORDER BY issued_at DESC LIMIT 1
        """, (company_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
