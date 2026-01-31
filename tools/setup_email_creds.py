import sys
import os
import json
import getpass
try:
    from cryptography.fernet import Fernet
except ImportError:
    print("cryptography module not found. Please install it: pip install cryptography")
    sys.exit(1)

def setup_creds():
    print("Email Credentials Setup")
    print("-----------------------")
    
    email = input("Sender Email [system@sustainage.tr]: ").strip() or "system@sustainage.tr"
    password = getpass.getpass("Sender Password: ").strip()
    
    if not password:
        print("Password cannot be empty.")
        return

    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(password.encode('utf-8')).decode('utf-8')
    
    data = {
        "sender_email": email,
        "password_enc": token
    }
    
    # Save to file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    creds_path = os.path.join(config_dir, 'email_credentials.json')
    
    with open(creds_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print(f"\nCredentials saved to: {creds_path}")
    print("\nIMPORTANT: You must set the following environment variable:")
    print(f"SENDER_PASSWORD_KEY={key.decode('utf-8')}")
    print("\nIn PowerShell:")
    print(f'$env:SENDER_PASSWORD_KEY="{key.decode("utf-8")}"')
    print("\nIn Command Prompt:")
    print(f'set SENDER_PASSWORD_KEY={key.decode("utf-8")}')

if __name__ == "__main__":
    setup_creds()
