import os
import json
import logging
from backend.core.database_manager import DatabaseManager
from config.database import DB_PATH

class MaintenanceManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self.db = DatabaseManager(self.db_path)

    def run_all_checks(self):
        results = []
        results.append(self.check_database_connection())
        results.append(self.check_critical_tables())
        results.append(self.check_translation_files())
        results.append(self.check_directory_structure())
        return results

    def check_database_connection(self):
        try:
            if not os.path.exists(self.db_path):
                return {'name': 'Database File', 'status': 'FAIL', 'message': f'File not found at {self.db_path}'}
            
            # Use DatabaseManager to execute a simple query
            self.db.execute_query("SELECT 1")
            return {'name': 'Database Connection', 'status': 'OK', 'message': 'Connection successful'}
        except Exception as e:
            return {'name': 'Database Connection', 'status': 'FAIL', 'message': str(e)}

    def check_critical_tables(self):
        required_tables = ['users', 'companies', 'report_registry', 'audit_logs', 'roles', 'permissions']
        missing_tables = []
        try:
            # Query sqlite_master using DatabaseManager
            rows = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row['name'] for row in rows]

            for table in required_tables:
                if table not in existing_tables:
                    missing_tables.append(table)
            
            if missing_tables:
                return {'name': 'Critical Tables', 'status': 'FAIL', 'message': f'Missing: {", ".join(missing_tables)}'}
            return {'name': 'Critical Tables', 'status': 'OK', 'message': 'All critical tables exist'}
        except Exception as e:
            return {'name': 'Critical Tables', 'status': 'FAIL', 'message': str(e)}

    def check_translation_files(self):
        path = os.path.join('backend', 'locales', 'tr.json')
        if not os.path.exists(path):
            return {'name': 'Translation File (TR)', 'status': 'FAIL', 'message': 'tr.json not found'}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Sample keys to check integrity
            keys = ['admin_panel', 'btn_save', 'login_title']
            missing = [k for k in keys if k not in data]
            
            if missing:
                return {'name': 'Translation Integrity', 'status': 'WARN', 'message': f'Missing keys: {", ".join(missing)}'}
            return {'name': 'Translation Integrity', 'status': 'OK', 'message': 'File valid and keys present'}
        except Exception as e:
            return {'name': 'Translation Integrity', 'status': 'FAIL', 'message': str(e)}

    def check_directory_structure(self):
        dirs = [
            'backend/data',
            'backend/locales',
            'templates',
            'static'
        ]
        missing = []
        for d in dirs:
            if not os.path.exists(d):
                missing.append(d)
        
        if missing:
            return {'name': 'Directory Structure', 'status': 'FAIL', 'message': f'Missing: {", ".join(missing)}'}
        return {'name': 'Directory Structure', 'status': 'OK', 'message': 'All critical directories exist'}
