"""
BU DOSYA OTOMATİK OLUŞTURULMUŞ BİR KISAYOLDUR.
--------------------------------------------------
Açıklama: Bu test dosyası 'test_memory_usage.py' dosyasını çalıştırır. Otomatik oluşturulmuştur.
Orijinal Dosya: c:\SDG\tests\performance\test_memory_usage.py
--------------------------------------------------
"""
import sys
import os
import subprocess
import time

# Orijinal dosyanın yolu
original_file = r"c:\SDG\tests\performance\test_memory_usage.py"

def main():
    print("=" * 70)
    print(f"TEST BAŞLATILIYOR: {os.path.basename(sys.argv[0])}")
    print(f"Hedef: {original_file}")
    print("-" * 70)
    
    if not os.path.exists(original_file):
        print(f"HATA: Orijinal dosya bulunamadı!")
        input("Çıkmak için Enter'a basın...")
        return

    try:
        # Çalışma dizinini orijinal dosyanın olduğu yere ayarla (import sorunlarını önlemek için)
        original_dir = os.path.dirname(original_file)
        env = os.environ.copy()
        env["PYTHONPATH"] = r"c:\SDG" + os.pathsep + os.path.dirname(original_dir) + os.pathsep + env.get("PYTHONPATH", "")
        
        # Testi çalıştır
        result = subprocess.run([sys.executable, original_file], cwd=original_dir, env=env)
        
        print("-" * 70)
        if result.returncode == 0:
            print("✅ TEST BAŞARIYLA TAMAMLANDI")
        else:
            print(f"❌ TEST HATAYLA SONLANDI (Kod: {result.returncode})")
            
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")

    print("=" * 70)
    input("\nPencereyi kapatmak için Enter'a basın...")

if __name__ == "__main__":
    main()
