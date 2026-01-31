
import sys
import os
import traceback

# Setup paths like web_app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(BASE_DIR, 'server')
if os.path.exists(SERVER_DIR):
    sys.path.insert(0, SERVER_DIR)
    
BACKEND_DIR = os.path.join(SERVER_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)

print(f"Testing imports with paths: {sys.path[:2]}")

try:
    print("Attempting: from yonetim.kullanici_yonetimi.models.user_manager import UserManager")
    from yonetim.kullanici_yonetimi.models.user_manager import UserManager
    print("SUCCESS: Original import worked!")
except ImportError as e:
    print(f"FAILED: Original import failed: {e}")
    # traceback.print_exc()

try:
    print("\nAttempting: from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager")
    from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager
    print("SUCCESS: Full path import worked!")
except ImportError as e:
    print(f"FAILED: Full path import failed: {e}")
    traceback.print_exc()

# Check dependencies
print("\nChecking dependencies...")
modules = ['sqlite3', 'werkzeug', 'flask', 'flask_session']
for m in modules:
    try:
        __import__(m)
        print(f"OK: {m}")
    except ImportError:
        print(f"MISSING: {m}")
