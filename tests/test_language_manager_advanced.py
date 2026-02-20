import unittest
import os
import time
import json
import threading
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.language_manager import LanguageManager

class TestLanguageManagerAdvanced(unittest.TestCase):
    def setUp(self):
        self.lm = LanguageManager()
        self.test_lang = 'test_lang'
        self.test_file = os.path.join(self.lm.locales_dir, f"{self.test_lang}.json")
        
        # Create initial test file
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump({"hello": "Hello Initial"}, f)
            
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_readable_fallback(self):
        # Test fallback for missing key
        key = "active_surveys"
        expected = "Active surveys"
        # Ensure key is not in translations (it shouldn't be in tr or en unless added)
        # We use a random key to be sure
        random_key = "very_random_key_example"
        expected_random = "Very random key example"
        
        result = self.lm.tr(random_key)
        self.assertEqual(result, expected_random)
        
        key2 = "data-entry-form"
        expected2 = "Data entry form"
        self.assertEqual(self.lm.tr(key2), expected2)

    def test_reload_on_change(self):
        # Load the test language
        self.lm.load_language(self.test_lang)
        self.assertEqual(self.lm.tr("hello"), "Hello Initial")
        
        # Modify the file
        time.sleep(1.1) # Ensure mtime changes (some filesystems have 1s resolution)
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump({"hello": "Hello Modified"}, f)
            
        # Force check (simulate time passing if needed, but check_interval is 5s)
        # We need to mock time or wait, or just set last_check_time to 0
        self.lm.last_check_time = 0
        
        # Trigger tr to cause reload
        result = self.lm.tr("hello")
        self.assertEqual(result, "Hello Modified")

if __name__ == '__main__':
    unittest.main()
