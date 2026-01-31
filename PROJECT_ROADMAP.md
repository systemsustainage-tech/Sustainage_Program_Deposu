# Sustainage Proje Yol Haritası (Faz 2 & 3)

Bu belge, Sustainage projesinin `trae_prompts_2_status.md` dosyasındaki "Orta Vade" ve "Uzun Vade" hedeflerine yönelik uygulama planını içerir.

## Faz 1: Temel Sistem ve Stabilizasyon (TAMAMLANDI)
*   Tüm 29 modülün backend/frontend entegrasyonu.
*   Uzak sunucu deploy süreçleri ve şema senkronizasyonu.
*   Kritik hata düzeltmeleri (500/502 hataları, güvenlik açıkları).
*   Çeviri altyapısı ve temel UI iyileştirmeleri.

---

## Faz 2: Modernizasyon ve İleri Özellikler (AKTİF)
**Hedef:** Kullanıcı deneyimini modernleştirmek ve yapay zeka yeteneklerini derinleştirmek.

### 2.1. Kullanıcı Arayüzü Modernizasyonu (JS Framework Geçişi)
*   **Mevcut Durum:** Jinja2 server-side rendering + jQuery.
*   **Hedef:** Vue.js 3 (Composition API) veya React entegrasyonu.
*   **Strateji:** Hibrit geçiş (Incremental Adoption).
    *   Mevcut Flask şablonları korunacak.
    *   Etkileşimi yüksek bileşenler (Dashboard, Grafik Panelleri, Veri Giriş Tabloları) Vue.js bileşenlerine dönüştürülecek.
    *   API-First yaklaşımıyla backend endpoint'leri JSON dönecek şekilde optimize edilecek.
*   **Adımlar:**
    1.  Frontend build sistemi (Vite/Webpack) kurulumu.
    2.  `base.html` içine Vue mount point eklenmesi.
    3.  Pilot modül (örn. Dashboard) seçilip dönüştürülmesi.

### 2.2. Rol ve Yetki Yönetimi (RBAC) Genişletme
*   Mevcut `user_companies` ve `roles` tablolarının detaylandırılması.
*   Modül bazlı ince ayarlı yetkiler (Read-Only, Editor, Admin).
*   UI üzerinde yetki matrisi yönetim ekranı.

### 2.3. İleri Yapay Zeka Entegrasyonu
*   **Senaryo Analizleri:** TCFD ve İklim Riski modüllerinde "What-If" senaryoları (örn. karbon fiyatı 100€ olursa kârlılık etkisi).
*   **Öneri Sistemi:** Kullanıcı verilerine göre eksik SDG/GRI göstergelerini öneren ML modeli.
*   **Global Mevzuat Takibi:** Scraping botları ile AB/Global mevzuat değişikliklerinin taranması ve özetlenmesi.

---

## Faz 3: Pilot Testler ve İteratif Geliştirme (PLANLAMA)
**Hedef:** Gerçek kullanıcı verileriyle sistemi doğrulamak ve iyileştirmek.

### 3.1. Pilot Test Planı
*   **Hedef Kitle:** 3 farklı sektörden (Üretim, Enerji, Hizmet) pilot firma.
*   **Süreç:**
    1.  **Onboarding:** Firma verilerinin içeri aktarılması.
    2.  **Kullanım:** 2 haftalık aktif veri girişi ve raporlama.
    3.  **Geri Bildirim:** Anket ve mülakat ile UX sorunlarının tespiti.

### 3.2. Sorumlu Ekipler (Sanal)
*   **Core Backend:** API, Veritabanı, Güvenlik (Python/Flask).
*   **Frontend UX:** Vue.js dönüşümü, UI Tasarım.
*   **AI/Data Science:** Raporlama modelleri, Senaryo algoritmaları.
*   **QA/Test:** Otomasyon testleri, Pilot kullanıcı desteği.

### 3.3. İterasyon Döngüsü
*   Haftalık Sprint'ler.
*   Her Cuma Pilot kullanıcılardan gelen hataların triajı.
*   Pazar günleri otomatik deploy ve regresyon testleri (`verify_full_system.py`).

---

## Sonraki Adımlar (Immediate Next Steps)
1.  **JS Framework Altyapısı:** `frontend/` dizini oluşturulup Vite + Vue 3 kurulumunun yapılması.
2.  **API Dönüşümü:** Dashboard verilerini sağlayan API endpoint'lerinin (`/api/dashboard/...`) standartlaştırılması.
3.  **Pilot Kullanıcı Senaryosu:** `tools/create_pilot_data.py` ile örnek pilot veri setinin hazırlanması.
