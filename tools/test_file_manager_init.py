import unittest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.modules.file_manager.file_manager import FileManager

class TestFileManagerInit(unittest.TestCase):
    def test_init_company_id(self):
        # Create a dummy DB path
        db_path = "test_file_manager.db"
        
        # Initialize with company_id
        manager = FileManager(db_path=db_path, company_id=123)
        
        self.assertEqual(manager.company_id, 123)
        print("FileManager initialized successfully with company_id=123")

if __name__ == '__main__':
    unittest.main()
