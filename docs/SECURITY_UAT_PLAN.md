# Güvenlik Taraması ve Kullanıcı Kabul Testi (UAT) Planı

## 1. Güvenlik Taraması (Security Scan)

### Araçlar
- **OWASP ZAP (Zed Attack Proxy)**: Web uygulaması güvenlik taraması için.
- **Bandit**: Python kod tabanı statik analizi için.
- **Manuel Kod İncelemesi**: Kritik modüller ve auth akışları için.

### Tarama Kapsamı
1. **Kimlik Doğrulama ve Yetkilendirme**:
   - Brute-force saldırıları (Rate limiting etkin mi?)
   - SQL Enjeksiyonu (Giriş formları ve API parametreleri)
   - Oturum Yönetimi (Session timeout, cookie güvenliği)
2. **Çoklu Kiracı İzolasyonu**:
   - Bir kiracının verisine başka bir kiracı erişebiliyor mu? (TenantAwareModel doğrulaması)
   - API uç noktalarında `company_id` sızıntısı var mı?
3. **Veri Güvenliği**:
   - Hassas veriler (Parola, TOTP secret) şifreli mi?
   - `.env` ve config dosyalarında düz metin secret var mı? (Verify_env aracı ile kontrol edildi)

### Aksiyon Planı
- [ ] Bandit ile statik kod analizi çalıştır: `bandit -r backend/`
- [ ] OWASP ZAP ile `http://localhost:5000` üzerinde otomatik tarama başlat.
- [ ] Kritik bulguları `security_scan_report_final.txt` dosyasına kaydet ve önceliklendir.

---

## 2. Kullanıcı Kabul Testi (UAT) Senaryoları

Bu testler, son kullanıcı deneyimini ve işlevsel gereksinimleri doğrulamak içindir.

### Test Ortamı
- **URL**: `http://localhost:5000` (veya test sunucusu)
- **Kullanıcılar**:
  - `admin` (Süper Admin)
  - `manager_a` (Şirket A Yöneticisi)
  - `user_b` (Şirket B Kullanıcısı)

### Senaryo 1: Çoklu Kiracı İzolasyonu
1. **Adım**: `manager_a` ile giriş yap ve yeni bir ESG verisi ekle.
2. **Adım**: `user_b` ile giriş yap.
3. **Beklenen Sonuç**: `user_b`, `manager_a` tarafından eklenen veriyi GÖREMEMELİ.

### Senaryo 2: Rate Limiting
1. **Adım**: Giriş sayfasında 1 dakika içinde 60'tan fazla hatalı istek gönder.
2. **Beklenen Sonuç**: `429 Too Many Requests` hatası alınmalı ve IP/User engellenmeli.

### Senaryo 3: Raporlama Performansı
1. **Adım**: Büyük veri seti (10.000+ kayıt) ile "Yıllık Entegre Rapor" oluştur.
2. **Beklenen Sonuç**: Rapor oluşturma süresi < 10 saniye olmalı ve sunucu kilitlenmemeli (Async process kontrolü).

### Senaryo 4: Lisans Kısıtlaması
1. **Adım**: İzin verilmeyen bir IP adresinden API isteği gönder (X-Forwarded-For header simülasyonu ile).
2. **Beklenen Sonuç**: `403 Forbidden` ve "License Violation" hatası dönmeli.

## 3. Onay ve Canlıya Geçiş
- Tüm kritik (High/Critical) güvenlik açıkları kapatılmalı.
- UAT senaryolarının %100'ü başarıyla geçilmeli.
- Performans testlerinde (Load Test) 200 eşzamanlı kullanıcıda hata oranı < %1 olmalı.
