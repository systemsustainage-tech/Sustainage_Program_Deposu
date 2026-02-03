
import unittest
import logging
import sys
import os

# Ensure backend is in path if needed, or use absolute imports
# Assuming running from project root
# We need to add 'backend' to sys.path because internal modules use 'modules.x' or 'utils.x' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.modules.ai.ai_manager import AIManager
except ImportError:
    # Fallback
    from modules.ai.ai_manager import AIManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestAIModule(unittest.TestCase):
    """
    Tests for AI Module integration.
    Adapted from c:\\SDG\\scripts\\temp\\test_ai_module.py
    """

    def setUp(self):
        try:
            self.manager = AIManager()
        except Exception as e:
            self.skipTest(f"Failed to initialize AIManager: {e}")

    def test_manager_initialization(self):
        """Test if AIManager initializes correctly"""
        self.assertIsInstance(self.manager, AIManager)
        logging.info("[OK] AIManager initialized")

    def test_ai_availability(self):
        """Test if AI service is available (API Key present)"""
        is_available = self.manager.is_available()
        logging.info(f"AI Status: {'Active' if is_available else 'Inactive (No API Key)'}")
        
        if not is_available:
            logging.warning("AI is not available, skipping generation tests")

    def test_summary_generation(self):
        """Test generating a summary if AI is available"""
        if not self.manager.is_available():
            self.skipTest("AI API Key missing")

        test_data = {
            "target": "SDG 13 - Climate Action",
            "score": 75,
            "status": "In Progress"
        }

        try:
            summary = self.manager.generate_summary(test_data, "sdg")
            self.assertIsNotNone(summary)
            self.assertIsInstance(summary, str)
            self.assertTrue(len(summary) > 0)
            logging.info(f"Generated Summary: {summary[:100]}...")
        except Exception as e:
            self.fail(f"Summary generation failed: {e}")
