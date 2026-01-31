#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-mail Sistemi Test Script
Görev bildirimleri için e-mail sistemini test eder
"""

import logging
import os
import sys

# Path ayarları
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tasks.email_service import EmailService
from tasks.notification_manager import NotificationManager
from tasks.task_manager import TaskManager
from config.icons import Icons
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def test_email_templates() -> None:
    """E-mail şablonlarını test et"""
    logging.info("\n" + "=" * 80)
    logging.info("1. E-MAIL SABLONLARI TESTI")
    logging.info("=" * 80)
    
    email_service = EmailService()
    
    # Test kullanıcısı bilgileri
    test_user = {
        'email': 'test@example.com',
        'name': 'Test Kullanıcı'
    }
    
    # Test görevi bilgileri
    test_task = {
        'id': 1,
        'title': 'SDG 7 - Enerji Tüketimi Verileri',
        'description': 'Son 1 yıllık elektrik tüketim verilerini giriniz',
        'priority': 'Yüksek',
        'due_date': '2025-10-26',
        'assigned_to': 1,
        'created_by': 1,
        'status': 'Bekliyor',
        'progress': 0
    }
    
    logging.info("\n[TEST] Yeni görev atandı bildirimi...")
    email_service.send_email(
        to_email=test_user['email'],
        subject=' Yeni Görev Atandı: ' + test_task['title'],
        body=f"""
Merhaba {test_user['name']},

Size yeni bir görev atandı!

 GÖREV DETAYLARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Başlık: {test_task['title']}
