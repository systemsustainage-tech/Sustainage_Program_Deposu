import sys
import os
import sqlite3
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from services.email_service import EmailService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sustainage.db'))

def verify_email_config():
    print(f"Verifying EmailService with DB: {DB_PATH}")
    
    # Ensure DB exists
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    try:
        # Initialize EmailService with db_path
        email_service = EmailService(db_path=DB_PATH)
        
        # Check if config is loaded
        config = email_service.config
        print("Email Configuration Loaded:")
        print(f"SMTP Server: {config.get('smtp_server')}")
        print(f"SMTP Port: {config.get('smtp_port')}")
        print(f"SMTP User: {config.get('smtp_user')}")
        print(f"Sender Email: {config.get('sender_email')}")
        
        # Check if we have valid settings (mock check)
        if config.get('smtp_server'):
            print("SUCCESS: SMTP server configuration found.")
        else:
            print("WARNING: SMTP server not configured in DB or env. (This might be expected if not set up yet)")

    except Exception as e:
        print(f"FAILED: Error initializing EmailService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_email_config()
