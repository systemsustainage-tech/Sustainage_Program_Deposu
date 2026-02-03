
"""
BU DOSYA GÜNCELLENMİŞTİR.
--------------------------------------------------
Açıklama: Web programı için uyarlanmış e-posta servisi testi.
Hedef Dosya: tests/test_email_service.py
--------------------------------------------------
"""
import sys
import os
import subprocess

# Yeni test dosyasının yolu
target_test = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_email_service.py'))

def main():
    print("=" * 70)
    print(f"WEB TEST BAŞLATILIYOR: {os.path.basename(sys.argv[0])}")
    print(f"Hedef: {target_test}")
    print("-" * 70)
    
    if not os.path.exists(target_test):
        print(f"HATA: Hedef test dosyası bulunamadı: {target_test}")
        input("Çıkmak için Enter'a basın...")
        return

    try:
        # Testi çalıştır
        result = subprocess.run([sys.executable, target_test], cwd=os.path.dirname(target_test))
        
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