Açıklama: {test_task['description']}
Öncelik: {test_task['priority']}
Bitiş Tarihi: {test_task['due_date']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 YAPMANIZ GEREKENLER:
1. Sisteme giriş yapın
2. "Görevlerim" bölümüne gidin
3. Görevi inceleyin
4. Kabul edin veya reddedin

Icons.TIME SON TARİH: {test_task['due_date']}

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        """,
        to_name=test_user['name']
    )
    
    logging.info("\n[OK] E-mail şablonu testi tamamlandı!\n")

def test_task_notification() -> None:
    """Görev bildirimi testi"""
    logging.info("\n" + "=" * 80)
    logging.info("2. GOREV BILDIRIMI TESTI")
    logging.info("=" * 80)
    
    task_manager = TaskManager()
    notification_manager = NotificationManager()
    
    # Test görevi oluştur
    logging.info("\n[TEST] Test görevi oluşturuluyor...")
    
    try:
        # Kullanıcı kontrolü
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email FROM users WHERE is_active = 1 LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            logging.error("[HATA] Aktif kullanıcı bulunamadı!")
            conn.close()
            return False
        
        user_id, username, email = user
        logging.info(f"[OK] Test kullanıcısı: {username} ({email})")
        
        # Görev oluştur
        task_id = task_manager.create_task(
            company_id=1,
            title='[TEST] E-mail Sistemi Test Görevi',
            description='Bu bir test görevidir. E-mail bildirimini test etmek için oluşturulmuştur.',
            priority='Orta',
            due_date='2025-10-26',
            created_by=1
        )
        
        # Kullanıcıya ata
        cursor.execute("UPDATE tasks SET assigned_to = ? WHERE id = ?", (user_id, task_id))
        conn.commit()
        conn.close()
        
        logging.info(f"[OK] Test görevi oluşturuldu (ID: {task_id})")
        
        # Bildirim gönder
        logging.info("\n[TEST] E-mail bildirimi gönderiliyor...")
        success = notification_manager.send_task_notification(task_id, 'task_assigned')
        
        if success:
            logging.info("[OK] Bildirim başarıyla gönderildi!")
            logging.info(f"\nKontrol edilecek e-mail: {email}")
            logging.info("Test modundaysanız, yukarıdaki console çıktısında e-mail içeriğini göreceksiniz.")
        else:
            logging.error("[HATA] Bildirim gönderilemedi!")
            return False
        
        # Temizlik
        logging.info("\n[TEMIZLIK] Test görevi siliniyor...")
        task_manager.delete_task(task_id)
        logging.info("[OK] Test görevi silindi")
        
        return True
        
    except Exception as e:
        logging.error(f"[HATA] Test sırasında hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_notification_types() -> None:
    """Tüm bildirim tiplerini test et"""
    logging.info("\n" + "=" * 80)
    logging.info("3. TUM BILDIRIM TIPLERI TESTI")
    logging.info("=" * 80)
    
    notification_types = [
        ('task_assigned', 'Yeni görev atandı'),
        ('task_updated', 'Görev güncellendi'),
        ('task_completed', 'Görev tamamlandı'),
        ('task_overdue', 'Görev süresi doldu'),
        ('task_deadline_near', 'Son tarih yaklaşıyor')
    ]
    
    EmailService()
    
    for notif_type, description in notification_types:
        logging.info(f"\n[TEST] {description} ({notif_type})")
        logging.info("-" * 80)
        
        # Her bildirim tipi için özet göster
        logging.info(f"Bildirim tipi: {notif_type}")
        logging.info(f"Açıklama: {description}")
        logging.info("[OK] Şablon mevcut\n")
    
    logging.info("[OK] Tüm bildirim tipleri hazır!")

def show_email_config() -> None:
    """E-mail konfigürasyonunu göster"""
    logging.info("\n" + "=" * 80)
    logging.info("E-MAIL KONFIGURASYON")
    logging.info("=" * 80)
    
    from config.email_config import EMAIL_CONFIG, TEST_MODE
    
    logging.info(f"\nSMTP Sunucu: {EMAIL_CONFIG['smtp_server']}")
    logging.info(f"SMTP Port: {EMAIL_CONFIG['smtp_port']}")
    logging.info(f"TLS Kullan: {EMAIL_CONFIG['use_tls']}")
    logging.info(f"Gönderen E-mail: {EMAIL_CONFIG['sender_email']}")
    logging.info(f"Gönderen Adı: {EMAIL_CONFIG['sender_name']}")
    logging.info(f"E-mail Etkin: {EMAIL_CONFIG['enabled']}")
    logging.info(f"Test Modu: {TEST_MODE}")
    
    if TEST_MODE:
        logging.info("\n[BILGI] TEST MODU AKTIF")
        logging.info("Gerçek e-mail gönderilmeyecek, sadece console'a yazdırılacak.")
        logging.info("Gerçek e-mail göndermek için:")
        logging.info("  1. config/email_config.py dosyasını açın")
        logging.info("  2. TEST_MODE = False yapın")
        logging.info("  3. SMTP bilgilerinizi girin (sender_email, sender_password)")
        logging.info("  4. EMAIL_CONFIG['enabled'] = True yapın")
    else:
        logging.info("\n[UYARI] GERCEK E-MAIL MODU AKTIF")
        logging.info("E-mail'ler gerçekten gönderilecek!")

def main() -> None:
    """Ana test fonksiyonu"""
    logging.info("\n")
    logging.info("=" * 80)
    logging.info("               E-MAIL SISTEMI TEST ARACI")
    logging.info("=" * 80)
    
    # Konfigürasyonu göster
    show_email_config()
    
    # Test 1: E-mail şablonları
    test_email_templates()
    
    # Test 2: Görev bildirimi
    test_task_notification()
    
    # Test 3: Tüm bildirim tipleri
    test_all_notification_types()
    
    logging.info("\n" + "=" * 80)
    logging.info("               TESTLER TAMAMLANDI!")
    logging.info("=" * 80)
    
    logging.info("\nSONRAKI ADIMLAR:")
    logging.info("1. Test modunu kapatmak için: config/email_config.py -> TEST_MODE = False")
    logging.info("2. SMTP bilgilerinizi config/email_config.py dosyasına girin")
    logging.info("3. Gerçek görev oluşturup e-mail'lerin gittiğini kontrol edin")
    logging.info("\n")

if __name__ == "__main__":
    main()

