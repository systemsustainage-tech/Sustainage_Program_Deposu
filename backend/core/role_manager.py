# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Optional, Union
from config.database import DB_PATH
from backend.core.database_manager import DatabaseManager

class RoleManager:
    """
    Manages Roles and Permissions for RBAC (Role-Based Access Control).
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseManager(db_path)

    def check_permission(self, user_id: int, permission_name: str) -> bool:
        """
        Check if a user has a specific permission via any of their roles.
        Also returns True if user has '__super__' role or similar (optional logic).
        """
        try:
            # Check for Super Admin (optional, depending on requirements)
            # Assuming role 'Super Admin' has all permissions or id=1 is super admin
            rows = self.db.execute_query("""
                SELECT 1 FROM user_roles ur
                JOIN roles r ON ur.role_id = r.id
                WHERE ur.user_id = ? AND r.name = 'Super Admin'
            """, (user_id,))
            if rows:
                return True

            # Check specific permission
            query = """
                SELECT 1
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE ur.user_id = ? AND p.name = ?
            """
            rows = self.db.execute_query(query, (user_id, permission_name))
            return len(rows) > 0
        except Exception as e:
            self.logger.error(f"Error checking permission {permission_name} for user {user_id}: {e}")
            return False

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Returns a list of all permission names a user has."""
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
            rows = self.db.execute_query(query, (user_id,))
            return [row[0] for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting permissions for user {user_id}: {e}")
            return []

    def create_role(self, name: str, description: str = "") -> Optional[int]:
        try:
            display_name = name.replace('_', ' ').title()
            # Note: execute_update returns rowcount, not lastrowid.
            # We need to use execute_query with INSERT ... RETURNING id (if SQLite supports it, version >= 3.35)
            # OR run separate query.
            # DatabaseManager's execute_update only returns rowcount.
            # But DatabaseManager handles connection.
            # To get lastrowid, we might need a custom method or use 'execute_query' if we use RETURNING.
            # SQLite 3.35+ supports RETURNING.
            # If not, we have to do: INSERT; SELECT last_insert_rowid(); in a transaction or script.
            
            # Let's try execute_query with RETURNING first?
            # Or use transaction method of DatabaseManager.
            
            # Using transaction to ensure we get correct ID
            def _create(conn):
                cursor = conn.cursor()
                cursor.execute("INSERT INTO roles (name, display_name, description, is_active) VALUES (?, ?, ?, 1)", (name, display_name, description))
                return cursor.lastrowid
            
            return self.db.transaction(_create)
            
        except Exception as e:
            self.logger.error(f"Error creating role {name}: {e}")
            return None

    def assign_permission_to_role(self, role_id: int, permission_name: str) -> bool:
        try:
            # Find permission id
            rows = self.db.execute_query("SELECT id FROM permissions WHERE name = ?", (permission_name,))
            if not rows:
                self.logger.warning(f"Permission {permission_name} not found.")
                return False
            perm_id = rows[0][0]

            self.db.execute_update("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, perm_id))
            return True
        except Exception as e:
            self.logger.error(f"Error assigning permission {permission_name} to role {role_id}: {e}")
            return False

    def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        try:
            rows = self.db.execute_query("SELECT id FROM roles WHERE name = ?", (role_name,))
            if not rows:
                return False
            role_id = rows[0][0]
            
            self.db.execute_update("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
            return True
        except Exception as e:
            self.logger.error(f"Error assigning role {role_name} to user {user_id}: {e}")
            return False
