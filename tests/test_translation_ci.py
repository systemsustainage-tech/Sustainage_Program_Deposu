import unittest
import json
import os

class TestTranslationCI(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.backend_locales = os.path.join(self.base_dir, "backend", "locales")
        self.root_locales = os.path.join(self.base_dir, "locales")
        
        # Load dictionary
        dict_path = os.path.join(self.base_dir, "tools", "translation_dictionary.json")
        with open(dict_path, 'r', encoding='utf-8') as f:
            self.translation_dict = json.load(f)

    def test_backend_en_translations(self):
        self._verify_translations(os.path.join(self.backend_locales, "en.json"), "en")

    def test_backend_de_translations(self):
        self._verify_translations(os.path.join(self.backend_locales, "de.json"), "de")

    def test_root_en_translations(self):
        self._verify_translations(os.path.join(self.root_locales, "en.json"), "en")

    def test_root_de_translations(self):
        self._verify_translations(os.path.join(self.root_locales, "de.json"), "de")

    def _verify_translations(self, file_path, lang):
        self.assertTrue(os.path.exists(file_path), f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        expected_updates = self.translation_dict.get(lang, {})
        for key, expected_value in expected_updates.items():
            # Check if key exists
            self.assertIn(key, data, f"Key '{key}' missing in {file_path}")
            # Check if value matches
            self.assertEqual(data[key], expected_value, 
                             f"Value mismatch for key '{key}' in {file_path}. Expected '{expected_value}', got '{data[key]}'")

if __name__ == '__main__':
    unittest.main()
