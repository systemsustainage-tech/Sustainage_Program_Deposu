
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Attempting to import web_app...")
    import web_app
    print("web_app imported successfully!")
except Exception as e:
    print(f"Failed to import web_app: {e}")
    import traceback
    traceback.print_exc()
