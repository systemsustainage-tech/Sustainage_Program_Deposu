
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root and backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from backend.modules.file_manager.advanced_file_manager import AdvancedFileManager
from backend.core.database_manager import DatabaseManager

class TestAdvancedFileManagerIsolation(unittest.TestCase):
    def setUp(self):
        # Reset Singleton
        DatabaseManager._instance = None
        
        # Use a unique temp file
        import uuid
        self.temp_db = os.path.abspath(f"test_afm_{uuid.uuid4().hex}.db")
        self.temp_upload_dir = os.path.abspath(f"test_uploads_{uuid.uuid4().hex}")
        
        self.manager = AdvancedFileManager(self.temp_db, self.temp_upload_dir)
        
        # Create companies table (required for FKs)
        self.manager.db.execute_update("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        self.manager.db.execute_update("INSERT INTO companies (id, name) VALUES (1, 'Company A')")
        self.manager.db.execute_update("INSERT INTO companies (id, name) VALUES (2, 'Company B')")
        
        # Insert test files directly to simulate state
        # File 1 for Company 1
        self.manager.db.execute_update("""
            INSERT INTO files (company_id, file_name, original_name, file_path, is_deleted)
            VALUES (1, 'file1.txt', 'file1.txt', '/tmp/file1.txt', 0)
        """)
        
        # File 2 for Company 2
        self.manager.db.execute_update("""
            INSERT INTO files (company_id, file_name, original_name, file_path, is_deleted)
            VALUES (2, 'file2.txt', 'file2.txt', '/tmp/file2.txt', 0)
        """)
        
        # Get IDs
        rows = self.manager.db.execute_query("SELECT id FROM files WHERE file_name = 'file1.txt'")
        self.file1_id = rows[0]['id']
        
        rows = self.manager.db.execute_query("SELECT id FROM files WHERE file_name = 'file2.txt'")
        self.file2_id = rows[0]['id']

    def tearDown(self):
        if hasattr(self, 'manager') and self.manager.db:
             while not self.manager.db._pool.empty():
                try:
                    conn = self.manager.db._pool.get_nowait()
                    conn.close()
                except:
                    pass
        
        if os.path.exists(self.temp_db):
            try:
                os.remove(self.temp_db)
            except:
                pass
        
        if os.path.exists(self.temp_upload_dir):
            import shutil
            shutil.rmtree(self.temp_upload_dir)

    def test_get_file_info_isolation(self):
        print("\nTesting get_file_info Isolation...")
        
        # Company 1 should see File 1
        info = self.manager.get_file_info(self.file1_id, company_id=1)
        self.assertIsNotNone(info)
        self.assertEqual(info['id'], self.file1_id)
        
        # Company 1 should NOT see File 2
        info = self.manager.get_file_info(self.file2_id, company_id=1)
        self.assertIsNone(info)
        
        # Company 2 should see File 2
        info = self.manager.get_file_info(self.file2_id, company_id=2)
        self.assertIsNotNone(info)

    def test_add_tags_ownership(self):
        print("\nTesting add_tags_to_file Ownership...")
        
        # Company 1 tries to tag File 2 -> Should fail
        success = self.manager.add_tags_to_file(self.file2_id, ['tag1'], company_id=1)
        self.assertFalse(success)
        
        # Company 1 tags File 1 -> Should succeed
        success = self.manager.add_tags_to_file(self.file1_id, ['tag1'], company_id=1)
        self.assertTrue(success)

    def test_metadata_ownership(self):
        print("\nTesting Metadata Ownership...")
        
        # Company 1 tries to add metadata to File 2 -> Should fail
        success = self.manager.add_metadata(self.file2_id, 'key', 'value', company_id=1)
        self.assertFalse(success)
        
        # Company 1 adds to File 1 -> Should succeed
        success = self.manager.add_metadata(self.file1_id, 'key', 'value', company_id=1)
        self.assertTrue(success)
        
        # Company 1 tries to read metadata of File 2 -> Should fail (empty dict)
        # First ensure File 2 has metadata (added by Company 2)
        self.manager.add_metadata(self.file2_id, 'key2', 'val2', company_id=2)
        
        meta = self.manager.get_metadata(self.file2_id, company_id=1)
        self.assertEqual(meta, {})
        
        # Company 2 reads File 2 -> Should succeed
        meta = self.manager.get_metadata(self.file2_id, company_id=2)
        self.assertEqual(meta['key2'], 'val2')

    def test_share_file_ownership(self):
        print("\nTesting Share File Ownership...")
        
        # Company 1 tries to share File 2 -> Should fail
        success = self.manager.share_file(self.file2_id, shared_with_user_id=99, company_id=1)
        self.assertFalse(success)
        
        # Company 1 shares File 1 -> Should succeed
        success = self.manager.share_file(self.file1_id, shared_with_user_id=99, company_id=1)
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
