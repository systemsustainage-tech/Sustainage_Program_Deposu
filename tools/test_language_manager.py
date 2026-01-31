import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from core.language_manager import LanguageManager

lm = LanguageManager()
print(f"Testing 'active' in TR: {lm.get_text('active', 'tr')}")
print(f"Testing 'active' in EN: {lm.get_text('active', 'en')}")
