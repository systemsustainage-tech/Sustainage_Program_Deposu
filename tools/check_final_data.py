import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('sdg.db')
cur = conn.cursor()

logging.info(" SON DURUM KONTROLÜ")
logging.info("="*50)

# Firma bilgileri
cur.execute("SELECT ticari_unvan, sirket_adi FROM company_info WHERE company_id = 1")
company = cur.fetchone()
if company:
    logging.info(f" Firma: {company[0]}")
    logging.info(f"   Kısa Ad: {company[1]}")
else:
    logging.info(" Firma bilgisi bulunamadı")

logging.info("\n Admin Kullanıcılar:")
cur.execute("SELECT username, display_name, email FROM users WHERE role IN ('admin', 'super_admin')")
users = cur.fetchall()
for user in users:
    logging.info(f"   {user[0]} - {user[1]} ({user[2]})")

logging.info("\n Tüm Kullanıcılar:")
cur.execute("SELECT username, display_name, role FROM users ORDER BY role")
all_users = cur.fetchall()
for user in all_users:
    logging.info(f"   {user[0]} - {user[1]} ({user[2]})")

logging.info("\n Aktif Modüller:")
cur.execute("""
    SELECT m.module_name, m.module_code 
    FROM modules m 
    JOIN company_modules cm ON m.id = cm.module_id 
    WHERE cm.company_id = 1 AND cm.is_enabled = 1
    ORDER BY m.display_order
""")
modules = cur.fetchall()
for module in modules:
    logging.info(f"   {module[0]} ({module[1]})")

logging.info("\n Aktif Görevler:")
cur.execute("SELECT title, assigned_to, status FROM tasks WHERE status != 'completed' LIMIT 5")
tasks = cur.fetchall()
for task in tasks:
    logging.info(f"   {task[0]} - {task[1]} ({task[2]})")

conn.close()

logging.info("\n" + "="*50)
logging.info(" GERÇEK VERİLERLE GÜNCELLEME TAMAMLANDI!")
logging.info("="*50)
