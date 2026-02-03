import os
import sys
import sqlite3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(os.path.dirname(current_dir), 'backend')
sys.path.append(backend_dir)

try:
    from security.core.enhanced_2fa import _encrypt_secret, _decrypt_secret, ENCRYPTION_KEY
except ImportError as e:
    logging.error(f"Failed to import from backend: {e}")
    sys.exit(1)

def migrate_secrets(db_path):
    """
    Migrates TOTP secrets in the users table to be Fernet encrypted.
    
    Process for each user:
    1. Retrieve totp_secret.
    2. Decrypt it (if already encrypted) or get plain text (if not).
    3. Encrypt it (re-encrypt or encrypt for first time).
    4. Save back to DB.
    """
    
    if not ENCRYPTION_KEY:
        logging.error("TOTP_ENCRYPTION_KEY not found in environment. Cannot proceed with encryption.")
        return False

    if not os.path.exists(db_path):
        logging.error(f"Database not found at: {db_path}")
        return False

    logging.info(f"Starting migration on database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check which column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        target_column = None
        if 'totp_secret' in columns:
            target_column = 'totp_secret'
        elif 'totp_secret_encrypted' in columns:
            target_column = 'totp_secret_encrypted'
            
        if not target_column:
            logging.warning("Neither 'totp_secret' nor 'totp_secret_encrypted' columns exist in users table. Nothing to migrate.")
            return True

        logging.info(f"Using column: {target_column}")

        # Get users with secret
        cursor.execute(f"SELECT id, username, {target_column} FROM users WHERE {target_column} IS NOT NULL AND {target_column} != ''")
        users = cursor.fetchall()
        
        logging.info(f"Found {len(users)} users with TOTP secrets.")
        
        updated_count = 0
        
        for user_id, username, current_secret in users:
            try:
                # Step 1: Decrypt (handles backward compatibility)
                plain_secret = _decrypt_secret(current_secret)
                
                # Step 2: Encrypt
                new_encrypted_secret = _encrypt_secret(plain_secret)
                
                # Step 3: Save
                cursor.execute(f"UPDATE users SET {target_column} = ? WHERE id = ?", (new_encrypted_secret, user_id))
                updated_count += 1
                
            except Exception as e:
                logging.error(f"Error processing user {username} (ID: {user_id}): {e}")
        
        conn.commit()
        logging.info(f"Migration completed. Updated {updated_count} users.")
        return True
        
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    # Default DB path
    default_db_path = os.path.join(os.path.dirname(current_dir), 'backend', 'data', 'sdg_desktop.sqlite')
    
    # Allow override via arg
    if len(sys.argv) > 1:
        target_db_path = sys.argv[1]
    else:
        target_db_path = default_db_path
        
    migrate_secrets(target_db_path)
