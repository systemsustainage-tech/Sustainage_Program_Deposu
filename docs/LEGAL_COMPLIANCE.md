# Yasal Uyum ve Dokümantasyon (Legal Compliance)

Bu belge, Sustainage platformunun yasal uyumluluk özelliklerini ve geliştirici notlarını içerir.

## 1. Yasal Dokümanlar

Platformda aşağıdaki yasal dokümanlar mevcuttur ve `/legal/` altında sunulmaktadır:

*   **Gizlilik Politikası (Privacy Policy):** `/legal/privacy` - Kişisel verilerin toplanması, kullanımı ve korunması.
*   **Hizmet Seviyesi Anlaşması (SLA):** `/legal/sla` - Uptime garantisi (%99.5) ve destek süreçleri.
*   **Veri İşleme Sözleşmesi (DPA):** `/legal/dpa` - GDPR ve KVKK uyumlu veri işleme şartları.

### Şablonlar
Bu dokümanların HTML şablonları `templates/legal/` dizininde bulunur:
*   `privacy.html`
*   `sla.html`
*   `dpa.html`

## 2. Çerez Yönetimi (Cookie Consent)

Kullanıcıların çerez kullanımını onaylaması için bir banner mekanizması eklenmiştir.

*   **Mekanizma:** `localStorage` kullanılarak kullanıcının onayı tarayıcıda saklanır.
*   **Anahtar:** `cookieConsent` (Değer: `'true'`)
*   **Davranış:** Eğer `cookieConsent` anahtarı yoksa, sayfa yüklendikten 1 saniye sonra banner gösterilir. "Kabul Et" butonuna basıldığında banner gizlenir ve onay saklanır.
*   **Kod:** `templates/base.html` içinde JavaScript bloğu.

## 3. GDPR ve KVKK Uyumu

### Veri Güvenliği
*   Parolalar `Argon2` ile hashlenmektedir.
*   Tüm trafik SSL/TLS üzerinden şifrelenir.
*   Veritabanı yedekleri şifreli olarak saklanabilir (konfigürasyona bağlı).

### Kullanıcı Hakları
Kullanıcılar, Gizlilik Politikası'nda belirtilen iletişim kanalları üzerinden verilerini silme, düzeltme veya erişme talebinde bulunabilirler.

## 4. Geliştirici Notları

Yeni bir yasal gereksinim eklendiğinde:
1.  İlgili HTML şablonunu `templates/legal/` altında oluşturun.
2.  `web_app.py` dosyasına yeni bir route ekleyin.
3.  `templates/base.html` footer kısmına linki ekleyin.
