
import sys
import os
import logging

# Add project root
sys.path.append(os.getcwd())

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

print("--- STARTING VERIFICATION ---")

try:
    print("Attempting to import remote_web_app...")
    import remote_web_app
    print("remote_web_app imported successfully.")
    
    print("Checking for app instance...")
    if hasattr(remote_web_app, 'app'):
        print("remote_web_app.app found.")
    else:
        print("remote_web_app.app NOT found.")

    print("--- SUCCESS ---")

except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Exception: {e}")
    sys.exit(1)
except SystemExit as e:
    print(f"SystemExit caught: {e}")
