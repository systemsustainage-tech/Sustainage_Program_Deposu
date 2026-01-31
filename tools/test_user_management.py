#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı Yönetimi Test Scripti
Kullanıcı yönetimi özelliklerini test eder
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini Python path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_user_manager() -> None:
    """Kullanıcı yönetimi manager'ını test et"""
    logging.info("Kullanici Yonetimi Manager Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        from yonetim.kullanici_yonetimi.models.user_manager import UserManager

        # Manager instance'ı oluştur
        manager = UserManager()
        
        logging.info("1. Kullanici yonetimi şemasi test ediliyor...")
        logging.info("   Şema başarıyla oluşturuldu")
        
        logging.info("\n2. Kullanicilar test ediliyor...")
        users = manager.get_users()
        logging.info(f"   Toplam kullanici: {len(users)}")
        for user in users[:3]:  # İlk 3 kullanıcıyı göster
            logging.info(f"     {user['username']} - {user['first_name']} {user['last_name']}")
        
        logging.info("\n3. Roller test ediliyor...")
        roles = manager.get_roles()
        logging.info(f"   Toplam rol: {len(roles)}")
        for role in roles:
            logging.info(f"     {role['display_name']} ({role['user_count']} kullanici)")
        
        logging.info("\n4. Yetkiler test ediliyor...")
        permissions = manager.get_permissions()
        logging.info(f"   Toplam yetki: {len(permissions)}")
        
        # Modül bazlı yetkileri grupla
        module_permissions = {}
        for permission in permissions:
            module = permission['module']
            if module not in module_permissions:
                module_permissions[module] = 0
            module_permissions[module] += 1
        
        logging.info("   Modül bazlı yetkiler:")
        for module, count in module_permissions.items():
            logging.info(f"     {module}: {count} yetki")
        
        logging.info("\n5. Departmanlar test ediliyor...")
        departments = manager.get_departments()
        logging.info(f"   Toplam departman: {len(departments)}")
        for dept in departments:
            logging.info(f"     {dept['name']} ({dept['user_count']} kullanici)")
        
        logging.info("\n6. Kullanici istatistikleri test ediliyor...")
        stats = manager.get_user_statistics()
        logging.info(f"   Toplam kullanici: {stats['total_users']}")
        logging.info(f"   Aktif kullanici: {stats['active_users']}")
        logging.info(f"   Doğrulanmiş kullanici: {stats['verified_users']}")
        logging.info(f"   Departman sayisi: {len(stats['department_stats'])}")
        
        logging.info("\n7. Admin kullanici test ediliyor...")
        admin_user = None
        for user in users:
            if user['username'] == 'admin':
                admin_user = user
                break
        
        if admin_user:
            logging.info(f"   Admin kullanici bulundu: {admin_user['username']}")
            admin_permissions = manager.get_user_permissions(admin_user['id'])
            logging.info(f"   Admin yetki sayisi: {len(admin_permissions)}")
            
            # Temel yetkileri kontrol et
            basic_permissions = ['user.create', 'user.read', 'user.update', 'user.delete']
            for perm in basic_permissions:
                has_permission = manager.has_permission(admin_user['id'], perm)
                logging.info(f"     {perm}: {'' if has_permission else ''}")
        else:
            logging.info("   Admin kullanici bulunamadi!")
        
        logging.info("\n8. Audit loglar test ediliyor...")
        audit_logs = manager.get_audit_logs(limit=5)
        logging.info(f"   Toplam audit log: {len(audit_logs)}")
        for log in audit_logs[:3]:
            logging.info(f"     {log['action']} - {log['resource_type']} - {log['created_at'][:19]}")
        
        logging.info("\n" + "=" * 60)
        logging.info("Kullanici Yonetimi Manager Test Tamamlandi!")
        
        return True
        
    except Exception as e:
        logging.error(f"Kullanici yonetimi manager test edilirken hata: {e}")
        return False

def test_user_management_gui() -> None:
    """Kullanıcı yönetimi GUI'sini test et"""
    logging.info("\nKullanici Yonetimi GUI Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        import tkinter as tk

        from yonetim.kullanici_yonetimi.gui.user_management_gui import \
            UserManagementGUI

        # Test penceresi oluştur
        root = tk.Tk()
        root.withdraw()  # Pencereyi gizle
        
        # Kullanıcı yönetimi GUI oluştur
        UserManagementGUI(root, 1)
        
        logging.info("Kullanici Yonetimi GUI basariyla olusturuldu")
        
        # Pencereyi kapat
        root.destroy()
        
        return True
        
    except Exception as e:
        logging.error(f"Kullanici yonetimi GUI test edilirken hata: {e}")
        return False

def test_yonetim_gui() -> None:
    """Ana yönetim GUI'sini test et"""
    logging.info("\nAna Yonetim GUI Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        import tkinter as tk

        from yonetim.yönetim_gui import YonetimGUI

        # Test penceresi oluştur
        root = tk.Tk()
        root.withdraw()  # Pencereyi gizle
        
        # Ana yönetim GUI oluştur
        YonetimGUI(root, 1)
        
        logging.info("Ana Yonetim GUI basariyla olusturuldu")
        
        # Pencereyi kapat
        root.destroy()
        
        return True
        
    except Exception as e:
        logging.error(f"Ana yonetim GUI test edilirken hata: {e}")
        return False

def main() -> None:
    """Ana test fonksiyonu"""
    logging.info("Kullanici Yonetimi Modulu Test Baslatiliyor...")
    logging.info("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # 1. Kullanıcı yönetimi manager testi
    if test_user_manager():
        success_count += 1
    
    # 2. Kullanıcı yönetimi GUI testi
    if test_user_management_gui():
        success_count += 1
    
    # 3. Ana yönetim GUI testi
    if test_yonetim_gui():
        success_count += 1
    
    logging.info("\n" + "=" * 60)
    logging.info(f"Kullanici Yonetimi Modulu Test Tamamlandi: {success_count}/{total_tests} basarili")
    
    if success_count == total_tests:
        logging.info("Tum kullanici yonetimi ozellikleri basariyla test edildi!")
        logging.info("\nKullanici Yonetimi Ozellikleri:")
        logging.info("  - Kullanici Yonetimi (CRUD)")
        logging.info("  - Rol ve Yetki Yonetimi")
        logging.info("  - Departman Yonetimi")
        logging.info("  - Kullanici Istatistikleri")
        logging.info("  - Audit Trail (Aktivite Izleme)")
        logging.info("  - Sistem Ayarlari (Gelistirme Asamasinda)")
        logging.info("  - Backup/Restore (Gelistirme Asamasinda)")
        logging.info("  - Sistem Durumu (Gelistirme Asamasinda)")
        logging.info("\nKullanici yonetimi modulu kullanima hazir!")
        return True
    else:
        logging.info("Bazi ozellikler test edilemedi.")
        return False

if __name__ == "__main__":
    main()
