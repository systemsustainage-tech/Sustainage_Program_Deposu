
import sys
import os

print("Checking imports...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR.endswith('tools'):
    BASE_DIR = os.path.dirname(BASE_DIR)

BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, BASE_DIR)

print(f"Added to path: {BACKEND_DIR}, {BASE_DIR}")

try:
    from backend.modules.dashboard_stats import DashboardStatsManager
    print("SUCCESS: backend.modules.dashboard_stats imported.")
except ImportError as e:
    print(f"FAIL: backend.modules.dashboard_stats import failed: {e}")
except Exception as e:
    print(f"FAIL: backend.modules.dashboard_stats import error: {e}")

try:
    import web_app
    print("SUCCESS: web_app imported.")
except ImportError as e:
    print(f"FAIL: web_app import failed: {e}")
except Exception as e:
    print(f"FAIL: web_app import error: {e}")
