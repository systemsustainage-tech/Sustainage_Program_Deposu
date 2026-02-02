import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCalculations(unittest.TestCase):
    def test_basic_math(self):
        """Sanity check to ensure test runner works."""
        self.assertEqual(1 + 1, 2)

    # Future: Add ESG calculation tests here
    # from backend.esg.esg_manager import calculate_esg_score
    # def test_esg_score(self):
    #     ...

if __name__ == '__main__':
    unittest.main()
