
import unittest
import os
import sqlite3
import logging
from backend.modules.advanced_reporting.report_templates import AdvancedReportTemplates, ReportSection

class TestMandatorySections(unittest.TestCase):
    def setUp(self):
        self.db_path = 'tests/test_mandatory_sections.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.templates_manager = AdvancedReportTemplates(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_mandatory_sections_creation(self):
        """Test if mandatory sections are created for templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for a specific template's sections
        template_id = 'sdg_template_tr'
        cursor.execute("SELECT section_name, is_required FROM report_sections WHERE template_id = ?", (template_id,))
        sections = cursor.fetchall()
        
        section_names = [s[0] for s in sections]
        self.assertIn('Veri Kaynağı', section_names)
        self.assertIn('Metodoloji', section_names)
        self.assertIn('Standart Referans', section_names)
        
        # Verify is_required flag
        for name, is_required in sections:
            if name in ['Veri Kaynağı', 'Metodoloji', 'Standart Referans']:
                self.assertEqual(is_required, 1, f"Section {name} should be required")
                
        conn.close()

    def test_delete_mandatory_section_prevention(self):
        """Test prevention of deleting mandatory sections"""
        # Get a mandatory section ID
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM report_sections WHERE template_id = 'sdg_template_tr' AND section_name = 'Veri Kaynağı'")
        section_id = cursor.fetchone()[0]
        conn.close()
        
        # Try to delete
        result = self.templates_manager.delete_section(section_id)
        self.assertFalse(result, "Should not be able to delete mandatory section")
        
        # Verify it still exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM report_sections WHERE id = ?", (section_id,))
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1, "Mandatory section should still exist")

    def test_delete_optional_section(self):
        """Test deleting an optional section"""
        # Create an optional section
        section = ReportSection(
            section_id='test_optional_section',
            template_id='sdg_template_tr',
            section_name='Optional Section',
            section_type='text',
            content='Optional content',
            order=999,
            is_required=False
        )
        self.templates_manager._save_section(section)
        
        # Verify it exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM report_sections WHERE id = 'test_optional_section'")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        
        # Delete it
        result = self.templates_manager.delete_section('test_optional_section')
        self.assertTrue(result, "Should be able to delete optional section")
        
        # Verify it's gone
        cursor.execute("SELECT count(*) FROM report_sections WHERE id = 'test_optional_section'")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
