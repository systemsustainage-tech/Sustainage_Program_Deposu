import sys
import os

sys.path.insert(0, '/var/www/sustainage')

try:
    print("Attempting to import web_app...")
    from web_app import app
    print("Import Success")
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()
