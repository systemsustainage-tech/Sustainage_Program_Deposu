import os
import sys
import logging

# Set up paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    from backend.services.email_service import EmailService
except ImportError:
    logging.error("Could not import EmailService. Check paths.")
    sys.exit(1)

def check_mail_via_service():
    print("--- Checking Mail System via EmailService ---")
    
    try:
        # Initialize Service
        service = EmailService()
        
        # Access config directly for display (if needed, though Service encapsulates it)
        # We can peek at internal config for debugging
        from backend.services.email_service import EMAIL_CONFIG
        
        print(f"SMTP Server: {EMAIL_CONFIG.get('smtp_server')}")
        print(f"Sender Email: {EMAIL_CONFIG.get('sender_email')}")
        print(f"Enabled: {EMAIL_CONFIG.get('enabled')}")
        
        # Send Test Email using the Service
        print("Attempting to send test email via EmailService...")
        
        # We'll use a simple direct email first
        user_email = EMAIL_CONFIG.get('sender_email')
        
        success = service.send_email(
            to_email=user_email,
            subject="Sustainage Service Test",
            body="This email confirms that the EmailService is working correctly."
        )
        
        if success:
            print("Test email sent successfully!")
        else:
            print("Failed to send test email.")

    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_mail_via_service()
