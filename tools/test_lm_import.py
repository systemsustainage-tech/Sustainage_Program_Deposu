import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from core.language_manager import LanguageManager

try:
    lm = LanguageManager("some_path")
    print("Success")
except TypeError as e:
    print(f"TypeError: {e}")
except Exception as e:
    print(f"Error: {e}")
