import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)

from backend.services.email_service import EmailService

def test_email_service():
    print("Initializing EmailService...")
    service = EmailService()
    
    print("Configuration:")
    print(f"Server: {service.config.get('smtp_server')}")
    print(f"Port: {service.config.get('smtp_port')}")
    print(f"TLS: {service.config.get('use_tls')}")
    print(f"Validate SSL: {service.config.get('validate_ssl')}")
    print(f"Sender: {service.config.get('sender_email')}")
    
    recipient = service.config.get('sender_email') # Send to self
    print(f"\nSending test email to {recipient}...")
    
    success = service.send_email(
        to_email=recipient,
        subject="SUSTAINAGE SDG - Service Integration Test",
        body="This email confirms that EmailService is correctly configured and working with SSL validation disabled."
    )
    
    if success:
        print("\nSUCCESS: Email sent via EmailService!")
        return True
    else:
        print("\nFAILED: EmailService returned False.")
        return False

if __name__ == "__main__":
    if test_email_service():
        sys.exit(0)
    else:
        sys.exit(1)
