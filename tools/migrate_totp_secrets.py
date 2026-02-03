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
        # Check if column exists first
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'totp_secret' not in columns:
            logging.warning("Column 'totp_secret' does not exist in users table. Nothing to migrate.")
            return True

        # Get users with totp_secret
        cursor.execute("SELECT id, username, totp_secret FROM users WHERE totp_secret IS NOT NULL AND totp_secret != ''")
        users = cursor.fetchall()
        
        logging.info(f"Found {len(users)} users with TOTP secrets.")
        
        updated_count = 0
        
        for user_id, username, current_secret in users:
            try:
                # Step 1: Decrypt (handles backward compatibility)
                # If current_secret is plain, returns plain.
                # If current_secret is encrypted, returns decrypted plain.
                plain_secret = _decrypt_secret(current_secret)
                
                # Step 2: Encrypt
                # Always returns encrypted version
                new_encrypted_secret = _encrypt_secret(plain_secret)
                
                # Check if it actually changed (ignoring IV randomization for a moment, just check if it looks encrypted)
                # But Fernet produces different output every time, so direct comparison might not be useful to skip.
                # However, if it was already encrypted, we are re-encrypting it, which is fine (key rotation support effectively).
                
                # Step 3: Save
                cursor.execute("UPDATE users SET totp_secret = ? WHERE id = ?", (new_encrypted_secret, user_id))
                updated_count += 1
                
                # Verify immediately (optional but good for debugging logs)
                # decrypted_check = _decrypt_secret(new_encrypted_secret)
                # if decrypted_check != plain_secret:
                #     logging.error(f"Verification failed for user {username}!")
                
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
