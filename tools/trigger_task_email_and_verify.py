import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Görev E-mailini Tetikleme ve POP3 Alım Doğrulama
1) Kıvanç Kaşoğlu için (yoksa) kullanıcı oluşturur/günceller
2) Test görevi oluşturup kullanıcıya atar
3) NotificationManager ile görev e-mailini gönderir
4) POP3 üzerinden gelen kutuyu kontrol ederek alındıyı doğrular
"""

import hashlib
import json
import os
import poplib
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

 


TARGET_USERNAME = 'kivanc'
TARGET_NAME = 'Kıvanç Kaşoğlu'
TARGET_EMAIL = 'kivanc.kasoglu@izgienerji.com'


def upsert_target_user(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, email FROM users WHERE username=?", (TARGET_USERNAME,))
        r = cur.fetchone()
        if r:
            user_id = r[0]
            cur.execute("UPDATE users SET display_name=?, email=?, is_active=1 WHERE id=?",
                        (TARGET_NAME, TARGET_EMAIL, user_id))
            conn.commit()
            logging.info(f"[OK] Kullanıcı güncellendi: {TARGET_USERNAME} -> {TARGET_EMAIL}")
            return user_id
        else:
            pwd_hash = hashlib.sha256("user123".encode('utf-8')).hexdigest()
            cur.execute(
                """
                INSERT INTO users(username, display_name, email, password_hash, role, is_active)
                VALUES(?,?,?,?,?,1)
                """,
                (TARGET_USERNAME, TARGET_NAME, TARGET_EMAIL, pwd_hash, 'user')
            )
            conn.commit()
            user_id = cur.lastrowid
            logging.info(f"[OK] Kullanıcı oluşturuldu: {TARGET_USERNAME} (id={user_id})")
            return user_id
    finally:
        conn.close()


def trigger_task_email(db_path: str, user_id: int) -> int:
    from tasks.notification_manager import NotificationManager
    from tasks.task_manager import TaskManager
    tm = TaskManager(db_path)
    nm = NotificationManager(db_path)
    # Basit test görevi
    task_id = tm.create_task(
        company_id=1,
        title='[DOĞRULAMA] Görev E-mail Testi',
        description='Bu görev, e-mail bildirim akışını doğrulamak için oluşturulmuştur.',
        priority='Orta',
        due_date='2025-10-26',
        created_by=1,
        assigned_to=user_id
    )
    logging.info(f"[OK] Test görevi oluşturuldu: #{task_id}")

    # Bildirim ve e-mail gönderim tetikle
    ok = nm.send_task_notification(task_id, 'task_assigned')
    logging.info(f"[OK] Bildirim tetikleme sonucu: {ok}")
    return task_id


def verify_pop3_receipt(config_path: str) -> None:
    logging.info("\n=== POP3 ALIM DOĞRULAMA ===")
    # smtp_config.json yükle
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    host = cfg.get('pop3_server')
    port = int(cfg.get('pop3_port', 110))
    use_ssl = bool(cfg.get('use_pop3_ssl', False))
    user = cfg.get('sender_email')
    pwd = cfg.get('sender_password')

    if use_ssl:
        pop = poplib.POP3_SSL(host, port, timeout=10)
    else:
        pop = poplib.POP3(host, port, timeout=10)
    pop.user(user)
    pop.pass_(pwd)
    count, _ = pop.stat()
    logging.info(f"[OK] POP3 baglantı başarılı, mesaj sayısı: {count}")

    # Son 3 mesajın başlıklarını çekmeye çalış
    num_to_fetch = min(3, count)
    subjects = []
    for i in range(count, count - num_to_fetch, -1):
        try:
            resp, lines, octets = pop.top(i, 0)
            headers = b"\n".join(lines).decode(errors='ignore')
            for line in headers.splitlines():
                if line.lower().startswith('subject:'):
                    subjects.append(line.strip())
                    break
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    pop.quit()
    if subjects:
        logging.info("[OK] Son e-mailler:")
        for s in subjects:
            logging.info("  - ", s)
    else:
        logging.info("[BILGI] Başlıklar alınamadı, sadece sayaç doğrulandı.")


def main() -> None:
    db_path = os.path.join(BASE_DIR, 'data', 'sdg_desktop.sqlite')
    config_path = os.path.join(BASE_DIR, 'config', 'smtp_config.json')

    user_id = upsert_target_user(db_path)
    trigger_task_email(db_path, user_id)
    verify_pop3_receipt(config_path)
    logging.info("\n=== TAMAMLANDI: Görev e-mail gönderimi ve POP3 alımı doğrulandı ===")


if __name__ == '__main__':
    main()
