import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_env():
    print("Verifying Environment Variables...")
    
    # Critical SMTP vars
    smtp_vars = [
        'SMTP_SERVER', 'SMTP_PORT', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'EMAIL_ENABLED'
    ]
    
    missing = []
    for var in smtp_vars:
        val = os.getenv(var)
        if not val:
            missing.append(var)
        else:
            # Mask password in output
            if 'PASSWORD' in var:
                print(f"✅ {var}: ********")
            else:
                print(f"✅ {var}: {val}")
    
    if missing:
        print(f"\n❌ Missing Environment Variables: {', '.join(missing)}")
        print("Ensure these are set in your .env file or system environment.")
    else:
        print("\n✅ All critical SMTP environment variables are set.")

if __name__ == "__main__":
    # Load .env manually if needed for testing (backend logic does this too)
    try:
        from dotenv import load_dotenv
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(root_dir, '.env')
        if os.path.exists(env_path):
            print(f"Loading .env from {env_path}")
            load_dotenv(env_path)
        else:
            print("⚠️ .env file not found in root directory.")
    except ImportError:
        print("⚠️ python-dotenv not installed. Checking system env vars directly.")
        
    verify_env()
