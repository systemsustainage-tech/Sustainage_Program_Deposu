
import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.modules.database.backup_recovery_manager import BackupRecoveryManager
    from backend.config.database import DB_PATH
except ImportError:
    # Fallback if run directly from tools
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
    from modules.database.backup_recovery_manager import BackupRecoveryManager
    # Mock DB_PATH if needed or hardcode
    DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("=== Yedekleme ve Geri Yükleme Doğrulama Testi ===")
    
    # Backup dir
    backup_dir = os.path.join(os.path.dirname(DB_PATH), 'backups')
    
    # 1. Manager'ı başlat
    print(f"DB Path: {DB_PATH}")
    print(f"Backup Dir: {backup_dir}")
    
    manager = BackupRecoveryManager(DB_PATH, backup_dir)
    
    # 2. Yeni bir yedek oluştur (Test için)
    print("\n[ADIM 1] Test yedeği oluşturuluyor...")
    success, result = manager.create_backup(backup_type='database_only', created_by='test_script', upload_to_cloud=False)
    
    if not success:
        print(f"FAILED: Yedek oluşturulamadı: {result}")
        return
        
    backup_path = result
    print(f"SUCCESS: Yedek oluşturuldu: {backup_path}")
    
    # 3. Yedeği doğrula
    print("\n[ADIM 2] Yedek doğrulanıyor (Restore Testi)...")
    success, message = manager.verify_backup(backup_path)
    
    if success:
        print(f"SUCCESS: {message}")
    else:
        print(f"FAILED: {message}")
        
    print("\n=== Test Tamamlandı ===")

if __name__ == "__main__":
    main()
