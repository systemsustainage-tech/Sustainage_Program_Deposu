import os
import sys
import sqlite3
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock
from datetime import datetime

# Add paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.modules.surveys.hosting_survey_manager import HostingSurveyManager
from backend.modules.social.training_manager import TrainingManager

class TestSurveyIntegration(unittest.TestCase):
    def setUp(self):
        # Use temp DB file for testing to persist across connections
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_sustainage.db')
        
        # Init TrainingManager with test DB
        self.tm = TrainingManager(db_path=self.db_path)
        
        # Create company
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT)")
        c.execute("INSERT INTO companies (name) VALUES ('Test Company')")
        conn.commit()
        conn.close()
        
        # Init HostingSurveyManager
        self.sm = HostingSurveyManager(db_path=self.db_path)
        
        # Mock get_summary
        self.sm.get_summary = MagicMock(return_value={
            'success': True,
            'summary': [
                {
                    'topic_name': 'İş Sağlığı ve Güvenliği',
                    'materiality_score': 20.0 # Should trigger
                },
                {
                    'topic_name': 'Atık Yönetimi',
                    'materiality_score': 5.0 # Should NOT trigger (threshold 12)
                },
                {
                    'topic_name': 'Veri Gizliliği',
                    'materiality_score': 15.0 # Should trigger
                }
            ]
        })

    def tearDown(self):
        # Cleanup temp dir
        shutil.rmtree(self.temp_dir)

    def test_export_to_training(self):
        company_id = 1
        
        # Run export
        result = self.sm.export_to_training(
            survey_id=123,
            training_manager=self.tm,
            company_id=company_id,
            threshold=12.0
        )
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['created_count'], 2)
        
        # Verify DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT program_name FROM training_programs WHERE company_id=?", (company_id,))
        programs = [row[0] for row in c.fetchall()]
        conn.close()
        
        self.assertIn('İş Sağlığı ve Güvenliği Eğitimi', programs)
        self.assertIn('Veri Gizliliği Eğitimi', programs)
        self.assertNotIn('Atık Yönetimi Eğitimi', programs)
        
        print("\nTest passed: Training programs created correctly from survey results.")
        for p in programs:
            print(f"- Created: {p}")

    def test_duplicate_prevention(self):
        company_id = 1
        
        # First run
        self.sm.export_to_training(123, self.tm, company_id)
        
        # Second run
        result = self.sm.export_to_training(123, self.tm, company_id)
        
        self.assertEqual(result['created_count'], 0)
        self.assertIn("Mevcut: İş Sağlığı ve Güvenliği Eğitimi", result['details'])
        print("\nTest passed: Duplicate prevention works.")

if __name__ == '__main__':
    unittest.main()
