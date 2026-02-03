# Sustainage Felaket Kurtarma Planı (Disaster Recovery Plan)

## 1. Genel Bakış
Bu belge, Sustainage platformunda olası veri kaybı, sistem çökmesi veya felaket durumlarında uygulanacak kurtarma prosedürlerini tanımlar.

**Amaç:** İş sürekliliğini sağlamak ve veri kaybını en aza indirmek (RPO ve RTO hedeflerine uygun olarak).

## 2. Yedekleme Stratejisi

### 2.1. Otomatik Yedekleme Programı
Sistem, Celery Beat zamanlayıcısı aracılığıyla aşağıdaki periyotlarda otomatik yedekleme alır:

- **Günlük Tam Yedek (Daily Full Backup):**
  - **Zaman:** Her gece 02:00
  - **Kapsam:** Veritabanı (SQLite) + Kullanıcı Dosyaları (uploads, exports, reports) + Konfigürasyonlar
  - **Saklama Süresi:** 30 Gün (otomatik temizlenir)
  
- **Saatlik Veritabanı Yedeği (Hourly DB Backup):**
  - **Zaman:** Her saat başı (XX:00)
  - **Kapsam:** Sadece Veritabanı (SQLite)
  - **Saklama Süresi:** 24 Saat (veya yapılandırmaya göre)

### 2.2. Yedekleme Konumu
Yedekler şifrelenmiş ZIP formatında saklanır:
1. **Yerel Disk:** `backend/data/backups/` dizininde.
2. **Bulut Depolama:** `CloudStorageManager` entegrasyonu ile yapılandırılmış bulut sağlayıcıya (örn. AWS S3, Azure Blob veya Yerel Simülasyon) otomatik yüklenir.

## 3. Doğrulama ve Testler (Verification)

### 3.1. Otomatik Doğrulama
Her yedekleme işlemi sonrasında ve talep üzerine `verify_backup` fonksiyonu çalıştırılır:
- ZIP arşivinin bütünlüğü (CRC kontrolü) test edilir.
- SQLite veritabanı geçici bir alana çıkarılır ve `PRAGMA integrity_check` komutu ile yapısal bütünlüğü doğrulanır.

### 3.2. Manuel Doğrulama Scripti
Düzenli aralıklarla (haftalık önerilir) manuel test yapılmalıdır:
```bash
python tools/verify_backup_restore.py
```
Bu script, canlı veritabanına dokunmadan bir test yedeği oluşturur ve geri yükleme simülasyonu yapar.

## 4. Kurtarma Prosedürleri (Recovery Procedures)

### 4.1. Senaryo A: Veritabanı Bozulması (Database Corruption)
Veritabanı dosyası bozulduysa veya yanlışlıkla veri silindiyse:

1. **Servisi Durdurun:**
   ```bash
   # Uzak sunucuda
   sudo systemctl stop sustainage
   ```

2. **Mevcut Durumu Koruyun (Opsiyonel ama Önerilir):**
   Mevcut bozuk veritabanını `sdg_desktop.sqlite.corrupted` olarak yeniden adlandırın.

3. **En Son Sağlam Yedeği Belirleyin:**
   `backend/data/backups` klasöründeki veya buluttaki en güncel yedeği bulun.

4. **Geri Yükleme:**
   
   **Yöntem 1: Otomatik Script ile (Eğer erişilebiliyorsa)**
   ```python
   from backend.modules.database.backup_recovery_manager import BackupRecoveryManager
   mgr = BackupRecoveryManager('/path/to/db')
   mgr.restore_backup('/path/to/backup.zip')
   ```
   
   **Yöntem 2: Manuel**
   - ZIP dosyasını açın.
   - `database/sdg_desktop.sqlite` dosyasını `backend/data/` altına kopyalayın.
   - Dosya izinlerinin doğru olduğundan emin olun (örn. `www-data` kullanıcısı).

5. **Servisi Başlatın:**
   ```bash
   sudo systemctl start sustainage
   ```

### 4.2. Senaryo B: Sunucu Kaybı (Total Server Loss)
Sunucu tamamen erişilemez hale gelirse:

1. **Yeni Sunucu Kurulumu:**
   - İşletim sistemi ve bağımlılıkları yükleyin (Python, Redis vb.).
   - Proje kodlarını Git üzerinden çekin.

2. **Verilerin Geri Yüklenmesi:**
   - Bulut depolamadan en son "Full Backup" dosyasını indirin.
   - ZIP dosyasını `backend/data/backups` altına koyun.
   - Manuel geri yükleme (Yöntem 2) ile veritabanı ve dosyaları (`files/` klasörü altındakileri `backend/` altındaki ilgili klasörlere) geri yükleyin.

3. **Sistemi Başlatın:**
   - Servisleri başlatın ve `tools/verify_full_system.py` ile kontrol edin.

## 5. İletişim ve Sorumluluklar

- **Sistem Yöneticisi:** [İsim/İletişim] - Kurtarma operasyonunu yönetir.
- **Veri Sorumlusu:** [İsim/İletişim] - Veri kaybı durumunda paydaşları bilgilendirir.

---
*Son Güncelleme: 03.02.2026*
