
import smtplib
import json
import os
import sys

# Load config
try:
    with open('c:/SUSTAINAGESERVER/backend/config/smtp_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except Exception as e:
    print(f"Error loading config: {e}")
    sys.exit(1)

smtp_server = config.get('smtp_server')
smtp_port = config.get('smtp_port')
sender_email = config.get('sender_email')
sender_password = config.get('sender_password')
use_tls = config.get('use_tls')

print(f"Connecting to {smtp_server}:{smtp_port}...")

try:
    server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
    server.set_debuglevel(1)
    
    if use_tls:
        print("Starting TLS...")
        server.starttls()
    
    print(f"Logging in as {sender_email}...")
    server.login(sender_email, sender_password)
    
    print("Login successful!")
    server.quit()
    print("Test completed successfully.")

except Exception as e:
    print(f"SMTP Error: {e}")
