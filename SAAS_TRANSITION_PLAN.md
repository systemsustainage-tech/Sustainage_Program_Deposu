# SaaS ve Çok Kiracılı (Multi-Tenant) Mimari Geçiş Planı

Bu belge, Sustainage projesinin mevcut "Masaüstü/Tekil Sunucu" yapısından, tam ölçekli "SaaS / Bulut Tabanlı Çok Kiracılı" mimariye geçiş stratejisini tanımlar.

## 1. Mevcut Durum Analizi (Güncel: 29.01.2026)

### Tamamlananlar
*   **Veritabanı Altyapısı:** Tüm kritik tablolarda `company_id` sütunu mevcut ve veri izolasyonu sağlanıyor.
*   **Oturum Yönetimi:** `session['company_id']` ile şirket bağlamı taşınıyor.
*   **Middleware:** `require_company_context` dekoratörü `remote_web_app.py` içinde tanımlı ve Dashboard gibi ana sayfalarda aktif.
*   **Dashboard:** SaaS uyumlu hale getirildi, `esrs_stats`, `module_stats` gibi eksik değişkenler tamamlandı.
*   **Supplier Portal:** Ayrı bir Blueprint olarak izole edildi.

### Devam Eden / Eksik Kısımlar
*   **Dekoratör Yaygınlaştırma:** Çoğu modül (Carbon, Energy, Water vb.) hala manuel `session.get('company_id', 1)` kontrolü kullanıyor. `@require_company_context` dekoratörü tüm rotalara uygulanmalı.
*   **API İzolasyonu:** `/api/` endpoint'lerinin tamamının `require_company_context` ile korunduğundan emin olunmalı.
*   **Varsayılan Şirket Riski:** Kodda hala `session.get('company_id', 1)` şeklinde, bulunamazsa ID=1'e (varsayılan şirket) düşen mantıklar var. Bu, SaaS ortamında güvenlik riski oluşturabilir; ID bulunamazsa oturum kapatılmalı.

---

## 2. Geçiş Stratejisi (Adım Adım)

### Aşama 1: Sıkı İzolasyon (Backend Enforcement) - %80 Tamamlandı
*   **Hedef:** Geliştirici hatasını engellemek.
*   **Durum:** `require_company_context` hazır. Dashboard ve Admin panellerinde aktif.
*   **Yapılacak:** Tüm 19 modülün rotalarına (`/carbon`, `/water`, `/social` vb.) bu dekoratör eklenmeli.

### Aşama 2: SPA Uyumlu API Katmanı - %40 Tamamlandı
*   **Hedef:** Vue.js frontend'in çok kiracılı yapıda çalışabilmesi.
*   **Durum:** API endpoint'leri kısmen mevcut.
*   **Yapılacak:** Modüllerin veri alışverişini tamamen JSON API üzerinden yapması sağlanmalı.

### Aşama 3: Veritabanı Şema Doğrulaması - %90 Tamamlandı
*   **Hedef:** Tüm kritik tabloların `company_id` içerdiğinden emin olmak.
*   **Durum:** Çoğu tablo güncellendi. `survey_questions` ve yeni eklenen modüller kontrol edilmeli.

---

## 3. Sonraki Adımlar
1.  `remote_web_app.py` içindeki tüm modül rotalarına `@require_company_context` ekle.
2.  Manuel `session.get('company_id', 1)` kullanımlarını temizle veya `g.company_id` kullanımına çevir.
3.  `verify_saas_features.py` testini tüm modülleri kapsayacak şekilde genişlet.
