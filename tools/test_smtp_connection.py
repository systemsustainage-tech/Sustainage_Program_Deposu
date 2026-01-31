import smtplib
import json
import os

def test_smtp():
    # backend/config/smtp_config.json yolunu kullan
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/config/smtp_config.json'))
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return

    server = config.get('smtp_server')
    port = config.get('smtp_port')
    user = config.get('sender_email')
    password = config.get('sender_password')
    use_tls = config.get('use_tls')

    print(f"Testing connection to {server}:{port} as {user}...")

    try:
        smtp = smtplib.SMTP(server, port, timeout=10)
        smtp.set_debuglevel(1)
        
        print("Connected.")
        
        if use_tls:
            print("Starting TLS...")
            smtp.starttls()
            print("TLS started.")
        
        print("Logging in...")
        smtp.login(user, password)
        print("Login SUCCESS!")
        
        smtp.quit()
    except Exception as e:
        print(f"SMTP TEST FAILED: {e}")

if __name__ == "__main__":
    test_smtp()
