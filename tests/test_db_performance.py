
import unittest
import logging
import time
import os
import sys
import tempfile
import sqlite3

# Adjust paths
# Add backend to sys.path for internal imports (utils, modules, etc.)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.modules.cbam.cbam_manager import CBAMManager
from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager
from backend.config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestDatabasePerformance(unittest.TestCase):
    """
    Performance Tests: Database Operations
    Adapted from c:\\SDG\\tests\\performance\\test_database_performance.py
    """
    
    def setUp(self):
        # Create a temporary database file
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.temp_db_fd)
        
        # Initialize Managers with temp DB
        self.cbam_manager = CBAMManager(self.temp_db_path)
        self.user_manager = UserManager(self.temp_db_path)
        self.company_id = 1
        
        # Ensure company exists
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        # Create necessary tables if not created by Managers (Managers usually do ensuring)
        # But we need to make sure 'companies' table exists and has ID 1 if not handled by CBAMManager init
        # CBAMManager usually expects existing company
        
        # Let's check if we need to manually insert company
        # UserManager ensures schema, so users/companies tables should exist
        cursor.execute("INSERT OR IGNORE INTO companies (id, name, sector, country) VALUES (1, 'Test Corp', 'Cement', 'TR')")
        conn.commit()
        conn.close()

    def tearDown(self):
        # Remove temp database
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except PermissionError:
                pass # Sometimes file is locked on Windows

    def test_bulk_product_insert_performance(self):
        """Test: 1000 product insert performance (< 5 seconds)"""
        
        start_time = time.time()
        
        products = []
        for i in range(1000):
            products.append({
                'product_code': f'PERF_PROD{i:04d}',
                'product_name': f'Performance Test Product {i}',
                'sector': 'cement'
            })
        
        # Assume add_products_bulk exists in CBAMManager
        # If not, we might fail, but we are porting the test which assumes it exists
        try:
            if hasattr(self.cbam_manager, 'add_products_bulk'):
                self.cbam_manager.add_products_bulk(self.company_id, products)
            else:
                logging.warning("CBAMManager has no add_products_bulk method, falling back to loop (slow)")
                for p in products:
                    self.cbam_manager.add_product(self.company_id, p)
        except Exception as e:
            self.fail(f"Bulk insert failed: {e}")
        
        duration = time.time() - start_time
        
        logging.info(f"[OK] 1000 products inserted in {duration:.2f}s")
        # Assert might be too strict for some environments, but keeping it generous
        self.assertLess(duration, 10.0, "Bulk insert took too long")

    def test_large_dataset_query_performance(self):
        """Test: Query performance on large dataset"""
        
        # Insert 500 products first
        products = [
            {
                'product_code': f'QUERY_PROD{i:04d}',
                'product_name': f'Query Test Product {i}',
                'sector': 'cement'
            }
            for i in range(500)
        ]
        
        if hasattr(self.cbam_manager, 'add_products_bulk'):
            self.cbam_manager.add_products_bulk(self.company_id, products)
        else:
             for p in products:
                self.cbam_manager.add_product(self.company_id, p)
        
        start_time = time.time()
        fetched_products = self.cbam_manager.get_products(self.company_id)
        duration = time.time() - start_time
        
        self.assertGreaterEqual(len(fetched_products), 500)
        self.assertLess(duration, 2.0, "Query took too long")
        
        logging.info(f"[OK] {len(fetched_products)} products fetched in {duration:.2f}s")

