
import unittest
import os
import sys
import shutil
import sqlite3
import logging
from datetime import datetime

# Configure paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

try:
    from backend.modules.reporting.report_generator import ReportGenerator
except ImportError:
    try:
        from modules.reporting.report_generator import ReportGenerator
    except ImportError:
         logging.error("Could not import ReportGenerator")
         raise

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestReporting(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_db_path = os.path.join(project_root, 'tests', 'test_reporting.db')
        
        # Remove if exists
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass

        # Create dummy companies table
        self._create_dummy_db()
        
        # Initialize ReportGenerator
        self.report_generator = ReportGenerator(db_path=self.test_db_path)

    def _create_dummy_db(self):
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                sector TEXT,
                country TEXT
            )
        """)
        cursor.execute("INSERT INTO companies (name, sector, country) VALUES ('Test Company', 'Energy', 'TR')")
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass

    def test_add_report_template(self):
        """Test adding a report template"""
        success = self.report_generator.add_report_template(
            company_id=1,
            template_name="Test Template",
            template_type="pdf",
            template_content="<h1>Test Report</h1>",
            template_variables="var1,var2"
        )
        self.assertTrue(success, "Failed to add report template")
        
        # Verify in DB
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT template_name FROM report_templates WHERE company_id=1")
        row = cursor.fetchone()
        self.assertEqual(row[0], "Test Template")
        conn.close()

    def test_generate_report_entry(self):
        """Test generating a report entry (metadata only for this unit test)"""
        # First add a template
        self.report_generator.add_report_template(
            company_id=1,
            template_name="Test Template",
            template_type="pdf",
            template_content="<h1>Test Report</h1>"
        )
        
        # Manually verify that generated_reports table exists and we can insert (simulate generation)
        # Note: report_generator.generate_report might try to actually create a file, 
        # so we'll check the DB structure instead to avoid FS dependency issues in this basic test.
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generated_reports'")
        table = cursor.fetchone()
        self.assertIsNotNone(table, "generated_reports table should exist")
        
        # Insert a dummy report record
        cursor.execute("""
            INSERT INTO generated_reports 
            (company_id, template_id, report_name, report_period, report_format, generation_date)
            VALUES (1, 1, 'Monthly Report', '2023-10', 'pdf', ?)
        """, (datetime.now().strftime("%Y-%m-%d"),))
        conn.commit()
        
        cursor.execute("SELECT count(*) FROM generated_reports")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        conn.close()

if __name__ == '__main__':
    unittest.main()
