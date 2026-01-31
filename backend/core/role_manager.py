# -*- coding: utf-8 -*-
import sqlite3
import logging
from typing import List, Dict, Optional, Union
from config.database import DB_PATH

class RoleManager:
    """
    Manages Roles and Permissions for RBAC (Role-Based Access Control).
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def check_permission(self, user_id: int, permission_name: str) -> bool:
        """
        Check if a user has a specific permission via any of their roles.
        Also returns True if user has '__super__' role or similar (optional logic).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check for Super Admin (optional, depending on requirements)
            # Assuming role 'Super Admin' has all permissions or id=1 is super admin
            cursor.execute("""
                SELECT 1 FROM user_roles ur
                JOIN roles r ON ur.role_id = r.id
                WHERE ur.user_id = ? AND r.name = 'Super Admin'
            """, (user_id,))
            if cursor.fetchone():
                return True

            # Check specific permission
            query = """
                SELECT 1
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE ur.user_id = ? AND p.name = ?
            """
            cursor.execute(query, (user_id, permission_name))
            return cursor.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error checking permission {permission_name} for user {user_id}: {e}")
            return False
        finally:
            conn.close()

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Returns a list of all permission names a user has."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Super Admin check again? Or just list all?
            # Let's list actual assigned permissions.
            query = """
                SELECT DISTINCT p.name
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE ur.user_id = ?
            """
            cursor.execute(query, (user_id,))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting permissions for user {user_id}: {e}")
            return []
        finally:
            conn.close()

    def create_role(self, name: str, description: str = "") -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            display_name = name.replace('_', ' ').title()
            cursor.execute("INSERT INTO roles (name, display_name, description, is_active) VALUES (?, ?, ?, 1)", (name, display_name, description))
            role_id = cursor.lastrowid
            conn.commit()
            return role_id
        except Exception as e:
            self.logger.error(f"Error creating role {name}: {e}")
            return None
        finally:
            conn.close()

    def assign_permission_to_role(self, role_id: int, permission_name: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Find permission id
            cursor.execute("SELECT id FROM permissions WHERE name = ?", (permission_name,))
            res = cursor.fetchone()
            if not res:
                self.logger.warning(f"Permission {permission_name} not found.")
                return False
            perm_id = res[0]

            cursor.execute("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, perm_id))
            conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error assigning permission {permission_name} to role {role_id}: {e}")
            return False
        finally:
            conn.close()

    def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
            res = cursor.fetchone()
            if not res:
                return False
            role_id = res[0]
            
            cursor.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
            conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error assigning role {role_name} to user {user_id}: {e}")
            return False
        finally:
            conn.close()
