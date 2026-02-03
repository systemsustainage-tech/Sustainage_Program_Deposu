
import unittest
import sqlite3
import time
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config.database import DB_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestDatabasePerformance(unittest.TestCase):
    def setUp(self):
        """Set up test database connection"""
        self.db_path = DB_PATH
        # If DB_PATH is relative, make it absolute
        if not os.path.isabs(self.db_path):
             self.db_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), self.db_path)
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create a temporary table for testing
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def tearDown(self):
        """Clean up"""
        self.cursor.execute("DROP TABLE IF EXISTS performance_test")
        self.conn.commit()
        self.conn.close()

    def test_insert_performance(self):
        """Test INSERT performance (1000 records)"""
        start_time = time.time()
        
        # Batch insert is faster, but we want to test individual inserts or transaction handling
        self.cursor.execute("BEGIN TRANSACTION")
        for i in range(1000):
            self.cursor.execute("INSERT INTO performance_test (name, value) VALUES (?, ?)", (f"Item {i}", i * 1.5))
        self.conn.commit()
        
        duration = time.time() - start_time
        logging.info(f"[PERF] Insert 1000 records: {duration:.4f} seconds")
        self.assertLess(duration, 1.0, "Inserting 1000 records took too long (> 1s)")

    def test_select_performance(self):
        """Test SELECT performance"""
        # Seed data
        self.cursor.execute("BEGIN TRANSACTION")
        for i in range(1000):
            self.cursor.execute("INSERT INTO performance_test (name, value) VALUES (?, ?)", (f"Item {i}", i * 1.5))
        self.conn.commit()
        
        start_time = time.time()
        self.cursor.execute("SELECT * FROM performance_test")
        rows = self.cursor.fetchall()
        duration = time.time() - start_time
        
        self.assertEqual(len(rows), 1000)
        logging.info(f"[PERF] Select 1000 records: {duration:.4f} seconds")
        self.assertLess(duration, 0.5, "Selecting 1000 records took too long (> 0.5s)")

    def test_update_performance(self):
        """Test UPDATE performance"""
        # Seed data
        self.cursor.execute("BEGIN TRANSACTION")
        for i in range(1000):
            self.cursor.execute("INSERT INTO performance_test (name, value) VALUES (?, ?)", (f"Item {i}", i * 1.5))
        self.conn.commit()
        
        start_time = time.time()
        self.cursor.execute("UPDATE performance_test SET value = value + 1")
        self.conn.commit()
        duration = time.time() - start_time
        
        logging.info(f"[PERF] Update 1000 records: {duration:.4f} seconds")
        self.assertLess(duration, 1.0, "Updating 1000 records took too long (> 1s)")

if __name__ == '__main__':
    unittest.main()
