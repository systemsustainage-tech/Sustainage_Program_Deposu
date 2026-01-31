import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
License Generator Component
JWT-based license key generation and validation
"""

import hashlib
import json
import platform
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
from config.database import DB_PATH

# Secret key for JWT signing (in production, use environment variable)
JWT_SECRET = "SUSTAINAGE_SDG_LICENSE_SECRET_KEY_2025"
JWT_ALGORITHM = "HS256"

class LicenseGenerator:
    """License key generator and validator"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("PRAGMA synchronous=NORMAL")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        return conn

    def generate_license_key(
        self,
        company_name: str,
        license_type: str,
        duration_days: int,
        max_users: int,
        enabled_modules: List[str],
        hardware_id: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a new license key
        
        Returns:
            {
                'success': bool,
                'license_key': str,
                'license_id': int,
                'expires_at': str,
                'message': str
            }
        """
        try:
            # Calculate expiry date
            issued_date = datetime.now()
            if duration_days > 0:
                expiry_date = issued_date + timedelta(days=duration_days)
            else:
                expiry_date = None  # Unlimited

            # Create JWT payload
            payload = {
                'company': company_name,
                'type': license_type,
                'max_users': max_users,
                'modules': enabled_modules,
                'iat': int(issued_date.timestamp()),
            }

            if expiry_date:
                payload['exp'] = int(expiry_date.timestamp())

            if hardware_id:
                payload['hw_id'] = hardware_id

            # Generate JWT token
            license_key = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            # Create signature for additional security
            signature = self._create_signature(license_key, company_name)

            # Save to database
            conn = self._connect()
            try:
                cursor = conn.cursor()

                cursor.execute("""
                INSERT INTO licenses (
                    license_key, license_type, company_name, contact_email, contact_phone,
                    issued_date, expiry_date, max_users, enabled_modules,
                    hardware_id, signature, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    license_key,
                    license_type,
                    company_name,
                    contact_email,
                    contact_phone,
                    issued_date.isoformat(),
                    expiry_date.isoformat() if expiry_date else None,
                    max_users,
                    json.dumps(enabled_modules),
                    hardware_id,
                    signature
                ))

                license_id = cursor.lastrowid

                # Log to history
                cursor.execute("""
                    INSERT INTO license_history (license_id, action, new_value, performed_by)
                    VALUES (?, 'created', ?, 'system')
                """, (license_id, f"License created for {company_name}"))
                conn.commit()
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

            return {
                'success': True,
                'license_key': license_key,
                'license_id': license_id,
                'expires_at': expiry_date.isoformat() if expiry_date else 'Unlimited',
                'message': 'License key generated successfully!'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating license: {str(e)}'
            }

    def validate_license(
        self,
        license_key: str,
        hardware_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a license key
        
        Returns:
            {
                'valid': bool,
                'license_type': str,
                'company_name': str,
                'expires_at': str,
                'max_users': int,
                'enabled_modules': list,
                'days_remaining': int,
                'message': str
            }
        """
        try:
            # Decode JWT
            payload = jwt.decode(license_key, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            # Check hardware ID if provided
            if hardware_id and 'hw_id' in payload:
                if payload['hw_id'] != hardware_id:
                    return {
                        'valid': False,
                        'message': 'Hardware ID mismatch - License bound to different machine'
                    }

            # Check expiry
            expires_at = None
            days_remaining = -1

            if 'exp' in payload:
                expiry_timestamp = payload['exp']
                expires_at = datetime.fromtimestamp(expiry_timestamp)
                days_remaining = (expires_at - datetime.now()).days

                if days_remaining < 0:
                    return {
                        'valid': False,
                        'message': f'License expired {abs(days_remaining)} days ago'
                    }

            # Check if license exists in database and is active
            conn = self._connect()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT is_active, company_name FROM licenses WHERE license_key = ?
                """, (license_key,))
                result = cursor.fetchone()
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

            if not result:
                return {
                    'valid': False,
                    'message': 'License not found in database'
                }

            is_active, company_name = result
            if not is_active:
                return {
                    'valid': False,
                    'message': 'License has been deactivated'
                }

            return {
                'valid': True,
                'license_type': payload.get('type', 'unknown'),
                'company_name': payload.get('company', company_name),
                'expires_at': expires_at.isoformat() if expires_at else 'Unlimited',
                'max_users': payload.get('max_users', 0),
                'enabled_modules': payload.get('modules', []),
                'days_remaining': days_remaining if days_remaining >= 0 else -1,
                'message': 'License is valid'
            }

        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'message': 'License has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'valid': False,
                'message': 'Invalid license key format'
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error validating license: {str(e)}'
            }

    def get_all_licenses(self) -> List[Dict[str, Any]]:
        """Get all licenses from database"""
        try:
            conn = self._connect()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id, license_key, license_type, company_name, contact_email,
                        issued_date, expiry_date, max_users, enabled_modules,
                        hardware_id, is_active
                    FROM licenses
                    ORDER BY issued_date DESC
                """)
                licenses = []
                for row in cursor.fetchall():
                    license_id, key, type_, company, email, issued, expiry, max_users, modules, hw_id, active = row
                    status = 'Active'
                    if not active:
                        status = 'Deactivated'
                    elif expiry:
                        expiry_date = datetime.fromisoformat(expiry)
                        if expiry_date < datetime.now():
                            status = 'Expired'
                        elif (expiry_date - datetime.now()).days < 30:
                            status = 'Expiring Soon'
                    licenses.append({
                        'id': license_id,
                        'key': key,
                        'type': type_,
                        'company': company,
                        'email': email,
                        'issued': issued,
                        'expiry': expiry if expiry else 'Unlimited',
                        'max_users': max_users,
                        'modules': json.loads(modules) if modules else [],
                        'hardware_id': hw_id,
                        'active': bool(active),
                        'status': status
                    })
                return licenses
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

        except Exception as e:
            logging.error(f"Error fetching licenses: {e}")
            return []

    def deactivate_license(self, license_id: int, reason: str = '') -> bool:
        """Deactivate a license"""
        try:
            conn = self._connect()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE licenses SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (license_id,))

                cursor.execute("""
                    INSERT INTO license_history (license_id, action, new_value, performed_by)
                    VALUES (?, 'deactivated', ?, 'admin')
                """, (license_id, reason))

                conn.commit()
                return True
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
        except Exception as e:
            logging.error(f"Error deactivating license: {e}")
            return False

    def renew_license(self, license_id: int, additional_days: int) -> bool:
        """Renew/extend a license"""
        try:
            conn = self._connect()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT expiry_date FROM licenses WHERE id = ?", (license_id,))
                result = cursor.fetchone()

                if not result:
                    return False

                current_expiry = result[0]
                if current_expiry:
                    new_expiry = datetime.fromisoformat(current_expiry) + timedelta(days=additional_days)
                else:
                    new_expiry = datetime.now() + timedelta(days=additional_days)

                cursor.execute("""
                    UPDATE licenses 
                    SET expiry_date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_expiry.isoformat(), license_id))

                cursor.execute("""
                    INSERT INTO license_history (license_id, action, new_value, performed_by)
                    VALUES (?, 'renewed', ?, 'admin')
                """, (license_id, f"Extended by {additional_days} days"))

                conn.commit()
                return True
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
        except Exception as e:
            logging.error(f"Error renewing license: {e}")
            return False

    def get_hardware_id(self) -> str:
        """Get current machine's hardware ID"""
        try:
            # Combine multiple hardware identifiers
            machine = platform.machine()
            processor = platform.processor()
            node = platform.node()

            # Get MAC address
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0,2*6,2)][::-1])

            # Create hash
            hw_string = f"{machine}_{processor}_{node}_{mac}"
            hw_id = hashlib.sha256(hw_string.encode()).hexdigest()[:32]

            return hw_id
        except Exception:
            return "UNKNOWN"

    def _create_signature(self, license_key: str, company_name: str) -> str:
        """Create additional signature for license"""
        data = f"{license_key}_{company_name}_{JWT_SECRET}"
        return hashlib.sha256(data.encode()).hexdigest()

    def get_license_statistics(self) -> Dict[str, Any]:
        """Get license statistics"""
        try:
            conn = self._connect()
            try:
                cursor = conn.cursor()

                # Total licenses
                cursor.execute("SELECT COUNT(*) FROM licenses")
                total = cursor.fetchone()[0]

                # Active licenses
                cursor.execute("SELECT COUNT(*) FROM licenses WHERE is_active = 1")
                active = cursor.fetchone()[0]

                # Expired licenses
                cursor.execute("""
                    SELECT COUNT(*) FROM licenses 
                    WHERE expiry_date IS NOT NULL AND expiry_date < datetime('now')
                """)
                expired = cursor.fetchone()[0]

                # Expiring soon (30 days)
                cursor.execute("""
                    SELECT COUNT(*) FROM licenses 
                    WHERE expiry_date IS NOT NULL 
                    AND expiry_date BETWEEN datetime('now') AND datetime('now', '+30 days')
                    AND is_active = 1
                """)
                expiring_soon = cursor.fetchone()[0]

                # By type
                cursor.execute("""
                    SELECT license_type, COUNT(*) FROM licenses 
                    WHERE is_active = 1
                    GROUP BY license_type
                """)
                by_type = dict(cursor.fetchall())

                return {
                    'total': total,
                    'active': active,
                    'expired': expired,
                    'expiring_soon': expiring_soon,
                    'by_type': by_type
                }
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {
                'total': 0,
                'active': 0,
                'expired': 0,
                'expiring_soon': 0,
                'by_type': {}
            }

