import sys
import os
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def try_send(server_host, port, user, password, use_tls, ignore_cert=False):
    print(f"\n--- Testing {server_host}:{port} (Ignore Cert: {ignore_cert}) ---")
    
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = user
    msg['Subject'] = "SUSTAINAGE SDG - SMTP Test"
    msg.attach(MIMEText("Test email.", 'plain'))
    
    try:
        context = ssl.create_default_context()
        if ignore_cert:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
        with smtplib.SMTP(server_host, port) as server:
            if use_tls:
                print("Starting TLS...")
                server.starttls(context=context)
            
            print("Logging in...")
            server.login(user, password)
            
            print("Sending email...")
            server.send_message(msg)
            
        print("SUCCESS!")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_smtp_connection():
    config_path = os.path.join('backend', 'config', 'smtp_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    smtp_server = config.get('smtp_server')
    smtp_port = config.get('smtp_port')
    sender_email = config.get('sender_email')
    sender_password = config.get('sender_password')
    use_tls = config.get('use_tls', True)
    
    # 1. Try configured settings (failed previously)
    # 2. Try with check_hostname=False (to verify password)
    print("Attempt 1: Ignore Certificate Verification")
    if try_send(smtp_server, smtp_port, sender_email, sender_password, use_tls, ignore_cert=True):
        print("-> Credentials are correct, but Certificate is invalid for this hostname.")
        
        # 3. Try mail.sustainage.tr if different
        if smtp_server != "mail.sustainage.tr":
             print("\nAttempt 2: Try 'mail.sustainage.tr' with strict verification")
             if try_send("mail.sustainage.tr", smtp_port, sender_email, sender_password, use_tls, ignore_cert=False):
                 print("-> 'mail.sustainage.tr' is the correct hostname for the certificate.")
                 return "UPDATE_HOST"
        
        return "DISABLE_VERIFY"
    
    return "FAIL"

if __name__ == "__main__":
    result = test_smtp_connection()
    print(f"\nRESULT CODE: {result}")
