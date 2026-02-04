import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

try:
    from web_app import app, user_manager, get_db
    from backend.yonetim.security.core.crypto import verify_password_compat
except ImportError as e:
    print(f"Import Error: {e}")
    # Try setting cwd to project root
    os.chdir(project_root)
    sys.path.append(project_root)
    from web_app import app, user_manager, get_db
    from backend.yonetim.security.core.crypto import verify_password_compat

print("--- Testing Direct Authentication ---")
username = "admin"
password = "Admin123!"

try:
    with app.app_context():
        # 1. Check DB directly
        print(f"Checking DB for user '{username}'...")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            print("ERROR: User not found in DB!")
            sys.exit(1)
        print(f"User found. ID: {user['id']}")
        print(f"Stored Hash: {user['password_hash']}")

        # 2. Check Authentication Logic
        print(f"Attempting user_manager.authenticate('{username}', '***')...")
        result = user_manager.authenticate(username, password)
        
        if result:
            print("SUCCESS: Authentication successful!")
            print(f"Returned user: {result['username']}")
        else:
            print("FAILURE: Authentication failed.")
            
            # Debugging why
            print("Debugging Hash Verification:")
            is_valid = verify_password_compat(user['password_hash'], password)
            print(f"verify_password_compat result: {is_valid}")
            
except Exception as e:
    print(f"EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
