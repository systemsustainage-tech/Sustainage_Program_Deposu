import logging
import jwt
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from collections import defaultdict
from backend.core.database_manager import DatabaseManager

# Configuration (should be in env vars in production)
JWT_SECRET = "SUSTAINAGE_SDG_LICENSE_SECRET_KEY_2025"
JWT_ALGORITHM = "HS256"

class LicenseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = DatabaseManager(db_path)
        # In-memory store for rate limiting: {license_key: [timestamp1, timestamp2, ...]}
        self._request_history = defaultdict(list)
        # Abuse thresholds
        self.ABUSE_WINDOW_SECONDS = 60
        self.ABUSE_LIMIT_REQUESTS = 300  # 300 requests per minute (5 req/sec)
        self._init_db()

    def _init_db(self):
        """Initialize the licenses table if it doesn't exist."""
        try:
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    license_key TEXT UNIQUE NOT NULL,
                    issued_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    max_users INTEGER,
                    status TEXT DEFAULT 'active',
                    allowed_ips TEXT,
                    allowed_domains TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_usage_at TIMESTAMP,
                    suspended_at TIMESTAMP,
                    suspension_reason TEXT
                )
            """)
        except Exception as e:
            logging.error(f"Error initializing license DB: {e}")

    def generate_license(self, company_id: int, duration_days: int = 365, max_users: int = 5, allowed_ips: list = None, allowed_domains: list = None) -> Dict[str, Any]:
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
            'jti': str(uuid.uuid4()), # Unique identifier for the token
            'allowed_ips': allowed_ips,
            'allowed_domains': allowed_domains
        }
        
        license_key = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        try:
            # Check if licenses table exists and has correct columns
            # If allowed_ips column missing, add it (migration on the fly for simplicity)
            try:
                self.db.execute_update("ALTER TABLE licenses ADD COLUMN allowed_ips TEXT")
            except: pass
            try:
                self.db.execute_update("ALTER TABLE licenses ADD COLUMN allowed_domains TEXT")
            except: pass
            
            self.db.execute_update("""
                INSERT INTO licenses (company_id, license_key, issued_at, expires_at, max_users, status, allowed_ips, allowed_domains)
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
            """, (
                company_id, 
                license_key, 
                issued_at, 
                expires_at, 
                max_users, 
                json.dumps(allowed_ips) if allowed_ips else None,
                json.dumps(allowed_domains) if allowed_domains else None
            ))
            
            return {
                'success': True,
                'license_key': license_key,
                'expires_at': expires_at.isoformat(),
                'max_users': max_users
            }
        except Exception as e:
            logging.error(f"Error generating license: {e}")
            return {'success': False, 'message': str(e)}

    def check_abuse_and_update_usage(self, license_key: str, request_ip: str = None) -> Tuple[bool, str]:
        """
        Updates usage stats and checks for abuse (Rate Limit + IP Tracking).
        Returns: (is_abusive, reason)
        """
        current_time = time.time()
        
        # 1. Update in-memory history
        if license_key not in self._request_history:
             self._request_history[license_key] = []
             
        history = self._request_history[license_key]
        # Remove old requests (sliding window)
        # Filter list in place
        self._request_history[license_key] = [t for t in history if t > current_time - self.ABUSE_WINDOW_SECONDS]
        history = self._request_history[license_key]
        
        history.append(current_time)
        
        # 2. Check threshold
        if len(history) > self.ABUSE_LIMIT_REQUESTS:
            reason = f"Abuse detected: {len(history)} requests in {self.ABUSE_WINDOW_SECONDS}s from IP {request_ip}"
            self.suspend_license(license_key, reason)
            return True, reason
            
        # 3. Update DB stats (every 10th request to save DB writes, or just always if critical)
        # For strict tracking, we update always.
        try:
            self.db.execute_update("""
                UPDATE licenses 
                SET usage_count = COALESCE(usage_count, 0) + 1, 
                    last_usage_at = CURRENT_TIMESTAMP 
                WHERE license_key = ?
            """, (license_key,))
        except Exception as e:
            logging.error(f"Error updating license usage: {e}")
            
        return False, ""

    def suspend_license(self, license_key: str, reason: str):
        """Suspends a license due to abuse."""
        try:
            self.db.execute_update("""
                UPDATE licenses 
                SET status = 'suspended', 
                    suspended_at = CURRENT_TIMESTAMP,
                    suspension_reason = ?
                WHERE license_key = ?
            """, (reason, license_key))
            logging.warning(f"License {license_key} suspended. Reason: {reason}")
        except Exception as e:
            logging.error(f"Error suspending license: {e}")

    def verify_license_key(self, license_key: str, request_ip: str = None, request_domain: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Verifies a license key.
        Optional checks for IP and Domain if provided.
        Returns: (is_valid, message, payload)
        """
        if not license_key:
            return False, "License key is missing", {}

        try:
            # 1. Decode and verify signature/expiry
            payload = jwt.decode(license_key, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # 2. Check against database (revocation check)
            rows = self.db.execute_query("SELECT status, company_id FROM licenses WHERE license_key = ?", (license_key,))
            
            if not rows:
                return False, "License not found in database", {}
            
            row = rows[0]
            status = row['status']
            db_company_id = row['company_id']
            
            if status != 'active':
                return False, f"License is {status}", {}
            
            if payload.get('company_id') != db_company_id:
                return False, "License company mismatch", {}

            # 3. Check IP and Domain Restrictions if provided
            allowed_ips = payload.get('allowed_ips')
            if allowed_ips and request_ip:
                if request_ip not in allowed_ips:
                    return False, f"Access denied from IP: {request_ip}", {}

            allowed_domains = payload.get('allowed_domains')
            if allowed_domains and request_domain:
                # Simple domain check (exact match or subdomain check could be added)
                # For now, exact match or presence in list
                domain_match = False
                for domain in allowed_domains:
                    if domain == request_domain or request_domain.endswith('.' + domain):
                        domain_match = True
                        break
                if not domain_match:
                    return False, f"Access denied from Domain: {request_domain}", {}

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
        rows = self.db.execute_query("""
            SELECT license_key FROM licenses 
            WHERE company_id = ? AND status = 'active' 
            ORDER BY issued_at DESC LIMIT 1
        """, (company_id,))
        return rows[0]['license_key'] if rows else None
