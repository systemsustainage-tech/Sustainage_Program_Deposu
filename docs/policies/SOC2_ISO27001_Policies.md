# Sustainage Güvenlik ve Uyumluluk Politikaları

Bu doküman, Sustainage platformunun SOC 2 ve ISO 27001 standartlarına uyumunu sağlamak amacıyla oluşturulan temel güvenlik politikalarını içerir.

## 1. Erişim Kontrol Politikası (Access Control Policy)

### Amaç
Bilgi varlıklarına yetkisiz erişimi önlemek.

### Kurallar
*   **En Az Yetki Prensibi:** Kullanıcılara yalnızca işlerini yapmaları için gereken en düşük yetki seviyesi tanımlanır (Role-Based Access Control - RBAC).
*   **Kullanıcı Kimlik Doğrulama:**
    *   Tüm kullanıcılar benzersiz bir kullanıcı adı ve güçlü bir şifreye sahip olmalıdır.
    *   Şifreler Argon2 veya bcrypt algoritmaları ile hashlenerek saklanır.
    *   Yönetici hesapları için İki Faktörlü Doğrulama (2FA) zorunludur.
*   **Oturum Yönetimi:**
    *   Belirli bir süre işlem yapılmayan oturumlar otomatik olarak sonlandırılır.
    *   Başarısız giriş denemeleri (brute-force) izlenir ve hesap geçici olarak kilitlenir.

## 2. Log Yönetimi ve İzleme Politikası (Logging & Monitoring Policy)

### Amaç
Güvenlik olaylarını tespit etmek ve hesap verebilirliği sağlamak.

### Kurallar
*   **Denetim İzleri (Audit Logs):**
    *   Kritik işlemler (giriş/çıkış, veri silme, yetki değişimi) `audit_logs` tablosunda kayıt altına alınır.
    *   Her kayıt; Kullanıcı ID, IP Adresi, İşlem Türü, Zaman Damgası ve Etkilenen Kaynak bilgisini içerir.
*   **Hata İzleme:**
    *   Sistem hataları `system_logs` tablosunda seviyelerine göre (INFO, ERROR, CRITICAL) saklanır.
    *   Kritik hatalar otomatik izleme sistemi tarafından tespit edilir ve yöneticilere e-posta ile bildirilir.
*   **Log Koruması:** Log kayıtları değiştirilemez ve yetkisiz erişime karşı korunur. Düzenli olarak arşivlenir.

## 3. Veri Güvenliği ve Şifreleme Politikası (Data Security & Encryption Policy)

### Amaç
Verilerin gizliliğini ve bütünlüğünü korumak.

### Kurallar
*   **İletim Halindeki Veriler:** Tüm veri trafiği TLS 1.2 veya üzeri protokoller (HTTPS) üzerinden şifrelenir.
*   **Durağan Veriler (Data at Rest):**
    *   Kritik kullanıcı verileri (şifreler, API anahtarları) şifreli olarak saklanır.
    *   Veritabanı düzenli olarak yedeklenir ve yedekler güvenli bir lokasyonda saklanır.
*   **Veri İzolasyonu:** SaaS yapısında her şirketin verisi mantıksal olarak (`company_id`) izole edilir.

## 4. Olay Müdahale Planı (Incident Response Plan)

### Amaç
Güvenlik ihlallerine hızlı ve etkili müdahale etmek.

### Adımlar
1.  **Tespit:** İzleme sistemi veya kullanıcı bildirimi ile olayın fark edilmesi.
2.  **Analiz:** Olayın kapsamının ve etkisinin belirlenmesi.
3.  **Karantina:** Etkilenen sistemlerin veya hesapların geçici olarak devre dışı bırakılması.
4.  **Düzeltme:** Güvenlik açığının kapatılması ve sistemin temizlenmesi.
5.  **Raporlama:** Olayın kök neden analizi ve alınan önlemlerin raporlanması.

## 5. İş Sürekliliği ve Yedekleme (Business Continuity & Backup)

*   Veritabanı günlük olarak otomatik yedeklenir.
*   Son 30 günün yedekleri saklanır.
*   Yedekleme sistemi düzenli olarak test edilir (Restore testleri).

---
*Son Güncelleme: 2026-01-31*
*Onaylayan: Güvenlik Yöneticisi*
