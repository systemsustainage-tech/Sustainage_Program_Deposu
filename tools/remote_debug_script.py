import sys
import os
sys.path.append('/var/www/sustainage')

try:
    print("Starting import...")
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from web_app import app
    print("IMPORT_SUCCESS")
except Exception as e:
    print(f"IMPORT_FAILED: {e}")
    import traceback
    traceback.print_exc()
