import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('sdg.db')
cur = conn.cursor()

logging.info(" SON TEMİZLİK")
logging.info("="*30)

# Test kullanıcılarını sil
cur.execute("DELETE FROM users WHERE username LIKE 'manual_user_%'")
deleted = cur.rowcount
logging.info(f" {deleted} test kullanıcısı silindi")

# Test görevlerini sil
cur.execute("DELETE FROM tasks WHERE title LIKE '%Test%' OR title LIKE '%Örnek%'")
deleted_tasks = cur.rowcount
logging.info(f" {deleted_tasks} test görevi silindi")

# Test anketlerini sil
cur.execute("DELETE FROM survey_templates WHERE name LIKE '%Test%' OR name LIKE '%Örnek%'")
deleted_surveys = cur.rowcount
logging.info(f" {deleted_surveys} test anketi silindi")

conn.commit()
conn.close()

logging.info("\n SON TEMİZLİK TAMAMLANDI!")
logging.info("="*30)
