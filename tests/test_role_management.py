
import os
import sys
import unittest
import sqlite3
import logging
import uuid
from datetime import datetime

# Backend yolunu ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from yonetim.kullanici_yonetimi.models.user_manager import UserManager

class TestRoleManagement(unittest.TestCase):
    def setUp(self):
        # Her test için benzersiz DB dosyası
        self.db_path = f"test_role_mgr_{uuid.uuid4().hex}.db"
        
        # UserManager'ı başlat (DB otomatik oluşur)
        self.user_manager = UserManager(self.db_path)
        
        # Test için admin kullanıcısı oluştur
        self.admin_id = 1 # UserManager __init__ içinde admin oluşturuyor

    def tearDown(self):
        if self.user_manager:
            try:
                # Varsa açık bağlantıları kapat (UserManager yapısına bağlı)
                pass
            except:
                pass
        
        # DB dosyasını sil
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception as e:
                print(f"Uyarı: DB silinemedi {self.db_path}: {e}")

    def test_default_permissions_generation(self):
        """Varsayılan yetkilerin doğru oluşturulduğunu test et"""
        perms = self.user_manager.get_permissions()
        print(f"Toplam yetki sayısı: {len(perms)}")
        
        # Örnek modüllerin yetkilerini kontrol et
        modules_to_check = ['sdg', 'reporting', 'csrd', 'social']
        for mod in modules_to_check:
            mod_perms = [p for p in perms if p['module'] == mod]
            self.assertTrue(len(mod_perms) >= 4, f"{mod} modülü için en az 4 yetki olmalı (CRUD)")
            
            actions = [p['action'] for p in mod_perms]
            self.assertIn('read', actions)
            self.assertIn('create', actions)
            self.assertIn('update', actions)
            self.assertIn('delete', actions)

    def test_role_crud(self):
        """Rol oluşturma, güncelleme ve silme testi"""
        # 1. Rol Oluştur
        role_data = {
            'name': 'test_role',
            'display_name': 'Test Rolü',
            'description': 'Test açıklaması',
            'is_system_role': False,
            'is_active': True,
            'permission_ids': [] 
        }
        role_id = self.user_manager.create_role(role_data, created_by=self.admin_id)
        
        # Hata durumunda logu görmek için
        if role_id == -1:
            print("Rol oluşturma başarısız. Mevcut roller:")
            conn = self.user_manager.get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM roles")
            print(c.fetchall())
            conn.close()
            
        self.assertGreater(role_id, 0, "Rol oluşturulamadı")
        
        # Rolü getir ve kontrol et
        role = self.user_manager.get_role_by_id(role_id)
        self.assertEqual(role['name'], 'test_role')
        
        # 2. Rol Güncelle (Yetki ekleyerek)
        perms = self.user_manager.get_permissions()
        perm_ids = [p['id'] for p in perms[:5]] # İlk 5 yetkiyi al
        
        update_data = {
            'display_name': 'Test Rolü Güncel',
            'permission_ids': perm_ids
        }
        success = self.user_manager.update_role_full(role_id, update_data, updated_by=self.admin_id)
        self.assertTrue(success, "Rol güncellenemedi")
        
        # Güncellemeyi kontrol et
        role = self.user_manager.get_role_by_id(role_id)
        self.assertEqual(role['display_name'], 'Test Rolü Güncel')
        
        role_perms = self.user_manager.get_role_permissions(role_id)
        role_perm_ids = [p['id'] for p in role_perms]
        for pid in perm_ids:
            self.assertIn(pid, role_perm_ids, f"Yetki ID {pid} role atanmamış")
            
        # 3. Rol Sil
        success = self.user_manager.delete_role(role_id, deleted_by=self.admin_id)
        self.assertTrue(success, "Rol silinemedi")
        
        # Silinen rolü kontrol et (soft delete olduğu için is_active=0 olmalı)
        role = self.user_manager.get_role_by_id(role_id)
        self.assertEqual(role['is_active'], 0, "Rol pasif yapılmadı (silinmedi)")

    def test_user_permissions(self):
        """Kullanıcı yetki kontrolü testi"""
        # Yeni bir kullanıcı oluştur
        cursor = self.user_manager.get_connection().cursor()
        cursor.execute("""
            INSERT INTO users (username, email, first_name, last_name, password_hash, is_active) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('testuser', 'test@example.com', 'Test', 'User', 'hash', 1))
        user_id = cursor.lastrowid
        self.user_manager.get_connection().commit()
        
        # Rol oluştur ve yetki ata (ör: sdg.read)
        perms = self.user_manager.get_permissions()
        sdg_read = next(p for p in perms if p['name'] == 'sdg.read')
        
        role_data = {
            'name': 'sdg_viewer',
            'permission_ids': [sdg_read['id']]
        }
        role_id = self.user_manager.create_role(role_data, created_by=self.admin_id)
        
        # Kullanıcıya rolü ata
        cursor.execute("INSERT INTO user_roles (user_id, role_id, assigned_by) VALUES (?, ?, ?)", (user_id, role_id, self.admin_id))
        self.user_manager.get_connection().commit()
        
        # Yetki kontrolü
        has_perm = self.user_manager.has_permission(user_id, 'sdg.read')
        self.assertTrue(has_perm, "Kullanıcıda sdg.read yetkisi olmalı")
        
        has_perm = self.user_manager.has_permission(user_id, 'sdg.delete')
        self.assertFalse(has_perm, "Kullanıcıda sdg.delete yetkisi olmamalı")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
