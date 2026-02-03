import sqlite3
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Tuple, Optional
from core.audit_manager import AuditManager

# Configuration
APPROVAL_WINDOW_SECONDS = 120  # 2 minutes to confirm
SUPER_ADMIN_USERNAME = "__super__"

def _get_connection(db_path: str):
    return sqlite3.connect(db_path)

def _ensure_approval_table(conn):
    """Ensures the approval table exists."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS super_admin_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id INTEGER,
            target_username TEXT,
            action_type TEXT,
            created_at REAL,
            expires_at REAL,
            UNIQUE(actor_id, target_username, action_type)
        )
    """)
    conn.commit()

def _is_super_admin(conn, username: str) -> bool:
    """Checks if the user is a super admin (by username or role)."""
    if username == SUPER_ADMIN_USERNAME:
        return True
    
    # Check roles
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.name 
            FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            JOIN users u ON u.id = ur.user_id
            WHERE u.username = ?
        """, (username,))
        roles = [row[0] for row in cursor.fetchall()]
        if 'Super Admin' in roles or 'Admin' in roles: # Treating Admin as protected too if needed, but sticking to Super Admin as per prompt
             if 'Super Admin' in roles:
                 return True
    except Exception as e:
        logging.error(f"Error checking super admin status: {e}")
    
    return False

def _check_two_stage_approval(db_path: str, actor_id: int, target_username: str, action_type: str) -> Tuple[bool, str]:
    """
    Implements the two-stage approval logic.
    1. Checks for existing valid approval request.
    2. If exists -> Consumes it and returns True.
    3. If not -> Creates it and returns False (requiring confirmation).
    """
    conn = _get_connection(db_path)
    try:
        _ensure_approval_table(conn)
        cursor = conn.cursor()
        now = time.time()
        
        # Clean up expired records
        cursor.execute("DELETE FROM super_admin_approvals WHERE expires_at < ?", (now,))
        conn.commit()
        
        # Check for existing pending request
        cursor.execute("""
            SELECT id FROM super_admin_approvals 
            WHERE actor_id = ? AND target_username = ? AND action_type = ? AND expires_at > ?
        """, (actor_id, target_username, action_type, now))
        
        row = cursor.fetchone()
        
        if row:
            # Confirmation received (Second Stage)
            # Consume the token
            cursor.execute("DELETE FROM super_admin_approvals WHERE id = ?", (row[0],))
            conn.commit()
            
            # Audit Log
            audit = AuditManager(db_path)
            audit.log_action(
                user_id=actor_id,
                action=f"SUPER_ADMIN_{action_type}_CONFIRMED",
                resource="user",
                details=json.dumps({"target": target_username, "status": "approved"}),
                ip_address="internal"
            )
            return True, "Action confirmed and authorized."
        else:
            # First Stage: Create request
            expires_at = now + APPROVAL_WINDOW_SECONDS
            # Upsert (using DELETE + INSERT to simplify unique constraint handling if SQLite version is old)
            cursor.execute("""
                DELETE FROM super_admin_approvals 
                WHERE actor_id = ? AND target_username = ? AND action_type = ?
            """, (actor_id, target_username, action_type))
            
            cursor.execute("""
                INSERT INTO super_admin_approvals (actor_id, target_username, action_type, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (actor_id, target_username, action_type, now, expires_at))
            conn.commit()
            
            # Audit Log
            audit = AuditManager(db_path)
            audit.log_action(
                user_id=actor_id,
                action=f"SUPER_ADMIN_{action_type}_REQUESTED",
                resource="user",
                details=json.dumps({"target": target_username, "status": "pending_confirmation"}),
                ip_address="internal"
            )
            
            return False, f"⚠️ GÜVENLİK UYARISI: Süper Yönetici ({target_username}) üzerinde işlem yapmak üzeresiniz. İşlemi onaylamak için lütfen 2 dakika içinde tekrar deneyin."
            
    except Exception as e:
        logging.error(f"Approval check error: {e}")
        return False, f"System error during approval check: {e}"
    finally:
        conn.close()

def check_delete_protection(db_path: str, username: str, actor_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Checks if a user can be deleted. Enforces 2-stage approval for Super Admins.
    """
    # 1. Basic Protection: Prevent deleting the hardcoded root superuser
    if username == SUPER_ADMIN_USERNAME:
        return False, "Root Super Admin cannot be deleted."
    
    conn = _get_connection(db_path)
    try:
        # 2. Check if target is a Super Admin
        if not _is_super_admin(conn, username):
            return True, "User is not a super admin, deletion allowed."
            
        # 3. If target IS Super Admin, enforce 2-stage approval
        if actor_id is None:
            return False, "Security check failed: Actor ID is required for Super Admin operations."
            
        # Check authorization (Actor must also be powerful, but we assume the caller checks basic permissions. 
        # Here we enforce the 2-step process.)
        
        return _check_two_stage_approval(db_path, actor_id, username, "DELETE")
        
    except Exception as e:
        logging.error(f"Delete protection error: {e}")
        return False, "Error checking delete protection."
    finally:
        conn.close()

def check_password_change_protection(db_path: str, username: str, new_password: str, actor_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Checks if a user's password can be changed. Enforces 2-stage approval for Super Admins.
    """
    conn = _get_connection(db_path)
    try:
        if not _is_super_admin(conn, username):
            return True, "User is not a super admin, modification allowed."
            
        if actor_id is None:
             # If actor is None, it might be the user changing their own password via a different flow,
             # but usually UserManager passes updated_by. 
             # If it's a self-service password change, we might want to skip this or handle it differently.
             # For now, if we don't know who is doing it, we block external modification.
             # BUT: If username matches the session user, it's a self-change. 
             # However, this function doesn't know the session user.
             # We will assume secure usage requiring actor_id.
             return False, "Security check failed: Actor ID required."

        return _check_two_stage_approval(db_path, actor_id, username, "PASSWORD_CHANGE")
        
    except Exception as e:
        logging.error(f"Password change protection error: {e}")
        return False, "Error checking protection."
    finally:
        conn.close()
