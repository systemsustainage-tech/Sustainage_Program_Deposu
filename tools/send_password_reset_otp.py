import logging
import os
import sqlite3
import secrets
import string
from datetime import datetime, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.email_service import EmailService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run(username: str = "sibel123", new_email: str = "admin@digage.tr", db_path: str = os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, username))
    conn.commit()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    cur.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        logging.error("[HATA] Kullanıcı bulunamadı:", username)
        return
    user_id, username, email = row
    otp = ''.join(secrets.choice(string.digits) for _ in range(6))
    expires_at = (datetime.now() + timedelta(minutes=15)).isoformat(sep=' ')
    cur.execute(
        "INSERT OR REPLACE INTO password_reset_tokens (user_id, token, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (user_id, otp, expires_at, datetime.now().isoformat(sep=' '))
    )
    conn.commit()
    conn.close()
    es = EmailService(db_path)
    # Use standard template method
    ok = es.send_password_reset_email(email, username, otp)
    
    logging.info(f"[INFO] OTP generated for {username}")
    logging.info(f"[INFO] To: {email}")
    if ok:
        logging.info("[OK] Email gönderildi")
    else:
        logging.error("[HATA] Email gönderilemedi")

if __name__ == "__main__":
    run()

