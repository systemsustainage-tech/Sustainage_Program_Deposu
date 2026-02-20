import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.language_manager import LanguageManager

class TestTranslationFallback(unittest.TestCase):
    def setUp(self):
        self.lm = LanguageManager()
        
    def test_readable_fallback(self):
        # Key that definitely doesn't exist
        key = "this_key_does_not_exist_123"
        expected = "This key does not exist 123"
        result = self.lm.get_text(key, lang='tr')
        self.assertEqual(result, expected)
        
    def test_readable_fallback_with_underscores(self):
        key = "very_random_feature_flag"
        expected = "Very random feature flag"
        result = self.lm.get_text(key, lang='tr')
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
